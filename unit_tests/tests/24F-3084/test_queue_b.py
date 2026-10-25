"""Person B (24F-3084) - CircularQueue: __init__, __len__, is_empty, first + scenarios + CSV tests."""
import csv
from pathlib import Path

import pytest

from data_structures.queues.circular_queue import CircularQueue

pytestmark = [pytest.mark.queue, pytest.mark.person_b, pytest.mark.xdist_group("queue")]
DATA = Path(__file__).resolve().parents[2] / "data"
# make_queue(n, ops): 'e' = enqueue next letter A,B,C.. ; 'd' = dequeue  (see conftest.py)


class TestInit:
    @pytest.mark.ecp
    @pytest.mark.parametrize("n", [1, 5, 100])
    def test_new_queue_is_blank(self, n):
        q = CircularQueue(n)
        assert q.array == [None] * n
        assert (q.size, q.front, q.rear) == (0, 0, 0)

    @pytest.mark.bva
    def test_zero_capacity_cannot_hold_anything(self):
        q = CircularQueue(0)
        assert q.array == []
        with pytest.raises(Exception, match="QUEUE IS FULL"):
            q.enqueue("A")

    @pytest.mark.bva
    @pytest.mark.negative
    def test_negative_capacity_behaves_like_zero(self):
        q = CircularQueue(-1)
        assert q.array == []
        with pytest.raises(Exception, match="QUEUE IS FULL"):
            q.enqueue("A")

    @pytest.mark.negative
    @pytest.mark.parametrize("bad", ["a", 2.5], ids=["str", "float"])
    def test_non_integer_capacity_raises_typeerror(self, bad):
        with pytest.raises(TypeError):
            CircularQueue(bad)


class TestLen:
    @pytest.mark.smoke
    def test_new_queue_has_length_zero(self):
        assert len(CircularQueue(3)) == 0

    @pytest.mark.ecp
    @pytest.mark.parametrize(
        "ops, expected", [("e", 1), ("ee", 2), ("eed", 1), ("eedd", 0)]
    )
    def test_len_after_operations(self, make_queue, ops, expected):
        assert len(make_queue(5, ops)) == expected

    @pytest.mark.negative
    def test_len_unchanged_by_failed_enqueue(self, make_queue):
        q = make_queue(1, "e")
        with pytest.raises(Exception, match="QUEUE IS FULL"):
            q.enqueue("Z")
        assert len(q) == 1


class TestIsEmpty:
    @pytest.mark.ecp
    @pytest.mark.parametrize(
        "ops, expected",
        [("", True), ("e", False), ("ed", True), ("eed", False), ("eedd", True)],
    )
    def test_is_empty_after_operations(self, make_queue, ops, expected):
        assert make_queue(5, ops).is_empty() is expected

    @pytest.mark.bva
    def test_full_queue_is_not_empty(self, make_queue):
        assert make_queue(2, "ee").is_empty() is False


class TestFirst:
    @pytest.mark.negative
    def test_first_on_empty_returns_false_not_none(self):
        assert CircularQueue(3).first() is False

    @pytest.mark.ecp
    @pytest.mark.parametrize("ops, expected", [("e", "A"), ("ee", "A"), ("eed", "B")])
    def test_first_returns_oldest_item(self, make_queue, ops, expected):
        assert make_queue(5, ops).first() == expected

    @pytest.mark.ecp
    def test_first_does_not_remove(self, make_queue):
        q = make_queue(5, "ee")
        q.first()
        assert len(q) == 2

    @pytest.mark.ecp
    def test_first_returns_falsy_data_correctly(self):
        q = CircularQueue(3)
        q.enqueue(0)
        assert q.first() == 0 and q.first() is not False


class TestQueueInvariants:
    """Class-level checks that must hold after any sequence of operations."""

    SEQUENCES = ["", "eee", "eeded"]

    @pytest.mark.scenario
    @pytest.mark.parametrize("ops", SEQUENCES)
    def test_len_always_matches_size_attribute(self, make_queue, ops):
        q = make_queue(3, ops)
        assert len(q) == q.size

    @pytest.mark.scenario
    @pytest.mark.parametrize("ops", SEQUENCES)
    def test_is_empty_matches_len_zero(self, make_queue, ops):
        q = make_queue(3, ops)
        assert q.is_empty() == (len(q) == 0)

    @pytest.mark.scenario
    def test_capacity_one_queue_cycle(self):
        q = CircularQueue(1)
        for ch in "ABC":
            q.enqueue(ch)
            assert q.first() == ch and q.dequeue() == ch
        assert q.is_empty()

    @pytest.mark.scenario
    def test_enqueue_calls_can_be_chained(self):
        q = CircularQueue(3).enqueue("A").enqueue("B").enqueue("C")
        assert len(q) == 3 and q.first() == "A"

    @pytest.mark.scenario
    def test_first_tracks_front_through_wraparound(self, make_queue):
        q = make_queue(3, "eeedde")      # A,B,C in; A,B out; D in (wraps)
        assert q.first() == "C" and len(q) == 2


def _rows():
    with open(DATA / "queue_scenarios.csv", newline="") as f:
        return [pytest.param(r, id=r["tc_id"]) for r in csv.DictReader(f)]


@pytest.mark.csv_driven
@pytest.mark.parametrize("row", _rows())
def test_queue_scenarios_from_csv(row):
    q = CircularQueue(int(row["capacity"]))
    ops = [op.split(":") for op in row["operations"].split("|")]
    msg = {"full": "QUEUE IS FULL", "underflow": "UNDERFLOW"}.get(row["expected_error"])

    def run():
        for op in ops:
            if op[0] == "E":
                q.enqueue(op[1])
            else:
                q.dequeue()

    if msg:
        with pytest.raises(Exception, match=msg):
            run()
    else:
        run()

    assert len(q) == int(row["expected_len"])
    expected_first = False if row["expected_first"] == "EMPTY" else row["expected_first"]
    assert q.first() == expected_first
