from __future__ import annotations  # noqa: I001

from typing import Optional, Callable, TypeVar  # noqa: UP035

T = TypeVar("T")


class LinkedListNode[T]:
    """A node in a singly linked list."""

    value: T
    next: Optional[LinkedListNode[T]]  # noqa: UP045

    def __init__(self, value: T, next: Optional[LinkedListNode[T]] = None) -> None:  # noqa: UP045
        self.value = value
        self.next = next

    def __str__(self) -> str:
        return f"{self.value}"

    def __repr__(self) -> str:
        return f"LinkedListNode(value='{self.value}'"

    def to_string(self, callback: Optional[Callable[[T], str]] = None) -> str:  # noqa: UP045
        if callback is not None:
            return callback(self.value)
        return str(self)
