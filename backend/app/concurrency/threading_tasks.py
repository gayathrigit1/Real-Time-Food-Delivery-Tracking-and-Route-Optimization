"""
Concurrency: Multi-threading using ThreadPoolExecutor
-----------------------------------------------------
Workload: I/O-Bound (e.g. Legacy synchronous HTTP clients, blocking third-party SMS/Email notification dispatches)
Mechanism: OS native operating-system threads scheduled preemptively.

Why Threading for this workload?
- When integrating legacy blocking libraries (e.g. standard `requests` or blocking socket writes),
  separate threads allow multiple network waits to execute concurrently without freezing the main thread.

GIL Impact:
- The Global Interpreter Lock (GIL) is released during blocking system I/O calls (e.g. time.sleep, socket.recv),
  allowing threads to wait in parallel and yield significant real-time speedup for I/O tasks.
"""

import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any


def dispatch_simulated_notification(
    notification_id: int, delay_secs: float = 0.05
) -> dict[str, Any]:
    """Simulates a synchronous blocking outbound push notification/SMS dispatch."""
    t0 = time.perf_counter()
    time.sleep(delay_secs)  # Releases GIL during OS sleep
    duration = (time.perf_counter() - t0) * 1000
    thread_name = threading.current_thread().name
    return {
        "task_id": notification_id,
        "task_name": f"Push Notification #{notification_id}",
        "result": f"Sent SMS update for delivery #{notification_id}",
        "duration_ms": round(duration, 2),
        "thread_or_process_id": f"Thread-{thread_name} (PID {os.getpid()})",
    }


def run_threading_benchmark(task_count: int = 10, max_workers: int = 5) -> dict[str, Any]:
    """Runs threaded benchmark with ThreadPoolExecutor."""
    start_total = time.perf_counter()

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(dispatch_simulated_notification, i, 0.04)
            for i in range(1, task_count + 1)
        ]
        for fut in as_completed(futures):
            results.append(fut.result())

    # Sort back by task_id
    results.sort(key=lambda x: x["task_id"])

    total_elapsed_ms = (time.perf_counter() - start_total) * 1000
    sequential_baseline = sum(r["duration_ms"] for r in results)
    speedup = round(sequential_baseline / max(total_elapsed_ms, 1e-6), 2)

    return {
        "mechanism": "threading",
        "workload_type": "I/O-Bound (Blocking System Sleep / Notification Network Wait)",
        "task_count": task_count,
        "total_elapsed_time_ms": round(total_elapsed_ms, 2),
        "sequential_baseline_ms": round(sequential_baseline, 2),
        "speedup_ratio": speedup,
        "detailed_tasks": results,
        "explanation": (
            f"Executed {task_count} blocking tasks across a pool of {max_workers} threads. "
            f"Since the GIL is released during OS sleep/network blocking calls, threads make concurrent progress."
        ),
        "gil_impact_analysis": "GIL is released during underlying C-level I/O / sleep operations.",
    }
