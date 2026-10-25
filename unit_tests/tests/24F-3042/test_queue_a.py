"""Person A (24F-3042) - CircularQueue: enqueue, dequeue + class-level scenarios."""
import pytest

from data_structures.queues.circular_queue import CircularQueue

pytestmark = [pytest.mark.queue, pytest.mark.person_a, pytest.mark.xdist_group("queue")]


class TestEnqueue:
    @pytest.mark.smoke
    def test_enqueue_returns_the_same_queue(self):
        q = CircularQueue(3)
        assert q.enqueue("A") is q

    @pytest.mark.ecp
    def test_first_value_goes_to_slot_zero(self):
        q = CircularQueue(3)
        q.enqueue("A")
        assert q.array[0] == "A"

    @pytest.mark.bva
    @pytest.mark.parametrize("n", [1, 3, 5])
    def test_fill_to_capacity_succeeds(self, n):
        q = CircularQueue(n)
        for i in range(n):
            q.enqueue(i)
        assert q.size == n

    @pytest.mark.bva
    @pytest.mark.negative
    @pytest.mark.parametrize("n", [1, 3])
    def test_enqueue_when_full_raises(self, n):
        q = CircularQueue(n)
        for i in range(n):
            q.enqueue(i)
        with pytest.raises(Exception, match="QUEUE IS FULL"):
            q.enqueue("extra")

    @pytest.mark.negative
    def test_failed_enqueue_does_not_change_size(self):
        q = CircularQueue(1)
        q.enqueue("A")
        with pytest.raises(Exception, match="QUEUE IS FULL"):
            q.enqueue("B")
        assert q.size == 1

    @pytest.mark.ecp
    def test_enqueue_wraps_around_after_dequeue(self):
        q = CircularQueue(3)
        q.enqueue("A").enqueue("B").enqueue("C")
        q.dequeue()
        q.enqueue("D")
        assert q.array == ["D", "B", "C"]


class TestDequeue:
    @pytest.mark.ecp
    @pytest.mark.parametrize("items", [["A"], ["A", "B"], ["A", "B", "C"]])
    def test_dequeue_returns_oldest(self, items):
        q = CircularQueue(5)
        for i in items:
            q.enqueue(i)
        assert q.dequeue() == "A"

    @pytest.mark.negative
    def test_dequeue_on_empty_raises_underflow(self):
        with pytest.raises(Exception, match="UNDERFLOW"):
            CircularQueue(3).dequeue()

    @pytest.mark.bva
    def test_drain_then_underflow(self):
        q = CircularQueue(2)
        q.enqueue("A")
        q.dequeue()
        with pytest.raises(Exception, match="UNDERFLOW"):
            q.dequeue()

    @pytest.mark.ecp
    def test_dequeue_clears_the_slot(self):
        q = CircularQueue(3)
        q.enqueue("A")
        q.dequeue()
        assert q.array[0] is None

    @pytest.mark.ecp
    def test_dequeue_decrements_size(self):
        q = CircularQueue(3)
        q.enqueue("A").enqueue("B")
        q.dequeue()
        assert q.size == 1


class TestQueueScenarios:
    """Class-level, multi-step behaviour of CircularQueue."""

    @pytest.mark.scenario
    def test_fifo_order_is_kept_across_wraparound(self):
        q = CircularQueue(3)
        out = []
        for i in range(10):          # 10 items through a 3-slot queue = several wraps
            q.enqueue(i)
            out.append(q.dequeue())
        assert out == list(range(10))

    @pytest.mark.scenario
    def test_fill_drain_refill(self):
        q = CircularQueue(3)
        for _ in range(2):
            q.enqueue(1).enqueue(2).enqueue(3)
            assert [q.dequeue() for _ in range(3)] == [1, 2, 3]
        assert q.size == 0

    @pytest.mark.scenario
    def test_steady_state_interleaving(self):
        q = CircularQueue(2)
        q.enqueue("A")
        for ch in "BCDE":
            q.enqueue(ch)
            q.dequeue()
        assert q.size == 1 and q.dequeue() == "E"

    @pytest.mark.scenario
    def test_queue_usable_after_full_error(self):
        q = CircularQueue(1)
        q.enqueue("A")
        with pytest.raises(Exception, match="QUEUE IS FULL"):
            q.enqueue("B")
        assert q.dequeue() == "A"

    @pytest.mark.scenario
    def test_front_and_rear_indexes_wrap_to_zero(self):
        q = CircularQueue(2)
        q.enqueue("A").enqueue("B")
        q.dequeue()
        q.dequeue()
        assert (q.front, q.rear) == (0, 0)
