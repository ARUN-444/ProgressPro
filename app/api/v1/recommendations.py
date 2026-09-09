"""
Explainable recommendations API endpoints.
Evaluates training volume, recovery, and nutrition against predefined sports-science rules.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.recommendation import RecommendationItem, RecommendationReportResponse
from app.services.recommendations.nutrition_rules import NutritionRulesEngine
from app.services.recommendations.rules_engine import RecommendationEngine
from app.services.recommendations.training_rules import TrainingRulesEngine

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get(
    "/fitness",
    response_model=List[RecommendationItem],
    summary="Get explainable fitness and training recommendations",
)
def get_fitness_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Evaluates training volume landmarks, fatigue indicators, and consistency against sports-science rules."""
    engine = TrainingRulesEngine(db)
    return engine.evaluate_training_rules(current_user.id)


@router.get(
    "/nutrition",
    response_model=List[RecommendationItem],
    summary="Get explainable nutrition and macro recommendations",
)
def get_nutrition_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Evaluates Mifflin-St Jeor TDEE energy balance, protein sufficiency, and hydration rules."""
    engine = NutritionRulesEngine(db)
    return engine.evaluate_nutrition_rules(current_user.id)


@router.get(
    "/report",
    response_model=RecommendationReportResponse,
    summary="Get unified fitness & nutrition progress audit report",
)
def get_recommendation_report(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Generates a complete diagnostic audit with overall progress score and all actionable recommendations."""
    engine = RecommendationEngine(db)
    return engine.generate_report(current_user.id)
