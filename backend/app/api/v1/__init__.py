from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.algorithms import router as algorithms_router
from app.api.v1.auth import router as auth_router
from app.api.v1.concurrency import router as concurrency_router
from app.api.v1.deliveries import router as deliveries_router
from app.api.v1.orders import router as orders_router
from app.api.v1.restaurants import router as restaurants_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(restaurants_router)
api_v1_router.include_router(orders_router)
api_v1_router.include_router(deliveries_router)
api_v1_router.include_router(algorithms_router)
api_v1_router.include_router(concurrency_router)
api_v1_router.include_router(admin_router)
