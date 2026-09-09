"""
Recovery and sleep debt analysis module.
Computes rolling sleep duration, accumulated sleep debt, and a normalized 0-100 recovery score.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.sleep_repo import SleepRepository
from app.repositories.workout_repo import WorkoutRepository
from app.schemas.analytics import RecoveryResponse


class RecoveryAnalyzer:
    """
    Evaluates recovery readiness and accumulated CNS/systemic fatigue.
    """

    def __init__(self, db: Session):
        self.db = db
        self.sleep_repo = SleepRepository(db)
        self.workout_repo = WorkoutRepository(db)

    def analyze_recovery(
        self,
        user_id: int,
        evaluation_window_days: int = 7,
    ) -> RecoveryResponse:
        """
        Analyzes rolling sleep duration, sleep debt, and computes a composite recovery score (0-100).
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=evaluation_window_days)

        sleep_logs = self.sleep_repo.list_by_user(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=50,
        )

        target_sleep_per_day = Decimal("8.0")

        if not sleep_logs:
            # Baseline assumptions if user has not logged sleep yet
            return RecoveryResponse(
                evaluation_window_days=evaluation_window_days,
                rolling_average_sleep_hours=Decimal("7.0"),
                accumulated_sleep_debt_hours=Decimal("7.0"),
                average_quality_score=Decimal("3.0"),
                recovery_score=70,
                recovery_status="ADEQUATE",
            )

        total_sleep = sum((s.sleep_duration_hours for s in sleep_logs), Decimal("0.0"))
        total_quality = sum((Decimal(str(s.quality_score)) for s in sleep_logs), Decimal("0.0"))
        count = Decimal(str(len(sleep_logs)))

        avg_sleep = total_sleep / count
        avg_quality = total_quality / count

        # Sleep debt calculation
        accumulated_debt = sum(
            (max(Decimal("0.0"), target_sleep_per_day - s.sleep_duration_hours) for s in sleep_logs),
            Decimal("0.0"),
        )

        # Check average workout RPE in this window for fatigue penalty
        recent_workouts = self.workout_repo.list_by_user(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=20,
        )
        rpe_ratings = [w.rpe for w in recent_workouts if w.rpe is not None]
        if rpe_ratings:
            avg_rpe = sum(rpe_ratings, Decimal("0.0")) / Decimal(str(len(rpe_ratings)))
            fatigue_factor = max(Decimal("0.0"), Decimal("100.0") - max(Decimal("0.0"), avg_rpe - Decimal("7.0")) * Decimal("20.0"))
        else:
            fatigue_factor = Decimal("85.0")

        # Composite Recovery Score formula (0 to 100)
        # 55% sleep duration, 35% subjective quality, 10% training fatigue factor
        duration_component = (min(avg_sleep, Decimal("9.0")) / target_sleep_per_day) * Decimal("100.0")
        quality_component = (avg_quality / Decimal("5.0")) * Decimal("100.0")

        raw_score = (
            (Decimal("0.55") * duration_component)
            + (Decimal("0.35") * quality_component)
            + (Decimal("0.10") * fatigue_factor)
        )
        recovery_score = int(max(Decimal("0.0"), min(Decimal("100.0"), raw_score)))

        if recovery_score >= 80:
            status = "OPTIMAL"
        elif recovery_score >= 60:
            status = "ADEQUATE"
        else:
            status = "COMPROMISED"

        return RecoveryResponse(
            evaluation_window_days=evaluation_window_days,
            rolling_average_sleep_hours=avg_sleep.quantize(Decimal("0.1")),
            accumulated_sleep_debt_hours=accumulated_debt.quantize(Decimal("0.1")),
            average_quality_score=avg_quality.quantize(Decimal("0.1")),
            recovery_score=recovery_score,
            recovery_status=status,
        )
