from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv("../.env")

from db.audit_log import get_logs, get_stats, init_db, update_review_status
from models.schemas import QueryRequest, ReviewAction
from proxy.interceptor import process_query


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="ClinicalGuard AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/proxy/query")
async def proxy_query(request: QueryRequest):
    result = await process_query(
        user_id=request.user_id,
        session_id=request.session_id,
        llm_target=request.llm_target,
        prompt=request.prompt,
    )
    return result


@app.get("/audit/logs")
async def audit_logs(limit: int = 100):
    return await get_logs(limit)


@app.get("/audit/stats")
async def audit_stats():
    return await get_stats()


@app.post("/audit/review/{row_id}")
async def audit_review(row_id: int, action: ReviewAction):
    await update_review_status(row_id, action.action)
    return {"success": True, "id": row_id, "status": action.action}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ClinicalGuard AI"}
