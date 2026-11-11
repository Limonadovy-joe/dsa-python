from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from dsa.queues.deque import Deque
    from tests.queues.deque.deque_backends import MakeDeque

PAIRS = ({"key": "key1", "value": "test1"}, {"key": "key2", "value": "test2"})


def _key_value(item: dict[str, str]) -> str:
    return f"{item['key']}:{item['value']}"


def test_creates_empty_deque(make_deque: MakeDeque) -> None:
    deque: Deque[int] = make_deque()
    assert deque.is_empty()
    assert deque.size() == 0


def test_peek_front_and_back_of_empty_deque(make_deque: MakeDeque) -> None:
    deque: Deque[int] = make_deque()
    assert deque.peek_front() is None
    assert deque.peek_back() is None


def test_remove_from_empty_deque_returns_none(make_deque: MakeDeque) -> None:
    deque: Deque[int] = make_deque()
    assert deque.remove_front() is None
    assert deque.remove_back() is None


def test_add_back_remove_front_queue_behaviour(make_deque: MakeDeque) -> None:
    deque = make_deque([1, 2, 3])
    assert deque.remove_front() == 1
    assert deque.remove_front() == 2
    assert deque.remove_front() == 3
    assert deque.is_empty()


def test_add_front_remove_back_reversed_queue(make_deque: MakeDeque) -> None:
    deque: Deque[int] = make_deque()
    deque.add_front(1)
    deque.add_front(2)
    deque.add_front(3)
    assert deque.remove_back() == 1
    assert deque.remove_back() == 2
    assert deque.remove_back() == 3
    assert deque.is_empty()


def test_add_front_remove_front_stack_behaviour(make_deque: MakeDeque) -> None:
    deque: Deque[int] = make_deque()
    deque.add_front(1)
    deque.add_front(2)
    deque.add_front(3)
    assert deque.remove_front() == 3
    assert deque.remove_front() == 2
    assert deque.remove_front() == 1
    assert deque.is_empty()


def test_mixed_add_front_and_add_back(make_deque: MakeDeque) -> None:
    deque: Deque[int] = make_deque()
    deque.add_back(1)
    deque.add_front(2)
    deque.add_back(3)
    deque.add_front(4)
    # order: 4, 2, 1, 3
    assert deque.peek_front() == 4
    assert deque.peek_back() == 3
    assert deque.remove_front() == 4
    assert deque.remove_front() == 2
    assert deque.remove_front() == 1
    assert deque.remove_front() == 3


def test_mixed_remove_front_and_remove_back(make_deque: MakeDeque) -> None:
    deque = make_deque([1, 2, 3, 4])
    assert deque.remove_front() == 1
    assert deque.remove_back() == 4
    assert deque.remove_front() == 2
    assert deque.remove_back() == 3
    assert deque.is_empty()


def test_single_element(make_deque: MakeDeque) -> None:
    deque = make_deque([42])
    assert deque.peek_front() == 42
    assert deque.peek_back() == 42
    assert deque.size() == 1
    assert deque.remove_front() == 42
    assert deque.is_empty()


def test_object_values(make_deque: MakeDeque) -> None:
    deque = make_deque(PAIRS)
    assert deque.remove_front() == {"key": "key1", "value": "test1"}
    assert deque.remove_front() == {"key": "key2", "value": "test2"}
    assert deque.is_empty()


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        pytest.param([], "", id="empty"),
        pytest.param([1], "1", id="single"),
        pytest.param([1, 2, 3], "1,2,3", id="ints"),
        pytest.param(["a", "b"], "a,b", id="strs"),
    ],
)
def test_to_string(make_deque: MakeDeque, values: list[object], expected: str) -> None:
    assert make_deque(values).to_string() == expected


def test_to_string_with_custom_callback(make_deque: MakeDeque) -> None:
    assert make_deque(PAIRS).to_string(_key_value) == "key1:test1,key2:test2"


def test_size_tracks_many_operations(make_deque: MakeDeque) -> None:
    deque: Deque[int] = make_deque()
    assert deque.size() == 0

    deque.add_back(1)
    deque.add_back(2)
    deque.add_front(3)
    assert deque.size() == 3

    deque.remove_front()
    assert deque.size() == 2

    deque.remove_back()
    assert deque.size() == 1

    deque.add_back(4)
    deque.add_front(5)
    assert deque.size() == 3

    deque.remove_front()
    deque.remove_front()
    deque.remove_front()
    assert deque.size() == 0
    assert deque.is_empty()


# DequeCircularArray's default capacity: a deque this big has every slot taken, so
# its front and back indices meet.
_FULL_SIZE = 16


@pytest.mark.parametrize(
    "values",
    [
        pytest.param([], id="empty"),
        pytest.param([1], id="single"),
        pytest.param([1, 2, 3], id="ints"),
        pytest.param(["a", "b"], id="strs"),
    ],
)
def test_iterates_front_to_back(make_deque: MakeDeque, values: list[object]) -> None:
    assert list(make_deque(values)) == values


def test_iterates_items_added_to_front_in_reverse(make_deque: MakeDeque) -> None:
    deque: Deque[int] = make_deque()
    deque.add_front(1)
    deque.add_front(2)
    deque.add_front(3)
    assert list(deque) == [3, 2, 1]


def test_iterates_mixed_front_and_back_adds(make_deque: MakeDeque) -> None:
    deque: Deque[int] = make_deque()
    deque.add_back(1)
    deque.add_front(2)
    deque.add_back(3)
    deque.add_front(4)
    assert list(deque) == [4, 2, 1, 3]


def test_iteration_skips_removed_items(make_deque: MakeDeque) -> None:
    deque = make_deque([1, 2, 3, 4, 5])
    deque.remove_front()
    deque.remove_back()
    assert list(deque) == [2, 3, 4]


def test_iterates_after_emptying(make_deque: MakeDeque) -> None:
    deque = make_deque([1, 2])
    deque.remove_front()
    deque.remove_front()
    assert list(deque) == []


def test_iterates_across_wrap_around(make_deque: MakeDeque) -> None:
    # Sliding a three-item window past _FULL_SIZE adds wraps the circular indices.
    deque = make_deque([0, 1, 2])
    for value in range(3, _FULL_SIZE + 5):
        deque.add_back(value)
        deque.remove_front()
    assert list(deque) == [_FULL_SIZE + 2, _FULL_SIZE + 3, _FULL_SIZE + 4]


def test_iterates_full_deque(make_deque: MakeDeque) -> None:
    deque = make_deque(range(_FULL_SIZE))
    assert list(deque) == list(range(_FULL_SIZE))


def test_iteration_does_not_consume(make_deque: MakeDeque) -> None:
    deque = make_deque([1, 2, 3])
    assert list(deque) == [1, 2, 3]
    assert list(deque) == [1, 2, 3]
    assert deque.size() == 3
    assert deque.peek_front() == 1
    assert deque.peek_back() == 3


def test_iterators_are_independent(make_deque: MakeDeque) -> None:
    deque = make_deque([1, 2, 3])
    first, second = iter(deque), iter(deque)
    assert next(first) == 1
    assert next(first) == 2
    assert next(second) == 1


def test_iterates_in_for_loop(make_deque: MakeDeque) -> None:
    seen: list[int] = []
    for value in make_deque([1, 2, 3]):
        seen.append(value)
    assert seen == [1, 2, 3]


def test_search_returns_matching_item(make_deque: MakeDeque) -> None:
    assert make_deque([1, 2, 3]).search(2) == 2


def test_search_missing_item_returns_none(make_deque: MakeDeque) -> None:
    assert make_deque([1, 2, 3]).search(4) is None


def test_search_empty_deque_returns_none(make_deque: MakeDeque) -> None:
    deque: Deque[int] = make_deque()
    assert deque.search(1) is None


def test_search_returns_first_match_from_front(make_deque: MakeDeque) -> None:
    front, back = {"id": 1}, {"id": 1}
    found = make_deque([front, back]).search({"id": 1})
    assert found is front
