# Running ClinicalGuard AI — Full Stack

## Prerequisites

Ensure `.env` exists at the project root with your API keys:

```bash
cat .env
# Should contain:
# BASETEN_API_KEY=...
# YOU_API_KEY=...
# ANTHROPIC_API_KEY=...   (optional — needed for claude target)
# OPENAI_API_KEY=...      (optional — needed for chatgpt target)
```

---

## Terminal 1 — Backend

```bash
cd /Users/jli-cims/ai/clinicalguard-ai/backend
uv run uvicorn main:app --reload --port 8000
```

Wait until you see:
```
INFO:     Application startup complete.
```

---

## Terminal 2 — Seed Demo Data (run once)

```bash
cd /Users/jli-cims/ai/clinicalguard-ai/backend
uv run python seed_demo_data.py
# Expected: Seeded 15 demo rows ✓
```

---

## Terminal 3 — Frontend

```bash
cd /Users/jli-cims/ai/clinicalguard-ai/frontend
npm run dev
```

Wait until you see:
```
  ➜  Local:   http://localhost:5173/
```

---

## Open the Dashboard

```
http://localhost:5173
```

---

## Verify Everything Works

```bash
# Health check
curl http://localhost:8000/health
# → {"status":"ok","service":"ClinicalGuard AI"}

# Stats (should show seeded data)
curl http://localhost:8000/audit/stats
# → {"total_today":15+,"phi_violations":9,"flagged":9,"compliance_failures":4}
```

---

## Live End-to-End Tests

Run these with both servers running to see the dashboard update in real time:

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

---

## Final Demo Checklist

- [ ] All 3 curl tests show correct status (flagged / clean / flagged)
- [ ] Dashboard updates within 5 seconds of each request
- [ ] FlagQueue shows flagged rows with Approve/Block buttons
- [ ] Clicking View opens QueryDetail drawer with PHI entities
- [ ] StatsBar numbers update correctly
