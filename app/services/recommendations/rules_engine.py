"""
Recommendation coordinator engine.
Aggregates training and nutrition rule evaluations into a unified, explainable audit report.
"""

from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session

from app.schemas.recommendation import RecommendationItem, RecommendationReportResponse
from app.services.analytics.progress_scorer import ProgressScorer
from app.services.recommendations.nutrition_rules import NutritionRulesEngine
from app.services.recommendations.training_rules import TrainingRulesEngine


class RecommendationEngine:
    """Coordinates evaluation of sports-science training and nutrition rules."""

    def __init__(self, db: Session):
        self.db = db
        self.training_engine = TrainingRulesEngine(db)
        self.nutrition_engine = NutritionRulesEngine(db)
        self.progress_scorer = ProgressScorer(db)

    def generate_report(self, user_id: int) -> RecommendationReportResponse:
        """
        Runs both training and nutrition rule evaluations and bundles them with the current overall progress score.
        """
        training_recs = self.training_engine.evaluate_training_rules(user_id)
        nutrition_recs = self.nutrition_engine.evaluate_nutrition_rules(user_id)
        all_recs: List[RecommendationItem] = training_recs + nutrition_recs

        progress_data = self.progress_scorer.calculate_overall_score(user_id)

        return RecommendationReportResponse(
            generated_at=datetime.now(timezone.utc),
            user_id=user_id,
            overall_progress_score=progress_data.score,
            total_recommendations=len(all_recs),
            recommendations=all_recs,
        )
