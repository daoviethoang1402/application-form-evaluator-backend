from app.utils.excel import read_sheet_from_excel, find_resume_column
from app.utils.filepath import get_file_path, set_file_path
from app.modules.resume_parser import service
from app.worker import celery_app

import pandas as pd
import json
import os

@celery_app.task(bind=True, name='resume_parser.extract_cv')
def extract_cv_task(self, subpath: str, filename: str, required_fields: str):
    try:
        self.update_state(state='PROGRESS', meta={'status': 'Đang trích xuất thông tin từ CV...'})

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

        file_path = get_file_path(subpath, filename)
        table, name = read_sheet_from_excel(file_path)
        print(f"Table {name} found")
        resume_column = find_resume_column(table)
        result_df = pd.DataFrame(columns=list(parsed_json_schema.keys()))
        error_list = []

        for index, row in table.iterrows():
            print(f"Processing row {index + 1}/{len(table)}")
            resume_link = row[resume_column]
            if pd.isna(resume_link) or not isinstance(resume_link, str):
                continue

            # Parse the resume. If failed, skip the row
            response_as_str = service.parse_resume(resume_link, required_fields, json_schema)
            try:
                parsed_data = json.loads(response_as_str.replace('```json\n', '').replace('\n```', ''))
            except Exception as e:
                error_list.append({
                    "row": index + 1,
                    "error": str(e),
                    "resume_link": resume_link,
                    "response": response_as_str
                })
                print(f"Error parsing resume at row {index + 1}: {str(e)}")
                continue

            try:
                result_df.loc[index] = parsed_data
            except Exception as e:
                error_list.append({
                    "row": index + 1,
                    "error": str(e),
                    "resume_link": resume_link,
                    "response": response_as_str
                })
                print(f"Error adding parsed data to DataFrame at row {index + 1}: {str(e)}")
                continue
        combined_df = pd.concat([table, result_df], axis=1)

        # Save output file to the results directory
        file_name, file_ext = os.path.splitext(os.path.basename(filename))
        result_path = set_file_path("results/resume_parser", file_name + "_parsed" + file_ext)    
        combined_df.to_excel(result_path, index=False)    
        return {
            'status': 'success',
            'message': {
                'file_path': result_path,
                'errors_while_parsing': error_list,
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': {
                'details': str(e),
                'errors_while_parsing': error_list,
            }
        }