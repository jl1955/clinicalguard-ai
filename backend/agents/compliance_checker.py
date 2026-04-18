from youdotcom import You
from youdotcom.models import ResearchEffort
import os

you_client = You(api_key_auth=os.environ["YOU_API_KEY"])


async def check_gcp_compliance(prompt: str) -> dict:
    """
    Check if a statistician prompt violates ICH E6(R3) GCP
    or FDA 21 CFR Part 11 data integrity requirements.
    """

    research_query = f"""
    A clinical trial statistician submitted this query to an AI system:
    "{prompt}"

    Does this query violate any of the following regulations?
    1. ICH E6(R3) Good Clinical Practice (GCP) guidelines
    2. FDA 21 CFR Part 11 (electronic records / data integrity)
    3. HIPAA PHI data handling requirements
    4. ICH E9 Statistical Principles for Clinical Trials

    Answer with:
    - Compliance status: COMPLIANT, NON_COMPLIANT, or NEEDS_REVIEW
    - Which specific guideline is relevant
    - Brief reason (2 sentences max)
    """

    try:
        res = you_client.research(
            input=research_query,
            research_effort=ResearchEffort.LITE,
        )

        content = res.output.content.lower()
        sources = [
            {"title": s.title or "Reference", "url": s.url}
            for s in res.output.sources[:3]
        ]

        if "non_compliant" in content or "violation" in content or "violates" in content:
            status = "NON_COMPLIANT"
        elif "needs review" in content or "unclear" in content or "consider" in content:
            status = "NEEDS_REVIEW"
        else:
            status = "COMPLIANT"

        return {
            "status": status,
            "summary": res.output.content[:300],
            "guideline_reference": "ICH E6(R3) GCP / FDA 21 CFR Part 11",
            "sources": sources,
        }

    except Exception as e:
        return {
            "status": "NEEDS_REVIEW",
            "summary": f"Compliance check unavailable: {str(e)}",
            "guideline_reference": "ICH E6(R3) GCP",
            "sources": [],
        }
