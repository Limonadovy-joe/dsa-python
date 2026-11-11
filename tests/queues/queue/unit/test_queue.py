from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from dsa.queues.queue import Queue
    from tests.queues.queue.queue_backends import MakeQueue

# Every test below runs once per backend via the `make_queue` fixture, so the
# tables only list data.
PAIRS = ({"key": "key1", "value": "test1"}, {"key": "key2", "value": "test2"})

FIFO_CASES = [
    pytest.param([], id="empty"),
    pytest.param([1], id="single"),
    pytest.param([1, 2, 3], id="ints"),
    pytest.param(list(PAIRS), id="dicts"),
]


def _key_value(item: dict[str, str]) -> str:
    return f"{item['key']}:{item['value']}"


def test_new_queue_is_empty(make_queue: MakeQueue) -> None:
    queue: Queue[int] = make_queue()
    assert queue.is_empty()


@pytest.mark.parametrize("count", [1, 2, 10])
def test_is_empty_tracks_enqueue_and_dequeue(make_queue: MakeQueue, count: int) -> None:
    queue = make_queue(range(count))
    assert not queue.is_empty()

    for _ in range(count):
        queue.dequeue()

    assert queue.is_empty()


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        pytest.param([], "", id="empty"),
        pytest.param([1], "1", id="single"),
        pytest.param([1, 2, 3], "1,2,3", id="ints"),
        pytest.param(["a", "b"], "a,b", id="strs"),
    ],
)
def test_to_string_joins_items_in_fifo_order(
    make_queue: MakeQueue, values: list[object], expected: str
) -> None:
    assert make_queue(values).to_string() == expected


def test_to_string_applies_custom_stringifier(make_queue: MakeQueue) -> None:
    assert make_queue(PAIRS).to_string(_key_value) == "key1:test1,key2:test2"


@pytest.mark.parametrize("values", FIFO_CASES)
def test_dequeue_returns_items_in_fifo_order(
    make_queue: MakeQueue, values: list[object]
) -> None:
    queue = make_queue(values)
    assert [queue.dequeue() for _ in values] == values
    assert queue.is_empty()


def test_dequeue_on_empty_returns_none(make_queue: MakeQueue) -> None:
    queue: Queue[int] = make_queue()
    assert queue.dequeue() is None


@pytest.mark.parametrize("values", FIFO_CASES[1:])
def test_peek_returns_front_without_removing(
    make_queue: MakeQueue, values: list[object]
) -> None:
    queue = make_queue(values)
    assert queue.peek() == values[0]
    assert queue.peek() == values[0]
    assert [queue.dequeue() for _ in values] == values


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        pytest.param([], None),
        pytest.param([1], 1),
        pytest.param([1, 2, 3], 1),
        pytest.param(["a", "b"], "a"),
    ],
)
def test_peek(make_queue: MakeQueue, values: list[object], expected: object) -> None:
    queue = make_queue(values)
    assert queue.peek() is expected


def test_search_returns_matching_item(make_queue: MakeQueue) -> None:
    assert make_queue([1, 2, 3]).search(2) == 2


def test_search_missing_item_returns_none(make_queue: MakeQueue) -> None:
    assert make_queue([1, 2, 3]).search(4) is None
