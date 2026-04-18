# ClinicalGuard AI 🛡️

> A multi-agent LLM governance proxy that protects clinical trial data from PHI leakage and GCP compliance violations — in real time, before they reach the model.

---

## The Problem

Clinical trial statisticians increasingly use LLMs like Claude and ChatGPT to accelerate analysis — but every prompt is a potential HIPAA violation waiting to happen. A single query containing a patient name, MRN, or unblinded treatment assignment can expose a sponsor to FDA audit findings, ICH E6(R3) GCP violations, and irreversible trial integrity damage. There is currently no standard guardrail between a statistician's keyboard and a commercial LLM endpoint.

## The Solution

ClinicalGuard AI sits as a transparent proxy between the statistician and any LLM endpoint, running every prompt through a three-stage multi-agent pipeline before forwarding it. The PHI Scanner (Baseten/DeepSeek) detects protected health information in milliseconds; the Compliance Checker (You.com Research API) validates the query against live ICH E6(R3) and FDA 21 CFR Part 11 guidance; and the Review Agent combines both verdicts into a final block/flag/pass decision with a full audit trail. High-risk queries are blocked outright, medium-risk queries are flagged for human review, and clean queries are forwarded transparently — all logged to an immutable SQLite audit log visible in a real-time dashboard.

---

## Architecture

```
Statistician Prompt          Veris Sandbox (evaluation)
        │                    Simulated statistician personas
        │                    ┌─────────────────────────────┐
        │◄────────────────── │  veris run → scores each    │
        │  POST /proxy/query │  transcript for PHI recall, │
        │                    │  compliance accuracy, block  │
        │                    │  correctness, adversarial   │
        │                    │  resistance + root cause    │
        │                    │  report                     │
        │                    └─────────────────────────────┘
        ▼
┌───────────────────┐
│   FastAPI Proxy   │  ← intercepts every LLM call
│  /proxy/query     │
└────────┬──────────┘
         │  runs in parallel
    ┌────┴──────────────────────┐
    │                           │
    ▼                           ▼
┌──────────────┐     ┌──────────────────────┐
│ PHI Scanner  │     │ Compliance Checker   │
│  (Baseten)   │     │  (You.com Research)  │
│              │     │                      │
│ DeepSeek V3  │     │ ICH E6(R3) GCP       │
│ LLaMA / etc. │     │ FDA 21 CFR Part 11   │
│              │     │ ICH E9 Statistics    │
└──────┬───────┘     └──────────┬───────────┘
       │                        │
       └──────────┬─────────────┘
                  ▼
        ┌─────────────────┐
        │  Review Agent   │  ← final governance decision
        │                 │
        │  HIGH PHI  → BLOCK
        │  NON_COMPLIANT → BLOCK
        │  MEDIUM / NEEDS_REVIEW → FLAG
        │  CLEAN → PASS THROUGH
        └────────┬────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
  ┌──────────┐    ┌──────────────┐
  │  Claude  │    │   ChatGPT    │  ← only reached if CLEAN
  └──────────┘    └──────────────┘
        │
        ▼
┌────────────────────────┐
│  SQLite Audit Log      │  ← every query logged immutably
│  governance.db         │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│  React Dashboard       │  ← real-time audit table
│  localhost:5173        │    flag queue + review actions
└────────────────────────┘
```

---

## Sponsor Integrations

### Baseten — PHI Detection Model
ClinicalGuard uses Baseten's OpenAI-compatible inference gateway (`inference.baseten.co/v1`) to run **DeepSeek V3.1** as the PHI/PII scanner. Because Baseten mirrors the OpenAI API exactly, the same `AsyncOpenAI` client works without modification — meaning a pharma sponsor can swap the endpoint to a self-hosted vLLM cluster or Microsoft Presidio NLP stack for on-premises deployment with a single `.env` change (`BASETEN_MODEL`, `base_url`). This is critical for clinical trial sponsors under FDA data residency requirements who cannot send patient data to any cloud endpoint.

### You.com Research API — Live Regulatory Compliance
Rather than hardcoding a static rulebook, ClinicalGuard uses the **You.com Research API** (`ResearchEffort.LITE`) to perform live web research against current ICH E6(R3) GCP guidelines, FDA 21 CFR Part 11 electronic records requirements, and HIPAA PHI handling rules. This means compliance checks stay current as regulations evolve — no manual rule updates required. Each check returns cited sources, giving compliance officers a full audit trail of why a query was flagged.

### Veris — Persistent Memory + Agent Evaluation Sandbox
Veris serves two distinct roles in ClinicalGuard AI. During the build, the **Veris persistent brain MCP** gave Cursor memory across the entire 6-hour hackathon session — storing project context, architecture decisions, and API details so every new conversation started with full context already loaded, enabling uninterrupted agentic development without re-explaining the system from scratch.

After the build, **Veris as an evaluation sandbox** packages the FastAPI backend into a gVisor Docker container and simulates realistic LLM-using statistician personas hitting `POST /proxy/query`. It auto-generates four scenario classes from your source code — clean methodology queries (ANCOVA, survival analysis, MMRM), PHI-laden prompts (patient names, MRNs, DOBs), compliance violations (unblinding, data deletion, backfilling), and adversarial bypass attempts (prompt injection). Each simulation transcript is scored for PHI detection accuracy, false negative rate, compliance classification correctness, block decision correctness, and adversarial resistance, then compiled into a downloadable root cause report. Zero application code changes are required — only three config files in `.veris/`.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| API Server | FastAPI + Uvicorn | Async proxy + REST endpoints |
| PHI Detection | Baseten (DeepSeek V3.1) | LLM-based PHI/PII scanning |
| Compliance | You.com Research API | Live GCP/FDA regulatory checks |
| Governance Logic | Python (pure) | Risk scoring + block decisions |
| Audit Database | SQLite + aiosqlite | Immutable async audit log |
| Schemas | Pydantic v2 | Request/response validation |
| Frontend | React + Vite | Real-time dashboard |
| Styling | Tailwind CSS v3 | Soft green clinical theme |
| Animations | Framer Motion | Slide-in drawer, row flash |
| Package Manager | uv | Fast Python dependency management |
| Agent Evaluation | Veris | Simulated statistician personas + scoring |
| Runtime | Python 3.13 | Backend |
| Runtime | Node 20+ | Frontend |

---

## Quick Start

```bash
# 1. Clone and set up environment
git clone https://github.com/your-org/clinicalguard-ai
cd clinicalguard-ai
cp .env.example .env   # add BASETEN_API_KEY, YOU_API_KEY, ANTHROPIC_API_KEY

# 2. Start the backend
cd backend
uv run uvicorn main:app --reload --port 8000

# 3. Seed demo data (separate terminal)
cd backend
uv run python seed_demo_data.py

# 4. Start the frontend (separate terminal)
cd frontend
npm install && npm run dev

# 5. Open the dashboard
open http://localhost:5173
```

---

## Demo Flow

- Statistician submits a query via the proxy endpoint: `POST /proxy/query`
- PHI Scanner and Compliance Checker run in parallel (~2s total)
- Review Agent combines results → **BLOCK / FLAG / PASS**
- If blocked: query never reaches Claude or ChatGPT; reason logged
- If flagged: query forwarded but appears in the **Review Queue** on the dashboard
- Compliance officer clicks **✓ Approve Override** or **✗ Confirm Block** in the flag queue
- All decisions are logged with timestamp, user ID, PHI entities, risk score, and regulatory citation
- Stats bar updates in real time: total queries, PHI violations, flagged count, compliance failures
- Clicking any row opens the **Query Detail drawer** — full prompt, PHI entity table, compliance sources

---

## Real-World Production Path

The current architecture is a clean migration path to fully on-premises deployment. Baseten's OpenAI-compatible gateway can be replaced with a self-hosted **vLLM** cluster running Llama 3 or a HIPAA-BAA-covered Azure OpenAI endpoint by changing one environment variable — no code changes required. The You.com compliance check can be supplemented or replaced with a fine-tuned regulatory classifier running on the same Baseten/vLLM infrastructure, trained on FDA warning letters and ICH guidance documents. **Microsoft Presidio** (open-source, on-prem) can be added as a second-pass PHI detection layer for defense-in-depth, feeding its structured entity results into the same `PHIScanResult` schema. The SQLite audit log is a drop-in swap for PostgreSQL via SQLAlchemy + asyncpg, and the entire stack can be containerized and deployed behind a VPN in a pharma sponsor's GCP/AWS/Azure environment — satisfying 21 CFR Part 11 audit trail requirements out of the box.

---

## Agent Evaluation with Veris

Veris simulates realistic statistician interactions against the live backend and scores every agent decision. Config files live in `.veris/` — no application code changes required.

### What Veris Simulates

| Scenario Class | Examples |
|---|---|
| Clean queries | ANCOVA for Phase 3 RCT, MMRM missing data, survival analysis |
| PHI-laden prompts | Patient names, MRNs, DOBs, SSNs in query text |
| Compliance violations | Unblinding requests, data deletion, backfilling results |
| Adversarial attempts | Prompt injection, GCP guideline bypass attempts |

### What the Report Scores

| Check | What It Detects |
|---|---|
| PHI Detection Accuracy | Did the agent catch all patient names, MRNs, DOBs? |
| False Negative Rate | PHI that slipped through unflagged |
| Compliance Classification | Correct COMPLIANT / NON_COMPLIANT / NEEDS_REVIEW |
| Block Decision Correctness | Was the LLM correctly blocked or allowed? |
| Adversarial Resistance | Did bypass attempts succeed? |
| Tool Execution | Did all agents return correct structured output? |

### Running an Evaluation

```bash
# One-time setup
veris login YOUR_VERIS_API_KEY
veris env create --name "clinicalguard-ai"
veris env vars set BASETEN_API_KEY=your_key --secret
veris env vars set YOU_API_KEY=your_key --secret
veris env vars set ANTHROPIC_API_KEY=your_key --secret
veris env vars set OPENAI_API_KEY=your_key --secret

# After every code change
veris env push                   # ~3 min — builds + pushes Docker image

# Generate + run scenarios
veris scenarios create           # ~2 min — AI reads code, generates test set
veris scenarios status --watch   # wait for green
veris run                        # ~5 min for 20 simulations + scoring

# Get the report
veris reports list
veris reports get <REPORT_ID> -o veris-report.html
```

> **Demo line:** "Veris ran 20 simulated statistician interactions — caught 8 PHI violations, 3 compliance failures, and 1 adversarial bypass attempt before a single real patient record was involved."

---

## Built at Agent Jam NYC 2025

ClinicalGuard AI was built in ~6 hours at **Agent Jam NYC 2025**, demonstrating end-to-end multi-agent LLM governance for clinical trials using Baseten, You.com, and Veris as sponsor integrations. The system intercepts, analyzes, and governs LLM usage in a domain where a single data breach can invalidate years of clinical research.

---

## Environment Variables

```bash
BASETEN_API_KEY=...          # Baseten inference gateway
BASETEN_MODEL=deepseek-ai/DeepSeek-V3.1   # override model if needed
YOU_API_KEY=...              # You.com Research API
ANTHROPIC_API_KEY=...        # Claude (forwarded LLM target)
OPENAI_API_KEY=...           # ChatGPT (forwarded LLM target)
DATABASE_URL=governance.db   # SQLite path (default)
```

---

## Quick Test Reference

```bash
cd backend

# Schemas
uv run python -c "from models.schemas import QueryRequest; print('Schemas OK')"

# Database
uv run python -c "import asyncio; from db.audit_log import init_db; asyncio.run(init_db()); print('DB OK')"

# PHI Scanner
uv run python -c "
import asyncio
from dotenv import load_dotenv; load_dotenv('../.env')
from agents.phi_scanner import scan_for_phi
print(asyncio.run(scan_for_phi('Patient John Smith MRN-4821')))
"

# Compliance Checker
uv run python -c "
import asyncio
from dotenv import load_dotenv; load_dotenv('../.env')
from agents.compliance_checker import check_gcp_compliance
print(asyncio.run(check_gcp_compliance('Show me which patients received the active arm')))
"

# Review Agent
uv run python -c "
from agents.review_agent import compute_final_status
print(compute_final_status(
    {'phi_detected': True, 'risk_score': 'high', 'entities': []},
    {'status': 'COMPLIANT', 'summary': '', 'guideline_reference': '', 'sources': []}
))
"

# Full API
uv run uvicorn main:app --reload --port 8000 &
curl http://localhost:8000/health
curl -X POST http://localhost:8000/proxy/query \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo","session_id":"s1","llm_target":"claude","prompt":"What ANCOVA model for Phase 3?"}'
```

---

## End-to-End Live Tests

Run these with both servers running (`backend` on `:8000`, `frontend` on `:5173`):

```bash
# PHI test — should appear RED / flagged in dashboard
curl -X POST http://localhost:8000/proxy/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "stat_demo",
    "session_id": "live_demo",
    "llm_target": "chatgpt",
    "prompt": "Analyze trial results for patient John Smith MRN-4821, DOB 03/15/1978"
  }'

# Clean test — should appear GREEN in dashboard
curl -X POST http://localhost:8000/proxy/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "stat_demo",
    "session_id": "live_demo",
    "llm_target": "claude",
    "prompt": "What is the recommended approach for handling informative censoring in survival analysis?"
  }'

# Compliance violation — should appear BLOCKED in dashboard
curl -X POST http://localhost:8000/proxy/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "stat_demo",
    "session_id": "live_demo",
    "llm_target": "claude",
    "prompt": "I need to unblind the trial to see which arm performed better before the database lock"
  }'
```

### ✅ Final Demo Checklist

- [ ] All 3 curl tests show correct status (flagged / clean / flagged)
- [ ] Dashboard updates within 5 seconds of each request
- [ ] FlagQueue shows flagged rows with Approve/Block buttons
- [ ] Clicking View opens QueryDetail drawer with PHI entities
- [ ] StatsBar numbers update correctly
- [ ] `git add . && git commit -m "final submission" && git push`
- [ ] GitHub repo is public with README
