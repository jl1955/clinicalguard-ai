from openai import AsyncOpenAI
import os
import json

client = AsyncOpenAI(
    base_url="https://inference.baseten.co/v1",
    api_key=os.environ["BASETEN_API_KEY"]
)

# Override with BASETEN_MODEL in .env to switch models.
# Available on this account: openai/gpt-oss-120b | nvidia/Nemotron-120B-A12B |
#   deepseek-ai/DeepSeek-V3.1 | MiniMaxAI/MiniMax-M2.5 | zai-org/GLM-4.7
_MODEL = os.environ.get("BASETEN_MODEL", "deepseek-ai/DeepSeek-V3.1")

PHI_SYSTEM_PROMPT = """You are a PHI/PII detection system for clinical trials.
Detect Protected Health Information in the input text.

PHI types:
- PATIENT_NAME: Real patient full or partial names
- MRN: Medical Record Numbers (e.g. MRN-1234, #4821)
- DOB: Dates of birth
- TRIAL_ID: Trial participant IDs (e.g. PT-001, SUBJ-2024)
- SSN: Social Security Numbers
- EMAIL: Personal email addresses
- PHONE: Phone numbers
- ADDRESS: Physical addresses
- DIAGNOSIS: Patient-specific diagnoses tied to identifiers

Risk scoring:
- high: any PATIENT_NAME, MRN, SSN, DOB found
- medium: EMAIL, PHONE, ADDRESS, TRIAL_ID found
- low: nothing found

You MUST respond ONLY with valid JSON matching this exact structure:
{
  "phi_detected": true,
  "risk_score": "high",
  "entities": [
    {"type": "PATIENT_NAME", "value": "John Smith", "confidence": 0.98}
  ],
  "reason": "Patient name and MRN detected"
}"""


async def scan_for_phi(prompt: str) -> dict:
    response = await client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": PHI_SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze for PHI:\n\n{prompt}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
        max_tokens=500
    )
    result = json.loads(response.choices[0].message.content)
    return result
