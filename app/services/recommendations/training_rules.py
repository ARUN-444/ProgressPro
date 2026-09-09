"""
Training recommendation rules module.
Implements explainable rules TR-001 through TR-005 using sports-science landmarks.
"""

from typing import List
from sqlalchemy.orm import Session

from app.models.workout import Workout
from app.repositories.profile_repo import ProfileRepository
from app.repositories.workout_repo import WorkoutRepository
from app.schemas.recommendation import RecommendationItem
from app.services.analytics.consistency_analyzer import ConsistencyAnalyzer
from app.services.analytics.recovery_analyzer import RecoveryAnalyzer
from app.services.analytics.volume_analyzer import VolumeAnalyzer


class TrainingRulesEngine:
    """Evaluates training volume, recovery fatigue, and consistency against predefined rules."""

    def __init__(self, db: Session):
        self.db = db
        self.volume_analyzer = VolumeAnalyzer(db)
        self.recovery_analyzer = RecoveryAnalyzer(db)
        self.consistency_analyzer = ConsistencyAnalyzer(db)
        self.profile_repo = ProfileRepository(db)
        self.workout_repo = WorkoutRepository(db)

    def evaluate_training_rules(self, user_id: int) -> List[RecommendationItem]:
        """Runs all deterministic training rules and returns actionable recommendations."""
        recommendations: List[RecommendationItem] = []

        recovery = self.recovery_analyzer.analyze_recovery(user_id=user_id, evaluation_window_days=7)
        volume = self.volume_analyzer.analyze_volume(user_id=user_id)
        consistency = self.consistency_analyzer.analyze_consistency(user_id=user_id, evaluation_window_days=30)
        recent_workouts = self.workout_repo.list_by_user(user_id=user_id, limit=10)

        # -------------------------------------------------------------------
        # Rule TR-001: Deload Week Recommended
        # -------------------------------------------------------------------
        high_rpe_sessions = sum(1 for w in recent_workouts if w.rpe is not None and w.rpe >= 8.5)
        if recovery.recovery_score < 55 and high_rpe_sessions >= 3:
            recommendations.append(
                RecommendationItem(
                    rule_id="TR-001",
                    category="RECOVERY",
                    severity="ACTION_REQUIRED",
                    title="Deload Week Recommended",
                    metric_observed={
                        "recovery_score": recovery.recovery_score,
                        "high_rpe_sessions": high_rpe_sessions,
                        "sleep_debt_hours": float(recovery.accumulated_sleep_debt_hours),
                    },
                    rationale=(
                        "Sustained high CNS fatigue and compromised recovery blunt muscle protein synthesis "
                        "and elevate joint injury risk. A planned deload permits supercompensation."
                    ),
                    actionable_guidance=(
                        "Schedule a 1-week deload: decrease total working sets by 40-50% and reduce "
                        "loads by 10-15% while keeping movement technique crisp."
                    ),
                )
            )

        # -------------------------------------------------------------------
        # Rule TR-002: Volume Below Minimum Effective Volume (MEV)
        # -------------------------------------------------------------------
        for mg in volume.muscle_group_breakdown:
            if mg.volume_landmark_status == "below_mev" and mg.effective_working_sets > 0:
                recommendations.append(
                    RecommendationItem(
                        rule_id="TR-002",
                        category="TRAINING",
                        severity="WARNING",
                        title=f"Increase Volume for {mg.muscle_group.title()}",
                        metric_observed={
                            "muscle_group": mg.muscle_group,
                            "weekly_effective_sets": mg.effective_working_sets,
                            "landmark": "below_mev",
                            "mev_target": 10,
                        },
                        rationale=(
                            f"Weekly training volume for {mg.muscle_group} is below the Minimum Effective Volume (MEV) "
                            "threshold (~10 sets/week) necessary to stimulate optimal muscular hypertrophy."
                        ),
                        actionable_guidance=(
                            f"Add 2 to 3 quality working sets per week for {mg.muscle_group} across your scheduled sessions."
                        ),
                    )
                )

        # -------------------------------------------------------------------
        # Rule TR-003: Volume Exceeding Maximum Recoverable Volume (MRV)
        # -------------------------------------------------------------------
        for mg in volume.muscle_group_breakdown:
            if mg.volume_landmark_status == "above_mrv":
                recommendations.append(
                    RecommendationItem(
                        rule_id="TR-003",
                        category="TRAINING",
                        severity="WARNING",
                        title=f"Excessive Volume for {mg.muscle_group.title()}",
                        metric_observed={
                            "muscle_group": mg.muscle_group,
                            "weekly_effective_sets": mg.effective_working_sets,
                            "landmark": "above_mrv",
                            "mrv_threshold": 20,
                        },
                        rationale=(
                            f"Working volume for {mg.muscle_group} exceeds the Maximum Recoverable Volume (~20-22 sets/week). "
                            "Excessive volume generates junk fatigue that impairs growth and neuromuscular recovery."
                        ),
                        actionable_guidance=(
                            f"Reduce weekly sets for {mg.muscle_group} to the 12-16 sets (MAV) range to enhance quality."
                        ),
                    )
                )

        # -------------------------------------------------------------------
        # Rule TR-005: Low Workout Consistency
        # -------------------------------------------------------------------
        if consistency.adherence_percentage < 60.0 and consistency.total_workouts_completed > 0:
            recommendations.append(
                RecommendationItem(
                    rule_id="TR-005",
                    category="TRAINING",
                    severity="ACTION_REQUIRED",
                    title="Re-establish Baseline Training Consistency",
                    metric_observed={
                        "adherence_percentage": consistency.adherence_percentage,
                        "actual_frequency": consistency.actual_frequency_per_week,
                        "target_frequency": consistency.target_frequency_per_week,
                    },
                    rationale=(
                        "Training consistency is the primary driver of motor unit adaptation and progressive overload. "
                        "An adherence rate below 60% impairs long-term progress."
                    ),
                    actionable_guidance=(
                        "Commit to an achievable 3-day Full Body routine rather than a higher-frequency split "
                        "until you establish an unbroken 4-week workout streak."
                    ),
                )
            )

        return recommendations
