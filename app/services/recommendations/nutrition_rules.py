"""
Nutrition recommendation rules module.
Implements energy expenditure calculations (Mifflin-St Jeor BMR & TDEE) and explainable rules NR-001 through NR-004.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.fitness_profile import FitnessProfile
from app.repositories.nutrition_repo import NutritionRepository
from app.repositories.profile_repo import ProfileRepository
from app.repositories.weight_repo import WeightRepository
from app.schemas.recommendation import RecommendationItem


def calculate_bmr(gender: str, weight_kg: Decimal, height_cm: Decimal, age_years: int) -> Decimal:
    """
    Computes Basal Metabolic Rate using the Mifflin-St Jeor equation:
    Men: 10 * weight(kg) + 6.25 * height(cm) - 5 * age + 5
    Women: 10 * weight(kg) + 6.25 * height(cm) - 5 * age - 161
    """
    w = weight_kg * Decimal("10.0")
    h = height_cm * Decimal("6.25")
    a = Decimal(str(age_years)) * Decimal("5.0")

    if gender.lower() == "female":
        bmr = w + h - a - Decimal("161.0")
    else:
        bmr = w + h - a + Decimal("5.0")

    return max(Decimal("1000.0"), bmr)


def calculate_tdee(bmr: Decimal, activity_level: str) -> Decimal:
    """
    Multiplies BMR by Physical Activity Level (PAL) multiplier to compute TDEE.
    """
    multipliers = {
        "sedentary": Decimal("1.20"),
        "lightly_active": Decimal("1.375"),
        "moderately_active": Decimal("1.55"),
        "very_active": Decimal("1.725"),
        "extra_active": Decimal("1.90"),
    }
    pal = multipliers.get(activity_level.lower(), Decimal("1.375"))
    return (bmr * pal).quantize(Decimal("1.0"))


class NutritionRulesEngine:
    """Evaluates calorie and macronutrient adherence against scientific guidelines."""

    def __init__(self, db: Session):
        self.db = db
        self.profile_repo = ProfileRepository(db)
        self.weight_repo = WeightRepository(db)
        self.nutrition_repo = NutritionRepository(db)

    def evaluate_nutrition_rules(self, user_id: int) -> List[RecommendationItem]:
        """Evaluates dietary intake logs against energy requirements and ISSN protein guidelines."""
        recommendations: List[RecommendationItem] = []

        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            return recommendations

        today = date.today()
        # Calculate athlete age
        age = today.year - profile.date_of_birth.year - (
            (today.month, today.day) < (profile.date_of_birth.month, profile.date_of_birth.day)
        )

        # Retrieve most recent body weight log or profile fallback
        latest_weight = self.weight_repo.get_latest_by_user(user_id=user_id)
        if latest_weight:
            body_weight = latest_weight.weight_kg
        elif profile.target_weight_kg:
            body_weight = profile.target_weight_kg
        else:
            body_weight = Decimal("75.0")

        bmr = calculate_bmr(profile.gender, body_weight, profile.height_cm, age)
        tdee = calculate_tdee(bmr, profile.activity_level)

        # Fetch recent 7-day nutrition logs
        nutrition_logs = self.nutrition_repo.list_by_user(
            user_id=user_id,
            start_date=today - timedelta(days=7),
            end_date=today,
            limit=14,
        )

        if not nutrition_logs:
            return recommendations

        avg_calories = sum((Decimal(str(n.calories)) for n in nutrition_logs), Decimal("0.0")) / Decimal(str(len(nutrition_logs)))
        avg_protein = sum((n.protein for n in nutrition_logs), Decimal("0.0")) / Decimal(str(len(nutrition_logs)))
        water_logs = [n.water for n in nutrition_logs if n.water is not None]
        avg_water = (sum(water_logs, Decimal("0.0")) / Decimal(str(len(water_logs)))) if water_logs else None

        goal = profile.primary_goal.lower()

        # -------------------------------------------------------------------
        # Rule NR-001: Protein Target Deficit
        # ISSN standard: 1.6 - 2.2 g/kg (Hypertrophy/Strength), 2.0 - 2.4 g/kg (Fat loss deficit)
        # -------------------------------------------------------------------
        if goal == "fat_loss":
            target_g_per_kg = Decimal("2.2")
        elif goal in ("hypertrophy", "strength"):
            target_g_per_kg = Decimal("1.8")
        else:
            target_g_per_kg = Decimal("1.5")

        target_protein = (body_weight * target_g_per_kg).quantize(Decimal("1.0"))
        if avg_protein < (target_protein * Decimal("0.85")):
            deficit_g = int(target_protein - avg_protein)
            recommendations.append(
                RecommendationItem(
                    rule_id="NR-001",
                    category="NUTRITION",
                    severity="ACTION_REQUIRED",
                    title="Increase Daily Dietary Protein",
                    metric_observed={
                        "current_avg_protein_g": float(avg_protein.quantize(Decimal("0.1"))),
                        "target_protein_g": float(target_protein),
                        "target_g_per_kg": float(target_g_per_kg),
                        "deficit_grams": deficit_g,
                    },
                    rationale=(
                        f"Your current protein intake ({avg_protein:.1f}g) is below the recommended "
                        f"{target_g_per_kg}g/kg body weight required to optimize muscle protein synthesis (MPS) "
                        f"and support recovery."
                    ),
                    actionable_guidance=(
                        f"Increase daily protein intake by ~{deficit_g}g per day using lean sources "
                        f"(chicken breast, fish, eggs, tofu, Greek yogurt, or whey protein)."
                    ),
                )
            )

        # -------------------------------------------------------------------
        # Rule NR-002: Caloric Deficit Impairing Hypertrophy
        # -------------------------------------------------------------------
        if goal in ("hypertrophy", "strength") and avg_calories < (tdee - Decimal("100.0")):
            cal_deficit = int(tdee - avg_calories)
            recommendations.append(
                RecommendationItem(
                    rule_id="NR-002",
                    category="NUTRITION",
                    severity="WARNING",
                    title="Caloric Intake Below Maintenance for Hypertrophy",
                    metric_observed={
                        "current_avg_calories": int(avg_calories),
                        "estimated_tdee": int(tdee),
                        "energy_deficit_kcal": cal_deficit,
                    },
                    rationale=(
                        f"Your estimated Total Daily Energy Expenditure is {int(tdee)} kcal, but current intake "
                        f"averages {int(avg_calories)} kcal. Building muscle tissue in an energy deficit is suboptimal."
                    ),
                    actionable_guidance=(
                        f"Increase daily intake by +{cal_deficit + 250} kcal/day to enter a lean caloric surplus "
                        f"(~{int(tdee + Decimal('250.0'))} kcal/day) to support muscular hypertrophy."
                    ),
                )
            )

        # -------------------------------------------------------------------
        # Rule NR-003: Aggressive Caloric Deficit Warning
        # -------------------------------------------------------------------
        if goal == "fat_loss" and avg_calories < (tdee - Decimal("800.0")):
            excessive_deficit = int(tdee - avg_calories)
            recommendations.append(
                RecommendationItem(
                    rule_id="NR-003",
                    category="NUTRITION",
                    severity="WARNING",
                    title="Excessive Caloric Deficit",
                    metric_observed={
                        "current_avg_calories": int(avg_calories),
                        "estimated_tdee": int(tdee),
                        "deficit_kcal": excessive_deficit,
                    },
                    rationale=(
                        f"An aggressive caloric deficit ({excessive_deficit} kcal below TDEE) elevates the risk of "
                        "lean muscle tissue catabolism, metabolic slowdown, and acute fatigue."
                    ),
                    actionable_guidance=(
                        f"Moderate your deficit to 400-500 kcal below TDEE (target ~{int(tdee - Decimal('450.0'))} kcal/day) "
                        "to promote sustainable fat loss while preserving metabolically active muscle."
                    ),
                )
            )

        # -------------------------------------------------------------------
        # Rule NR-004: Daily Hydration Target
        # ACSM recommendation: ~35 mL/kg body weight
        # -------------------------------------------------------------------
        if avg_water is not None:
            recommended_water = (body_weight * Decimal("0.035")).quantize(Decimal("0.1"))
            if avg_water < (recommended_water * Decimal("0.75")):
                recommendations.append(
                    RecommendationItem(
                        rule_id="NR-004",
                        category="NUTRITION",
                        severity="INFO",
                        title="Suboptimal Daily Hydration",
                        metric_observed={
                            "current_avg_water_liters": float(avg_water.quantize(Decimal("0.1"))),
                            "recommended_water_liters": float(recommended_water),
                        },
                        rationale=(
                            "Mild dehydration impairs muscular force transmission, increases perceived exertion (RPE), "
                            "and delays recovery."
                        ),
                        actionable_guidance=(
                            f"Aim for at least {recommended_water} Liters of water daily, especially around your workout sessions."
                        ),
                    )
                )

        return recommendations
