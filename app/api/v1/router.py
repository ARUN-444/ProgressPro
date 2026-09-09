"""
Master API v1 router.
Aggregates all domain routers under the /api/v1 prefix.
"""

from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.exercises import router as exercises_router
from app.api.v1.nutrition import router as nutrition_router
from app.api.v1.profiles import router as profiles_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.sleep import router as sleep_router
from app.api.v1.users import router as users_router
from app.api.v1.weight import router as weight_router
from app.api.v1.workouts import router as workouts_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(profiles_router)
api_v1_router.include_router(exercises_router)
api_v1_router.include_router(workouts_router)
api_v1_router.include_router(weight_router)
api_v1_router.include_router(sleep_router)
api_v1_router.include_router(nutrition_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(recommendations_router)
