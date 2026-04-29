"""Tests for Vector, Queue and Stack — the three linear ADTs of Phase 2."""

import pytest

from aurora_siger.landing.module import Module
from aurora_siger.landing.structures import Queue, Stack, Vector


def make_module(**overrides) -> Module:
    """Build a Module with defaults; override per case."""
    defaults = dict(
        id=1, name="M", type="lab", priority=5,
        fuel_level=80.0, mass=1000.0, cargo_criticality=3,
        distance=400.0, speed=200.0,
    )
    defaults.update(overrides)
    return Module(**defaults)


# --- Vector container interface ---

def test_vector_starts_empty():
    v = Vector()
    assert v.is_empty()
    assert v.size() == 0
    assert len(v) == 0


def test_vector_append_then_iterate_preserves_order():
    v = Vector()
    for i in range(5):
        v.append(i)
    assert list(v) == [0, 1, 2, 3, 4]


def test_vector_insert_places_at_index():
    v = Vector()
    for i in [0, 1, 3, 4]:
        v.append(i)
    v.insert(2, 2)
    assert list(v) == [0, 1, 2, 3, 4]


def test_vector_remove_at_returns_and_shifts():
    v = Vector()
    for c in "abcd":
        v.append(c)
    removed = v.remove_at(1)
    assert removed == "b"
    assert list(v) == ["a", "c", "d"]


def test_vector_remove_at_out_of_range_raises():
    v = Vector()
    v.append(1)
    with pytest.raises(IndexError):
        v.remove_at(5)


def test_vector_get_does_not_mutate():
    v = Vector()
    v.append("x")
    assert v.get(0) == "x"
    assert v.size() == 1


def test_vector_to_list_returns_independent_copy():
    v = Vector()
    v.append(1)
    snapshot = v.to_list()
    snapshot.append(99)
    assert v.size() == 1


# --- Queue (FIFO) ---

def test_queue_is_fifo():
    q = Queue()
    for i in range(3):
        q.enqueue(i)
    assert q.dequeue() == 0
    assert q.dequeue() == 1
    assert q.dequeue() == 2


def test_queue_dequeue_on_empty_returns_none():
    q = Queue()
    assert q.dequeue() is None


def test_queue_peek_does_not_remove():
    q = Queue()
    q.enqueue("first")
    q.enqueue("second")
    assert q.peek() == "first"
    assert q.size() == 2


# --- Stack (LIFO) ---

def test_stack_is_lifo():
    s = Stack()
    for i in range(3):
        s.push(i)
    assert s.pop() == 2
    assert s.pop() == 1
    assert s.pop() == 0


def test_stack_pop_on_empty_returns_none():
    s = Stack()
    assert s.pop() is None


def test_stack_peek_returns_top_without_removing():
    s = Stack()
    s.push("bottom")
    s.push("top")
    assert s.peek() == "top"
    assert s.size() == 2


# --- Module-specific search ---

def test_search_by_type_returns_all_matching():
    v = Vector()
    v.append(make_module(id=1, type="solar"))
    v.append(make_module(id=2, type="nuclear"))
    v.append(make_module(id=3, type="solar"))
    results = v.search_by_type("solar")
    ids = sorted(m.id for m in results)
    assert ids == [1, 3]


def test_search_by_type_empty_when_no_match():
    v = Vector()
    v.append(make_module(type="solar"))
    assert v.search_by_type("nuclear") == []


def test_search_min_fuel_returns_lowest():
    v = Vector()
    v.append(make_module(id=1, fuel_level=80.0))
    v.append(make_module(id=2, fuel_level=20.0))  # min
    v.append(make_module(id=3, fuel_level=50.0))
    assert v.search_min_fuel().id == 2


def test_search_min_fuel_on_empty_returns_none():
    assert Vector().search_min_fuel() is None


def test_search_highest_priority_returns_lowest_priority_number():
    v = Vector()
    v.append(make_module(id=1, priority=5))
    v.append(make_module(id=2, priority=1))  # highest priority
    v.append(make_module(id=3, priority=3))
    assert v.search_highest_priority().id == 2


def test_search_highest_priority_on_empty_returns_none():
    assert Vector().search_highest_priority() is None


def test_find_by_id_returns_match():
    v = Vector()
    v.append(make_module(id=7))
    v.append(make_module(id=11))
    assert v.find_by_id(11).id == 11


def test_find_by_id_returns_none_when_absent():
    v = Vector()
    v.append(make_module(id=1))
    assert v.find_by_id(99) is None


# --- Sort ---

def test_sort_by_priority_orders_ascending():
    v = Vector()
    v.append(make_module(id=1, priority=5))
    v.append(make_module(id=2, priority=2))
    v.append(make_module(id=3, priority=8))
    v.sort_by_priority()
    assert [m.id for m in v] == [2, 1, 3]


def test_sort_by_fuel_orders_ascending():
    v = Vector()
    v.append(make_module(id=1, fuel_level=80.0))
    v.append(make_module(id=2, fuel_level=20.0))
    v.append(make_module(id=3, fuel_level=50.0))
    v.sort_by_fuel()
    assert [m.id for m in v] == [2, 3, 1]


def test_sort_multi_breaks_ties_by_priority_then_fuel():
    """When ETA matches, priority decides; when both match, fuel decides."""
    v = Vector()
    # Three modules with identical ETA (distance/speed = 1).
    # (eta, priority, fuel) → expected order:
    #   id 10: (1, 3, 80.0)
    #   id 11: (1, 1, 50.0)
    #   id 12: (1, 1, 30.0)
    # Sorted ascending → 12, 11, 10.
    v.append(make_module(id=10, distance=200.0, speed=200.0, priority=3, fuel_level=80.0))
    v.append(make_module(id=11, distance=200.0, speed=200.0, priority=1, fuel_level=50.0))
    v.append(make_module(id=12, distance=200.0, speed=200.0, priority=1, fuel_level=30.0))
    v.sort_multi()
    assert [m.id for m in v] == [12, 11, 10]


def test_sort_multi_eta_takes_precedence_over_priority():
    v = Vector()
    # Lower priority number = higher mission priority. But ETA wins.
    v.append(make_module(id=20, distance=600.0, speed=200.0, priority=1, fuel_level=80.0))   # eta=3
    v.append(make_module(id=21, distance=200.0, speed=200.0, priority=10, fuel_level=80.0))  # eta=1
    v.sort_multi()
    assert [m.id for m in v] == [21, 20]


def test_sort_multi_handles_empty_vector():
    v = Vector()
    v.sort_multi()  # must not raise
    assert v.is_empty()


# --- Inheritance ---

def test_queue_inherits_search_and_sort():
    q = Queue()
    q.enqueue(make_module(id=1, fuel_level=80.0))
    q.enqueue(make_module(id=2, fuel_level=20.0))
    assert q.search_min_fuel().id == 2
    q.sort_by_fuel()
    assert [m.id for m in q] == [2, 1]


def test_stack_inherits_find_by_id():
    s = Stack()
    s.push(make_module(id=42))
    assert s.find_by_id(42).id == 42
