from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, overload

from dsa.linked_lists.doubly_linked_list_node import DoublyLinkedListNode
from utils.comparator.comparator import Comparator

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from utils.comparator.comparator import ComparatorFunc

T = TypeVar("T")


class DoublyLinkedList[T]:
    comparator: Comparator[T]
    head: DoublyLinkedListNode[T] | None
    tail: DoublyLinkedListNode[T] | None

    def __init__(self, compare_fun: ComparatorFunc[T] | None = None) -> None:
        self.head = None
        self.tail = None
        self.comparator = Comparator(compare_fun)

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        items: list[T] = list(self)
        return f"DoublyLinkedList({items!r})"

    def __iter__(self) -> Iterator[T]:
        current_node = self.head
        while current_node:
            yield current_node.value
            current_node = current_node.next

    @overload
    def to_array(self, cb: None = None) -> list[T]: ...
    @overload
    def to_array(self, cb: Callable[[T], str]) -> list[str]: ...
    def to_array(self, cb: Callable[[T], str] | None = None) -> list[T] | list[str]:
        if cb is None:
            return list(self)
        return [cb(value) for value in self]

    def to_string(self, stringifier: Callable[[T], str] | None = None) -> str:
        return ",".join(self.to_array(stringifier or str))

    def append(self, value: T) -> DoublyLinkedList[T]:
        new_node = DoublyLinkedListNode(value)

        if self.tail is None:
            self.head = new_node
            self.tail = self.head
            return self

        self.tail.link(new_node)
        self.tail = new_node
        return self

    def prepend(self, value: T) -> DoublyLinkedList[T]:
        new_node = DoublyLinkedListNode(value)

        if self.head is None:
            self.head = new_node
            self.tail = self.head
            return self

        new_node.link(self.head)
        self.head = new_node
        return self

    # TODO(DSA-30): refactor delete_head to eliminate if statements
    #   [Refactor | Linked Lists | Core | agent-ready]
    def delete_head(self) -> DoublyLinkedListNode[T] | None:
        if self.head is None:
            return None

        node_to_return: DoublyLinkedListNode[T] = self.head
        new_head = node_to_return.next
        node_to_return.next = None

        if new_head:
            new_head.previous = None
            self.head = new_head

            return node_to_return

        self.head = None
        self.tail = self.head
        return node_to_return

    def delete_tail(self) -> DoublyLinkedListNode[T] | None:
        if self.tail is None:
            return None

        node_to_return: DoublyLinkedListNode[T] = self.tail
        new_tail = node_to_return.previous
        node_to_return.previous = None

        if new_tail:
            new_tail.next = None
            self.tail = new_tail
        else:
            self.head = None
            self.tail = self.head

        return node_to_return

    def delete(self, value: T) -> DoublyLinkedListNode[T] | None:
        if self.head is None:
            return None

        current_node: DoublyLinkedListNode[T] | None = self.head
        node_to_return: DoublyLinkedListNode[T] | None = None
        while current_node is not None:
            previous_node = current_node.previous
            next_node = current_node.next

            if self.comparator.equal(current_node.value, value):
                node_to_return = node_to_return or current_node

                # head position
                if previous_node is None:
                    # TODO(DSA-30): should this assignment be outside the nested if?
                    #   [Refactor | Linked Lists | Core | agent-ready]
                    #   Should delete_head be used here instead?
                    current_node.next = None

                    if next_node is None:
                        self.head = None
                        self.tail = self.head
                    else:
                        next_node.previous = None

                    self.head = next_node

                # tail position
                elif next_node is None:
                    current_node.previous = None
                    previous_node.next = None

                    self.tail = previous_node
                else:
                    current_node.previous = None
                    current_node.next = None

                    previous_node.link(next_node)

            current_node = next_node
        return node_to_return

    def reverse(self) -> None:
        head, tail = self.head, self.tail
        # head and tail are None together; checking both narrows both for mypy.
        if head is None or tail is None or head.next is None:
            return None

        if head.next.next is None:
            self.head = tail
            tail.previous = None
            tail.next = head

            head.next = None
            head.previous = tail
            self.tail = head
            return None

        new_head = tail
        previous_node = tail.previous
        new_head.previous = None
        new_tail = new_head

        while previous_node:
            new_node = DoublyLinkedListNode(previous_node.value)

            new_tail.link(new_node)
            new_tail = new_node
            previous_node = previous_node.previous

        self.head = new_head
        self.tail = new_tail
        return None
