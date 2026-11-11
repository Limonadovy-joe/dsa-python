"""Queue backends under test, shared by unit, integration and performance tests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from dsa.linked_lists import LinkedList
from dsa.queues.queue import Queue, QueueLinkedList, QueueList

if TYPE_CHECKING:
    from collections.abc import Iterable


class MakeQueue(Protocol):
    """Build a fresh queue, optionally pre-filled with ``values`` in FIFO order."""

    def __call__[T](self, values: Iterable[T] = ()) -> Queue[T]: ...


def _fill[T](queue: Queue[T], values: Iterable[T]) -> Queue[T]:
    for value in values:
        queue.enqueue(value)
    return queue


def linked_list_queue[T](values: Iterable[T] = ()) -> Queue[T]:
    return _fill(Queue(QueueLinkedList(LinkedList[T]())), values)


def list_queue[T](values: Iterable[T] = ()) -> Queue[T]:
    return _fill(Queue(QueueList[T]([])), values)


# Adding a backend here runs every queue test against it.
BACKENDS: dict[str, MakeQueue] = {
    "linked_list": linked_list_queue,
    "list": list_queue,
}
