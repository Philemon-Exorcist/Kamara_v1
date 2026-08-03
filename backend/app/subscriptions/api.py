from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth import verify_student_token

from .service import (
    enforce_feature_access,
    evaluate_feature_access,
    get_subscription_summary,
    record_usage_event,
)

subscription_router = APIRouter(prefix="/api/v1/subscription", tags=["Subscription"])


class FeatureCheckRequest(BaseModel):
    feature: str
    quantity: int = Field(default=1, ge=1)
    size_bytes: int | None = Field(default=None, ge=0)
    content_chars: int | None = Field(default=None, ge=0)
    has_external_source: bool = False


@subscription_router.get("/me")
async def get_my_subscription(current_user: dict = Depends(verify_student_token)):
    summary = get_subscription_summary(str(current_user.id))
    return summary.__dict__


@subscription_router.post("/check")
async def check_feature_access(
    payload: FeatureCheckRequest,
    current_user: dict = Depends(verify_student_token),
):
    return evaluate_feature_access(
        str(current_user.id),
        payload.feature,
        quantity=payload.quantity,
        size_bytes=payload.size_bytes,
        content_chars=payload.content_chars,
        has_external_source=payload.has_external_source,
    )


@subscription_router.post("/consume")
async def consume_feature_access(
    payload: FeatureCheckRequest,
    current_user: dict = Depends(verify_student_token),
):
    decision = enforce_feature_access(
        str(current_user.id),
        payload.feature,
        quantity=payload.quantity,
        size_bytes=payload.size_bytes,
        content_chars=payload.content_chars,
        has_external_source=payload.has_external_source,
    )
    record_usage_event(str(current_user.id), payload.feature, quantity=payload.quantity)
    return decision

