"""
AI service for extracting project status information from transcriptions.
"""
import json
import logging
from typing import Optional, Dict, Any
from openai import OpenAI

from app.core.config import settings
from app.services.openai_service import get_openai_client

logger = logging.getLogger(__name__)


def extract_status_from_transcription(
    transcription_text: str,
    project_name: str,
    client_name: str
) -> Optional[Dict[str, Any]]:
    """
    Extract project status information from transcription text using AI.
    
    Args:
        transcription_text: The transcribed text from the meeting
        project_name: Name of the project (for context)
        client_name: Name of the client (for context)
        
    Returns:
        Dictionary with extracted status fields or None if extraction fails
    """
    openai_client = get_openai_client()
    if not openai_client:
        logger.error("OpenAI client not initialized. Cannot extract status.")
        return None
    
    try:
        # Create prompt for status extraction
        prompt = f"""You are analyzing a project status meeting transcription. Extract the following information and return it as a JSON object.

Project Context:
- Project Name: {project_name}
- Client: {client_name}

Transcription:
{transcription_text}

Extract the following information:
1. **is_on_scope**: Boolean (true/false/null) - Is the project on scope? Look for mentions of scope, scope changes, out of scope, within scope, etc.
2. **is_on_time**: Boolean (true/false/null) - Is the project on time? Look for mentions of deadlines, delays, on schedule, behind schedule, etc.
3. **is_on_budget**: Boolean (true/false/null) - Is the project on budget? Look for mentions of budget, costs, over budget, within budget, financial concerns, etc.
4. **next_delivery**: String or null - What is the next delivery? Extract dates, milestones, deliverables, deadlines mentioned.
5. **risks**: String or null - What are the project risks? Extract any concerns, blockers, issues, challenges, or risks mentioned.

Important:
- Return ONLY valid JSON, no additional text
- Use null for unknown/not mentioned values
- Use true/false for boolean values (not "yes"/"no")
- Be specific and concise in your extractions
- If information is not mentioned, use null

Return format:
{{
    "is_on_scope": true/false/null,
    "is_on_time": true/false/null,
    "is_on_budget": true/false/null,
    "next_delivery": "string or null",
    "risks": "string or null"
}}"""

        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Using gpt-4o-mini for cost efficiency
            messages=[
                {
                    "role": "system",
                    "content": "You are a project management assistant that extracts structured information from meeting transcriptions. Always return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for more consistent extraction
            response_format={"type": "json_object"}  # Force JSON response
        )
        
        # Parse response
        content = response.choices[0].message.content
        if not content:
            logger.error("Empty response from OpenAI")
            return None
        
        # Parse JSON response
        try:
            extracted_data = json.loads(content)
            logger.info(f"Successfully extracted status from transcription")
            return extracted_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response content: {content}")
            return None
            
    except Exception as e:
        logger.error(f"Error extracting status from transcription: {str(e)}")
        return None


def validate_extracted_status(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize extracted status data.
    
    Args:
        data: Raw extracted data from AI
        
    Returns:
        Validated and normalized status data
    """
    validated = {
        "is_on_scope": None,
        "is_on_time": None,
        "is_on_budget": None,
        "next_delivery": None,
        "risks": None
    }
    
    # Validate boolean fields
    for field in ["is_on_scope", "is_on_time", "is_on_budget"]:
        if field in data:
            value = data[field]
            if value is None:
                validated[field] = None
            elif isinstance(value, bool):
                validated[field] = value
            elif isinstance(value, str):
                # Handle string booleans
                if value.lower() in ["true", "yes", "on", "1"]:
                    validated[field] = True
                elif value.lower() in ["false", "no", "off", "0"]:
                    validated[field] = False
                else:
                    validated[field] = None
            else:
                validated[field] = None
    
    # Validate string fields
    if "next_delivery" in data and data["next_delivery"]:
        validated["next_delivery"] = str(data["next_delivery"]).strip()[:1000]  # Limit length
    
    if "risks" in data and data["risks"]:
        validated["risks"] = str(data["risks"]).strip()[:2000]  # Limit length
    
    return validated
