"""
Pydantic schemas package for ProgressPro.
Exports request, response, and analytics data transfer objects (DTOs).
"""

from app.schemas.common import MessageResponse, PaginationParams, PaginatedResponse
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    TokenPayload,
    RefreshTokenRequest,
)
from app.schemas.user import UserRead, UserUpdate
from app.schemas.fitness_profile import (
    FitnessProfileCreate,
    FitnessProfileUpdate,
    FitnessProfileRead,
)
from app.schemas.exercise import (
    ExerciseCreate,
    ExerciseRead,
    ExerciseFilterParams,
)
from app.schemas.workout import (
    ExerciseSetCreate,
    ExerciseSetRead,
    WorkoutExerciseCreate,
    WorkoutExerciseRead,
    WorkoutCreate,
    WorkoutUpdate,
    WorkoutRead,
)
from app.schemas.weight import (
    WeightRecordCreate,
    WeightRecordUpdate,
    WeightRecordRead,
)
from app.schemas.sleep import (
    SleepRecordCreate,
    SleepRecordUpdate,
    SleepRecordRead,
)
from app.schemas.nutrition import (
    NutritionRecordCreate,
    NutritionRecordUpdate,
    NutritionRecordRead,
)
from app.schemas.analytics import (
    MuscleGroupVolume,
    VolumeAnalyticsResponse,
    StrengthHistoryPoint,
    StrengthProgressionResponse,
    ConsistencyResponse,
    ProgressiveOverloadResponse,
    RecoveryResponse,
    PillarBreakdown,
    OverallProgressScoreResponse,
)
from app.schemas.recommendation import (
    RecommendationItem,
    RecommendationReportResponse,
)

__all__ = [
    # Common
    "MessageResponse",
    "PaginationParams",
    "PaginatedResponse",
    # Auth
    "UserRegister",
    "UserLogin",
    "TokenResponse",
    "TokenPayload",
    "RefreshTokenRequest",
    # User
    "UserRead",
    "UserUpdate",
    # Fitness Profile
    "FitnessProfileCreate",
    "FitnessProfileUpdate",
    "FitnessProfileRead",
    # Exercise
    "ExerciseCreate",
    "ExerciseRead",
    "ExerciseFilterParams",
    # Workout
    "ExerciseSetCreate",
    "ExerciseSetRead",
    "WorkoutExerciseCreate",
    "WorkoutExerciseRead",
    "WorkoutCreate",
    "WorkoutUpdate",
    "WorkoutRead",
    # Tracking
    "WeightRecordCreate",
    "WeightRecordUpdate",
    "WeightRecordRead",
    "SleepRecordCreate",
    "SleepRecordUpdate",
    "SleepRecordRead",
    "NutritionRecordCreate",
    "NutritionRecordUpdate",
    "NutritionRecordRead",
    # Analytics
    "MuscleGroupVolume",
    "VolumeAnalyticsResponse",
    "StrengthHistoryPoint",
    "StrengthProgressionResponse",
    "ConsistencyResponse",
    "ProgressiveOverloadResponse",
    "RecoveryResponse",
    "PillarBreakdown",
    "OverallProgressScoreResponse",
    # Recommendations
    "RecommendationItem",
    "RecommendationReportResponse",
]
