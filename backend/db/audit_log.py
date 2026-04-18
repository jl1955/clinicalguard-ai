import aiosqlite
import json
import os
from datetime import datetime, date

DB_PATH = os.getenv("DATABASE_URL", "governance.db").replace("sqlite+aiosqlite:///./", "")

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS audit_log (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp           TEXT NOT NULL,
    user_id             TEXT NOT NULL,
    session_id          TEXT NOT NULL,
    llm_target          TEXT NOT NULL,
    prompt              TEXT NOT NULL,
    response            TEXT,
    phi_detected        INTEGER DEFAULT 0,
    phi_entities        TEXT DEFAULT '[]',
    risk_score          TEXT DEFAULT 'low',
    compliance_status   TEXT DEFAULT 'COMPLIANT',
    compliance_summary  TEXT DEFAULT '',
    status              TEXT DEFAULT 'clean'
)
"""


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(_CREATE_TABLE)
        await db.commit()


async def insert_log(data: dict) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO audit_log (
                timestamp, user_id, session_id, llm_target, prompt, response,
                phi_detected, phi_entities, risk_score,
                compliance_status, compliance_summary, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("timestamp", datetime.utcnow().isoformat()),
                data["user_id"],
                data["session_id"],
                data["llm_target"],
                data["prompt"],
                data.get("response"),
                int(data.get("phi_detected", 0)),
                json.dumps(data.get("phi_entities", [])),
                data.get("risk_score", "low"),
                data.get("compliance_status", "COMPLIANT"),
                data.get("compliance_summary", ""),
                data.get("status", "clean"),
            ),
        )
        await db.commit()
        return cursor.lastrowid


async def get_logs(limit: int = 100) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()

    result = []
    for row in rows:
        d = dict(row)
        d["phi_entities"] = json.loads(d.get("phi_entities") or "[]")
        result.append(d)
    return result


async def get_stats() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        row = await (
            await db.execute(
                """
                SELECT
                    COUNT(CASE WHEN date(timestamp) = date('now') THEN 1 END) AS total_today,
                    COUNT(CASE WHEN phi_detected = 1              THEN 1 END) AS phi_violations,
                    COUNT(CASE WHEN status = 'flagged'            THEN 1 END) AS flagged,
                    COUNT(CASE WHEN compliance_status = 'NON_COMPLIANT' THEN 1 END) AS compliance_failures
                FROM audit_log
                """
            )
        ).fetchone()

    return {
        "total_today": row[0],
        "phi_violations": row[1],
        "flagged": row[2],
        "compliance_failures": row[3],
    }


async def update_review_status(row_id: int, status: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE audit_log SET status = ? WHERE id = ?", (status, row_id)
        )
        await db.commit()
