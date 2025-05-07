import json
import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from app.services.file_service import read_sheet_from_excel
from app.modules.grader_summarizer.service import generate_prompt_for_category, process_llm_category_response
from app.llm.gemini_service import generate_content

async def grade_and_summarize_candidates(table, grading_schema):
    summaries = []
    for i in range(len(table)):
        candidate_answer = table.iloc[i].to_dict()
        print(f"Candidate: {candidate_answer['Họ & tên của bạn:']}")
        candidate_summary = {
            'Total score': 0
        }

        # Chấm điểm cho từng category
        for category in grading_schema['scoringCategories']:
            category_name = category['category_name']
            print(f"----- Category: {category_name}")
            if category['weight_percent'] == 0:
                continue # Skip to the next category
            # Create prompt
            prompt = generate_prompt_for_category(
                candidate_answer=candidate_answer,
                category=category
            )
            
            # Generate response and parse into JSON
            grading_successful = False
            times_grading = 1
            while not grading_successful:
                print(f"Grading candidate at attempt {times_grading}")
                response = generate_content(prompt, model="gemini-2.0-flash")
                try:
                    json_response = json.loads(response.replace('```json\n', '').replace('\n```', ''))
                except json.decoder.JSONDecodeError as e:
                    print(f"Error when decoding this candidate at {category_name}")
                    times_grading += 1
                else:
                    grading_successful = True
                    print(f"Grading sucessfully at attempt {times_grading}")
            # Return score of that category and its summary
            result = process_llm_category_response(json_response, category)
            candidate_summary['Total score'] += result['category_score'] * category['weight_percent'] / 100
            candidate_summary[category_name] = result['category_reasoning']
        
        # Add into a list of candidates
        candidate_summary['Total score'] = round(candidate_summary['Total score'], 1)
        summaries.append(candidate_summary)

    # Create a DataFrame from the summaries
    summaries_df = pd.DataFrame(summaries)
    result_df = pd.concat([table, summaries_df], axis=1)
    return result_df