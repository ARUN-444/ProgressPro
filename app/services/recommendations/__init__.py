"""
Deterministic sports-science recommendation engine package.
Evaluates training volume, recovery, and energy balance against predefined rules.
"""

from app.services.recommendations.training_rules import TrainingRulesEngine
from app.services.recommendations.nutrition_rules import NutritionRulesEngine
from app.services.recommendations.rules_engine import RecommendationEngine

__all__ = [
    "TrainingRulesEngine",
    "NutritionRulesEngine",
    "RecommendationEngine",
]
