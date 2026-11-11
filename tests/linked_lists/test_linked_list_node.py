import pytest

from dsa.linked_lists import LinkedListNode


# TODO(DSA-33): add a type error case for the node (type error object)
#   [Tooling | Linked Lists | Tests | needs-human]
#   Why is it better to generate ids for the given input test data?
#   Type error: object is not assignable to generic type parameter T.
#
# TODO: what does `class LinkedListNode[invariant T]` mean, i.e. invariant T?
#   [Analysis | Linked Lists | Tests | needs-human]
#   Related: object is not assignable to generic type parameter T.
@pytest.mark.parametrize(
    "value",
    [0, 42, -1, 3.14, "hello", None, [], (1, 2)],
    ids=["zero", "int", "negative", "float", "str", "none", "list", "tuple"],
)
def test_init_with_value_stores_value_and_sets_next_to_none(value: object) -> None:
    node: LinkedListNode[object] = LinkedListNode(value)
    assert node.value is value
    assert node.next is None


# ---------------------------------------------------------------------------
# Constructor: value + next
# ---------------------------------------------------------------------------


def test_init_with_value_and_next_links_nodes() -> None:
    tail: LinkedListNode[int] = LinkedListNode(2)
    head: LinkedListNode[int] = LinkedListNode(1, tail)
    assert head.value == 1
    assert head.next is tail
    assert tail.next is None


def test_init_with_value_and_none_next() -> None:
    node: LinkedListNode[int] = LinkedListNode(10, None)
    assert node.value == 10
    assert node.next is None


def test_init_three_node_chain() -> None:
    c: LinkedListNode[str] = LinkedListNode("c")
    b: LinkedListNode[str] = LinkedListNode("b", c)
    a: LinkedListNode[str] = LinkedListNode("a", b)
    assert a.value == "a"
    assert a.next is b
    assert b.next is c
    assert c.next is None


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
    node: LinkedListNode[object] = LinkedListNode(value)
    assert isinstance(node.value, expected_type)


def test_next_is_linked_list_node_or_none() -> None:
    lone: LinkedListNode[int] = LinkedListNode(1)
    assert lone.next is None

    chained: LinkedListNode[int] = LinkedListNode(1, LinkedListNode(2))
    assert isinstance(chained.next, LinkedListNode)


def test_node_default_string_conversion() -> None:
    """Test string conversion without a callback."""
    node = LinkedListNode(5)

    assert node.to_string() == "5"
    assert str(node) == "5"


def test_node_custom_callback_with_dict() -> None:
    """Test your specific use case with a dictionary and a custom callback."""
    node_value = {"value": 1, "key": "test"}
    node = LinkedListNode(node_value)

    def to_string_callback(val: dict[str, object]) -> str:
        return f"value: {val['value']}, key: {val['key']}"

    assert node.to_string(to_string_callback) == "value: 1, key: test"


def test_node_custom_callback_with_lambda() -> None:
    """Test using an inline lambda function as the callback."""
    node = LinkedListNode("Python")

    # Using a simple inline lambda function instead of defining a full function
    result = node.to_string(lambda v: f"Node contains: {v}")

    assert result == "Node contains: Python"
