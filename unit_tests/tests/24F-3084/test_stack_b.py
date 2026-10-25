"""Person B (24F-3084) - Stack: is_empty, is_full, size, __contains__, __bool__, __str__ + scenarios."""
import pytest

from data_structures.stacks.stack import Stack, StackOverflowError

pytestmark = [pytest.mark.stack, pytest.mark.person_b, pytest.mark.xdist_group("stack")]
# make_stack(limit, ops): 'p' = push next number, 'x' = pop  (see conftest.py)


class TestIsEmpty:
    @pytest.mark.smoke
    def test_new_stack_is_empty(self, make_stack):
        assert make_stack().is_empty() is True

    @pytest.mark.ecp
    @pytest.mark.parametrize(
        "ops, expected",
        [("p", False), ("pp", False), ("px", True), ("ppxx", True), ("ppx", False)],
    )
    def test_is_empty_after_operations(self, make_stack, ops, expected):
        assert make_stack(10, ops).is_empty() is expected

    @pytest.mark.bva
    def test_full_stack_is_not_empty(self, make_stack):
        assert make_stack(2, "pp").is_empty() is False


class TestIsFull:
    @pytest.mark.bva
    @pytest.mark.parametrize(
        "ops, expected",
        [("", False), ("p", False), ("pp", False), ("ppp", True), ("pppx", False), ("pppxp", True)],
    )
    def test_is_full_around_the_limit_of_3(self, make_stack, ops, expected):
        assert make_stack(3, ops).is_full() is expected

    @pytest.mark.bva
    def test_zero_limit_stack_is_full_immediately(self):
        assert Stack(0).is_full() is True

    @pytest.mark.negative
    @pytest.mark.xfail(reason="BUG: Stack(-1).is_full() is False although push() raises overflow")
    def test_negative_limit_is_full_matches_push_behaviour(self):
        s = Stack(-1)
        try:
            s.push(1)
            push_failed = False
        except StackOverflowError:
            push_failed = True
        assert s.is_full() == push_failed


class TestSize:
    @pytest.mark.ecp
    @pytest.mark.parametrize(
        "ops, expected",
        [("", 0), ("p", 1), ("pp", 2), ("ppx", 1), ("ppxx", 0), ("pppp", 4)],
    )
    def test_size_after_operations(self, make_stack, ops, expected):
        assert make_stack(10, ops).size() == expected

    @pytest.mark.negative
    def test_size_unchanged_by_failed_push(self, make_stack):
        s = make_stack(2, "pp")
        with pytest.raises(StackOverflowError):
            s.push(99)
        assert s.size() == 2


class TestContains:
    @pytest.mark.ecp
    def test_present_item_is_found(self, make_stack):
        assert 3 in make_stack(10, "ppp")

    @pytest.mark.ecp
    def test_absent_item_is_not_found(self, make_stack):
        assert 9 not in make_stack(10, "ppp")

    @pytest.mark.bva
    def test_empty_stack_contains_nothing(self):
        assert 1 not in Stack()

    @pytest.mark.ecp
    def test_popped_item_is_no_longer_found(self, make_stack):
        assert 3 not in make_stack(10, "pppx")

    @pytest.mark.ecp
    def test_none_can_be_found_when_pushed(self):
        s = Stack()
        s.push(None)
        assert None in s

    @pytest.mark.ecp
    def test_string_item_is_found(self):
        s = Stack()
        s.push(1)
        s.push("a")
        assert "a" in s


class TestBool:
    @pytest.mark.ecp
    @pytest.mark.parametrize(
        "ops, expected",
        [("", False), ("p", True), ("px", False), ("pp", True), ("ppx", True)],
    )
    def test_truthiness_follows_content(self, make_stack, ops, expected):
        assert bool(make_stack(10, ops)) is expected


class TestStr:
    @pytest.mark.ecp
    @pytest.mark.parametrize(
        "ops, expected",
        [("", "[]"), ("p", "[1]"), ("pp", "[1, 2]"), ("ppx", "[1]"), ("ppxx", "[]")],
    )
    def test_str_shows_list(self, make_stack, ops, expected):
        assert str(make_stack(10, ops)) == expected


class TestStackInvariants:
    """Class-level checks that must hold after any sequence of operations."""

    SEQUENCES = ["", "ppp", "pppxx"]

    @pytest.mark.scenario
    @pytest.mark.parametrize("ops", SEQUENCES)
    def test_size_always_matches_len_of_internal_list(self, make_stack, ops):
        s = make_stack(10, ops)
        assert s.size() == len(s.stack)

    @pytest.mark.scenario
    @pytest.mark.parametrize("ops", SEQUENCES)
    def test_is_empty_is_opposite_of_bool(self, make_stack, ops):
        s = make_stack(10, ops)
        assert s.is_empty() == (not bool(s))

    @pytest.mark.scenario
    def test_full_then_pop_then_not_full(self, make_stack):
        s = make_stack(2, "pp")
        assert s.is_full()
        s.pop()
        assert not s.is_full() and s.size() == 1

    @pytest.mark.scenario
    def test_contains_and_size_stay_consistent(self, make_stack):
        s = make_stack(5, "ppp")
        assert (1 in s) and (2 in s) and (3 in s) and s.size() == 3

    @pytest.mark.scenario
    def test_str_and_size_agree(self, make_stack):
        s = make_stack(5, "pppp")
        assert str(s).count(",") + 1 == s.size()
