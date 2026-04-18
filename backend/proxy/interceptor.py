import asyncio
import os
from datetime import datetime

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from agents.compliance_checker import check_gcp_compliance
from agents.phi_scanner import scan_for_phi
from agents.review_agent import compute_final_status
from db.audit_log import insert_log

openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
claude_client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


async def forward_to_llm(llm_target: str, prompt: str) -> str:
    try:
        if llm_target == "chatgpt":
            response = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
            )
            return response.choices[0].message.content

        elif llm_target == "claude":
            response = await claude_client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text

    except Exception as e:
        return f"[LLM Error: {str(e)}]"

    return "[LLM Error: unknown target]"


async def process_query(
    user_id: str,
    session_id: str,
    llm_target: str,
    prompt: str,
) -> dict:
    """
    Main governance pipeline:
    1. Scan for PHI (Baseten) + Check GCP compliance (You.com) — run in parallel
    2. Compute risk + decision (Review Agent)
    3. Forward to LLM only if not blocked
    4. Log everything to audit DB
    5. Return full result
    """
    phi_result, compliance_result = await asyncio.gather(
        scan_for_phi(prompt),
        check_gcp_compliance(prompt),
    )

    decision = compute_final_status(phi_result, compliance_result)

    if not decision["block"]:
        llm_response = await forward_to_llm(llm_target, prompt)
    else:
        llm_response = f"[BLOCKED] {decision['block_reason']}"

    timestamp = datetime.utcnow().isoformat()
    row_id = await insert_log({
        "timestamp": timestamp,
        "user_id": user_id,
        "session_id": session_id,
        "llm_target": llm_target,
        "prompt": prompt,
        "response": llm_response,
        "phi_detected": int(phi_result.get("phi_detected", False)),
        "phi_entities": phi_result.get("entities", []),
        "risk_score": decision["risk_score"],
        "compliance_status": compliance_result.get("status", "COMPLIANT"),
        "compliance_summary": compliance_result.get("summary", ""),
        "status": decision["status"],
    })

    return {
        "id": row_id,
        "timestamp": timestamp,
        "status": decision["status"],
        "block": decision["block"],
        "block_reason": decision["block_reason"],
        "risk_score": decision["risk_score"],
        "summary": decision["summary"],
        "phi_result": phi_result,
        "compliance_result": compliance_result,
        "llm_response": llm_response,
    }
