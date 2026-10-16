"""
Concurrency: Multi-processing using ProcessPoolExecutor
-------------------------------------------------------
Workload: CPU-Bound (e.g. Route permutation factorial calculations, cryptographic batch proofs, heavy analytics)
Mechanism: Multiple independent OS processes, each with its own Python interpreter and dedicated memory space.

Why Multiprocessing for CPU-Bound tasks?
- The Python GIL prevents true simultaneous multi-core execution of CPU-bound Python bytecode within threads of the same process.
- Spawning separate processes bypasses the GIL entirely, allowing parallel utilization of all CPU cores.

Windows Compatibility:
- Functions executed by worker processes must be importable at module top level.
- Windows uses the 'spawn' multiprocessing model, requiring clean serialization (pickle) of arguments.
"""

import hashlib
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any


def cpu_intensive_route_proof(batch_id: int, iterations: int = 75000) -> dict[str, Any]:
    """
    Top-level worker function: executes CPU-bound cryptographic hash hashing to simulate route proof calculations.
    """
    t0 = time.perf_counter()
    data = f"route_verification_token_{batch_id}".encode()
    for _ in range(iterations):
        data = hashlib.sha256(data).digest()

    duration = (time.perf_counter() - t0) * 1000
    return {
        "task_id": batch_id,
        "task_name": f"CPU Cryptographic Route Proof #{batch_id}",
        "result": f"Hash generated: {data.hex()[:12]}...",
        "duration_ms": round(duration, 2),
        "thread_or_process_id": f"Process-PID-{os.getpid()}",
    }


def run_multiprocessing_benchmark(
    task_count: int = 6, max_workers: int = 4, iterations: int = 60000
) -> dict[str, Any]:
    """Runs CPU-bound benchmark across separate process workers."""
    start_total = time.perf_counter()

    results: list[dict[str, Any]] = []
    # On Windows, ProcessPoolExecutor uses spawn
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(cpu_intensive_route_proof, i, iterations)
            for i in range(1, task_count + 1)
        ]
        for fut in as_completed(futures):
            results.append(fut.result())

    results.sort(key=lambda x: x["task_id"])

    total_elapsed_ms = (time.perf_counter() - start_total) * 1000
    sequential_baseline = sum(r["duration_ms"] for r in results)
    speedup = round(sequential_baseline / max(total_elapsed_ms, 1e-6), 2)

    return {
        "mechanism": "multiprocessing",
        "workload_type": "CPU-Bound (Heavy Cryptographic Hash Chain Computation)",
        "task_count": task_count,
        "total_elapsed_time_ms": round(total_elapsed_ms, 2),
        "sequential_baseline_ms": round(sequential_baseline, 2),
        "speedup_ratio": speedup,
        "detailed_tasks": results,
        "explanation": (
            f"Executed {task_count} CPU-bound workloads across {max_workers} separate Python processes. "
            f"Each process has its own GIL, enabling true parallel execution across multiple physical CPU cores."
        ),
        "gil_impact_analysis": "Bypasses the GIL entirely by utilizing independent OS processes.",
    }
