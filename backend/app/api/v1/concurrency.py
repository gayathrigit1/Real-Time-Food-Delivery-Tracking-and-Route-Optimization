from fastapi import APIRouter, Query

from app.concurrency.asyncio_tasks import run_concurrent_asyncio_benchmark
from app.concurrency.multiprocessing_tasks import run_multiprocessing_benchmark
from app.concurrency.threading_tasks import run_threading_benchmark
from app.schemas.concurrency import ConcurrencyBenchmarkResponse

router = APIRouter(prefix="/concurrency", tags=["Concurrency Demonstrations"])


@router.get("/asyncio", response_model=ConcurrencyBenchmarkResponse)
async def benchmark_asyncio(
    task_count: int = Query(default=10, ge=1, le=50, description="Number of concurrent coroutines"),
):
    """Demonstrates asynchronous non-blocking event-loop concurrency (I/O-Bound)."""
    res = await run_concurrent_asyncio_benchmark(task_count=task_count)
    return ConcurrencyBenchmarkResponse(**res)


@router.get("/threading", response_model=ConcurrencyBenchmarkResponse)
async def benchmark_threading(
    task_count: int = Query(
        default=8, ge=1, le=30, description="Number of blocking notification tasks"
    ),
    max_workers: int = Query(default=4, ge=1, le=16, description="Thread pool size"),
):
    """Demonstrates multi-threading with ThreadPoolExecutor (I/O-Bound with GIL release)."""
    res = run_threading_benchmark(task_count=task_count, max_workers=max_workers)
    return ConcurrencyBenchmarkResponse(**res)


@router.get("/multiprocessing", response_model=ConcurrencyBenchmarkResponse)
async def benchmark_multiprocessing(
    task_count: int = Query(default=4, ge=1, le=12, description="Number of CPU tasks"),
    max_workers: int = Query(default=4, ge=1, le=8, description="Process pool worker count"),
):
    """Demonstrates true multi-core CPU parallelism bypassing the GIL via ProcessPoolExecutor."""
    res = run_multiprocessing_benchmark(task_count=task_count, max_workers=max_workers)
    return ConcurrencyBenchmarkResponse(**res)
