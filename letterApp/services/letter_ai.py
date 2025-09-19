import json
import re
from api.services.ai_service import make_ai_call, extract_json_from_text, merge_dicts, AI_AVAILABLE


def generate_clean_letter(data: dict) -> dict:
    """
    Generate a professional letter with AI or a fallback template.
    Ensures all relevant information (recipient, purpose, sender) is included
    while keeping content clean of placeholders and sender name.
    """
    sender_name = data.get("sender_name", "").strip()
    sender_email = data.get("sender_email", "").strip()
    sender_phone = data.get("sender_phone", "").strip()
    recipient_title = data.get("recipient_title", "").strip()
    recipient_name = data.get("recipient", "").strip()
    purpose = data.get("purpose", "").strip()
    additional_context = data.get("context", "").strip()  # optional extra info

    if not AI_AVAILABLE:
        # fallback mode
        subject = f"Application: {purpose.capitalize()}" if purpose else "Letter"
        recipient_address = data.get("recipient_address", "")

        # Construct a simple body including context if provided
        content_lines = [
            f"Dear {recipient_title} {recipient_name},".strip(),
            f"I am writing regarding {purpose}." if purpose else "I am writing to you.",
        ]
        if additional_context:
            content_lines.append(f"{additional_context.strip()}")
        content_lines.append("Please consider this as my formal communication.")
        content = "\n\n".join(content_lines).strip()

        closing_line = "Sincerely,"
        if sender_name:
            closing_line += f" {sender_name}"

        return {
            "subject": subject,
            "recipientAddress": recipient_address,
            "content": content,
            "closing": closing_line,
        }

    # AI mode
    prompt = f"""
    You are a professional letter writer. Using the user input, generate a polished,
    polite, professional letter in JSON format.

    Requirements:
    - Include subject, recipientAddress, content, and closing
    - Use all provided information: recipient title, recipient name, purpose, context
    - Do NOT include closing phrases or sender name inside content
    - Closing should include sender name if provided
    - Clean content: remove placeholders like [Your Name], [senderName], etc.
    - Return ONLY valid JSON

    User Input:
    {json.dumps(data, indent=2)}
    """

    try:
        response_text = make_ai_call(prompt)
        if not response_text:
            return data

        cleaned_data = extract_json_from_text(response_text) or {}

        # Ensure closing exists
        if "closing" not in cleaned_data or not cleaned_data["closing"]:
            cleaned_data["closing"] = f"Sincerely, {sender_name}" if sender_name else "Sincerely,"

        # Clean content from placeholders and sender info
        if "content" in cleaned_data and cleaned_data["content"]:
            content = cleaned_data["content"]
            # Remove closing phrases
            content = re.sub(r"\b(Sincerely|Yours faithfully|Yours sincerely|Best regards),?\b", "", content, flags=re.IGNORECASE)
            # Remove sender name
            if sender_name:
                content = re.sub(re.escape(sender_name), "", content, flags=re.IGNORECASE)
            # Remove bracketed placeholders
            content = re.sub(r"\[[^\]]+\]", "", content)
            # Remove extra whitespace
            content = re.sub(r"\s{2,}", " ", content)
            content = re.sub(r",\s*,", ",", content)
            content = content.strip()
            cleaned_data["content"] = content

        return merge_dicts(data, cleaned_data)

    except Exception as e:
        print(f"Letter AI error: {e}")
        return {
            "subject": data.get("purpose", "Letter"),
            "recipientAddress": data.get("recipient_address", ""),
            "content": "An error occurred while generating the letter.",
            "closing": f"Sincerely, {sender_name}" if sender_name else "Sincerely,",
        }
