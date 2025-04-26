from app.modules.resume_parser import service, utils
from app.services.file_service import read_all_sheets_from_excel
import pandas as pd 
import json

async def parse_all_resumes_from_excel(file_path, required_fields):
    not_generate_json_schema = True
    times_generate_json_schema = 1
    while not_generate_json_schema:
        print(f"Generating JSON schema at attempt {times_generate_json_schema}")
        json_schema = service.generate_json_schema(required_fields)
        try:
            parsed_json_schema = json.loads(json_schema.replace('```json\n', '').replace('\n```', ''))
        except json.JSONDecodeError as e:
            print(f"Error generating JSON schema: {e}")
            times_generate_json_schema += 1
        else:
            not_generate_json_schema = False
            print(f"JSON schema generated successfully at attempt {times_generate_json_schema}")
            break

    _, table = read_all_sheets_from_excel(file_path)
    resume_column = utils.find_resume_column(table)
    result_df = pd.DataFrame(columns=list(parsed_json_schema.keys()))
    error_list = []

    for index, row in table.iterrows():
        print(f"Processing row {index + 1}/{len(table)}")
        resume_link = row[resume_column]
        if pd.isna(resume_link) or not isinstance(resume_link, str):
            continue

        # Parse the resume. If failed, skip the row
        try:
            parsed_data = service.parse_resume(resume_link, required_fields, json_schema)
        except Exception as e:
            error_list.append({
                "row": index + 1,
                "error": str(e),
                "resume_link": resume_link
            })
            print(f"Error parsing resume at row {index + 1}: {str(e)}")
            continue

        try:
            result_df.loc[index] = parsed_data
        except Exception as e:
            error_list.append({
                "row": index + 1,
                "error": str(e),
                "resume_link": resume_link
            })
            print(f"Error adding parsed data to DataFrame at row {index + 1}: {str(e)}")
            continue
    combined_df = pd.concat([table, result_df], axis=1)

    return result_df, error_list