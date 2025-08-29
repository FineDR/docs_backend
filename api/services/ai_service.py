# api/services/ai_service.py
import os
import json
import re
import time
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Any, Union, List

load_dotenv()

# Initialize OpenRouter client
try:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    AI_AVAILABLE = True
    print("OpenRouter initialized successfully")
except Exception as e:
    print(f"Error initializing OpenRouter: {str(e)}")
    AI_AVAILABLE = False


def extract_json_from_text(text: str) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
    """
    Extract one or more JSON objects from text that might contain extra content.
    Returns:
        - dict if one JSON object found
        - list of dicts if multiple JSON objects found
        - None if nothing could be parsed
    """
    results = []

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find all {...} blocks
    json_pattern = r'\{(?:[^{}]|(?R))*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)
    for match in matches:
        try:
            results.append(json.loads(match))
        except json.JSONDecodeError:
            continue

    # Markdown style ```json { ... } ```
    json_code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    code_matches = re.findall(json_code_block_pattern, text, re.DOTALL)
    for match in code_matches:
        try:
            results.append(json.loads(match))
        except json.JSONDecodeError:
            continue

    if not results:
        return None
    return results[0] if len(results) == 1 else results


def merge_dicts(original: Dict[str, Any], cleaned: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Merge cleaned data with original to avoid losing keys.
    If cleaned is a list, take the first element.
    """
    if isinstance(cleaned, list) and cleaned:
        cleaned = cleaned[0]

    if not isinstance(cleaned, dict):
        return original

    merged = original.copy()
    merged.update(cleaned)
    return merged


def make_ai_call(prompt: str, max_retries=3, initial_delay=1) -> str:
    """
    Make an AI call with retry logic and rate limit handling.
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="mistralai/mistral-7b-instruct:free",
                messages=[
                    {"role": "system", "content": "You are a professional CV writer. Always respond with concise, professional JSON or plain text only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800,
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "Django CV App",
                },
            )
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate limit" in error_str.lower():
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    print(f"Rate limit hit. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    print("Rate limit exceeded after retries. Skipping enhancement.")
                    return None
            else:
                print(f"AI call failed: {error_str}")
                return None
    
    return None


def clean_user_data_with_ai(serializer_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send user data from serializer to AI for cleaning and structuring.
    Ensures fallback to original keys if cleaned JSON misses fields.
    """
    if not AI_AVAILABLE:
        print("AI service not available, returning original data")
        return serializer_data
    
    prompt = f"""
    You are a professional CV data formatter. Your task is to clean and structure the following user data 
    into a consistent format suitable for building professional CVs. Please:

    - Standardize all dates to ISO format (YYYY-MM-DD)
    - Ensure consistent capitalization
    - Remove irrelevant info or filler words
    - Use professional language throughout
    - Improve career objectives, summaries, responsibilities, and project descriptions
    - IMPORTANT: Respond with **only valid JSON**, no text outside JSON.

    User Data:
    {json.dumps(serializer_data, indent=2)}
    """
    
    try:
        response_text = make_ai_call(prompt)
        if not response_text:
            print("AI call failed, returning original data")
            return serializer_data
        
        cleaned_data = extract_json_from_text(response_text)
        if cleaned_data:
            return merge_dicts(serializer_data, cleaned_data)
        else:
            print(f"Could not parse AI response as JSON: {response_text}")
            return serializer_data
            
    except Exception as e:
        print(f"AI processing error: {str(e)}")
        return serializer_data


def enhance_cv_data(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance the CV data using AI for better professional presentation.
    """
    if not AI_AVAILABLE:
        print("AI service not available, returning original data")
        return cv_data
    
    # Profile summary
    if cv_data.get('personal_details', {}).get('profile_summary'):
        summary_prompt = f"""
        Improve this professional summary, respond with only plain text:
        "{cv_data['personal_details']['profile_summary']}"
        """
        enhanced_summary = make_ai_call(summary_prompt)
        if enhanced_summary:
            cv_data['personal_details']['profile_summary'] = enhanced_summary
            time.sleep(2)

    # Career objectives
    for obj in cv_data.get('career_objectives', []):
        if obj.get('career_objective'):
            obj_prompt = f"""
            Improve this career objective, respond with only plain text:
            "{obj['career_objective']}"
            """
            enhanced_obj = make_ai_call(obj_prompt)
            if enhanced_obj:
                obj['career_objective'] = enhanced_obj
                time.sleep(2)

    # Responsibilities
    responsibilities_to_enhance = []
    for exp in cv_data.get('work_experiences', []):
        for resp in exp.get('responsibilities', []):
            if resp.get('value'):
                responsibilities_to_enhance.append(resp)

    if responsibilities_to_enhance:
        resp_prompt = {
            "task": "Improve job responsibilities to be professional and impactful",
            "responsibilities": [r["value"] for r in responsibilities_to_enhance]
        }
        batch_response = make_ai_call(
            f"Return only JSON array of improved responsibilities:\n{json.dumps(resp_prompt)}"
        )
        if batch_response:
            improved_list = extract_json_from_text(batch_response)
            if isinstance(improved_list, list):
                for i, val in enumerate(improved_list):
                    if i < len(responsibilities_to_enhance):
                        responsibilities_to_enhance[i]['value'] = val
            time.sleep(4)

    # Projects
    projects_to_enhance = []
    for proj in cv_data.get('projects', []):
        if proj.get('description'):
            projects_to_enhance.append(proj)

    if projects_to_enhance:
        proj_prompt = {
            "task": "Improve project descriptions to highlight achievements",
            "projects": [{"title": p["title"], "description": p["description"]} for p in projects_to_enhance]
        }
        batch_response = make_ai_call(
            f"Return only JSON array of improved projects with title and description:\n{json.dumps(proj_prompt)}"
        )
        if batch_response:
            improved_projects = extract_json_from_text(batch_response)
            if isinstance(improved_projects, list):
                for proj, improved in zip(projects_to_enhance, improved_projects):
                    proj['description'] = improved.get("description", proj['description'])
            time.sleep(4)

    return cv_data
