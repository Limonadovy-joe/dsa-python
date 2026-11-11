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

from typing import Optional, Generic, TypeVar, Protocol, Callable  # noqa: I001, UP035

from dsa.linked_lists.linked_list import LinkedList

T = TypeVar("T")


class QueueStorage(Protocol[T]):
    def add_to_back(self, item: T) -> None: ...

    def remove_from_front(self) -> Optional[T]: ...  # noqa: UP045

    def size(self) -> int: ...

    def search(self, item: T) -> Optional[T]: ...  # noqa: UP045

    def to_string(self, stringifier: Optional[Callable[[T], str]] = None) -> str: ...  # noqa: UP045

    def front(self) -> Optional[T]: ...  # noqa: UP045


class QueueList(Generic[T]):  # noqa: UP046
    _list: list[T]

    def __init__(self, list: list[T]) -> None:
        self._list = list

    def add_to_back(self, item: T) -> None:
        self._list.append(item)
        return None  # noqa: PLR1711

    def remove_from_front(self) -> Optional[T]:  # noqa: UP045
        return self._list.pop(0) if len(self._list) > 0 else None

    def size(self) -> int:
        return len(self._list)

    def search(self, item: T) -> Optional[T]:  # noqa: UP045
        filter_obj = filter(lambda current_item: current_item == item, self._list)
        items = list(filter_obj)
        if len(items) == 0:
            return None

        return items[0]

    def to_string(self, stringifier: Optional[Callable[[T], str]] = None) -> str:  # noqa: UP045
        callback: Callable[[T], str] = stringifier if stringifier is not None else str
        values = list(map(callback, self._list))
        return ",".join(values)

    def front(self) -> Optional[T]:  # noqa: UP045
        queue_list = self._list
        return queue_list[0] if len(queue_list) > 0 else None


class QueueLinkedList(Generic[T]):  # noqa: UP046
    _ll: LinkedList[T]

    def __init__(self, linked_list: LinkedList[T]) -> None:
        self._ll = linked_list

    def add_to_back(self, item: T) -> None:
        self._ll.append(item)
        return None  # noqa: PLR1711

    def remove_from_front(self) -> Optional[T]:  # noqa: UP045
        node = self._ll.delete_head()
        return node.value if node is not None else None

    def size(self) -> int:
        size = 0

        nodes = self._ll.head
        while nodes is not None:
            size = size + 1
            nodes = nodes.next
        return size

    def search(self, item: T) -> Optional[T]:  # noqa: UP045
        node = self._ll.find(item)
        return node.value if node is not None else None

    def to_string(self, stringifier: Optional[Callable[[T], str]] = None) -> str:  # noqa: UP045
        output: list[str] = []
        current_node = self._ll.head

        while current_node is not None:
            value = current_node.value
            string = stringifier(value) if stringifier is not None else str(value)
            output.append(string)
            current_node = current_node.next

        return ",".join(output)

    def front(self) -> Optional[T]:  # noqa: UP045
        node = self._ll.head
        return node.value if node else None


class Queue(Generic[T]):  # noqa: UP046
    _storage: QueueStorage[T]

    def __init__(self, storage: QueueStorage[T]) -> None:
        self._storage = storage

    def __str__(self) -> str:
        return self._storage.to_string()

    def search(self, item: T) -> T | None:
        return self._storage.search(item)

    def enqueue(self, item: T) -> None:
        self._storage.add_to_back(item)
        return None  # noqa: PLR1711

    def dequeue(self) -> T | None:
        return self._storage.remove_from_front()

    def to_string(self, stringifier: Optional[Callable[[T], str]] = None) -> str:  # noqa: UP045
        return self._storage.to_string(stringifier)

    def is_empty(self) -> bool:
        return self._storage.size() == 0

    def peek(self) -> Optional[T]:  # noqa: UP045
        return self._storage.front()
