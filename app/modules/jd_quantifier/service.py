import os
import time
import json
import math

from google import genai

from athina_logger.api_key import AthinaApiKey
from athina_logger.inference_logger import InferenceLogger
from athina_logger.exception.custom_exception import CustomException

def get_prompt(prompt_template: str, scoring_scale_min: int,
               scoring_scale_max: int, job_description: str):
    """
    Generates a prompt by filling in the provided template with the given parameters.

    Args:
        prompt_template (str): The template string for the prompt.
        scoring_scale_min (int): The minimum value on the scoring scale (e.g., 1).
        scoring_scale_max (int): The maximum value on the scoring scale (e.g., 5).
        screening_phase (str): The phase this schema is for (e.g., "Initial Application/Resume Screening").
        job_description (str): The job description to be included in the prompt.

    Returns:
        str: The generated prompt with the parameters filled in.

    Raises:
        Exception: If the minimum score is not less than the maximum score.
    """
    # Check if the minimum score is less than the maximum score
    if scoring_scale_min >= scoring_scale_max:
        raise Exception("The min score of the scale must be less than the max score.")
    
    # Replace single braces with double braces in the template first
    escaped_template = prompt_template.replace("{", "{{").replace("}", "}}")
    
    # But restore the actual format placeholders
    escaped_template = escaped_template.replace("{{scoring_scale_min}}", "{scoring_scale_min}")
    escaped_template = escaped_template.replace("{{scoring_scale_max}}", "{scoring_scale_max}")
    escaped_template = escaped_template.replace("{{job_description}}", "{job_description}")
    
    # Fill the prompt template with values of parameters
    prompt = escaped_template.format(
        scoring_scale_min=scoring_scale_min,
        scoring_scale_max=scoring_scale_max,
        job_description=job_description
    )
    
    return prompt

def check_valid_schema(scoring_schema: dict) -> bool:
    """
    Validates a scoring schema dictionary.

    Checks performed:
    1.  Input is a dictionary.
    2.  Attempts to find a list containing dictionary elements (assumed scoring categories).
    3.  Attempts to find a key within those dictionaries representing weight percentage
        (looks for keys containing 'weight' or 'percent' with numeric values).
    4.  Checks if the sum of these numeric weight percentages is close to 100.
    5.  Handles potential missing keys, non-list/dict structures, and non-numeric weights gracefully.

    Args:
        scoring_schema: The dictionary representing the parsed JSON scoring schema.

    Returns:
        True if the schema appears valid (primarily based on weights summing to 100
        and basic structure being identifiable), False otherwise.
    """
    print(f"--- Running Validation ---") # Optional: for debugging

    # 1. Basic Input Type Check
    if not isinstance(scoring_schema, dict):
        print("Validation Failed: Input is not a dictionary.")
        return False
    if not scoring_schema:
        print("Validation Failed: Input dictionary is empty.")
        return False

    category_list = None
    category_list_key = None

    # 2. Find the list containing category dictionaries
    for key, value in scoring_schema.items():
        if isinstance(value, list):
            # Check if the list primarily contains dictionaries
            if value and all(isinstance(item, dict) for item in value):
                 # Assume the first such list found is the one we want
                category_list = value
                category_list_key = key
                print(f"Found candidate category list under key: '{category_list_key}'") # Optional
                break
            elif not value: # It's an empty list
                 # Could be the category list, but empty. Handle later.
                 category_list = value
                 category_list_key = key
                 print(f"Found candidate category list (empty) under key: '{category_list_key}'") # Optional
                 break # Treat empty list as potential category list for now

    if category_list is None:
        print("Validation Failed: Could not find a list containing dictionaries (potential scoring categories).")
        return False

    # Handle case where the identified list is empty
    if not category_list:
        print("Validation Failed: The identified category list is empty. Schema requires categories.")
        # Assuming an empty schema isn't valid if weights are expected.
        # If a schema with 0 categories summing to 0 *is* valid, change this logic.
        return False

    weight_key = None
    # 3. Find the weight percentage key within the first category dictionary
    first_category = category_list[0] # We know the list is not empty here
    if isinstance(first_category, dict):
        for key, value in first_category.items():
            # Heuristic: key name suggests weight AND value is numeric
            key_lower = key.lower()
            if ('weight' in key_lower or 'percent' in key_lower) and isinstance(value, (int, float)):
                weight_key = key
                print(f"Found candidate weight key: '{weight_key}'") # Optional
                break # Assume the first match is the one we want

    if weight_key is None:
        print(f"Validation Failed: Could not find a suitable weight key (containing 'weight' or 'percent' with a numeric value) in the first item of list '{category_list_key}'.")
        return False

    # 4. Calculate the sum of weights
    total_weight = 0.0
    found_items = 0
    for index, item in enumerate(category_list):
        if not isinstance(item, dict):
            print(f"Validation Failed: Item at index {index} in list '{category_list_key}' is not a dictionary.")
            return False

        weight_value = item.get(weight_key) # Use .get() for safety

        if weight_value is None:
            # Treat missing weight key in an item as invalid
            print(f"Validation Failed: Weight key '{weight_key}' missing in item at index {index} of list '{category_list_key}'.")
            return False

        if not isinstance(weight_value, (int, float)):
             # Treat non-numeric weight as invalid
            print(f"Validation Failed: Weight value '{weight_value}' for key '{weight_key}' in item at index {index} is not numeric.")
            return False

        total_weight += float(weight_value) # Convert to float for consistent summation
        found_items += 1

    print(f"Calculated total weight: {total_weight} from {found_items} items.") # Optional

    # 5. Check if the sum is close to 100
    # Use math.isclose for robust floating-point comparison
    # abs_tol=1e-9 is a small tolerance for potential floating point inaccuracies
    is_sum_valid = math.isclose(total_weight, 100.0, abs_tol=1e-9)

    if not is_sum_valid:
        print(f"Validation Failed: Total weight {total_weight} is not equal to 100.")
        return False

    print("--- Validation Successful ---")
    return True

def gen_and_log_schema_from_jd(jd_path: str, 
                               scoring_scale_min: int, scoring_scale_max: int, 
                               prompt_template: str,
                               google_api_key: str, model: str, athina_api_key: str):
    """
    Generates a scoring schema from a job description using a specified Google GenAI model,
    validates it, calculates its trustworthiness score, logs the details, and returns the schema.

    Args:
        jd_path (str): Path to the job description file.
        scoring_scale_min (int): Minimum score for the schema scale.
        scoring_scale_max (int): Maximum score for the schema scale.
        google_api_key (str): API key for Google GenAI.
        model (str): The specific Google GenAI model to use (e.g., 'gemini-1.5-pro').
        prompt_template (str): The prompt template to be filled in.
        athina_api_key (str): API key for Athina Logger.

    Returns:
        dict or None: The generated scoring schema as a dictionary if successful,
                      None otherwise.

    Raises:
        FileNotFoundError: If the job description file at jd_path does not exist.
        Exception: Catches and prints various exceptions during the process
                   (e.g., API errors, JSON parsing errors, validation errors).
                   Returns None in these cases after printing the error.
    """
    try:
        # 1. Read Job Description
        print(f"  Reading job description from: {jd_path}")
        with open(jd_path, 'r', encoding='utf-8') as file:
            job_description = file.read()

        # 2. Generate Prompt (using globally loaded prompt_template)
        print("  Generating prompt...")
        prompt = get_prompt(
            prompt_template=prompt_template,
            scoring_scale_min=scoring_scale_min,
            scoring_scale_max=scoring_scale_max,
            job_description=job_description
        )

        # 3. Setup Google GenAI Client
        print(f"  Initializing Google GenAI client for model: {model}")
        client = genai.Client(api_key=google_api_key)

        # 4. Call LLM and Time it
        print("  Calling Google GenAI model...")
        start_time = time.perf_counter()
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        end_time = time.perf_counter()
        response_time = end_time - start_time
        print(f"  Received response in {response_time:.4f} seconds.")

        # 5. Extract and Clean Response
        print("  Cleaning response...")
        raw_response_text = response.text
        # Remove potential markdown code block fences and strip whitespace
        clean_json_string = raw_response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()

        # 6. Parse JSON
        print("  Parsing JSON response...")
        scoring_schema = json.loads(clean_json_string)

        # 7. Validate Schema
        print("  Validating schema...")
        response_validity = check_valid_schema(scoring_schema=scoring_schema)
        print(f"  Schema validity: {response_validity}")

        # # 8. Setup and Use Cleanlab TLM
        # # API key is assumed to be set via environment variable outside this function
        # print("  Getting Cleanlab TLM trustworthiness score...")
        # tlm = TLM(options={"log": ["explanation"]}) # Re-init TLM object if needed per call, or init globally
        # tlm_response = tlm.get_trustworthiness_score(prompt, response=str(scoring_schema)) # Pass string response
        # trustworthiness_score = tlm_response.get('trustworthiness_score', None)
        # trustworthiness_explanation = tlm_response.get('log', {}).get('explanation', 'No explanation provided.')
        # print(f"  Trustworthiness score: {trustworthiness_score}")

        # 9. Setup and Use Athina Logger
        print("  Setting up Athina Logger...")
        AthinaApiKey.set_api_key(athina_api_key) # Set key before logging

        # 10. Log Inference
        print("  Logging inference to Athina...")
        InferenceLogger.log_inference(
            prompt_slug="npo_hr_screening_schema_writer_jd", # Hardcoded slug from dev notebook
            prompt=prompt,
            language_model_id=model,
            response=str(scoring_schema), # Log the string representation
            response_time=int(response_time * 1000), # Log time in milliseconds
            custom_attributes={
                "response_validity": response_validity,
                "trustworthiness_score": None,
                "trustworthiness_explanation": None,
                "raw_response_text": raw_response_text, # Log raw response for debugging
                "job_description_file": os.path.basename(jd_path),
            }
        )
        print("  Logging successful.")

        # 11. Return Schema
        return scoring_schema

    except FileNotFoundError as e:
        print(f"Error: Job description file not found at {jd_path}. Details: {e}")
        raise # Re-raise file not found error as it's critical

    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON response from model {model} for {jd_path}.")
        print(f"  Raw response was: {raw_response_text}")
        print(f"  Cleaned string was: {clean_json_string}")
        print(f"  Error details: {e}")
        # Optionally log this failure state to Athina as well
        try:
            AthinaApiKey.set_api_key(athina_api_key)
            InferenceLogger.log_inference(
                prompt_slug="npo_hr_screening_schema_writer_jd",
                prompt=prompt if 'prompt' in locals() else "Prompt generation failed or skipped",
                language_model_id=model,
                response=raw_response_text if 'raw_response_text' in locals() else "No response captured",
                response_time=int(response_time * 1000) if 'response_time' in locals() else 0,
                custom_attributes={
                    "response_validity": False,
                    "error_type": "JSONDecodeError",
                    "error_message": str(e),
                    "job_description_file": os.path.basename(jd_path),
                }
            )
        except Exception as log_e:
            print(f"  Additionally, failed to log JSON error to Athina: {log_e}")
        return None

    except CustomException as e: # Athina specific exception
        print(f"Error logging to Athina for model {model} on {jd_path}: Status {e.status_code} - {e.message}")
        # Depending on severity, you might still return the schema or None
        # Let's return the schema if we got this far, as logging was the final step.
        return scoring_schema if 'scoring_schema' in locals() else None

    except Exception as e:
        # Catch any other unexpected errors
        import traceback
        print(f"An unexpected error occurred for model {model} on {jd_path}: {e}")
        print(traceback.format_exc()) # Print full traceback for debugging
        # Attempt to log the generic error
        try:
            AthinaApiKey.set_api_key(athina_api_key)
            InferenceLogger.log_inference(
                prompt_slug="npo_hr_screening_schema_writer_jd",
                prompt=prompt if 'prompt' in locals() else "Prompt generation failed or skipped",
                language_model_id=model,
                response=f"Unexpected error: {e}",
                response_time=int(response_time * 1000) if 'response_time' in locals() else 0,
                custom_attributes={
                    "response_validity": False, # Assume invalid on unexpected error
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                     "job_description_file": os.path.basename(jd_path),
                }
            )
        except Exception as log_e:
             print(f"  Additionally, failed to log the unexpected error to Athina: {log_e}")
        return None # Return None on unexpected errors