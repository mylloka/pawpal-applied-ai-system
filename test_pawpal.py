"""
test_pawpal.py — 13 automated tests for PawPal+ system
Run: python -m pytest test_pawpal.py -v
"""

import pytest
from datetime import datetime
from pawpal_system import (
    Task, parse_task, build_schedule,
    detect_and_resolve_conflicts, sort_by_priority, expand_recurring,
)

TODAY = datetime.today().strftime("%Y-%m-%d")


def make_task(name, hour, minute, duration, priority, recurring=None):
    start = datetime.strptime(f"{TODAY} {hour:02d}:{minute:02d}", "%Y-%m-%d %H:%M")
    return Task(name=name, start_time=start, duration_minutes=duration,
                priority=priority, recurring=recurring)


# ── Conflict detection ───────────────────────────────────────────────────────

def test_overlapping_tasks_conflict():
    a = make_task("Walk", 8, 0, 30, "HIGH")
    b = make_task("Bath", 8, 15, 30, "MEDIUM")
    assert a.conflicts_with(b)

def test_non_overlapping_tasks_no_conflict():
    a = make_task("Walk", 8, 0, 30, "HIGH")
    b = make_task("Bath", 9, 0, 30, "MEDIUM")
    assert not a.conflicts_with(b)

def test_adjacent_tasks_no_conflict():
    """Task ending exactly when the next one starts should NOT conflict."""
    a = make_task("Walk",     8, 0,  30, "HIGH")
    b = make_task("Grooming", 8, 30, 30, "MEDIUM")
    assert not a.conflicts_with(b)

def test_same_start_time_conflict():
    a = make_task("Walk", 8, 0, 30, "HIGH")
    b = make_task("Bath", 8, 0, 45, "MEDIUM")
    assert a.conflicts_with(b)


# ── Conflict resolution ──────────────────────────────────────────────────────

def test_high_priority_wins_conflict():
    high = make_task("Walk",     8, 0, 30, "HIGH")
    low  = make_task("Grooming", 8, 10, 45, "LOW")
    schedule, removed = detect_and_resolve_conflicts([high, low])
    names = [t.name for t in schedule]
    assert "Walk" in names
    assert "Grooming" not in names

def test_three_way_conflict_keeps_highest():
    a = make_task("Vet",      10, 0,  60, "HIGH")
    b = make_task("Bath",     10, 15, 45, "MEDIUM")
    c = make_task("Playtime", 10, 30, 30, "LOW")
    schedule, removed = detect_and_resolve_conflicts([a, b, c])
    assert len(schedule) == 1
    assert schedule[0].name == "Vet"
    assert len(removed) == 2

def test_no_conflicts_keeps_all():
    tasks = [
        make_task("Feeding",  7, 0,  15, "HIGH"),
        make_task("Walk",     9, 0,  30, "HIGH"),
        make_task("Nap time", 14, 0, 60, "LOW"),
    ]
    schedule, removed = detect_and_resolve_conflicts(tasks)
    assert len(schedule) == 3
    assert len(removed) == 0


# ── Priority sorting ─────────────────────────────────────────────────────────

def test_sort_by_priority_order():
    low    = make_task("Nap",  14, 0, 30, "LOW")
    high   = make_task("Walk",  8, 0, 30, "HIGH")
    medium = make_task("Bath", 10, 0, 30, "MEDIUM")
    sorted_tasks = sort_by_priority([low, medium, high])
    assert sorted_tasks[0].priority == "HIGH"
    assert sorted_tasks[1].priority == "MEDIUM"
    assert sorted_tasks[2].priority == "LOW"


# ── Recurrence ───────────────────────────────────────────────────────────────

def test_daily_recurrence_generates_7_instances():
    task = make_task("Morning walk", 8, 0, 30, "HIGH", recurring="daily")
    expanded = expand_recurring([task], days=7)
    assert len(expanded) == 7

def test_weekly_recurrence_generates_1_instance_in_7_days():
    task = make_task("Grooming", 10, 0, 60, "MEDIUM", recurring="weekly")
    expanded = expand_recurring([task], days=7)
    assert len(expanded) == 1

def test_non_recurring_task_unchanged():
    task = make_task("Vet visit", 10, 0, 60, "HIGH", recurring=None)
    expanded = expand_recurring([task], days=7)
    assert len(expanded) == 1


# ── Edge cases ───────────────────────────────────────────────────────────────

def test_empty_task_list_returns_empty_schedule():
    schedule, removed = build_schedule([])
    assert schedule == []
    assert removed == []

def test_single_task_is_always_scheduled():
    task = make_task("Walk", 8, 0, 30, "HIGH")
    schedule, removed = build_schedule([task])
    assert len(schedule) == 1
    assert len(removed) == 0

def test_invalid_priority_raises_error():
    with pytest.raises(ValueError, match="Priority must be HIGH, MEDIUM, or LOW"):
        parse_task("Walk", "08:00 AM", 30, "URGENT")
