"""FIFO queue with pluggable storage backends.

Uses the **Strategy** pattern: ``Queue`` delegates every operation to a
``QueueStorage`` backend chosen at construction time.  Each backend is an
**Adapter** that wraps a lower-level data structure (``list`` or
``LinkedList``) behind the uniform ``QueueStorage`` protocol.

This design lets performance benchmarks compare backends (linked-list vs
Python list) through the same ``Queue`` interface — swap the strategy,
rerun the test.

Classes:
    QueueStorage     Protocol (strategy interface) for all backends.
    QueueList        Adapter: Python ``list`` → ``QueueStorage``.
    QueueLinkedList  Adapter: ``LinkedList`` → ``QueueStorage``.
    Queue            Context that delegates to whichever ``QueueStorage`` it receives.
"""

from collections.abc import Callable
from typing import Protocol

from dsa.linked_lists.linked_list import LinkedList


class QueueStorage[T](Protocol):
    def add_to_back(self, item: T) -> None: ...

    def remove_from_front(self) -> T | None: ...

    def size(self) -> int: ...

    def search(self, item: T) -> T | None: ...

    def to_string(self, stringifier: Callable[[T], str] | None = None) -> str: ...

    def front(self) -> T | None: ...


class QueueList[T]:
    _list: list[T]

    def __init__(self, list: list[T]) -> None:
        self._list = list

    def add_to_back(self, item: T) -> None:
        self._list.append(item)

    def remove_from_front(self) -> T | None:
        return self._list.pop(0) if len(self._list) > 0 else None

    def size(self) -> int:
        return len(self._list)

    def search(self, item: T) -> T | None:
        filter_obj = filter(lambda current_item: current_item == item, self._list)
        items = list(filter_obj)
        if len(items) == 0:
            return None

        return items[0]

    def to_string(self, stringifier: Callable[[T], str] | None = None) -> str:
        callback: Callable[[T], str] = stringifier if stringifier is not None else str
        values = list(map(callback, self._list))
        return ",".join(values)

    def front(self) -> T | None:
        queue_list = self._list
        return queue_list[0] if len(queue_list) > 0 else None


class QueueLinkedList[T]:
    _ll: LinkedList[T]

    def __init__(self, linked_list: LinkedList[T]) -> None:
        self._ll = linked_list

    def add_to_back(self, item: T) -> None:
        self._ll.append(item)

    def remove_from_front(self) -> T | None:
        node = self._ll.delete_head()
        return node.value if node is not None else None

    def size(self) -> int:
        size = 0

        nodes = self._ll.head
        while nodes is not None:
            size = size + 1
            nodes = nodes.next
        return size

    def search(self, item: T) -> T | None:
        node = self._ll.find(item)
        return node.value if node is not None else None

    def to_string(self, stringifier: Callable[[T], str] | None = None) -> str:
        output: list[str] = []
        current_node = self._ll.head

        while current_node is not None:
            value = current_node.value
            string = stringifier(value) if stringifier is not None else str(value)
            output.append(string)
            current_node = current_node.next

        return ",".join(output)

    def front(self) -> T | None:
        node = self._ll.head
        return node.value if node else None


class Queue[T]:
    _storage: QueueStorage[T]

    def __init__(self, storage: QueueStorage[T]) -> None:
        self._storage = storage

    def __str__(self) -> str:
        return self._storage.to_string()

    def search(self, item: T) -> T | None:
        return self._storage.search(item)

    def enqueue(self, item: T) -> None:
        self._storage.add_to_back(item)

    def dequeue(self) -> T | None:
        return self._storage.remove_from_front()

    def to_string(self, stringifier: Callable[[T], str] | None = None) -> str:
        return self._storage.to_string(stringifier)

    def is_empty(self) -> bool:
        return self._storage.size() == 0

    def peek(self) -> T | None:
        return self._storage.front()
