"""Person A (24F-3042) - Stack: __init__, push, pop, peek + class-level scenarios + CSV tests."""
import csv
from pathlib import Path

import pytest

from data_structures.stacks.stack import Stack, StackOverflowError, StackUnderflowError

pytestmark = [pytest.mark.stack, pytest.mark.person_a, pytest.mark.xdist_group("stack")]
DATA = Path(__file__).resolve().parents[2] / "data"


class TestInit:
    @pytest.mark.smoke
    def test_default_limit_is_10(self):
        assert Stack().limit == 10

    @pytest.mark.ecp
    @pytest.mark.parametrize("limit", [1, 3, 100])
    def test_custom_limit_is_stored(self, limit):
        assert Stack(limit).limit == limit

    @pytest.mark.bva
    def test_zero_limit_rejects_first_push(self):
        with pytest.raises(StackOverflowError):
            Stack(0).push(1)

    @pytest.mark.ecp
    def test_new_stack_starts_empty(self):
        assert Stack().stack == []

    @pytest.mark.negative
    def test_two_stacks_do_not_share_state(self):
        a, b = Stack(), Stack()
        a.push(1)
        assert b.stack == []


class TestPush:
    @pytest.mark.ecp
    @pytest.mark.parametrize(
        "value",
        [
            pytest.param(42, id="int", marks=pytest.mark.smoke),
            pytest.param("text", id="str"),
            pytest.param(None, id="none"),
            pytest.param([1, 2], id="list"),
        ],
    )
    def test_push_accepts_value_types(self, value):
        s = Stack()
        s.push(value)
        assert s.stack == [value]

    @pytest.mark.bva
    @pytest.mark.parametrize("limit", [1, 10])
    def test_push_up_to_limit_succeeds(self, limit):
        s = Stack(limit)
        for i in range(limit):
            s.push(i)
        assert len(s.stack) == limit

    @pytest.mark.bva
    @pytest.mark.negative
    @pytest.mark.parametrize("limit", [1, 3])
    def test_push_one_past_limit_raises(self, limit):
        s = Stack(limit)
        for i in range(limit):
            s.push(i)
        with pytest.raises(StackOverflowError):
            s.push("extra")

    @pytest.mark.negative
    def test_failed_push_leaves_stack_unchanged(self):
        s = Stack(1)
        s.push("a")
        with pytest.raises(StackOverflowError):
            s.push("b")
        assert s.stack == ["a"]


class TestPop:
    @pytest.mark.ecp
    @pytest.mark.parametrize("items, expected", [([1], 1), ([1, 2], 2), ([1, 2, 3], 3)])
    def test_pop_returns_last_pushed(self, items, expected):
        s = Stack()
        for i in items:
            s.push(i)
        assert s.pop() == expected

    @pytest.mark.smoke
    def test_pop_removes_the_item(self):
        s = Stack()
        s.push(1)
        s.pop()
        assert s.stack == []

    @pytest.mark.bva
    def test_pop_last_item_then_underflow(self):
        s = Stack()
        s.push(1)
        s.pop()
        with pytest.raises(StackUnderflowError):
            s.pop()

    @pytest.mark.negative
    def test_pop_on_new_stack_raises_underflow(self):
        with pytest.raises(StackUnderflowError):
            Stack().pop()

    @pytest.mark.ecp
    def test_pop_returns_none_when_none_was_pushed(self):
        s = Stack()
        s.push(None)
        assert s.pop() is None


class TestPeek:
    @pytest.mark.ecp
    @pytest.mark.parametrize("items, expected", [([1], 1), ([1, 2], 2), ([1, 2, 3], 3)])
    def test_peek_returns_top(self, items, expected):
        s = Stack()
        for i in items:
            s.push(i)
        assert s.peek() == expected

    @pytest.mark.ecp
    def test_peek_does_not_remove(self):
        s = Stack()
        s.push(5)
        s.peek()
        assert s.stack == [5]

    @pytest.mark.negative
    def test_peek_on_empty_raises_underflow(self):
        with pytest.raises(StackUnderflowError):
            Stack().peek()

    @pytest.mark.ecp
    def test_peek_after_pop_shows_previous_item(self):
        s = Stack()
        s.push(1)
        s.push(2)
        s.pop()
        assert s.peek() == 1

    @pytest.mark.ecp
    def test_peek_after_push_pop_push_shows_newest(self):
        s = Stack()
        s.push(1)
        s.pop()
        s.push(9)
        assert s.peek() == 9


class TestStackScenarios:
    """Class-level, multi-step behaviour of Stack."""

    @pytest.mark.scenario
    def test_lifo_order(self):
        s = Stack()
        for i in range(1, 6):
            s.push(i)
        assert [s.pop() for _ in range(5)] == [5, 4, 3, 2, 1]

    @pytest.mark.scenario
    def test_interleaved_push_and_pop(self):
        s = Stack()
        s.push("a")
        s.push("b")
        assert s.pop() == "b"
        s.push("c")
        assert [s.pop(), s.pop()] == ["c", "a"]

    @pytest.mark.scenario
    def test_fill_drain_refill_cycle(self):
        s = Stack(3)
        for cycle in range(2):
            for i in range(3):
                s.push(i)
            for _ in range(3):
                s.pop()
        assert s.stack == []

    @pytest.mark.scenario
    def test_stack_still_usable_after_overflow_error(self):
        s = Stack(1)
        s.push(1)
        with pytest.raises(StackOverflowError):
            s.push(2)
        assert s.pop() == 1

    @pytest.mark.scenario
    def test_mixed_types_keep_order(self):
        s = Stack()
        for v in [1, "two", 3.0, None]:
            s.push(v)
        assert s.stack == [1, "two", 3.0, None]


def _rows():
    with open(DATA / "stack_scenarios.csv", newline="") as f:
        return [pytest.param(r, id=r["tc_id"]) for r in csv.DictReader(f)]


@pytest.mark.csv_driven
@pytest.mark.parametrize("row", _rows())
def test_stack_scenarios_from_csv(row):
    s = Stack(int(row["limit"]))
    pushes = [int(v) for v in row["pushes"].split(";") if v]
    pops = int(row["pops"])
    err = {"overflow": StackOverflowError, "underflow": StackUnderflowError}.get(row["expected_error"])

    def run():
        for v in pushes:
            s.push(v)
        for _ in range(pops):
            s.pop()

    if err:
        with pytest.raises(err):
            run()
    else:
        run()

    assert len(s.stack) == int(row["expected_size"])
    expected_top = int(row["expected_top"]) if row["expected_top"] else None
    assert (s.stack[-1] if s.stack else None) == expected_top
