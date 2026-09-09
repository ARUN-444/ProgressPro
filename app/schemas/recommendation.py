"""
Schemas for explainable, deterministic sports-science recommendations.
"""

from datetime import datetime
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    """An individual explainable advice item triggered by a sports-science rule."""
    rule_id: str = Field(description="Unique rule identifier (e.g. 'TR-001', 'NR-002')")
    category: str = Field(description="'TRAINING', 'RECOVERY', 'NUTRITION'")
    severity: str = Field(description="'INFO', 'WARNING', 'ACTION_REQUIRED'")
    title: str = Field(description="Brief headline for the recommendation")
    metric_observed: Dict[str, Any] = Field(
        description="The exact quantitative log values that triggered this rule"
    )
    rationale: str = Field(description="Sports-science justification underpinning this rule")
    actionable_guidance: str = Field(description="Clear, deterministic step for the athlete to take")


class RecommendationReportResponse(BaseModel):
    """Unified progress audit combining all rule evaluations."""
    generated_at: datetime
    user_id: int
    overall_progress_score: int
    total_recommendations: int
    recommendations: List[RecommendationItem]
