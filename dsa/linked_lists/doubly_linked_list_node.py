from __future__ import annotations

from dsa.linked_lists.linked_list_node import LinkedListNode


class DoublyLinkedListNode[T](LinkedListNode[T]):
    next: DoublyLinkedListNode[T] | None
    previous: DoublyLinkedListNode[T] | None

    def __init__(
        self,
        value: T,
        next_node: DoublyLinkedListNode[T] | None = None,
        prev_node: DoublyLinkedListNode[T] | None = None,
    ) -> None:
        super().__init__(value, next_node)
        self.previous = prev_node

    def link(self, right: DoublyLinkedListNode[T]) -> None:
        """Link ``right`` after this node in both directions. O(1) time and space."""
        self.next = right
        right.previous = self
