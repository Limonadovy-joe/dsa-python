from __future__ import annotations

from typing import Optional, TypeVar

from dsa.linked_lists.linked_list_node import LinkedListNode

T = TypeVar("T")


class DoublyLinkedListNode(LinkedListNode[T]):
    next: Optional[DoublyLinkedListNode[T]]  # noqa: UP045
    previous: Optional[DoublyLinkedListNode[T]]  # noqa: UP045

    def __init__(  # noqa: ANN204
        self,
        value: T,
        next_node: Optional[DoublyLinkedListNode[T]] = None,  # noqa: UP045
        prev_node: Optional[DoublyLinkedListNode[T]] = None,  # noqa: UP045
    ):
        super().__init__(value, next_node)
        self.previous = prev_node

    def link(self, right: DoublyLinkedListNode[T]) -> None:
        """Link ``right`` after this node in both directions. O(1) time and space."""
        self.next = right
        right.previous = self
