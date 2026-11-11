from __future__ import annotations

from typing import TYPE_CHECKING

from dsa.linked_lists.linked_list_node import LinkedListNode
from utils.comparator.comparator import Comparator

if TYPE_CHECKING:
    from collections.abc import Callable

    from utils.comparator.comparator import ComparatorFunc


class LinkedList[T]:
    head: LinkedListNode[T] | None
    tail: LinkedListNode[T] | None
    # TODO(DSA-27): comparator type should be an interface/ABC, not the class itself?
    #   [Refactor | Linked Lists | Core | needs-human]
    comparator: Comparator[T]

    def __init__(self, compare_fun: ComparatorFunc[T] | None = None) -> None:
        self.head = None
        self.tail = None
        self.comparator = Comparator(compare_fun)

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        items: list[T] = []
        current = self.head
        while current is not None:
            items.append(current.value)
            current = current.next
        return f"LinkedList({items!r})"

    def to_string(self) -> str:
        output: list[str] = []
        current_node = self.head

        while current_node is not None:
            output.append(str(current_node))
            current_node = current_node.next

        return ",".join(output)

    def append(self, value: T) -> LinkedList[T]:
        node = LinkedListNode[T](value)

        # head and tail are None together, so checking tail covers both.
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node

        return self

    def prepend(self, value: T) -> LinkedList[T]:
        if self.head is None:
            return self.append(value)

        new_head = LinkedListNode(value)
        new_head.next = self.head
        self.head = new_head
        return self

    # TODO(DSA-28): how to name a parameter that is either a value or a callback?
    #   [Refactor | Linked Lists | Core | needs-human]
    #
    # TODO: profile find() and check the garbage collector
    #   [Analysis | Linked Lists | Core | needs-human]
    #   Check when functions and instances are created.
    def find(
        self, value_or_callback: T | Callable[[T], bool]
    ) -> LinkedListNode[T] | None:
        next_node = self.head

        # TODO(DSA-27): curry comparator.equal so it takes only the actual value
        #   [Refactor | Linked Lists | Core | needs-human]
        #   and value_to_find is fixed.

        while next_node is not None:
            actual_value = next_node.value

            if callable(value_or_callback):
                if value_or_callback(actual_value):
                    return next_node
            elif self.comparator.equal(value_or_callback, actual_value):
                return next_node
            next_node = next_node.next
        return None

    def delete(self, value: T) -> LinkedListNode[T] | None:
        # TODO(DSA-28): check naming conventions of returning nodes
        #   [Refactor | Linked Lists | Core | needs-human]
        current_node = self.head
        prev_node = None
        node_to_return: LinkedListNode[T] | None = None

        while current_node is not None:
            next_node = current_node.next
            if self.comparator.equal(current_node.value, value):
                node_to_return = node_to_return or current_node
                # check head
                if self.head is not None and self.comparator.equal(
                    self.head.value, current_node.value
                ):
                    if next_node is None:
                        self.head = None
                        self.tail = self.head
                    else:
                        self.head = next_node
                elif prev_node is not None:
                    # check tail
                    if next_node is None:
                        prev_node.next = None
                        self.tail = prev_node
                    else:
                        prev_node.next = next_node
                current_node = next_node
            else:
                prev_node = current_node
                current_node = next_node

        if node_to_return is not None:
            node_to_return.next = None

        return node_to_return

    def delete_tail(self) -> LinkedListNode[T] | None:
        current_node = self.head
        prev_node: LinkedListNode[T] | None = None
        node_to_return: LinkedListNode[T] | None = self.tail

        while current_node is not None:
            next_node = current_node.next

            # check should be out of loop cycle
            if self.head is not None and self.head.next is None:
                node_to_return = self.head
                self.head = None
                self.tail = self.head
            elif next_node is None and prev_node is not None:
                prev_node.next = None
                self.tail = prev_node

            prev_node = current_node
            current_node = next_node

        return node_to_return

    def delete_head(self) -> LinkedListNode[T] | None:
        node_to_return = self.head
        if node_to_return is None:
            return node_to_return

        new_head = node_to_return.next

        if new_head is None:
            self.head = None
            self.tail = self.head
        else:
            self.head = new_head

        if node_to_return is not None:
            node_to_return.next = None

        return node_to_return

    def from_array(self, array: list[T]) -> LinkedList[T]:
        for item in array:
            self.append(item)

        return self

    def reverse(self) -> None:
        if self.head is None or self.head.next is None:
            return None

        # TODO(DSA-29): extract a swap helper function
        #   [Refactor | Linked Lists | Core | agent-ready]
        #   First algorithm: new_head as a separate variable; three pointer
        #   variables (current, next, new_head), without tmp_node.
        new_head: LinkedListNode[T] | None = None
        new_tail: LinkedListNode[T] | None = None
        current_node: LinkedListNode[T] | None = self.head
        next_node: LinkedListNode[T] | None = self.head.next
        # 1 -> 2 -> 3
        # 3 -> 2 -> 1

        # 1 -> 2 -> 3 -> 4
        # 4 -> 3 -> 2 -> 1

        while current_node is not None:
            next_next_node = next_node.next if next_node is not None else None

            current_node.next = None
            new_tail = new_tail or current_node

            if new_head is None and next_node is not None:
                new_head = next_node
                new_head.next = new_tail
            else:
                current_node.next = new_head
                new_head = current_node

            current_node = next_next_node
            next_node = current_node

        self.head = new_head
        self.tail = new_tail
        return None
