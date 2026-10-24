from typing import Any

from pydantic import BaseModel


class ConcurrencyTaskResult(BaseModel):
    task_id: int
    task_name: str
    result: Any
    duration_ms: float
    thread_or_process_id: str


class ConcurrencyBenchmarkResponse(BaseModel):
    mechanism: str  # "asyncio", "threading", "multiprocessing"
    workload_type: str  # "I/O-Bound", "CPU-Bound"
    task_count: int
    total_elapsed_time_ms: float
    sequential_baseline_ms: float
    speedup_ratio: float
    detailed_tasks: list[ConcurrencyTaskResult]
    explanation: str
    gil_impact_analysis: str
