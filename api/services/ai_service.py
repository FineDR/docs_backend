# api/services/ai_service.py
import os
import json
import re
import time
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Any

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

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Extract JSON from text that might contain other content or markdown code blocks.
    """
    try:
        # Try to parse the entire text as JSON first
        return json.loads(text)
    except json.JSONDecodeError:
        # If that fails, try to find JSON within the text
        # Look for JSON pattern between curly braces
        json_pattern = r'\{.*\}'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        
        # If still not found, try to extract from markdown code blocks
        # Pattern for ```json ... ```
        json_code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_code_block_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # If still not found, return None
        return None

def make_ai_call(prompt: str, max_retries=3, initial_delay=1) -> str:
    """
    Make an AI call with retry logic and rate limit handling.
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="mistralai/mistral-7b-instruct:free",
                messages=[
                    {"role": "system", "content": "You are a professional CV writer. Always respond with concise, professional text only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
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
                    delay = initial_delay * (2 ** attempt)  # Exponential backoff
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
    """
    if not AI_AVAILABLE:
        print("AI service not available, returning original data")
        return serializer_data
    
    prompt = f"""
    You are a professional CV data formatter. Your task is to clean and structure the following user data 
    into a consistent format suitable for building professional CVs. Please:
    
    1. Standardize all dates to ISO format (YYYY-MM-DD)
    2. Ensure consistent capitalization (proper nouns capitalized)
    3. Remove any irrelevant information or filler words
    4. Clean up any inconsistencies in formatting
    5. Ensure professional language throughout
    6. Fix any invalid URLs or contact information
    7. Improve the career objective to be more professional
    8. Enhance the profile summary to be more compelling
    9. Improve job responsibilities to be more impactful
    10. Enhance project descriptions to highlight achievements
    
    User Data:
    {json.dumps(serializer_data, indent=2)}
    
    Please return only the cleaned JSON object without any additional text or explanation.
    """
    
    try:
        response_text = make_ai_call(prompt)
        
        if not response_text:
            print("AI call failed, returning original data")
            return serializer_data
        
        # Try to parse the response as JSON
        cleaned_data = extract_json_from_text(response_text)
        
        if cleaned_data:
            return cleaned_data
        else:
            print(f"Could not parse AI response as JSON: {response_text}")
            return serializer_data
            
    except Exception as e:
        # If AI processing fails, return the original data
        print(f"AI processing error: {str(e)}")
        return serializer_data

def enhance_cv_data(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance the CV data using AI for better professional presentation.
    """
    if not AI_AVAILABLE:
        print("AI service not available, returning original data")
        return cv_data
    
    # Enhance profile summary
    if cv_data.get('personal_details', {}).get('profile_summary'):
        summary_prompt = f"""
        Improve the following professional summary to make it more compelling and professional:
        "{cv_data['personal_details']['profile_summary']}"
        
        Please return only the improved summary without any additional text.
        """
        
        enhanced_summary = make_ai_call(summary_prompt)
        if enhanced_summary:
            cv_data['personal_details']['profile_summary'] = enhanced_summary
            # Add a small delay to avoid rate limiting
            time.sleep(3)
    
    # Enhance career objectives
    for obj in cv_data.get('career_objectives', []):
        if obj.get('career_objective'):
            obj_prompt = f"""
            Improve the following career objective to make it more professional and compelling:
            "{obj['career_objective']}"
            
            Please return only the improved career objective without any additional text.
            """
            
            enhanced_obj = make_ai_call(obj_prompt)
            if enhanced_obj:
                obj['career_objective'] = enhanced_obj
                # Add a small delay to avoid rate limiting
                time.sleep(3)
    
    # Enhance job responsibilities - batch them to reduce API calls
    responsibilities_to_enhance = []
    for exp in cv_data.get('work_experiences', []):
        for resp in exp.get('responsibilities', []):
            if resp.get('value'):
                responsibilities_to_enhance.append(resp)
    
    if responsibilities_to_enhance:
        # Create a batch prompt for all responsibilities
        resp_prompt = "Improve the following job responsibilities to make them more professional and impactful:\n\n"
        for i, resp in enumerate(responsibilities_to_enhance):
            resp_prompt += f"{i+1}. {resp['value']}\n\n"
        
        resp_prompt += "Please return each improved responsibility on a new line, numbered accordingly."
        
        batch_response = make_ai_call(resp_prompt)
        if batch_response:
            # Parse the batch response
            lines = batch_response.strip().split('\n')
            for i, line in enumerate(lines):
                if i < len(responsibilities_to_enhance):
                    # Remove numbering and clean up
                    improved_resp = re.sub(r'^\d+\.\s*', '', line).strip()
                    if improved_resp:
                        responsibilities_to_enhance[i]['value'] = improved_resp
            
            # Add a longer delay after batch processing
            time.sleep(5)
    
    # Enhance project descriptions - batch them too
    projects_to_enhance = []
    for proj in cv_data.get('projects', []):
        if proj.get('description'):
            projects_to_enhance.append(proj)
    
    if projects_to_enhance:
        proj_prompt = "Improve the following project descriptions to make them more professional and highlight achievements:\n\n"
        for i, proj in enumerate(projects_to_enhance):
            proj_prompt += f"{i+1}. {proj['title']}: {proj['description']}\n\n"
        
        proj_prompt += "Please return each improved description on a new line, starting with the project title."
        
        batch_response = make_ai_call(proj_prompt)
        if batch_response:
            # Parse the batch response
            lines = batch_response.strip().split('\n')
            current_proj = None
            for line in lines:
                if line.strip():
                    if ':' in line:
                        # This is a project title
                        parts = line.split(':', 1)
                        title = parts[0].strip()
                        # Find the project
                        for proj in projects_to_enhance:
                            if proj['title'].lower() == title.lower():
                                current_proj = proj
                                break
                    elif current_proj:
                        # This is the description
                        current_proj['description'] = line.strip()
            
            # Add a longer delay after batch processing
            time.sleep(5)
    
    return cv_data