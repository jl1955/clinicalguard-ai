from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict


class QueryRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    session_id: str
    llm_target: Literal["claude", "chatgpt"]
    prompt: str


class PHIEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str
    value: str
    confidence: float


class PHIScanResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    phi_detected: bool
    risk_score: Literal["low", "medium", "high"]
    entities: list[PHIEntity]
    reason: str


class ComplianceResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: Literal["COMPLIANT", "NON_COMPLIANT", "NEEDS_REVIEW"]
    summary: str
    guideline_reference: str
    sources: list[dict]


class AuditLogRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: str
    user_id: str
    session_id: str
    llm_target: str
    prompt: str
    response: Optional[str]
    phi_detected: bool
    phi_entities: list[PHIEntity]
    risk_score: str
    compliance_status: str
    compliance_summary: str
    status: str  # clean | flagged | approved_override | confirmed_block


class ReviewAction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    action: Literal["approved_override", "confirmed_block"]
