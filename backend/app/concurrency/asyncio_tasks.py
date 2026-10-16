"""
Concurrency: Asynchronous I/O using Asyncio
-------------------------------------------
Workload: I/O-Bound (e.g. Asynchronous DB queries, external REST API calls, telemetry streaming)
Mechanism: Single-threaded event loop utilizing cooperative non-blocking coroutines (`async` / `await`).

Why Asyncio for this workload?
- When waiting for network sockets or database responses, the event loop yields control to other coroutines.
- Extremely lightweight (negligible memory overhead compared to spawning OS threads).
- Can easily handle 10,000+ concurrent connections on a single core.

GIL Impact:
- Zero GIL contention because execution yields during I/O wait states without blocking thread execution.
"""

import asyncio
import time
from typing import Any


async def simulate_io_order_verification(order_id: int, delay_secs: float = 0.05) -> dict[str, Any]:
    """Simulates non-blocking async verification against external service."""
    t0 = time.perf_counter()
    await asyncio.sleep(delay_secs)
    duration = (time.perf_counter() - t0) * 1000
    return {
        "task_id": order_id,
        "task_name": f"Async Verify Order #{order_id}",
        "result": f"Verified status for order {order_id} (Inventory & Balance OK)",
        "duration_ms": round(duration, 2),
        "thread_or_process_id": f"AsyncCoro-{order_id}",
    }


async def run_concurrent_asyncio_benchmark(task_count: int = 10) -> dict[str, Any]:
    """Runs concurrent async coroutines using asyncio.gather."""
    start_total = time.perf_counter()

    tasks = [simulate_io_order_verification(i, 0.04) for i in range(1, task_count + 1)]
    results: list[dict[str, Any]] = await asyncio.gather(*tasks)

    total_elapsed_ms = (time.perf_counter() - start_total) * 1000
    # Sequential estimate is sum of individual wait times
    sequential_baseline = sum(r["duration_ms"] for r in results)
    speedup = round(sequential_baseline / max(total_elapsed_ms, 1e-6), 2)

    return {
        "mechanism": "asyncio",
        "workload_type": "I/O-Bound (Non-blocking Network / DB Simulation)",
        "task_count": task_count,
        "total_elapsed_time_ms": round(total_elapsed_ms, 2),
        "sequential_baseline_ms": round(sequential_baseline, 2),
        "speedup_ratio": speedup,
        "detailed_tasks": results,
        "explanation": (
            f"Executed {task_count} async tasks concurrently via event loop. "
            f"Because coroutines yield during sleep/network waits, total time ~ single longest sleep rather than sum of sleeps."
        ),
        "gil_impact_analysis": "Python GIL is not a bottleneck here because the thread yields during async I/O waits.",
    }
