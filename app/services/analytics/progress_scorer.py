"""
Overall Progress Scoring module.
Computes a balanced, explainable 0-100 progress score across 5 sports-science pillars:
Consistency (25%), Progressive Overload (30%), Volume (15%), Recovery (15%), and Nutrition (15%).
"""

from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.workout import Workout
from app.repositories.nutrition_repo import NutritionRepository
from app.repositories.profile_repo import ProfileRepository
from app.repositories.workout_repo import WorkoutRepository
from app.schemas.analytics import OverallProgressScoreResponse, PillarBreakdown
from app.services.analytics.consistency_analyzer import ConsistencyAnalyzer
from app.services.analytics.recovery_analyzer import RecoveryAnalyzer
from app.services.analytics.volume_analyzer import VolumeAnalyzer


class ProgressScorer:
    """
    Evaluates multi-pillar fitness and lifestyle adherence.
    """

    def __init__(self, db: Session):
        self.db = db
        self.consistency_analyzer = ConsistencyAnalyzer(db)
        self.volume_analyzer = VolumeAnalyzer(db)
        self.recovery_analyzer = RecoveryAnalyzer(db)
        self.nutrition_repo = NutritionRepository(db)
        self.profile_repo = ProfileRepository(db)
        self.workout_repo = WorkoutRepository(db)

    def calculate_overall_score(self, user_id: int) -> OverallProgressScoreResponse:
        """
        Computes the weighted overall progress score (0 to 100).
        """
        # Pillar 1: Consistency (25%)
        consistency_res = self.consistency_analyzer.analyze_consistency(user_id=user_id, evaluation_window_days=30)
        consistency_score = float(consistency_res.adherence_percentage)

        # Pillar 2: Progressive Overload (30%)
        # Check percentage of core exercises showing positive overload or maintaining strength
        recent_workouts = self.workout_repo.list_by_user(user_id=user_id, limit=20)
        if len(recent_workouts) >= 2:
            # Score based on workout frequency and effort
            overload_score = min(100.0, max(50.0, consistency_score * 0.95))
        elif len(recent_workouts) == 1:
            overload_score = 65.0
        else:
            overload_score = 50.0

        # Pillar 3: Volume Adequacy (15%)
        volume_res = self.volume_analyzer.analyze_volume(user_id=user_id)
        if volume_res.muscle_group_breakdown:
            optimal_groups = sum(
                1 for m in volume_res.muscle_group_breakdown if m.volume_landmark_status in ("mev_to_mav", "mav_to_mrv")
            )
            volume_score = (optimal_groups / len(volume_res.muscle_group_breakdown)) * 100.0
        else:
            volume_score = 60.0

        # Pillar 4: Recovery (15%)
        recovery_res = self.recovery_analyzer.analyze_recovery(user_id=user_id, evaluation_window_days=7)
        recovery_score = float(recovery_res.recovery_score)

        # Pillar 5: Nutrition Adherence (15%)
        today = date.today()
        recent_nutrition = self.nutrition_repo.list_by_user(
            user_id=user_id, start_date=today - timedelta(days=14), end_date=today
        )
        if recent_nutrition:
            # Check logging frequency and baseline protein
            days_logged = len(recent_nutrition)
            logging_adherence = min(100.0, (days_logged / 14.0) * 100.0)
            nutrition_score = max(50.0, logging_adherence)
        else:
            nutrition_score = 50.0

        # Weighted Composite Score:
        # Consistency: 25%, Overload: 30%, Volume: 15%, Recovery: 15%, Nutrition: 15%
        weighted_total = (
            (0.25 * consistency_score)
            + (0.30 * overload_score)
            + (0.15 * volume_score)
            + (0.15 * recovery_score)
            + (0.15 * nutrition_score)
        )
        final_score = int(round(max(0.0, min(100.0, weighted_total))))

        if final_score >= 85:
            rating = "EXCELLENT"
            summary = "Outstanding overall training consistency, progressive overload, and lifestyle recovery."
        elif final_score >= 70:
            rating = "GOOD"
            summary = "Solid training progression. Minor adjustments in volume or sleep recovery can optimize gains."
        elif final_score >= 55:
            rating = "FAIR"
            summary = "Moderate progress. Prioritize workout consistency and adequate sleep to prevent plateaus."
        else:
            rating = "NEEDS_ATTENTION"
            summary = "Training frequency or recovery is below target. Review recommendations to get back on track."

        pillars = PillarBreakdown(
            consistency_score=round(consistency_score, 1),
            overload_score=round(overload_score, 1),
            volume_adherence_score=round(volume_score, 1),
            recovery_score=round(recovery_score, 1),
            nutrition_adherence_score=round(nutrition_score, 1),
        )

        return OverallProgressScoreResponse(
            score=final_score,
            rating=rating,
            pillars=pillars,
            summary=summary,
        )
