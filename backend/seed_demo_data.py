import asyncio
import random
from datetime import datetime, timedelta

from db.audit_log import init_db, insert_log

ROWS = [
    # CLEAN (5)
    {
        "user_id": "stat_johnson", "llm_target": "claude",
        "prompt": "What is the recommended ANCOVA approach for a Phase 3 RCT with baseline covariate adjustment?",
        "status": "clean", "risk_score": "low", "phi_detected": 0, "phi_entities": [],
        "compliance_status": "COMPLIANT", "compliance_summary": "Standard statistical methodology query",
        "response": "ANCOVA with baseline as covariate is recommended per ICH E9. Include treatment, baseline value, and stratification factors as covariates.",
    },
    {
        "user_id": "stat_patel", "llm_target": "chatgpt",
        "prompt": "Generate R code for Kaplan-Meier survival curve with log-rank test",
        "status": "clean", "risk_score": "low", "phi_detected": 0, "phi_entities": [],
        "compliance_status": "COMPLIANT", "compliance_summary": "Statistical programming query",
        "response": "Use survfit() from the survival package. Example: fit <- survfit(Surv(time, event) ~ group, data=df)",
    },
    {
        "user_id": "stat_chen", "llm_target": "claude",
        "prompt": "How should I handle missing data imputation in a superiority trial?",
        "status": "clean", "risk_score": "low", "phi_detected": 0, "phi_entities": [],
        "compliance_status": "COMPLIANT", "compliance_summary": "Missing data methodology query",
        "response": "Multiple imputation under MAR assumption is standard. Use MI with rubin's rules for combining estimates per ICH E9(R1).",
    },
    {
        "user_id": "stat_johnson", "llm_target": "chatgpt",
        "prompt": "What sample size is needed for 80% power in a two-arm parallel trial?",
        "status": "clean", "risk_score": "low", "phi_detected": 0, "phi_entities": [],
        "compliance_status": "COMPLIANT", "compliance_summary": "Sample size calculation query",
        "response": "Depends on effect size and alpha. For delta=0.5 SD, alpha=0.05 two-sided, n≈64 per arm.",
    },
    {
        "user_id": "stat_williams", "llm_target": "claude",
        "prompt": "Explain mixed effects model for repeated measures (MMRM) in clinical trials",
        "status": "clean", "risk_score": "low", "phi_detected": 0, "phi_entities": [],
        "compliance_status": "COMPLIANT", "compliance_summary": "Statistical methodology query",
        "response": "MMRM models the covariance structure of repeated measurements directly, handling missing data under MAR without imputation.",
    },
    # PHI VIOLATIONS (5)
    {
        "user_id": "stat_patel", "llm_target": "chatgpt",
        "prompt": "Analyze adverse events for patient John Smith MRN-4821 in trial CT-089",
        "status": "flagged", "risk_score": "high", "phi_detected": 1,
        "phi_entities": [{"type": "PATIENT_NAME", "value": "John Smith", "confidence": 0.99}, {"type": "MRN", "value": "4821", "confidence": 0.97}],
        "compliance_status": "COMPLIANT", "compliance_summary": "PHI detected — query blocked",
        "response": "[BLOCKED] PHI detected: PATIENT_NAME, MRN",
    },
    {
        "user_id": "stat_rodriguez", "llm_target": "claude",
        "prompt": "Patient Jane Doe DOB 03/15/1978 shows concerning lab values, what to do?",
        "status": "flagged", "risk_score": "high", "phi_detected": 1,
        "phi_entities": [{"type": "PATIENT_NAME", "value": "Jane Doe", "confidence": 0.99}, {"type": "DOB", "value": "03/15/1978", "confidence": 0.95}],
        "compliance_status": "COMPLIANT", "compliance_summary": "PHI detected — query blocked",
        "response": "[BLOCKED] PHI detected: PATIENT_NAME, DOB",
    },
    {
        "user_id": "stat_johnson", "llm_target": "chatgpt",
        "prompt": "Subject PT-2024-0891 responded to treatment, can I email dr.smith@hospital.com the results?",
        "status": "flagged", "risk_score": "medium", "phi_detected": 1,
        "phi_entities": [{"type": "TRIAL_ID", "value": "PT-2024-0891", "confidence": 0.92}, {"type": "EMAIL", "value": "dr.smith@hospital.com", "confidence": 0.99}],
        "compliance_status": "NEEDS_REVIEW", "compliance_summary": "Trial ID and email address detected — flagged for review",
        "response": "Forwarded for review — medium risk PHI",
    },
    {
        "user_id": "stat_chen", "llm_target": "claude",
        "prompt": "SSN 123-45-6789 participant had protocol deviation, document this",
        "status": "flagged", "risk_score": "high", "phi_detected": 1,
        "phi_entities": [{"type": "SSN", "value": "123-45-6789", "confidence": 0.99}],
        "compliance_status": "COMPLIANT", "compliance_summary": "SSN detected — query blocked",
        "response": "[BLOCKED] PHI detected: SSN",
    },
    {
        "user_id": "stat_patel", "llm_target": "chatgpt",
        "prompt": "Call participant at 555-867-5309 to follow up on adverse event report",
        "status": "flagged", "risk_score": "medium", "phi_detected": 1,
        "phi_entities": [{"type": "PHONE", "value": "555-867-5309", "confidence": 0.97}],
        "compliance_status": "NEEDS_REVIEW", "compliance_summary": "Phone number detected — flagged for review",
        "response": "Forwarded for review — medium risk PHI",
    },
    # COMPLIANCE VIOLATIONS (3)
    {
        "user_id": "stat_williams", "llm_target": "claude",
        "prompt": "Show me which patients received active drug vs placebo in the treatment arm — I need to unblind the trial",
        "status": "flagged", "risk_score": "high", "phi_detected": 0, "phi_entities": [],
        "compliance_status": "NON_COMPLIANT",
        "compliance_summary": "Unblinding request violates ICH E6(R3) Section 5.5 blind maintenance requirements",
        "response": "[BLOCKED] GCP compliance violation: ICH E6(R3) GCP / FDA 21 CFR Part 11",
    },
    {
        "user_id": "stat_rodriguez", "llm_target": "chatgpt",
        "prompt": "Can I delete these 3 data points that are outliers before the regulatory submission?",
        "status": "flagged", "risk_score": "high", "phi_detected": 0, "phi_entities": [],
        "compliance_status": "NON_COMPLIANT",
        "compliance_summary": "Data deletion violates FDA 21 CFR Part 11 audit trail requirements",
        "response": "[BLOCKED] GCP compliance violation: ICH E6(R3) GCP / FDA 21 CFR Part 11",
    },
    {
        "user_id": "stat_johnson", "llm_target": "claude",
        "prompt": "How do I backfill missing CRF entries with plausible values without detection?",
        "status": "flagged", "risk_score": "high", "phi_detected": 0, "phi_entities": [],
        "compliance_status": "NON_COMPLIANT",
        "compliance_summary": "Data fabrication violates ICH E6(R3) and constitutes research fraud",
        "response": "[BLOCKED] GCP compliance violation: ICH E6(R3) GCP / FDA 21 CFR Part 11",
    },
    # REVIEWED (2)
    {
        "user_id": "stat_chen", "llm_target": "chatgpt",
        "prompt": "Patient 4521-B at site 12 had SAE, reviewing their lab history",
        "status": "approved_override", "risk_score": "medium", "phi_detected": 1,
        "phi_entities": [{"type": "TRIAL_ID", "value": "4521-B", "confidence": 0.88}],
        "compliance_status": "NEEDS_REVIEW", "compliance_summary": "Trial ID detected — reviewed and approved by compliance officer",
        "response": "Lab values for this subject show elevated ALT at Week 4. Recommend hepatic monitoring.",
    },
    {
        "user_id": "stat_patel", "llm_target": "claude",
        "prompt": "Participant home address 123 Oak Street needed for follow-up visit scheduling",
        "status": "confirmed_block", "risk_score": "high", "phi_detected": 1,
        "phi_entities": [{"type": "ADDRESS", "value": "123 Oak Street", "confidence": 0.94}],
        "compliance_status": "COMPLIANT", "compliance_summary": "Home address detected — blocked by compliance officer",
        "response": "[BLOCKED] PHI detected: ADDRESS",
    },
]


async def seed():
    await init_db()

    now = datetime.utcnow()
    # Spread timestamps across today — oldest ~8 hours ago, most recent ~5 min ago
    total = len(ROWS)
    for i, row in enumerate(ROWS):
        minutes_ago = int((total - i) * (480 / total)) + random.randint(0, 5)
        ts = (now - timedelta(minutes=minutes_ago)).isoformat()
        await insert_log({**row, "timestamp": ts, "session_id": f"demo_sess_{i+1}"})

    print(f"Seeded {total} demo rows ✓")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv("../.env")
    asyncio.run(seed())
