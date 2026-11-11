"""Deque backends under test, shared by unit, integration and performance tests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from dsa.linked_lists import DoublyLinkedList
from dsa.queues import DequeCircularArray
from dsa.queues.deque import Deque, DequeDoubleLinkedList

if TYPE_CHECKING:
    from collections.abc import Iterable


class MakeDeque(Protocol):
    """Build a fresh deque, optionally pre-filled with ``values``."""

    def __call__[T](self, values: Iterable[T] = ()) -> Deque[T]: ...


def _fill[T](deque: Deque[T], values: Iterable[T]) -> Deque[T]:
    for value in values:
        deque.add_back(value)
    return deque


def doubly_linked_list_deque[T](values: Iterable[T] = ()) -> Deque[T]:
    return _fill(Deque(DequeDoubleLinkedList(DoublyLinkedList[T]())), values)


def circular_array_deque[T](values: Iterable[T] = ()) -> Deque[T]:
    return _fill(Deque(DequeCircularArray[T]()), values)


# Adding a backend here runs every deque test against it.
BACKENDS: dict[str, MakeDeque] = {
    "doubly_linked_list": doubly_linked_list_deque,
    "circular_array": circular_array_deque,
}
