import json
import os

import pandas as pd
from celery_once import QueueOnce

from app.worker import celery_app
from app.utils.excel import read_sheet_from_excel
from app.llm.gemini_service import generate_content
from app.utils.filepath import get_file_path, set_file_path
from app.modules.grader_summarizer.service import generate_prompt_for_category, process_llm_category_response


"""
Keys để phân biêt các task là argument của hàm. QueueOnce chỉ cho phép đến từng này.

Cần một cách khác "chính thống" hơn để xây dựng keys.
"""

@celery_app.task(
    bind=True,
    name='grader_summarizer.grade',
    base=QueueOnce,
    once={
        'graceful': True,
        'keys': ['subpath', 'filename', 'jd_schema_filename'],
    },
)
def grade_summarize_task(self, subpath, filename, jd_schema_filename):
    try:
        self.update_state(state='PROGRESS', meta={'status': 'Đang chấm điểm cho các ứng viên...'})
        excel_file_path = get_file_path(subpath, filename)
        jd_schema_file_path = get_file_path('results/jd_quantifier/', jd_schema_filename)

        table, name = read_sheet_from_excel(excel_file_path)
        with open(jd_schema_file_path, "r") as f:
            grading_schema = json.load(f)

        summaries = []
        for index, candidate_answer in table.iterrows():
            # candidate_answer = table.iloc[index].to_dict()
            candidate_answer = candidate_answer.to_dict()
            print(f"Grading candidate: {index + 1}/{len(table)}")
            candidate_summary = {
                'Total score': 0
            }

            # Chấm điểm cho từng category
            for category in grading_schema['scoringCategories']:
                category_name = category['category_name']
                print(f"--- Category: {category_name} ---")
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
                    print(f"----- Grading candidate at attempt {times_grading} -----")
                    response = generate_content(prompt, model="gemini-2.0-flash")
                    try:
                        json_response = json.loads(response.replace('```json\n', '').replace('\n```', ''))
                    except json.decoder.JSONDecodeError as e:
                        print(f"----- => Error when decoding this candidate at {category_name} -----")
                        times_grading += 1
                    else:
                        grading_successful = True
                        print(f"----- => Grading sucessfully at attempt {times_grading} -----")
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
        
        file_name, file_ext = os.path.splitext(os.path.basename(filename))
        result_path = set_file_path("results/grader_summarizer", file_name + "_graded" + file_ext)    
        
        result_df.to_excel(result_path, index=False)    
        return {
            'status': 'success',
            'message': {
                'result_path': result_path,
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': {
                'details': str(e),
            }
        }