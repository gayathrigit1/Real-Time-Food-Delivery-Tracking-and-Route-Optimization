"""
Hypothesis Property-Based Testing Module
----------------------------------------
Tests mathematical and algorithmic invariant properties across generated arbitrary inputs.
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.algorithms.divide_and_conquer import DivideAndConquerAnalytics
from app.algorithms.dynamic_programming import OrderSelectionDP
from app.patterns.functional_tools import apply_tax_and_delivery, calculate_item_subtotal


# Property 1: Item subtotal & tax calculation monotonicity and non-negativity
@given(
    unit_price=st.floats(min_value=0.1, max_value=1000.0, allow_nan=False),
    quantity=st.integers(min_value=1, max_value=50),
)
def test_hypothesis_subtotal_properties(unit_price: float, quantity: int):
    subtotal = calculate_item_subtotal(unit_price, quantity)
    assert subtotal > 0
    assert subtotal >= round(unit_price, 2) - 0.01

    grand_total = apply_tax_and_delivery(subtotal, tax_rate=0.05, delivery_fee=5.0)
    assert grand_total > subtotal
    assert grand_total >= round(subtotal + 5.0, 2) - 0.01


# Property 2: Divide and Conquer Sorting Invariants (Length preservation, min/max bounds, sortedness)
@given(
    values=st.lists(
        st.floats(min_value=1.0, max_value=5000.0, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=60,
    )
)
def test_hypothesis_divide_and_conquer_invariants(values: list[float]):
    dac = DivideAndConquerAnalytics()
    res = dac.analyze_order_values(values)

    # 1. Total count matches input
    assert res["total_orders_analyzed"] == len(values)
    # 2. Min and Max are actual bounds
    assert res["min_order_value"] <= res["max_order_value"]
    assert res["min_order_value"] == pytest.approx(min(values), abs=0.02)
    assert res["max_order_value"] == pytest.approx(max(values), abs=0.02)
    # 3. Total sum is invariant
    assert res["total_revenue"] == pytest.approx(sum(values), abs=0.05)


# Property 3: Dynamic Programming Monotonicity (Increasing budget never decreases max attainable profit)
@given(
    w1=st.integers(min_value=10, max_value=50),
    w2=st.integers(min_value=51, max_value=120),
)
def test_hypothesis_dp_capacity_monotonicity(w1: int, w2: int):
    sample_orders = [
        {"order_id": 1, "preparation_time": 15, "profit_or_priority": 30},
        {"order_id": 2, "preparation_time": 25, "profit_or_priority": 60},
        {"order_id": 3, "preparation_time": 35, "profit_or_priority": 80},
        {"order_id": 4, "preparation_time": 10, "profit_or_priority": 20},
    ]
    dp1 = OrderSelectionDP(w1).optimize_batch(sample_orders, w1)
    dp2 = OrderSelectionDP(w2).optimize_batch(sample_orders, w2)

    assert dp2["max_profit_or_priority"] >= dp1["max_profit_or_priority"]
