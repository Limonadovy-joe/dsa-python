from __future__ import annotations

from collections.abc import Callable  # noqa: TC003
from typing import Any, Protocol

import pytest

from dsa.linked_lists import LinkedList, LinkedListNode
from utils.comparator.comparator import ComparatorFunc  # noqa: TC001

# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def _values[T](llist: LinkedList[T]) -> list[T]:
    """Walk the list from head to tail and collect the values."""
    out: list[T] = []
    node: LinkedListNode[T] | None = llist.head
    while node is not None:
        out.append(node.value)
        node = node.next
    return out


def _nodes[T](llist: LinkedList[T]) -> list[LinkedListNode[T]]:
    out: list[LinkedListNode[T]] = []
    node: LinkedListNode[T] | None = llist.head
    while node is not None:
        out.append(node)
        node = node.next
    return out


def _compare_by_id(a: dict[str, Any], b: dict[str, Any]) -> int:
    if a["id"] == b["id"]:
        return 0
    return -1 if a["id"] < b["id"] else 1


def _compare_by_name_length(a: dict[str, Any], b: dict[str, Any]) -> int:
    if len(a["name"]) == len(b["name"]):
        return 0
    return -1 if len(a["name"]) < len(b["name"]) else 1


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
class LinkedListFactory(Protocol):
    def __call__(
        self,
        values: list[Any] | None = None,
        compare_fun: ComparatorFunc[Any] | None = None,
    ) -> LinkedList[Any]: ...


@pytest.fixture
def linked_list_factory() -> LinkedListFactory:
    def _create_linked_list(
        values: list[Any] | None = None,
        compare_fun: ComparatorFunc[Any] | None = None,
    ) -> LinkedList[Any]:
        if values is not None and len(values) > 0:
            ll: LinkedList[Any] = LinkedList(compare_fun)
            ll.from_array(values)
            return ll

        return LinkedList(compare_fun)

    return _create_linked_list


@pytest.fixture
def empty_linked_list(linked_list_factory: LinkedListFactory) -> LinkedList[Any]:
    return linked_list_factory()


# ---------------------------------------------------------------------------
# Initial data tests, constructors
# ---------------------------------------------------------------------------


def test_empty_linked_list(empty_linked_list: LinkedList[Any]) -> None:
    assert isinstance(empty_linked_list, LinkedList)
    assert empty_linked_list.head is None
    assert empty_linked_list.tail is None
    assert _values(empty_linked_list) == []


@pytest.mark.parametrize(
    "input_values, expected_head, expected_tail",
    [
        ([1, 2, 3, 4, 5], 1, 5),
        (["a", "b", "c"], "a", "c"),
        ([42], 42, 42),  # Single item: head and tail should be the same
    ],
)
def test_linked_list_initial_state(
    linked_list_factory: LinkedListFactory,
    input_values: list[Any],
    expected_head: object,
    expected_tail: object,
) -> None:
    ll = linked_list_factory(values=input_values)

    assert ll.head is not None
    assert ll.head.value == expected_head

    assert ll.tail is not None
    assert ll.tail.value == expected_tail
    assert _values(ll) == input_values


@pytest.mark.parametrize(
    "input_values, compare_by, expected_head, expected_tail",
    [
        # Scenario 1: Standard initialization with _compare_by_id
        (
            [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
                {"id": 3, "name": "Joe"},
            ],
            _compare_by_id,
            {"id": 1, "name": "Alice"},
            {"id": 3, "name": "Joe"},
        ),
        # Scenario 2: only one custom object
        (
            [{"id": 1, "name": "Alice"}],
            _compare_by_id,
            {"id": 1, "name": "Alice"},
            {"id": 1, "name": "Alice"},
        ),
        # Scenario 3: Using a completely different comparator
        (
            [{"id": 1, "name": "Bo"}, {"id": 2, "name": "Alexander"}],
            _compare_by_name_length,
            {"id": 1, "name": "Bo"},
            {"id": 2, "name": "Alexander"},
        ),
    ],
)
def test_custom_object_linked_list_initial_state(
    linked_list_factory: LinkedListFactory,
    input_values: list[Any],
    compare_by: ComparatorFunc[Any],
    expected_head: object,
    expected_tail: object,
) -> None:
    ll = linked_list_factory(values=input_values, compare_fun=compare_by)

    assert ll.head is not None
    assert ll.head.value == expected_head

    assert ll.tail is not None
    assert ll.tail.value == expected_tail
    assert _values(ll) == input_values


# ---------------------------------------------------------------------------
# append
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "initial_values, values_to_append, expected_head, expected_tail, expected_values",
    [
        # Append to empty list
        ([], [1], 1, 1, [1]),
        # Append to populated list
        ([1], [2], 1, 2, [1, 2]),
        # Append keeps duplicates
        ([], ["a", "b", "b", "c", "b"], "a", "b", ["a", "b", "b", "c", "b"]),
        # Append preserves insertion order
        ([], [1, 2, 3], 1, 3, [1, 2, 3]),
    ],
)
def test_append(  # noqa: PLR0913, PLR0917
    linked_list_factory: LinkedListFactory,
    initial_values: list[Any],
    values_to_append: list[Any],
    expected_head: object,
    expected_tail: object,
    expected_values: object,
) -> None:
    ll = linked_list_factory(values=initial_values)

    for value in values_to_append:
        ll.append(value)

    assert ll.head is not None
    assert ll.head.value == expected_head

    assert ll.tail is not None
    assert ll.tail.value == expected_tail
    assert _values(ll) == expected_values


def test_append_supports_method_chaining(empty_linked_list: LinkedList[Any]) -> None:
    result = empty_linked_list.append(1).append(2).append(3)

    assert (
        result is empty_linked_list
    )  # Verifies it returns the exact same list instance
    assert _values(empty_linked_list) == [1, 2, 3]


def test_append_keeps_head_pinned_to_the_first_node() -> None:
    llist: LinkedList[int] = LinkedList()
    llist.append(1)
    first = llist.head
    llist.append(2)
    llist.append(3)

    assert llist.head is first
    assert llist.head is not None
    assert llist.head.value == 1


def test_append_moves_tail_to_the_last_node() -> None:
    llist: LinkedList[int] = LinkedList()
    llist.append(1)
    llist.append(2)
    llist.append(3)

    assert llist.tail is not None
    assert llist.tail.value == 3
    assert llist.tail.next is None
    assert llist.tail is _nodes(llist)[-1]


def test_append_links_previous_tail_to_the_new_node() -> None:
    llist: LinkedList[int] = LinkedList()
    llist.append(1)
    previous_tail = llist.tail
    llist.append(2)

    assert previous_tail is not None
    assert previous_tail.next is llist.tail


def test_append_creates_a_distinct_node_per_call() -> None:
    llist: LinkedList[int] = LinkedList()
    llist.append(1)
    llist.append(1)

    nodes = _nodes(llist)
    assert len(nodes) == 2
    assert nodes[0] is not nodes[1]


# ---------------------------------------------------------------------------
# prepend
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "initial_values, values_to_prepend, expected_head, expected_tail, expected_values",
    [
        # Append to empty list
        ([], [1], 1, 1, [1]),
        # Append to populated list
        ([1], [2], 2, 1, [2, 1]),
        # Append keeps duplicates
        ([], ["a", "b", "b", "c", "b"], "b", "a", ["b", "c", "b", "b", "a"]),
        # Append preserves insertion order
        ([], [1, 2, 3], 3, 1, [3, 2, 1]),
    ],
)
def test_prepend(  # noqa: PLR0913, PLR0917
    linked_list_factory: LinkedListFactory,
    initial_values: list[Any],
    values_to_prepend: list[Any],
    expected_head: object,
    expected_tail: object,
    expected_values: object,
) -> None:
    ll = linked_list_factory(values=initial_values)

    for value in values_to_prepend:
        ll.prepend(value)

    assert ll.head is not None
    assert ll.head.value == expected_head

    assert ll.tail is not None
    assert ll.tail.value == expected_tail
    assert _values(ll) == expected_values


def test_prepend_to_empty_sets_head_and_tail_to_same_node() -> None:
    llist: LinkedList[int] = LinkedList()
    llist.prepend(1)

    assert llist.head is not None
    assert llist.tail is llist.head
    assert llist.head.value == 1
    assert llist.head.next is None
    assert _values(llist) == [1]


def test_prepend_wraps_value_in_a_node() -> None:
    llist: LinkedList[str] = LinkedList()
    llist.prepend("a")

    assert isinstance(llist.head, LinkedListNode)
    assert llist.head.value == "a"


def test_prepend_moves_head_to_the_new_node() -> None:
    llist: LinkedList[int] = LinkedList()
    llist.prepend(1)
    llist.prepend(2)

    assert llist.head is not None
    assert llist.head.value == 2
    assert llist.head is _nodes(llist)[0]


def test_prepend_links_new_head_to_the_previous_head() -> None:
    llist: LinkedList[int] = LinkedList()
    llist.prepend(1)
    previous_head = llist.head
    llist.prepend(2)

    assert llist.head is not None
    assert llist.head is not previous_head
    assert llist.head.next is previous_head


def test_prepend_leaves_the_tail_where_it_was() -> None:
    llist: LinkedList[int] = LinkedList()
    llist.prepend(1)
    tail_after_first = llist.tail
    llist.prepend(2)
    llist.prepend(3)

    assert llist.tail is tail_after_first
    assert llist.tail is not None
    assert llist.tail.value == 1
    assert llist.tail.next is None
    assert llist.tail is _nodes(llist)[-1]


def test_prepend_creates_a_distinct_node_per_call() -> None:
    llist: LinkedList[int] = LinkedList()
    llist.prepend(1)
    llist.prepend(1)

    nodes = _nodes(llist)
    assert len(nodes) == 2
    assert nodes[0] is not nodes[1]


@pytest.mark.parametrize("count", [1, 2, 5, 100], ids=["one", "two", "five", "many"])
def test_prepend_n_times_builds_a_chain_of_n_nodes(count: int) -> None:
    llist: LinkedList[int] = LinkedList()
    for value in range(count):
        llist.prepend(value)

    nodes = _nodes(llist)
    assert len(nodes) == count
    assert _values(llist) == list(reversed(range(count)))
    assert llist.head is nodes[0]
    assert llist.tail is nodes[-1]


# ---------------------------------------------------------------------------
# TODO(DSA-33): move the append + prepend tests into the integration test folder
#   [Tooling | Linked Lists | Tests | needs-human]
#   Prepend mixed with append: both ends stay consistent.
# ---------------------------------------------------------------------------


def test_prepend_after_append_keeps_tail_on_the_appended_node() -> None:
    llist: LinkedList[int] = LinkedList()
    llist.append(2)
    appended = llist.tail
    llist.prepend(1)

    assert _values(llist) == [1, 2]
    assert llist.tail is appended


def test_append_after_prepend_extends_from_the_current_tail() -> None:
    llist: LinkedList[int] = LinkedList()
    llist.prepend(1)
    llist.append(2)

    assert _values(llist) == [1, 2]
    assert llist.head is not None
    assert llist.tail is not None
    assert llist.head.next is llist.tail
    assert llist.tail.value == 2


def test_prepend_and_append_interleaved_grow_opposite_ends() -> None:
    llist: LinkedList[int] = LinkedList()
    llist.append(1)
    llist.prepend(0)
    llist.append(2)
    llist.prepend(-1)

    assert _values(llist) == [-1, 0, 1, 2]
    assert llist.head is not None
    assert llist.tail is not None
    assert llist.head.value == -1
    assert llist.tail.value == 2
    assert llist.tail.next is None


def test_prepend_only_list_is_a_reachable_chain_from_head_to_tail() -> None:
    llist: LinkedList[int] = LinkedList()
    for value in (1, 2, 3):
        llist.prepend(value)

    nodes = _nodes(llist)
    assert [node.value for node in nodes] == [3, 2, 1]
    assert nodes[0].next is nodes[1]
    assert nodes[1].next is nodes[2]
    assert nodes[2].next is None


# ---------------------------------------------------------------------------
# find
# ---------------------------------------------------------------------------
def is_equal_to[T](target_value: T) -> Callable[[T], bool]:
    return lambda current_value: current_value == target_value


def filter_object_by_name(name: str) -> Callable[[dict[str, Any]], bool]:
    return lambda current_object: str.lower(current_object["name"]) == str.lower(name)


@pytest.mark.parametrize(
    "initial_values, custom_comparator, value_to_find, expected_value, expected_head, expected_tail",  # noqa: E501
    [
        # Find on empty list
        ([], None, 1, None, None, None),
        # Find on populated list
        ([1, 2, 3], None, 2, 2, 1, 3),
        # Find on populated list by callback
        ([1, 2, 3], None, is_equal_to(2), 2, 1, 3),
        ([1, 2], None, is_equal_to(3), None, 1, 2),
        # Find using custom compare function with objects
        (
            [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
                {"id": 3, "name": "Joe"},
            ],
            _compare_by_id,
            filter_object_by_name("joe"),
            {"id": 3, "name": "Joe"},
            {"id": 1, "name": "Alice"},
            {"id": 3, "name": "Joe"},
        ),
    ],
)
def test_find(  # noqa: PLR0913, PLR0917
    linked_list_factory: LinkedListFactory,
    initial_values: list[Any],
    custom_comparator: ComparatorFunc[Any] | None,
    value_to_find: object,
    expected_value: object,
    expected_head: object,
    expected_tail: object,
) -> None:
    ll = linked_list_factory(values=initial_values, compare_fun=custom_comparator)
    node = ll.find(value_to_find)

    if ll.head is not None:
        assert ll.head.value == expected_head
    else:
        assert ll.head == expected_head

    if node:
        assert node.value == expected_value
    else:
        assert node == expected_value

    if ll.tail is not None:
        assert ll.tail.value == expected_tail
    else:
        assert ll.tail == expected_tail


def test_find_node_by_means_of_custom_compare_function() -> None:
    def comparator_function(a: dict[str, Any], b: dict[str, Any]) -> int:
        if a["custom_value"] == b["custom_value"]:
            return 0
        return -1 if a["custom_value"] < b["custom_value"] else 1

    linked_list = LinkedList(comparator_function)

    linked_list.append({"value": 1, "custom_value": "test1"})
    linked_list.append({"value": 2, "custom_value": "test2"})
    linked_list.append({"value": 3, "custom_value": "test3"})

    node = linked_list.find({"value": 2, "custom_value": "test2"})

    assert node is not None
    assert node.value["value"] == 2
    assert node.value["custom_value"] == "test2"

    assert linked_list.find({"value": 2, "custom_value": "test5"}) is None


@pytest.mark.parametrize(
    "input_values, expected_values, expected_head, expected_tail",
    [
        ([1, 2, 3, 4, 5], "1,2,3,4,5", 1, 5),
        ([], "", None, None),
        # TODO(DSA-33): to_string should accept a custom stringifier callback
        #   [Tooling | Linked Lists | Tests | needs-human]
        #   Needed for objects.
    ],
)
def test_to_string(
    linked_list_factory: LinkedListFactory,
    input_values: list[Any],
    expected_values: object,
    expected_head: object,
    expected_tail: object,
) -> None:
    ll = linked_list_factory(values=input_values)
    values = ll.to_string()

    assert values == expected_values

    if ll.head:
        assert ll.head.value == expected_head
    else:
        assert ll.head == expected_head

    if ll.tail is not None:
        assert ll.tail.value == expected_tail
    else:
        assert ll.tail == expected_tail


@pytest.mark.parametrize(
    "input_values, value_to_delete, expected_deleted_value, expected_values, expected_head, expected_tail",  # noqa: E501
    [
        # Delete from empty list
        ([], 1, None, [], None, None),
        # Delete the only node
        ([1], 1, 1, [], None, None),
        # Delete the head
        ([1, 2, 3], 1, 1, [2, 3], 2, 3),
        # Delete the tail
        ([1, 2, 3], 3, 3, [1, 2], 1, 2),
        # Delete middle
        ([1, 2, 3], 2, 2, [1, 3], 1, 3),
        # Delete multiple occurrences
        ([1, 2, 2, 3, 4, 2], 2, 2, [1, 3, 4], 1, 4),
        # Delete non-existent value
        ([1, 2, 3, 4], 5, None, [1, 2, 3, 4], 1, 4),
    ],
)
def test_delete(  # noqa: PLR0913, PLR0917
    linked_list_factory: LinkedListFactory,
    input_values: list[Any],
    value_to_delete: object,
    expected_deleted_value: object,
    expected_values: object,
    expected_head: object,
    expected_tail: object,
) -> None:
    ll = linked_list_factory(values=input_values)
    node = ll.delete(value_to_delete)

    if node:
        assert node.value == expected_deleted_value
    else:
        assert node is None

    assert _values(ll) == expected_values

    if ll.head:
        assert ll.head.value == expected_head
    else:
        assert ll.head is None

    if ll.tail is not None:
        assert ll.tail.value == expected_tail
    else:
        assert ll.tail is None


def test_delete_node_by_value() -> None:
    linked_list: LinkedList[int] = LinkedList()

    assert linked_list.delete(5) is None

    linked_list.append(1)
    linked_list.append(1)
    linked_list.append(2)
    linked_list.append(3)
    linked_list.append(3)
    linked_list.append(3)
    linked_list.append(4)
    linked_list.append(5)

    assert str(linked_list.head) == "1"
    assert str(linked_list.tail) == "5"

    deleted_node = linked_list.delete(1)
    assert deleted_node is not None
    assert deleted_node.value == 1
    assert str(linked_list) == "2,3,3,3,4,5"

    assert str(linked_list.head) == "2"
    assert str(linked_list.tail) == "5"

    linked_list.delete(3)
    assert str(linked_list) == "2,4,5"
    assert str(linked_list.head) == "2"
    assert str(linked_list.tail) == "5"

    linked_list.delete(5)
    assert str(linked_list) == "2,4"
    assert str(linked_list.head) == "2"
    assert str(linked_list.tail) == "4"

    linked_list.delete(4)
    assert str(linked_list) == "2"
    assert str(linked_list.head) == "2"
    assert str(linked_list.tail) == "2"

    deleted_node_2 = linked_list.delete(2)
    assert deleted_node_2 is not None
    assert deleted_node_2.value == 2
    assert str(linked_list) == ""
    assert linked_list.head is None
    assert linked_list.tail is None


def test_delete_tail() -> None:
    linked_list: LinkedList[int] = LinkedList()

    linked_list.append(1)
    linked_list.append(2)
    linked_list.append(3)

    assert str(linked_list.head) == "1"
    assert str(linked_list.tail) == "3"

    deleted_node_1 = linked_list.delete_tail()

    assert deleted_node_1 is not None
    assert deleted_node_1.value == 3
    assert str(linked_list) == "1,2"
    assert str(linked_list.head) == "1"
    assert str(linked_list.tail) == "2"

    deleted_node_2 = linked_list.delete_tail()

    assert deleted_node_2 is not None
    assert deleted_node_2.value == 2
    assert str(linked_list) == "1"
    assert str(linked_list.head) == "1"
    assert str(linked_list.tail) == "1"

    deleted_node_3 = linked_list.delete_tail()

    assert deleted_node_3 is not None
    assert deleted_node_3.value == 1
    assert str(linked_list) == ""
    assert linked_list.head is None
    assert linked_list.tail is None


def test_delete_head() -> None:
    linked_list: LinkedList[int] = LinkedList()

    assert linked_list.delete_head() is None

    linked_list.append(1)
    linked_list.append(2)

    assert str(linked_list.head) == "1"
    assert str(linked_list.tail) == "2"

    deleted_node_1 = linked_list.delete_head()

    assert deleted_node_1 is not None
    assert deleted_node_1.value == 1
    assert str(linked_list) == "2"
    assert str(linked_list.head) == "2"
    assert str(linked_list.tail) == "2"

    deleted_node_2 = linked_list.delete_head()

    assert deleted_node_2 is not None
    assert deleted_node_2.value == 2
    assert str(linked_list) == ""
    assert linked_list.head is None
    assert linked_list.tail is None


def test_reverse() -> None:
    linked_list: LinkedList[int] = LinkedList()
    linked_list.append(1).append(2)

    assert str(linked_list) == "1,2"
    assert linked_list.head is not None
    assert linked_list.tail is not None
    assert linked_list.head.value == 1
    assert linked_list.tail.value == 2

    # Reverse linked list.
    linked_list.reverse()

    assert str(linked_list) == "2,1"
    assert linked_list.head is not None
    assert linked_list.tail is not None
    assert linked_list.head.value == 2
    assert linked_list.tail.value == 1


def test_create_linked_list_from_array() -> None:
    linked_list: LinkedList[int] = LinkedList()
    linked_list.from_array([1, 1, 2, 3, 3, 3, 4, 5])

    assert str(linked_list) == "1,1,2,3,3,3,4,5"


# ---------------------------------------------------------------------------
# __repr__
# ---------------------------------------------------------------------------


def test_repr_empty_list() -> None:
    llist: LinkedList[int] = LinkedList()

    assert repr(llist) == "LinkedList([])"


def test_repr_single_element() -> None:
    llist: LinkedList[int] = LinkedList()
    llist.append(42)

    assert repr(llist) == "LinkedList([42])"


def test_repr_multiple_elements() -> None:
    llist: LinkedList[int] = LinkedList()
    llist.from_array([1, 2, 3])

    assert repr(llist) == "LinkedList([1, 2, 3])"


def test_repr_string_elements() -> None:
    llist: LinkedList[str] = LinkedList()
    llist.from_array(["a", "b", "c"])

    assert repr(llist) == "LinkedList(['a', 'b', 'c'])"
