import openai
import json
import os
from pathlib import Path

_client = None
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def get_client():
    global _client
    if _client is None:
        _client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / f"{name}.txt").read_text()


async def extract_intent(
    transcript: str,
    language: str,
    customer_context: dict = {}
) -> dict:
    """
    Core brain: extract intent, urgency, suggested actions from transcript.
    """
    client = get_client()
    system_prompt = load_prompt("intent_extraction")
    user_msg = f"""
Language: {language}
Customer Context: {json.dumps(customer_context)}
Transcript: {transcript}
"""
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_msg}
        ],
        response_format={"type": "json_object"},
        max_tokens=800,
        temperature=0.2,
    )

    return json.loads(response.choices[0].message.content)


async def analyze_document(image_base64: str, doc_type: str, customer_record: dict) -> dict:
    """
    GPT-4o Vision: OCR + cross-check against customer records.
    """
    client = get_client()
    system_prompt = load_prompt("document_analysis")

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {
                    "type": "text",
                    "text": f"Document type: {doc_type}\nCustomer record: {json.dumps(customer_record)}\nAnalyze this document."
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                }
            ]}
        ],
        response_format={"type": "json_object"},
        max_tokens=1000,
    )

    return json.loads(response.choices[0].message.content)


async def check_compliance(staff_utterance: str) -> dict:
    """
    Silent compliance whisper: did staff follow RBI disclosure norms?
    """
    client = get_client()
    system_prompt = load_prompt("compliance_check")

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": f"Staff said: {staff_utterance}"}
        ],
        response_format={"type": "json_object"},
        max_tokens=400,
        temperature=0.1,
    )

    return json.loads(response.choices[0].message.content)


async def generate_session_summary(session_data: dict) -> str:
    """Generate end-of-session PDF summary."""
    client = get_client()
    system_prompt = load_prompt("session_summary")

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": json.dumps(session_data)}
        ],
        max_tokens=1500,
    )

    return response.choices[0].message.content