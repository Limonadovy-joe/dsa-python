from itertools import pairwise

import pytest

from dsa.linked_lists import DoublyLinkedListNode, LinkedListNode


def _chain[T](values: list[T]) -> list[DoublyLinkedListNode[T]]:
    """Build a fully bidirectional chain, returning the nodes in order."""
    nodes = [DoublyLinkedListNode(value) for value in values]
    for left, right in pairwise(nodes):
        left.link(right)
    return nodes


def _values_forward[T](head: LinkedListNode[T] | None) -> list[T]:
    values: list[T] = []
    node = head
    while node is not None:
        values.append(node.value)
        node = node.next
    return values


def _values_backward[T](tail: DoublyLinkedListNode[T] | None) -> list[T]:
    values: list[T] = []
    node = tail
    while node is not None:
        values.append(node.value)
        node = node.previous
    return values


# ---------------------------------------------------------------------------
# Constructor: value only
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [0, 42, -1, 3.14, "hello", None, [], (1, 2)],
    ids=["zero", "int", "negative", "float", "str", "none", "list", "tuple"],
)
def test_init_with_value_stores_value_and_sets_both_pointers_to_none(
    value: object,
) -> None:
    node: DoublyLinkedListNode[object] = DoublyLinkedListNode(value)
    assert node.value is value
    assert node.next is None
    assert node.previous is None


def test_node_is_a_linked_list_node() -> None:
    node: DoublyLinkedListNode[int] = DoublyLinkedListNode(1)
    assert isinstance(node, LinkedListNode)


# ---------------------------------------------------------------------------
# Constructor: value + next + previous
# ---------------------------------------------------------------------------


def test_init_with_next_sets_next_and_leaves_previous_none() -> None:
    tail: DoublyLinkedListNode[int] = DoublyLinkedListNode(2)
    head: DoublyLinkedListNode[int] = DoublyLinkedListNode(1, tail)
    assert head.value == 1
    assert head.next is tail
    assert head.previous is None


def test_init_with_prev_node_sets_previous_and_leaves_next_none() -> None:
    head: DoublyLinkedListNode[int] = DoublyLinkedListNode(1)
    tail: DoublyLinkedListNode[int] = DoublyLinkedListNode(2, prev_node=head)
    assert tail.value == 2
    assert tail.previous is head
    assert tail.next is None


def test_init_with_next_and_prev_sets_both_pointers() -> None:
    first: DoublyLinkedListNode[int] = DoublyLinkedListNode(1)
    last: DoublyLinkedListNode[int] = DoublyLinkedListNode(3)
    middle: DoublyLinkedListNode[int] = DoublyLinkedListNode(2, last, first)
    assert middle.value == 2
    assert middle.next is last
    assert middle.previous is first


def test_init_with_explicit_none_pointers() -> None:
    node: DoublyLinkedListNode[int] = DoublyLinkedListNode(10, None, None)
    assert node.value == 10
    assert node.next is None
    assert node.previous is None


def test_init_does_not_back_link_the_neighbours() -> None:
    first: DoublyLinkedListNode[int] = DoublyLinkedListNode(1)
    last: DoublyLinkedListNode[int] = DoublyLinkedListNode(3)
    DoublyLinkedListNode(2, last, first)
    # Linking the other direction is the caller's job.
    assert first.next is None
    assert last.previous is None


@pytest.mark.parametrize(
    ("value", "expected_type"),
    [
        (42, int),
        ("hi", str),
        (3.14, float),
        (True, bool),
        ((1,), tuple),
    ],
    ids=["int", "str", "float", "bool", "tuple"],
)
def test_value_has_expected_runtime_type(value: object, expected_type: type) -> None:
    node: DoublyLinkedListNode[object] = DoublyLinkedListNode(value)
    assert isinstance(node.value, expected_type)


def test_next_and_previous_are_nodes_or_none() -> None:
    lone: DoublyLinkedListNode[int] = DoublyLinkedListNode(1)
    assert lone.next is None
    assert lone.previous is None

    linked: DoublyLinkedListNode[int] = DoublyLinkedListNode(
        2, DoublyLinkedListNode(3), DoublyLinkedListNode(1)
    )
    assert isinstance(linked.next, DoublyLinkedListNode)
    assert isinstance(linked.previous, DoublyLinkedListNode)


# ---------------------------------------------------------------------------
# String conversion (inherited from LinkedListNode)
# ---------------------------------------------------------------------------


def test_default_string_conversion() -> None:
    node: DoublyLinkedListNode[int] = DoublyLinkedListNode(5)
    assert node.to_string() == "5"
    assert str(node) == "5"


def test_string_conversion_ignores_neighbours() -> None:
    first, middle, last = _chain(["a", "b", "c"])
    assert str(middle) == "b"
    assert middle.to_string() == "b"
    assert str(first) == "a"
    assert str(last) == "c"


def test_custom_callback_with_dict() -> None:
    node: DoublyLinkedListNode[dict[str, object]] = DoublyLinkedListNode(
        {"value": 1, "key": "test"}
    )

    def to_string_callback(val: dict[str, object]) -> str:
        return f"value: {val['value']}, key: {val['key']}"

    assert node.to_string(to_string_callback) == "value: 1, key: test"


def test_custom_callback_with_lambda() -> None:
    node: DoublyLinkedListNode[str] = DoublyLinkedListNode("Python")
    assert node.to_string(lambda v: f"Node contains: {v}") == "Node contains: Python"


# ---------------------------------------------------------------------------
# Linking nodes together
# ---------------------------------------------------------------------------


def test_link_two_nodes_sets_both_pointers() -> None:
    a: DoublyLinkedListNode[int] = DoublyLinkedListNode(1)
    b: DoublyLinkedListNode[int] = DoublyLinkedListNode(2)

    a.link(b)

    assert a.next is b
    assert b.previous is a
    assert a.previous is None
    assert b.next is None


def test_link_three_nodes_by_constructor_and_assignment() -> None:
    a: DoublyLinkedListNode[str] = DoublyLinkedListNode("a")
    b: DoublyLinkedListNode[str] = DoublyLinkedListNode("b", prev_node=a)
    c: DoublyLinkedListNode[str] = DoublyLinkedListNode("c", prev_node=b)
    a.next = b
    b.next = c

    assert a.previous is None
    assert a.next is b
    assert b.previous is a
    assert b.next is c
    assert c.previous is b
    assert c.next is None


@pytest.mark.parametrize(
    "values",
    [[1], [1, 2], [1, 2, 3, 4, 5], list(range(1000))],
    ids=["single", "pair", "five", "thousand"],
)
def test_chain_walks_forward_and_backward(values: list[int]) -> None:
    nodes = _chain(values)

    assert _values_forward(nodes[0]) == values
    assert _values_backward(nodes[-1]) == values[::-1]


@pytest.mark.parametrize("length", [2, 3, 10], ids=["two", "three", "ten"])
def test_chain_pointers_are_symmetric(length: int) -> None:
    nodes = _chain(list(range(length)))

    for left, right in pairwise(nodes):
        assert left.next is right
        assert right.previous is left


def test_chain_ends_have_no_outer_neighbours() -> None:
    nodes = _chain([1, 2, 3])

    assert nodes[0].previous is None
    assert nodes[-1].next is None


def test_insert_node_between_two_linked_nodes() -> None:
    a, c = _chain(["a", "c"])
    b: DoublyLinkedListNode[str] = DoublyLinkedListNode("b")

    b.previous = a
    b.next = c
    a.next = b
    c.previous = b

    assert _values_forward(a) == ["a", "b", "c"]
    assert _values_backward(c) == ["c", "b", "a"]


def test_unlink_middle_node_bridges_its_neighbours() -> None:
    a, b, c = _chain(["a", "b", "c"])

    a.next = c
    c.previous = a
    b.next = None
    b.previous = None

    assert _values_forward(a) == ["a", "c"]
    assert _values_backward(c) == ["c", "a"]
    assert b.next is None
    assert b.previous is None


def test_unlink_head_leaves_next_node_as_new_head() -> None:
    a, b, c = _chain([1, 2, 3])

    b.previous = None
    a.next = None

    assert b.previous is None
    assert _values_forward(b) == [2, 3]
    assert _values_backward(c) == [3, 2]
    assert _values_forward(a) == [1]


def test_unlink_tail_leaves_previous_node_as_new_tail() -> None:
    a, b, c = _chain([1, 2, 3])

    b.next = None
    c.previous = None

    assert b.next is None
    assert _values_forward(a) == [1, 2]
    assert _values_backward(b) == [2, 1]
    assert _values_backward(c) == [3]


def test_link_nodes_into_a_ring() -> None:
    a, b, c = _chain([1, 2, 3])

    c.next = a
    a.previous = c

    # One full turn forward and one backward both land back on `a`.
    assert a.next is b
    assert b.next is c
    assert c.next is a
    assert a.previous is c
    assert c.previous is b
    assert b.previous is a
