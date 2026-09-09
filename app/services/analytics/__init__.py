"""
Mathematical analytics subsystem package.
Computes sports-science metrics: volume tonnage, 1RM progression, consistency, progressive overload, recovery, and overall scoring.
"""

from app.services.analytics.volume_analyzer import VolumeAnalyzer
from app.services.analytics.strength_analyzer import StrengthAnalyzer
from app.services.analytics.consistency_analyzer import ConsistencyAnalyzer
from app.services.analytics.overload_detector import OverloadDetector
from app.services.analytics.recovery_analyzer import RecoveryAnalyzer
from app.services.analytics.progress_scorer import ProgressScorer

__all__ = [
    "VolumeAnalyzer",
    "StrengthAnalyzer",
    "ConsistencyAnalyzer",
    "OverloadDetector",
    "RecoveryAnalyzer",
    "ProgressScorer",
]
