def compute_final_status(
    phi_result: dict,
    compliance_result: dict,
) -> dict:
    """
    Combine PHI and compliance results into final governance decision.

    Rules:
    - phi_detected=True AND risk_score=high  → status=flagged, block=True
    - compliance_status=NON_COMPLIANT        → status=flagged, block=True
    - phi_detected=True AND risk_score=medium → status=flagged, block=False
    - compliance_status=NEEDS_REVIEW         → status=flagged, block=False
    - Everything else                        → status=clean,   block=False
    """
    phi_detected = phi_result.get("phi_detected", False)
    phi_risk = phi_result.get("risk_score", "low")
    compliance_status = compliance_result.get("status", "COMPLIANT")

    if phi_detected and phi_risk == "high":
        entity_types = ", ".join(e["type"] for e in phi_result.get("entities", []))
        return {
            "status": "flagged",
            "block": True,
            "block_reason": f"PHI detected: {entity_types}",
            "risk_score": "high",
            "summary": "BLOCKED — High-risk PHI detected in prompt",
        }

    if compliance_status == "NON_COMPLIANT":
        return {
            "status": "flagged",
            "block": True,
            "block_reason": f"GCP compliance violation: {compliance_result.get('guideline_reference', '')}",
            "risk_score": "high",
            "summary": "BLOCKED — GCP compliance violation",
        }

    if (phi_detected and phi_risk == "medium") or compliance_status == "NEEDS_REVIEW":
        return {
            "status": "flagged",
            "block": False,
            "block_reason": "Medium risk — flagged for human review",
            "risk_score": "medium",
            "summary": "FLAGGED — Forwarded but requires human review",
        }

    return {
        "status": "clean",
        "block": False,
        "block_reason": "",
        "risk_score": "low",
        "summary": "CLEAN — No violations detected",
    }
