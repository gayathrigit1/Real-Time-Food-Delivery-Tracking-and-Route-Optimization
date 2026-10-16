"""
Functional Programming Paradigms & Utilities
--------------------------------------------
Demonstrates:
- Pure functions (deterministic, zero side-effects)
- Higher-order functions (functions accepting or returning functions)
- Lambda functions & functools.reduce
- map(), filter(), comprehensions (list, dict, set)
- Custom Iterators & Generators
- Function Decorators with metadata preservation (@wraps)
- Context Managers for safe timing & resource tracking
"""

import functools
import time
from collections.abc import Callable, Generator, Iterable, Iterator
from contextlib import contextmanager
from typing import Any, TypeVar

T = TypeVar("T")
R = TypeVar("R")


# 1. Pure Functions
def calculate_item_subtotal(unit_price: float, quantity: int) -> float:
    """Pure function: Computes subtotal deterministically."""
    return round(unit_price * quantity, 2)


def apply_tax_and_delivery(
    subtotal: float, tax_rate: float = 0.05, delivery_fee: float = 5.0
) -> float:
    """Pure function: Computes grand total without modifying inputs."""
    tax = subtotal * tax_rate
    return round(subtotal + tax + delivery_fee, 2)


# 2. Higher-Order Functions & Lambda
def order_filter_factory(min_amount: float) -> Callable[[dict[str, Any]], bool]:
    """Higher-order function returning a predicate closure."""
    return lambda order: float(order.get("total_amount", 0.0)) >= min_amount


def transform_and_aggregate(
    items: Iterable[dict[str, Any]],
    transform_fn: Callable[[dict[str, Any]], float],
    combine_fn: Callable[[float, float], float],
    initial_value: float = 0.0,
) -> float:
    """Higher-order function applying transform and reduction."""
    transformed_values = map(transform_fn, items)
    return functools.reduce(combine_fn, transformed_values, initial_value)


# 3. Custom Iterator
class OrderBatchIterator(Iterator[list[dict[str, Any]]]):
    """Custom iterator that yields chunks of orders for batch processing."""

    def __init__(self, orders: list[dict[str, Any]], batch_size: int = 5) -> None:
        self._orders = orders
        self._batch_size = max(1, batch_size)
        self._index = 0

    def __iter__(self) -> "OrderBatchIterator":
        return self

    def __next__(self) -> list[dict[str, Any]]:
        if self._index >= len(self._orders):
            raise StopIteration
        batch = self._orders[self._index : self._index + self._batch_size]
        self._index += self._batch_size
        return batch


# 4. Generator Function
def order_event_stream(events: list[dict[str, Any]]) -> Generator[dict[str, Any], None, None]:
    """Generator yielding formatted real-time event telemetry without loading entire history at once."""
    for idx, event in enumerate(events, start=1):
        yield {
            "sequence_number": idx,
            "event_type": event.get("type", "GENERAL"),
            "timestamp": event.get("timestamp", time.time()),
            "payload": event.get("payload", {}),
        }


# 5. Timing & Logging Decorators
def timed_execution(metric_name: str | None = None) -> Callable[..., Any]:
    """Decorator measuring and reporting exact execution duration."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start) * 1000
            # If result is dict, inject timing metadata cleanly
            if isinstance(result, dict) and "execution_time_ms" not in result:
                result["execution_time_ms"] = round(duration_ms, 4)
            return result

        return wrapper

    return decorator


# 6. Context Manager
@contextmanager
def execution_timer(label: str = "Task") -> Generator[dict[str, Any], None, None]:
    """Safe resource/timing context manager."""
    timing_info: dict[str, Any] = {"label": label, "start": time.perf_counter(), "duration_ms": 0.0}
    try:
        yield timing_info
    finally:
        timing_info["duration_ms"] = round((time.perf_counter() - timing_info["start"]) * 1000, 4)
