"""Double-ended queue with pluggable storage backends.

Uses the **Strategy** pattern: ``Deque`` delegates every operation to a
``DequeStorage`` backend chosen at construction time.  Each backend is an
**Adapter** that wraps a lower-level data structure (e.g.
``DoublyLinkedList``) behind the uniform ``DequeStorage`` protocol.

This design lets performance benchmarks compare backends (linked-list vs
circular-array) through the same ``Deque`` interface — swap the strategy,
rerun the test.

Classes:
    DequeStorage    Protocol (strategy interface) for all backends.
    DequeDoubleLinkedList  Adapter: ``DoublyLinkedList`` → ``DequeStorage``.
    DequeCircularArray     Adapter: circular array → ``DequeStorage`` (stub).
    Deque           Context that delegates to whichever ``DequeStorage`` it receives.
"""

from collections.abc import Callable, Iterator
from typing import Protocol, cast

from dsa.linked_lists import DoublyLinkedList, DoublyLinkedListNode
from utils.comparator.comparator import Comparator, ComparatorFunc


class DequeStorage[T](Protocol):
    def __iter__(self) -> Iterator[T]: ...

    def add_front(self, item: T) -> None: ...

    def remove_front(self) -> T | None: ...

    def peek_front(self) -> T | None: ...

    def add_back(self, item: T) -> None: ...

    def remove_back(self) -> T | None: ...

    def peek_back(self) -> T | None: ...

    def size(self) -> int: ...

    def is_empty(self) -> bool: ...

    def search(self, item: T) -> T | None: ...

    def to_string(self, stringifier: Callable[[T], str] | None = None) -> str: ...


class DequeDoubleLinkedList[T]:
    _size: int

    def __init__(self, ll: DoublyLinkedList[T]) -> None:
        self._ll = ll
        self._size = 0

    def __iter__(self) -> Iterator[T]:
        return iter(self._ll)

    def size(self) -> int:
        return self._size

    def _increment_size(self, value: int = 1) -> None:
        self._size = self._size + value

    def _decrement_size(self, value: int = 1) -> None:
        if self._size > 0:
            self._size = self._size - value

    def _get_node_value(self, node: DoublyLinkedListNode[T] | None) -> T | None:
        return node.value if node else None

    def add_front(self, item: T) -> None:
        self._increment_size()
        self._ll.prepend(item)

    def remove_front(self) -> T | None:
        self._decrement_size()
        return self._get_node_value(self._ll.delete_head())

    def peek_front(self) -> T | None:
        return self._get_node_value(self._ll.head)

    def add_back(self, item: T) -> None:
        self._increment_size()
        self._ll.append(item)

    def remove_back(self) -> T | None:
        self._decrement_size()
        return self._get_node_value(self._ll.delete_tail())

    def peek_back(self) -> T | None:
        return self._get_node_value(self._ll.tail)

    def is_empty(self) -> bool:
        return self._size == 0

    def to_string(self, stringifier: Callable[[T], str] | None = None) -> str:
        return self._ll.to_string(stringifier)

    def search(self, item: T) -> T | None:
        for value in self._ll:
            if self._ll.comparator.equal(value, item):
                return value
        return None


class DequeCircularArray[T]:
    _capacity: int
    _front_index: int
    _back_index: int
    _current_size: int
    _comparator: Comparator[T]
    _slots: list[T | None]

    def __init__(
        self, capacity: int = 16, compare_fun: ComparatorFunc[T] | None = None
    ) -> None:
        self._capacity = capacity
        self._front_index = 0
        self._back_index = 0
        self._current_size = 0
        self._slots = [None] * self._capacity
        self._comparator = Comparator(compare_fun)

    def _increment_current_size(self, value: int = 1) -> None:
        if self._current_size < self._capacity:
            self._current_size = self._current_size + value

    def _decrement_current_size(self, value: int = 1) -> None:
        if self._current_size > 0:
            self._current_size = self._current_size - value

    def add_front(self, item: T) -> None:

        if self.is_full():
            raise IndexError("Deque is full")

        self._increment_current_size()

        self._front_index = (self._front_index - 1) % self._capacity
        self._slots[self._front_index] = item

    def remove_back(self) -> T | None:
        if self.is_empty():
            return None

        self._decrement_current_size()

        self._back_index = (self._back_index - 1) % self._capacity
        return_value = self._slots[self._back_index]
        self._slots[self._back_index] = None

        return return_value

    def remove_front(self) -> T | None:
        if self.is_empty():
            return None

        self._decrement_current_size()

        return_value = self._slots[self._front_index]
        self._slots[self._front_index] = None
        self._front_index = (self._front_index + 1) % self._capacity
        return return_value

    def add_back(self, item: T) -> None:

        if self.is_full():
            raise IndexError("Deque is full")

        self._increment_current_size()

        self._slots[self._back_index] = item
        self._back_index = (self._back_index + 1) % self._capacity

    def peek_front(self) -> T | None:
        return self._slots[self._front_index]

    def peek_back(self) -> T | None:
        return self._slots[(self._back_index - 1) % self._capacity]

    def size(self) -> int:
        return self._current_size

    def is_full(self) -> bool:
        return self._current_size == self._capacity

    def is_empty(self) -> bool:
        return self._current_size == 0

    def __iter__(self) -> Iterator[T]:
        item_index = self._front_index
        for _ in range(self._current_size):
            # The _current_size slots from _front_index (wrapping) are always populated.
            yield cast("T", self._slots[item_index])
            item_index = (item_index + 1) % self._capacity

    def to_array(self) -> list[T]:
        return list(self)

    def to_string(self, stringifier: Callable[[T], str] | None = None) -> str:
        cb = stringifier if callable(stringifier) else str
        return ",".join(map(cb, self))

    def search(self, item: T) -> T | None:
        for value in self:
            if self._comparator.equal(value, item):
                return value
        return None


class Deque[T](DequeStorage[T]):
    _storage: DequeStorage[T]

    def __init__(self, storage: DequeStorage[T]) -> None:
        self._storage = storage

    def __iter__(self) -> Iterator[T]:
        return iter(self._storage)

    def __str__(self) -> str:
        return self._storage.to_string()

    def add_front(self, item: T) -> None:
        self._storage.add_front(item)

    def remove_front(self) -> T | None:
        return self._storage.remove_front()

    def peek_front(self) -> T | None:
        return self._storage.peek_front()

    def add_back(self, item: T) -> None:
        return self._storage.add_back(item)

    def remove_back(self) -> T | None:
        return self._storage.remove_back()

    def peek_back(self) -> T | None:
        return self._storage.peek_back()

    def to_string(self, stringifier: Callable[[T], str] | None = None) -> str:
        return self._storage.to_string(stringifier)

    def is_empty(self) -> bool:
        return self._storage.is_empty()

    def size(self) -> int:
        return self._storage.size()

    def search(self, item: T) -> T | None:
        return self._storage.search(item)
