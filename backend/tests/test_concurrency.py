import pytest

from app.concurrency.asyncio_tasks import run_concurrent_asyncio_benchmark
from app.concurrency.multiprocessing_tasks import run_multiprocessing_benchmark
from app.concurrency.threading_tasks import run_threading_benchmark


@pytest.mark.asyncio
async def test_asyncio_concurrency_benchmark():
    res = await run_concurrent_asyncio_benchmark(task_count=5)
    assert res["mechanism"] == "asyncio"
    assert res["task_count"] == 5
    assert len(res["detailed_tasks"]) == 5
    assert res["total_elapsed_time_ms"] < res["sequential_baseline_ms"]
    assert res["speedup_ratio"] > 1.0


def test_threading_concurrency_benchmark():
    res = run_threading_benchmark(task_count=4, max_workers=4)
    assert res["mechanism"] == "threading"
    assert res["task_count"] == 4
    assert len(res["detailed_tasks"]) == 4
    assert res["total_elapsed_time_ms"] < res["sequential_baseline_ms"]
    assert res["speedup_ratio"] > 1.0


def test_multiprocessing_concurrency_benchmark():
    res = run_multiprocessing_benchmark(task_count=2, max_workers=2, iterations=1000)
    assert res["mechanism"] == "multiprocessing"
    assert res["task_count"] == 2
    assert len(res["detailed_tasks"]) == 2
    assert "GIL" in res["gil_impact_analysis"]
