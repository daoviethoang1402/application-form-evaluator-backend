def generate_prompt_for_category(candidate_answer: dict, category: dict) -> str:
    """
    Generate an LLM prompt for evaluating a candidate's performance on a scoring category.

    Args:
        candidate_answer (dict): Các câu trả lời của ứng viên, ví dụ:
            {
                "why_gdsc": "...",
                "how_know_gdsc": "...",
                "expectation": "..."
            }
        category (dict): Dictionary chứa thông tin category, bao gồm weight, name, criteria, ...
    
    Returns:
        str: Prompt để gửi lên LLM.
    """
    category_name = category["category_name"]
    weight = category.get("weight_percent", 0)
    criteria = category["criteria"]

    # ===== 1. Candidate responses section =====
    responses_section = "### Candidate Responses:\n"
    for question_key, answer in candidate_answer.items():
        # question_text = question_key.replace("_", " ").capitalize()
        question_text = question_key
        responses_section += f"- {question_text}:\n  > \"{answer}\"\n"

    # ===== 2. Scoring Criteria section =====
    criteria_section = "### Scoring Criteria:\nPlease rate the candidate from 1 to 5 (only pick 1 score for each) based on the following criteria and anchors.\n\n"
    for crit in criteria:
        criteria_section += f"{crit['criterion_name']}. **{crit['criterion_name']}**\n"
        for score, desc in crit["scoring_anchors"].items():
            criteria_section += f"   - {score}: {desc}\n"
        criteria_section += "\n"

    # ===== 3. Output format section =====
    output_section = (
        "### Output Format:\n"
        "```json\n"
        "{\n"
    )
    for crit in criteria:
        output_section += (
            f"  \"{crit['criterion_name']}\": {{\n"
            f"    \"score\": 1,\n"
            f"    \"reasoning\": \"Your justification here.\"\n"
            f"  }},\n"
        )
    output_section = output_section.rstrip(",\n") + "\n}\n```\n\nPlease use Vietnamese when answering and return only the JSON above."

    # ===== Final prompt =====
    final_prompt = (
        f"You are an evaluator scoring a candidate based on their answers to an application form.\n"
        f"The scoring is based on the category: **\"{category_name}\"**, which has a total weight of {weight}%.\n"
        "Below are the candidate’s responses and the scoring criteria.\n\n"
        + responses_section + "\n"
        + criteria_section + "\n"
        + output_section
    )

    return final_prompt

def process_llm_category_response(llm_json_response: dict, category: dict, max_category_score: int = 100) -> dict:
    """
    Tính điểm chuẩn hóa và gom lý do từ response của LLM cho một category.

    Args:
        llm_json_response (dict): JSON từ LLM, key là criterion_name, value là {"score": int, "reasoning": str}
        category (dict): category chứa các criteria để xác định điểm tối đa
        max_category_score (int): điểm tối đa cho phép của category này

    Returns:
        dict: {
            "category_score": float,  # chuẩn hóa từ 0 đến 100
            "category_reasoning": str  # nối tất cả các reasoning
        }
    """
    total_score = 0
    max_score = 0
    all_reasons = []

    for crit in category["criteria"]:
        crit_id = crit["criterion_name"]
        max_score += 5  # mỗi criterion tối đa là 5
        score_info = llm_json_response.get(crit_id, {})
        total_score += int(score_info.get("score", 0))
        reasoning = score_info.get("reasoning", "").strip()
        if reasoning:
            all_reasons.append(f"{crit['criterion_name']}: {reasoning}")

    normalized_score = round(total_score / max_score, 4) * max_category_score if max_score else 0.0
    category_reasoning = "\n".join(all_reasons)

    return {
        "category_score": normalized_score,
        "category_reasoning": category_reasoning
    }
