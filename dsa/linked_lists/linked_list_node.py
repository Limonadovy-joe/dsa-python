from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


class LinkedListNode[T]:
    """A node in a singly linked list."""

    value: T
    next: LinkedListNode[T] | None

    def __init__(self, value: T, next: LinkedListNode[T] | None = None) -> None:
        self.value = value
        self.next = next

    def __str__(self) -> str:
        return f"{self.value}"

    def __repr__(self) -> str:
        return f"LinkedListNode(value='{self.value}'"

    def to_string(self, callback: Callable[[T], str] | None = None) -> str:
        if callback is not None:
            return callback(self.value)
        return str(self)
