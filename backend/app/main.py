from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1_router
from app.config import settings
from app.core.database import AsyncSessionLocal, init_db
from app.utils.seed_data import seed_initial_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables and seed demo data
    await init_db()

    async with AsyncSessionLocal() as session:
        try:
            await seed_initial_data(session)
        except Exception as e:
            print(f"[Database Initialization Warning] {e}")

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "An enterprise-grade, academic demonstration platform featuring: "
        "Greedy Agent Selection, Dijkstra Shortest Path Routing, "
        "0/1 Knapsack Dynamic Programming, Backtracking Constrained Tours, "
        "Branch & Bound TSP, and Divide & Conquer Order Analytics."
    ),
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS Middleware
cors_origins = list(settings.BACKEND_CORS_ORIGINS or [])

for origin in [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]:
    if origin not in cors_origins:
        cors_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root_health_check():
    """Root health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs_url": "/docs",
        "api_v1_prefix": settings.API_V1_STR,
    }


# Include V1 API Router
app.include_router(
    api_v1_router,
    prefix=settings.API_V1_STR,
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )