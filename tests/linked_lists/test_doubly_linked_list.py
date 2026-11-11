from dataclasses import dataclass
from itertools import pairwise

import pytest

from dsa.linked_lists import DoublyLinkedList, DoublyLinkedListNode

# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _User:
    id: int
    name: str


def _compare_by_id(a: _User, b: _User) -> int:
    if a.id == b.id:
        return 0
    return -1 if a.id < b.id else 1


def _nodes[T](llist: DoublyLinkedList[T]) -> list[DoublyLinkedListNode[T]]:
    """Walk the list from head to tail following `next`."""
    out: list[DoublyLinkedListNode[T]] = []
    seen: set[int] = set()
    node = llist.head
    while node is not None:
        # A broken list must fail the test, not hang the run.
        assert id(node) not in seen, "cycle detected following `next`"
        seen.add(id(node))
        out.append(node)
        node = node.next
    return out


def _values_forward[T](llist: DoublyLinkedList[T]) -> list[T]:
    return [node.value for node in _nodes(llist)]


def _values_backward[T](llist: DoublyLinkedList[T]) -> list[T]:
    """Walk the list from tail to head following `previous`."""
    out: list[T] = []
    seen: set[int] = set()
    node = llist.tail
    while node is not None:
        assert id(node) not in seen, "cycle detected following `previous`"
        seen.add(id(node))
        out.append(node.value)
        node = node.previous
    return out


def _list_of[T](*values: T) -> DoublyLinkedList[T]:
    llist: DoublyLinkedList[T] = DoublyLinkedList()
    for value in values:
        llist.append(value)
    return llist


def _assert_well_formed[T](llist: DoublyLinkedList[T]) -> None:
    """Assert head/tail agree with the chain and every link is mutual."""
    nodes = _nodes(llist)
    if not nodes:
        assert llist.head is None
        assert llist.tail is None
        return

    assert llist.head is nodes[0]
    assert llist.tail is nodes[-1]
    assert nodes[0].previous is None
    assert nodes[-1].next is None
    for left, right in pairwise(nodes):
        assert left.next is right
        assert right.previous is left
    assert _values_backward(llist) == [node.value for node in nodes][::-1]


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------


def test_new_list_is_empty() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    assert llist.head is None
    assert llist.tail is None
    assert _values_forward(llist) == []
    assert _values_backward(llist) == []


def test_init_without_compare_fun_uses_default_comparison() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    assert llist.comparator.equal(1, 1)
    assert not llist.comparator.equal(1, 2)


def test_init_with_compare_fun_uses_it_for_equality() -> None:
    llist: DoublyLinkedList[_User] = DoublyLinkedList(_compare_by_id)

    assert llist.comparator.compare is _compare_by_id
    assert llist.comparator.equal(_User(1, "Alice"), _User(1, "Bob"))
    assert not llist.comparator.equal(_User(1, "Alice"), _User(2, "Alice"))


def test_init_with_compare_fun_still_starts_empty() -> None:
    llist: DoublyLinkedList[_User] = DoublyLinkedList(_compare_by_id)

    assert llist.head is None
    assert llist.tail is None


def test_lists_do_not_share_state() -> None:
    first: DoublyLinkedList[int] = DoublyLinkedList()
    second: DoublyLinkedList[int] = DoublyLinkedList()

    first.append(1)

    assert second.head is None
    assert second.tail is None
    assert _values_forward(second) == []


# ---------------------------------------------------------------------------
# append
# ---------------------------------------------------------------------------


def test_append_to_empty_list_sets_head_and_tail_to_the_same_node() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    llist.append(1)

    assert llist.head is not None
    assert llist.head is llist.tail
    assert llist.head.value == 1
    assert llist.head.next is None
    assert llist.head.previous is None


def test_append_second_value_links_both_directions() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    llist.append(1)
    llist.append(2)

    assert llist.head is not None
    assert llist.tail is not None
    assert llist.head is not llist.tail
    assert llist.head.next is llist.tail
    assert llist.tail.previous is llist.head
    assert llist.head.previous is None
    assert llist.tail.next is None


@pytest.mark.parametrize(
    "values",
    [
        [1],
        [1, 2],
        [1, 2, 3],
        ["a", "b", "b", "c", "b"],
    ],
    ids=["single", "pair", "ordered", "duplicates"],
)
def test_append_preserves_insertion_order_in_both_directions(
    values: list[object],
) -> None:
    llist: DoublyLinkedList[object] = DoublyLinkedList()

    for value in values:
        llist.append(value)

    assert _values_forward(llist) == values
    assert _values_backward(llist) == values[::-1]


def test_append_supports_method_chaining() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    result = llist.append(1).append(2).append(3)

    assert result is llist
    assert _values_forward(llist) == [1, 2, 3]
    assert _values_backward(llist) == [3, 2, 1]


def test_append_keeps_head_pinned_to_the_first_node() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()
    llist.append(1)
    first = llist.head

    llist.append(2)
    llist.append(3)

    assert llist.head is first
    assert llist.head is not None
    assert llist.head.value == 1
    assert llist.head.previous is None


def test_append_moves_tail_to_the_last_node() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    llist.append(1)
    llist.append(2)
    llist.append(3)

    assert llist.tail is not None
    assert llist.tail.value == 3
    assert llist.tail.next is None
    assert llist.tail is _nodes(llist)[-1]


def test_append_links_previous_tail_to_the_new_tail_and_back() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()
    llist.append(1)
    previous_tail = llist.tail

    llist.append(2)

    assert previous_tail is not None
    assert llist.tail is not None
    assert previous_tail.next is llist.tail
    assert llist.tail.previous is previous_tail


def test_append_creates_a_distinct_node_per_call() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    llist.append(1)
    llist.append(1)

    nodes = _nodes(llist)
    assert len(nodes) == 2
    assert nodes[0] is not nodes[1]


@pytest.mark.parametrize("value", [0, "", None, False, []], ids=repr)
def test_append_stores_falsy_values(value: object) -> None:
    llist: DoublyLinkedList[object] = DoublyLinkedList()

    llist.append(value)
    llist.append(value)

    assert len(_nodes(llist)) == 2
    assert all(node.value is value for node in _nodes(llist))


@pytest.mark.parametrize("count", [1, 2, 5, 1000], ids=["one", "two", "five", "many"])
def test_append_n_times_builds_a_chain_of_n_nodes(count: int) -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    for value in range(count):
        llist.append(value)

    nodes = _nodes(llist)
    assert len(nodes) == count
    assert nodes[0] is llist.head
    assert nodes[-1] is llist.tail
    assert _values_forward(llist) == list(range(count))
    assert _values_backward(llist) == list(range(count))[::-1]


@pytest.mark.parametrize("count", [2, 3, 10], ids=["two", "three", "ten"])
def test_append_leaves_every_adjacent_pair_mutually_linked(count: int) -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    for value in range(count):
        llist.append(value)

    for left, right in pairwise(_nodes(llist)):
        assert left.next is right
        assert right.previous is left


def test_append_custom_objects_stores_the_same_instances() -> None:
    alice = _User(1, "Alice")
    bob = _User(2, "Bob")
    llist: DoublyLinkedList[_User] = DoublyLinkedList(_compare_by_id)

    llist.append(alice).append(bob)

    assert llist.head is not None
    assert llist.tail is not None
    assert llist.head.value is alice
    assert llist.tail.value is bob
    assert _values_backward(llist) == [bob, alice]


# ---------------------------------------------------------------------------
# prepend
# ---------------------------------------------------------------------------


def test_prepend_to_empty_list_sets_head_and_tail_to_the_same_node() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    llist.prepend(1)

    assert llist.head is not None
    assert llist.head is llist.tail
    assert llist.head.value == 1
    assert llist.head.next is None
    assert llist.head.previous is None


def test_prepend_second_value_links_both_directions() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    llist.prepend(1)
    llist.prepend(2)

    assert llist.head is not None
    assert llist.tail is not None
    assert llist.head is not llist.tail
    assert llist.head.value == 2
    assert llist.tail.value == 1
    assert llist.head.next is llist.tail
    assert llist.tail.previous is llist.head
    assert llist.head.previous is None
    assert llist.tail.next is None


@pytest.mark.parametrize(
    "values",
    [
        [1],
        [1, 2],
        [1, 2, 3],
        ["a", "b", "b", "c", "b"],
    ],
    ids=["single", "pair", "ordered", "duplicates"],
)
def test_prepend_puts_the_latest_value_first_in_both_directions(
    values: list[object],
) -> None:
    llist: DoublyLinkedList[object] = DoublyLinkedList()

    for value in values:
        llist.prepend(value)

    assert _values_forward(llist) == values[::-1]
    assert _values_backward(llist) == values


def test_prepend_supports_method_chaining() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    result = llist.prepend(1).prepend(2).prepend(3)

    assert result is llist
    assert _values_forward(llist) == [3, 2, 1]
    assert _values_backward(llist) == [1, 2, 3]


def test_prepend_moves_head_to_the_new_node() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()
    llist.prepend(1)
    previous_head = llist.head

    llist.prepend(2)

    assert llist.head is not previous_head
    assert llist.head is not None
    assert llist.head.value == 2
    assert llist.head.previous is None
    assert llist.head is _nodes(llist)[0]


def test_prepend_links_new_head_to_the_previous_head_and_back() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()
    llist.prepend(1)
    previous_head = llist.head

    llist.prepend(2)

    assert previous_head is not None
    assert llist.head is not None
    assert llist.head.next is previous_head
    assert previous_head.previous is llist.head


def test_prepend_leaves_the_tail_where_it_was() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()
    llist.prepend(1)
    first = llist.tail

    llist.prepend(2)
    llist.prepend(3)

    assert llist.tail is first
    assert llist.tail is not None
    assert llist.tail.value == 1
    assert llist.tail.next is None


def test_prepend_creates_a_distinct_node_per_call() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    llist.prepend(1)
    llist.prepend(1)

    nodes = _nodes(llist)
    assert len(nodes) == 2
    assert nodes[0] is not nodes[1]


@pytest.mark.parametrize("value", [0, "", None, False, []], ids=repr)
def test_prepend_stores_falsy_values(value: object) -> None:
    llist: DoublyLinkedList[object] = DoublyLinkedList()

    llist.prepend(value)
    llist.prepend(value)

    assert len(_nodes(llist)) == 2
    assert all(node.value is value for node in _nodes(llist))


@pytest.mark.parametrize("count", [1, 2, 5, 1000], ids=["one", "two", "five", "many"])
def test_prepend_n_times_builds_a_chain_of_n_nodes(count: int) -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    for value in range(count):
        llist.prepend(value)

    nodes = _nodes(llist)
    assert len(nodes) == count
    assert nodes[0] is llist.head
    assert nodes[-1] is llist.tail
    assert nodes[0].previous is None
    assert nodes[-1].next is None
    assert _values_forward(llist) == list(range(count))[::-1]
    assert _values_backward(llist) == list(range(count))


@pytest.mark.parametrize("count", [2, 3, 10], ids=["two", "three", "ten"])
def test_prepend_leaves_every_adjacent_pair_mutually_linked(count: int) -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    for value in range(count):
        llist.prepend(value)

    for left, right in pairwise(_nodes(llist)):
        assert left.next is right
        assert right.previous is left


def test_prepend_after_append_keeps_tail_on_the_appended_node() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()
    llist.append(1)
    appended = llist.tail

    llist.prepend(0)

    assert llist.tail is appended
    assert llist.head is not None
    assert llist.head.value == 0
    assert llist.head.next is appended
    assert _values_forward(llist) == [0, 1]
    assert _values_backward(llist) == [1, 0]


def test_append_after_prepend_extends_from_the_current_tail() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()
    llist.prepend(2)
    prepended = llist.head

    llist.append(3)

    assert llist.head is prepended
    assert llist.tail is not None
    assert llist.tail.value == 3
    assert llist.tail.previous is prepended
    assert _values_forward(llist) == [2, 3]
    assert _values_backward(llist) == [3, 2]


@pytest.mark.parametrize(
    ("operations", "expected"),
    [
        ([("append", 1), ("prepend", 0)], [0, 1]),
        ([("prepend", 1), ("append", 2)], [1, 2]),
        (
            [("append", 3), ("prepend", 2), ("append", 4), ("prepend", 1)],
            [1, 2, 3, 4],
        ),
        (
            [("prepend", 2), ("prepend", 1), ("append", 3), ("append", 4)],
            [1, 2, 3, 4],
        ),
    ],
    ids=["append-then-prepend", "prepend-then-append", "alternating", "grouped"],
)
def test_prepend_and_append_interleaved_grow_opposite_ends(
    operations: list[tuple[str, int]], expected: list[int]
) -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    for operation, value in operations:
        if operation == "prepend":
            llist.prepend(value)
        else:
            llist.append(value)

    assert _values_forward(llist) == expected
    assert _values_backward(llist) == expected[::-1]
    for left, right in pairwise(_nodes(llist)):
        assert left.next is right
        assert right.previous is left


def test_prepend_custom_objects_stores_the_same_instances() -> None:
    alice = _User(1, "Alice")
    bob = _User(2, "Bob")
    llist: DoublyLinkedList[_User] = DoublyLinkedList(_compare_by_id)

    llist.prepend(alice).prepend(bob)

    assert llist.head is not None
    assert llist.tail is not None
    assert llist.head.value is bob
    assert llist.tail.value is alice
    assert _values_backward(llist) == [alice, bob]


# ---------------------------------------------------------------------------
# delete_head
# ---------------------------------------------------------------------------


def test_delete_head_on_empty_list_returns_none() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    assert llist.delete_head() is None
    assert llist.delete_head() is None
    _assert_well_formed(llist)


def test_delete_head_on_single_element_list_empties_it() -> None:
    llist = _list_of(1)
    only = llist.head

    removed = llist.delete_head()

    assert removed is only
    assert removed is not None
    assert removed.value == 1
    assert llist.head is None
    assert llist.tail is None


def test_delete_head_returns_the_removed_head_node() -> None:
    llist = _list_of(1, 2, 3)
    original_head = llist.head

    removed = llist.delete_head()

    assert removed is original_head
    assert removed is not None
    assert removed.value == 1


def test_delete_head_detaches_the_removed_node() -> None:
    llist = _list_of(1, 2, 3)

    removed = llist.delete_head()

    assert removed is not None
    assert removed.next is None
    assert removed.previous is None


def test_delete_head_promotes_the_next_node_and_clears_its_previous() -> None:
    llist = _list_of(1, 2, 3)
    second = _nodes(llist)[1]

    llist.delete_head()

    assert llist.head is second
    assert second.previous is None


def test_delete_head_leaves_the_tail_where_it_was() -> None:
    llist = _list_of(1, 2, 3)
    original_tail = llist.tail

    llist.delete_head()

    assert llist.tail is original_tail
    assert llist.tail is not None
    assert llist.tail.value == 3


def test_delete_head_on_two_element_list_leaves_one_node_as_head_and_tail() -> None:
    llist = _list_of(1, 2)
    second = _nodes(llist)[1]

    llist.delete_head()

    assert llist.head is second
    assert llist.tail is second
    assert second.next is None
    assert second.previous is None


def test_delete_head_keeps_remaining_values_in_order_in_both_directions() -> None:
    llist = _list_of(1, 2, 3, 4)

    llist.delete_head()

    assert _values_forward(llist) == [2, 3, 4]
    assert _values_backward(llist) == [4, 3, 2]
    _assert_well_formed(llist)


@pytest.mark.parametrize("count", [1, 2, 5, 100], ids=["one", "two", "five", "many"])
def test_delete_head_repeatedly_drains_the_list_in_insertion_order(
    count: int,
) -> None:
    llist = _list_of(*range(count))

    removed_values: list[int] = []
    for _ in range(count):
        removed = llist.delete_head()
        assert removed is not None
        removed_values.append(removed.value)
        _assert_well_formed(llist)

    assert removed_values == list(range(count))
    assert llist.delete_head() is None


@pytest.mark.parametrize("value", [0, "", None, False, []], ids=repr)
def test_delete_head_returns_a_node_even_when_its_value_is_falsy(
    value: object,
) -> None:
    llist = _list_of(value)

    removed = llist.delete_head()

    assert removed is not None
    assert removed.value is value


def test_append_after_delete_head_drained_the_list_starts_a_fresh_chain() -> None:
    llist = _list_of(1)
    llist.delete_head()

    llist.append(2)

    assert llist.head is llist.tail
    assert llist.head is not None
    assert llist.head.value == 2
    assert llist.head.next is None
    assert llist.head.previous is None
    _assert_well_formed(llist)


def test_prepend_after_delete_head_drained_the_list_starts_a_fresh_chain() -> None:
    llist = _list_of(1)
    llist.delete_head()

    llist.prepend(2)

    assert llist.head is llist.tail
    assert llist.head is not None
    assert llist.head.value == 2
    assert llist.head.next is None
    assert llist.head.previous is None
    _assert_well_formed(llist)


def test_delete_head_returns_the_same_custom_instance() -> None:
    alice = _User(1, "Alice")
    llist = _list_of(alice, _User(2, "Bob"))

    removed = llist.delete_head()

    assert removed is not None
    assert removed.value is alice


# ---------------------------------------------------------------------------
# delete_tail
# ---------------------------------------------------------------------------


def test_delete_tail_on_empty_list_returns_none() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    assert llist.delete_tail() is None
    assert llist.delete_tail() is None
    _assert_well_formed(llist)


def test_delete_tail_on_single_element_list_empties_it() -> None:
    llist = _list_of(1)
    only = llist.tail

    removed = llist.delete_tail()

    assert removed is only
    assert removed is not None
    assert removed.value == 1
    assert llist.head is None
    assert llist.tail is None


def test_delete_tail_returns_the_removed_tail_node() -> None:
    llist = _list_of(1, 2, 3)
    original_tail = llist.tail

    removed = llist.delete_tail()

    assert removed is original_tail
    assert removed is not None
    assert removed.value == 3


def test_delete_tail_detaches_the_removed_node() -> None:
    llist = _list_of(1, 2, 3)

    removed = llist.delete_tail()

    assert removed is not None
    assert removed.next is None
    assert removed.previous is None


def test_delete_tail_promotes_the_previous_node_and_clears_its_next() -> None:
    llist = _list_of(1, 2, 3)
    second = _nodes(llist)[1]

    llist.delete_tail()

    assert llist.tail is second
    assert second.next is None


def test_delete_tail_leaves_the_head_where_it_was() -> None:
    llist = _list_of(1, 2, 3)
    original_head = llist.head

    llist.delete_tail()

    assert llist.head is original_head
    assert llist.head is not None
    assert llist.head.value == 1


def test_delete_tail_on_two_element_list_leaves_one_node_as_head_and_tail() -> None:
    llist = _list_of(1, 2)
    first = _nodes(llist)[0]

    llist.delete_tail()

    assert llist.head is first
    assert llist.tail is first
    assert first.next is None
    assert first.previous is None


def test_delete_tail_keeps_remaining_values_in_order_in_both_directions() -> None:
    llist = _list_of(1, 2, 3, 4)

    llist.delete_tail()

    assert _values_forward(llist) == [1, 2, 3]
    assert _values_backward(llist) == [3, 2, 1]
    _assert_well_formed(llist)


@pytest.mark.parametrize("count", [1, 2, 5, 100], ids=["one", "two", "five", "many"])
def test_delete_tail_repeatedly_drains_the_list_in_reverse_order(
    count: int,
) -> None:
    llist = _list_of(*range(count))

    removed_values: list[int] = []
    for _ in range(count):
        removed = llist.delete_tail()
        assert removed is not None
        removed_values.append(removed.value)
        _assert_well_formed(llist)

    assert removed_values == list(range(count))[::-1]
    assert llist.delete_tail() is None


@pytest.mark.parametrize("value", [0, "", None, False, []], ids=repr)
def test_delete_tail_returns_a_node_even_when_its_value_is_falsy(
    value: object,
) -> None:
    llist = _list_of(value)

    removed = llist.delete_tail()

    assert removed is not None
    assert removed.value is value


def test_append_after_delete_tail_drained_the_list_starts_a_fresh_chain() -> None:
    llist = _list_of(1)
    llist.delete_tail()

    llist.append(2)

    assert llist.head is llist.tail
    assert llist.head is not None
    assert llist.head.value == 2
    assert llist.head.next is None
    assert llist.head.previous is None
    _assert_well_formed(llist)


def test_prepend_after_delete_tail_drained_the_list_starts_a_fresh_chain() -> None:
    llist = _list_of(1)
    llist.delete_tail()

    llist.prepend(2)

    assert llist.head is llist.tail
    assert llist.head is not None
    assert llist.head.value == 2
    assert llist.head.next is None
    assert llist.head.previous is None
    _assert_well_formed(llist)


def test_append_after_delete_tail_extends_from_the_new_tail() -> None:
    llist = _list_of(1, 2, 3)
    llist.delete_tail()

    llist.append(4)

    assert _values_forward(llist) == [1, 2, 4]
    assert _values_backward(llist) == [4, 2, 1]
    _assert_well_formed(llist)


def test_delete_tail_returns_the_same_custom_instance() -> None:
    bob = _User(2, "Bob")
    llist = _list_of(_User(1, "Alice"), bob)

    removed = llist.delete_tail()

    assert removed is not None
    assert removed.value is bob


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("values", "target", "expected_removed", "expected_remaining"),
    [
        ([], 1, None, []),
        ([1], 1, 1, []),
        ([1, 2, 3], 1, 1, [2, 3]),
        ([1, 2, 3], 3, 3, [1, 2]),
        ([1, 2, 3], 2, 2, [1, 3]),
        ([1, 2, 2, 3, 4, 2], 2, 2, [1, 3, 4]),
        ([1, 2, 3, 4], 5, None, [1, 2, 3, 4]),
    ],
    ids=["empty", "only-node", "head", "tail", "middle", "several-matches", "missing"],
)
def test_delete_removes_matching_nodes_and_keeps_the_list_well_formed(
    values: list[int],
    target: int,
    expected_removed: int | None,
    expected_remaining: list[int],
) -> None:
    llist = _list_of(*values)

    removed = llist.delete(target)

    if expected_removed is None:
        assert removed is None
    else:
        assert removed is not None
        assert removed.value == expected_removed
    assert _values_forward(llist) == expected_remaining
    assert _values_backward(llist) == expected_remaining[::-1]
    _assert_well_formed(llist)


def test_delete_on_empty_list_returns_none() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    assert llist.delete(1) is None
    _assert_well_formed(llist)


def test_delete_missing_value_returns_none_and_changes_nothing() -> None:
    llist = _list_of(1, 2, 3)
    before = _nodes(llist)

    assert llist.delete(9) is None

    assert _nodes(llist) == before
    _assert_well_formed(llist)


def test_delete_missing_value_from_single_element_list_changes_nothing() -> None:
    llist = _list_of(1)
    only = llist.head

    assert llist.delete(2) is None

    assert llist.head is only
    assert llist.tail is only
    _assert_well_formed(llist)


def test_delete_only_node_empties_the_list() -> None:
    llist = _list_of(1)
    only = llist.head

    removed = llist.delete(1)

    assert removed is only
    assert llist.head is None
    assert llist.tail is None


def test_delete_head_value_promotes_the_next_node_and_keeps_the_tail() -> None:
    llist = _list_of(1, 2, 3)
    second = _nodes(llist)[1]
    original_tail = llist.tail

    removed = llist.delete(1)

    assert removed is not None
    assert removed.value == 1
    assert llist.head is second
    assert second.previous is None
    assert llist.tail is original_tail


def test_delete_tail_value_promotes_the_previous_node_and_keeps_the_head() -> None:
    llist = _list_of(1, 2, 3)
    second = _nodes(llist)[1]
    original_head = llist.head

    removed = llist.delete(3)

    assert removed is not None
    assert removed.value == 3
    assert llist.tail is second
    assert second.next is None
    assert llist.head is original_head


def test_delete_middle_value_bridges_its_neighbours_in_both_directions() -> None:
    llist = _list_of(1, 2, 3)
    first, _, third = _nodes(llist)

    removed = llist.delete(2)

    assert removed is not None
    assert removed.value == 2
    assert first.next is third
    assert third.previous is first
    assert llist.head is first
    assert llist.tail is third


@pytest.mark.parametrize("target", [1, 3, 5], ids=["head", "middle", "tail"])
def test_delete_detaches_the_removed_node(target: int) -> None:
    llist = _list_of(1, 2, 3, 4, 5)

    removed = llist.delete(target)

    assert removed is not None
    assert removed.value == target
    assert removed.next is None
    assert removed.previous is None


@pytest.mark.parametrize("target", [1, 3, 5], ids=["head", "middle", "tail"])
def test_delete_keeps_every_other_node_in_place(target: int) -> None:
    llist = _list_of(1, 2, 3, 4, 5)
    before = _nodes(llist)

    llist.delete(target)

    assert _nodes(llist) == [node for node in before if node.value != target]
    _assert_well_formed(llist)


@pytest.mark.parametrize(
    "values",
    [
        [1, 2, 2, 3],
        [2, 2, 1],
        [1, 2, 2],
        [2, 1, 2],
        [2, 1, 2, 3, 2],
        [2, 2, 2],
        [2],
    ],
    ids=[
        "adjacent-middle",
        "adjacent-head",
        "adjacent-tail",
        "both-ends",
        "spread",
        "all",
        "only",
    ],
)
def test_delete_removes_every_occurrence_of_the_value(values: list[int]) -> None:
    llist = _list_of(*values)

    removed = llist.delete(2)

    assert removed is not None
    assert removed.value == 2
    assert _values_forward(llist) == [v for v in values if v != 2]
    _assert_well_formed(llist)


def test_delete_with_several_matches_returns_one_of_the_removed_nodes() -> None:
    llist = _list_of(1, 2, 3, 2)

    removed = llist.delete(2)

    assert removed is not None
    assert removed.value == 2
    assert removed.next is None
    assert removed.previous is None
    assert all(node is not removed for node in _nodes(llist))


def test_delete_same_value_twice_returns_none_the_second_time() -> None:
    llist = _list_of(1, 2, 3)
    llist.delete(2)
    before = _nodes(llist)

    assert llist.delete(2) is None

    assert _nodes(llist) == before
    _assert_well_formed(llist)


@pytest.mark.parametrize("count", [1, 2, 5, 50], ids=["one", "two", "five", "many"])
@pytest.mark.parametrize("reverse", [False, True], ids=["forward", "reverse"])
def test_delete_every_value_one_by_one_drains_the_list(
    count: int, reverse: bool
) -> None:
    values = list(range(count))
    llist = _list_of(*values)
    remaining = list(values)

    for target in values[::-1] if reverse else values:
        removed = llist.delete(target)
        assert removed is not None
        assert removed.value == target
        remaining.remove(target)
        assert _values_forward(llist) == remaining
        _assert_well_formed(llist)

    assert llist.delete(0) is None


@pytest.mark.parametrize(
    ("values", "target"),
    [([0, 1, 0], 0), (["", "a", ""], "")],
    ids=["zero", "empty-string"],
)
def test_delete_matches_falsy_values(values: list[object], target: object) -> None:
    llist = _list_of(*values)

    removed = llist.delete(target)

    assert removed is not None
    assert removed.value == target
    assert _values_forward(llist) == [v for v in values if v != target]
    _assert_well_formed(llist)


def test_delete_uses_the_list_comparator_to_find_matches() -> None:
    alice = _User(1, "Alice")
    bob = _User(2, "Bob")
    llist: DoublyLinkedList[_User] = DoublyLinkedList(_compare_by_id)
    llist.append(alice).append(bob)

    removed = llist.delete(_User(2, "someone else"))

    assert removed is not None
    assert removed.value is bob
    assert _values_forward(llist) == [alice]
    _assert_well_formed(llist)


def test_delete_with_custom_comparator_removes_every_equal_node() -> None:
    llist: DoublyLinkedList[_User] = DoublyLinkedList(_compare_by_id)
    llist.append(_User(1, "Alice")).append(_User(2, "Bob")).append(_User(1, "Alicia"))

    removed = llist.delete(_User(1, "ignored"))

    assert removed is not None
    assert removed.value.id == 1
    assert [user.id for user in _values_forward(llist)] == [2]
    _assert_well_formed(llist)


def test_append_after_delete_drained_the_list_starts_a_fresh_chain() -> None:
    llist = _list_of(1)
    llist.delete(1)

    llist.append(2)

    assert llist.head is llist.tail
    assert llist.head is not None
    assert llist.head.value == 2
    assert llist.head.next is None
    assert llist.head.previous is None
    _assert_well_formed(llist)


def test_prepend_after_delete_drained_the_list_starts_a_fresh_chain() -> None:
    llist = _list_of(1)
    llist.delete(1)

    llist.prepend(2)

    assert llist.head is llist.tail
    assert llist.head is not None
    assert llist.head.value == 2
    assert llist.head.next is None
    assert llist.head.previous is None
    _assert_well_formed(llist)


# ---------------------------------------------------------------------------
# delete_head and delete_tail together
# ---------------------------------------------------------------------------


def test_delete_head_then_delete_tail_on_two_elements_empties_the_list() -> None:
    llist = _list_of(1, 2)

    first = llist.delete_head()
    second = llist.delete_tail()

    assert first is not None
    assert second is not None
    assert (first.value, second.value) == (1, 2)
    assert llist.head is None
    assert llist.tail is None


def test_alternating_deletes_squeeze_the_list_from_both_ends() -> None:
    llist = _list_of(1, 2, 3, 4, 5)

    removed_values: list[int] = []
    for delete in (
        llist.delete_head,
        llist.delete_tail,
        llist.delete_head,
        llist.delete_tail,
        llist.delete_head,
    ):
        removed = delete()
        assert removed is not None
        removed_values.append(removed.value)
        _assert_well_formed(llist)

    assert removed_values == [1, 5, 2, 4, 3]
    assert llist.head is None
    assert llist.tail is None


# ---------------------------------------------------------------------------
# reverse
#
# These check values, order, head/tail and link integrity, not node identity:
# whether reverse relinks the existing nodes or builds new ones is left open.
# ---------------------------------------------------------------------------


def test_reverse_on_empty_list_leaves_it_empty() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    llist.reverse()

    assert llist.head is None
    assert llist.tail is None
    _assert_well_formed(llist)


def test_reverse_single_element_list_is_unchanged() -> None:
    llist = _list_of(1)

    llist.reverse()

    assert llist.head is llist.tail
    assert _values_forward(llist) == [1]
    assert _values_backward(llist) == [1]
    _assert_well_formed(llist)


@pytest.mark.parametrize(
    "values",
    [
        [1, 2],
        [1, 2, 3],
        [1, 2, 3, 4],
        [1, 2, 3, 4, 5],
        [1, 1, 2, 2],
        [3, 1, 2],
    ],
    ids=["two", "three", "four", "five", "duplicates", "unsorted"],
)
def test_reverse_reverses_the_order_in_both_directions(values: list[int]) -> None:
    llist = _list_of(*values)

    llist.reverse()

    assert _values_forward(llist) == values[::-1]
    assert _values_backward(llist) == values
    _assert_well_formed(llist)


def test_reverse_swaps_the_head_and_tail_values() -> None:
    llist = _list_of(1, 2, 3, 4)

    llist.reverse()

    assert llist.head is not None
    assert llist.tail is not None
    assert llist.head.value == 4
    assert llist.tail.value == 1
    assert llist.head.previous is None
    assert llist.tail.next is None


@pytest.mark.parametrize(
    "count",
    [2, 3, 10, 100, 1000],
    ids=["two", "three", "ten", "hundred", "thousand"],
)
def test_reverse_handles_longer_lists(count: int) -> None:
    values = list(range(count))
    llist = _list_of(*values)

    llist.reverse()

    assert _values_forward(llist) == values[::-1]
    assert _values_backward(llist) == values
    _assert_well_formed(llist)


@pytest.mark.parametrize(
    "count",
    [0, 1, 2, 3, 4, 5, 100],
    ids=["empty", "one", "two", "three", "four", "five", "hundred"],
)
def test_reverse_twice_restores_the_original_order(count: int) -> None:
    values = list(range(count))
    llist = _list_of(*values)

    llist.reverse()
    _assert_well_formed(llist)
    llist.reverse()

    assert _values_forward(llist) == values
    assert _values_backward(llist) == values[::-1]
    _assert_well_formed(llist)


def test_reverse_keeps_the_same_value_instances() -> None:
    alice = _User(1, "Alice")
    bob = _User(2, "Bob")
    carol = _User(3, "Carol")
    llist: DoublyLinkedList[_User] = DoublyLinkedList(_compare_by_id)
    llist.append(alice).append(bob).append(carol)

    llist.reverse()

    first, second, third = _values_forward(llist)
    assert first is carol
    assert second is bob
    assert third is alice


def test_reverse_keeps_falsy_values() -> None:
    values: list[object] = [0, "", None, False, []]
    llist = _list_of(*values)

    llist.reverse()

    reversed_values = _values_forward(llist)
    assert len(reversed_values) == len(values)
    for actual, expected in zip(reversed_values, values[::-1], strict=True):
        assert actual is expected


def test_append_after_reverse_extends_from_the_new_tail() -> None:
    llist = _list_of(1, 2, 3)
    llist.reverse()

    llist.append(0)

    assert _values_forward(llist) == [3, 2, 1, 0]
    assert _values_backward(llist) == [0, 1, 2, 3]
    _assert_well_formed(llist)


def test_prepend_after_reverse_extends_from_the_new_head() -> None:
    llist = _list_of(1, 2, 3)
    llist.reverse()

    llist.prepend(4)

    assert _values_forward(llist) == [4, 3, 2, 1]
    assert _values_backward(llist) == [1, 2, 3, 4]
    _assert_well_formed(llist)


def test_delete_head_after_reverse_removes_the_old_tail_value() -> None:
    llist = _list_of(1, 2, 3)
    llist.reverse()

    removed = llist.delete_head()

    assert removed is not None
    assert removed.value == 3
    assert _values_forward(llist) == [2, 1]
    _assert_well_formed(llist)


def test_delete_tail_after_reverse_removes_the_old_head_value() -> None:
    llist = _list_of(1, 2, 3)
    llist.reverse()

    removed = llist.delete_tail()

    assert removed is not None
    assert removed.value == 1
    assert _values_forward(llist) == [3, 2]
    _assert_well_formed(llist)


def test_delete_after_reverse_unlinks_the_middle_node() -> None:
    llist = _list_of(1, 2, 3, 4)
    llist.reverse()
    # delete() walks `next`, so a cyclic list would hang it: fail fast here instead.
    _assert_well_formed(llist)

    removed = llist.delete(3)

    assert removed is not None
    assert removed.value == 3
    assert _values_forward(llist) == [4, 2, 1]
    _assert_well_formed(llist)


def test_reverse_after_delete_head_reverses_only_the_remaining_nodes() -> None:
    llist = _list_of(1, 2, 3, 4)
    llist.delete_head()

    llist.reverse()

    assert _values_forward(llist) == [4, 3, 2]
    assert _values_backward(llist) == [2, 3, 4]
    _assert_well_formed(llist)


def test_reverse_after_mixed_prepend_and_append() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()
    llist.prepend(2).prepend(1).append(3).append(4)

    llist.reverse()

    assert _values_forward(llist) == [4, 3, 2, 1]
    assert _values_backward(llist) == [1, 2, 3, 4]
    _assert_well_formed(llist)


# ---------------------------------------------------------------------------
# __repr__
# ---------------------------------------------------------------------------


def test_repr_empty_list() -> None:
    llist: DoublyLinkedList[int] = DoublyLinkedList()

    assert repr(llist) == "DoublyLinkedList([])"


def test_repr_single_element() -> None:
    llist = _list_of(42)

    assert repr(llist) == "DoublyLinkedList([42])"


def test_repr_multiple_elements() -> None:
    llist = _list_of(1, 2, 3)

    assert repr(llist) == "DoublyLinkedList([1, 2, 3])"


def test_repr_string_elements() -> None:
    llist: DoublyLinkedList[str] = DoublyLinkedList()
    llist.append("a").append("b").append("c")

    assert repr(llist) == "DoublyLinkedList(['a', 'b', 'c'])"
