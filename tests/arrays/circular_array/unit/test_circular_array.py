from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from dsa.arrays.circular_array import CircularArray

if TYPE_CHECKING:
    from tests.arrays.circular_array.circular_array_backends import MakeCircularArray


# ---------------------------------------------------------------------------
# Constructor / empty state
# ---------------------------------------------------------------------------


def test_new_array_is_empty() -> None:
    ca: CircularArray[int] = CircularArray()

    assert ca.is_empty()
    assert ca.size() == 0


def test_new_array_with_custom_capacity() -> None:
    ca: CircularArray[int] = CircularArray(4)

    assert ca.is_empty()
    assert ca.size() == 0


def test_peek_on_empty_returns_none() -> None:
    ca: CircularArray[int] = CircularArray()

    assert ca.peek() is None


def test_deque_on_empty_returns_none() -> None:
    ca: CircularArray[int] = CircularArray()

    result = ca.deque()

    assert result is None


# ---------------------------------------------------------------------------
# enqueue
# ---------------------------------------------------------------------------


def test_enqueue_single_item(make_circular_array: MakeCircularArray) -> None:
    ca = make_circular_array([1])

    assert ca.size() == 1
    assert not ca.is_empty()
    assert ca.peek() == 1


def test_enqueue_multiple_items(make_circular_array: MakeCircularArray) -> None:
    ca = make_circular_array([1, 2, 3])

    assert ca.size() == 3
    assert ca.peek() == 1


def test_enqueue_up_to_capacity(make_circular_array: MakeCircularArray) -> None:
    ca = make_circular_array(range(4), capacity=4)

    assert ca.size() == 4
    assert not ca.is_empty()
    assert ca.peek() == 0


def test_enqueue_beyond_capacity_overwrites_oldest(
    make_circular_array: MakeCircularArray,
) -> None:
    ca: CircularArray[int] = make_circular_array(capacity=3)
    ca.enqueue(1)
    ca.enqueue(2)
    ca.enqueue(3)
    # Buffer is full: [1, 2, 3]
    ca.enqueue(4)
    # Oldest (1) overwritten: [4, 2, 3], write wraps around

    assert ca.size() == 3


# ---------------------------------------------------------------------------
# deque (dequeue)
# ---------------------------------------------------------------------------


def test_deque_returns_first_enqueued(
    make_circular_array: MakeCircularArray,
) -> None:
    ca = make_circular_array([10, 20, 30])

    assert ca.deque() == 10


def test_deque_decreases_size(make_circular_array: MakeCircularArray) -> None:
    ca = make_circular_array([1, 2, 3])

    ca.deque()

    assert ca.size() == 2


def test_deque_fifo_order(make_circular_array: MakeCircularArray) -> None:
    ca = make_circular_array([1, 2, 3], capacity=4)

    results = [ca.deque() for _ in range(3)]

    assert results == [1, 2, 3]
    assert ca.is_empty()


def test_deque_all_then_is_empty(make_circular_array: MakeCircularArray) -> None:
    ca = make_circular_array([1, 2], capacity=4)

    ca.deque()
    ca.deque()

    assert ca.is_empty()
    assert ca.size() == 0


def test_deque_then_enqueue(make_circular_array: MakeCircularArray) -> None:
    ca = make_circular_array([1, 2, 3], capacity=4)

    assert ca.deque() == 1
    ca.enqueue(4)

    assert ca.size() == 3
    assert ca.deque() == 2
    assert ca.deque() == 3
    assert ca.deque() == 4
    assert ca.is_empty()


# ---------------------------------------------------------------------------
# peek
# ---------------------------------------------------------------------------


def test_peek_returns_front_without_removing(
    make_circular_array: MakeCircularArray,
) -> None:
    ca = make_circular_array([1, 2, 3])

    assert ca.peek() == 1
    assert ca.peek() == 1
    assert ca.size() == 3


def test_peek_after_deque(make_circular_array: MakeCircularArray) -> None:
    ca = make_circular_array([1, 2, 3], capacity=4)

    ca.deque()

    assert ca.peek() == 2


# ---------------------------------------------------------------------------
# is_empty / size
# ---------------------------------------------------------------------------


def test_is_empty_after_enqueue_and_deque() -> None:
    ca: CircularArray[int] = CircularArray(4)
    ca.enqueue(1)

    assert not ca.is_empty()

    ca.deque()

    assert ca.is_empty()


def test_size_tracks_enqueue_and_deque() -> None:
    ca: CircularArray[int] = CircularArray(4)

    assert ca.size() == 0
    ca.enqueue(1)
    assert ca.size() == 1
    ca.enqueue(2)
    assert ca.size() == 2
    ca.deque()
    assert ca.size() == 1
    ca.deque()
    assert ca.size() == 0


# ---------------------------------------------------------------------------
# Wrap-around behavior
# ---------------------------------------------------------------------------


def test_write_index_wraps_around() -> None:
    ca: CircularArray[int] = CircularArray(3)
    ca.enqueue(1)
    ca.enqueue(2)
    ca.enqueue(3)
    # write_index should have wrapped to 0
    ca.enqueue(4)
    # Slot 0 overwritten with 4

    assert ca.size() == 3


def test_read_index_wraps_around() -> None:
    ca: CircularArray[int] = CircularArray(3)
    ca.enqueue(1)
    ca.enqueue(2)
    ca.enqueue(3)

    assert ca.deque() == 1
    assert ca.deque() == 2
    assert ca.deque() == 3
    assert ca.is_empty()


def test_interleaved_enqueue_deque_with_wrap() -> None:
    ca: CircularArray[int] = CircularArray(3)
    ca.enqueue(1)
    ca.enqueue(2)
    assert ca.deque() == 1
    ca.enqueue(3)
    ca.enqueue(4)
    # Buffer: [_, 2, 3] then [4, 2, 3] after wrap

    assert ca.deque() == 2
    assert ca.deque() == 3
    assert ca.deque() == 4
    assert ca.is_empty()


# ---------------------------------------------------------------------------
# Different types
# ---------------------------------------------------------------------------


def test_string_values(make_circular_array: MakeCircularArray) -> None:
    ca = make_circular_array(["a", "b", "c"], capacity=4)

    assert ca.deque() == "a"
    assert ca.deque() == "b"
    assert ca.deque() == "c"


@pytest.mark.parametrize("value", [0, "", None, False], ids=repr)
def test_enqueue_falsy_values(value: object) -> None:
    ca: CircularArray[object] = CircularArray(4)
    ca.enqueue(value)

    assert ca.size() == 1
    assert ca.peek() is value


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_capacity_one() -> None:
    ca: CircularArray[int] = CircularArray(1)
    ca.enqueue(1)

    assert ca.size() == 1
    assert ca.peek() == 1
    assert ca.deque() == 1
    assert ca.is_empty()


def test_capacity_one_overwrite() -> None:
    ca: CircularArray[int] = CircularArray(1)
    ca.enqueue(1)
    ca.enqueue(2)

    assert ca.size() == 1
    assert ca.deque() == 2


def test_many_enqueue_dequeue_cycles() -> None:
    ca: CircularArray[int] = CircularArray(4)

    for cycle in range(10):
        for i in range(4):
            ca.enqueue(cycle * 4 + i)
        for i in range(4):
            assert ca.deque() == cycle * 4 + i

    assert ca.is_empty()
