import inspect
import math
from enum import IntEnum, StrEnum

import pytest

from utils.comparator.comparator import Comparator, Primitive

NAN = math.nan
INF = math.inf

# (x, y, expected default_compare(x, y)) for every supported, valid pair.
LESS_EQUAL_GREATER: list[tuple[Primitive, Primitive, int]] = [
    (1, 2, -1),
    (2, 2, 0),
    (3, 2, 1),
    (-5, 5, -1),
    (1.5, 2.5, -1),
    (2.5, 2.5, 0),
    (3.5, 2.5, 1),
    ("a", "b", -1),
    ("a", "a", 0),
    ("b", "a", 1),
    ("ab", "abc", -1),
    (b"a", b"b", -1),
    (b"a", b"a", 0),
    (b"b", b"a", 1),
]
MIXED_NUMERICS: list[tuple[Primitive, Primitive, int]] = [
    (1, 1.0, 0),
    (True, 1, 0),
    (False, 0.5, -1),
    (2, 1.5, 1),
    (True, False, 1),
    (0.0, -0.0, 0),
]
NAN_CASES: list[tuple[Primitive, Primitive, int]] = [
    (NAN, NAN, 0),
    (NAN, 0, 1),
    (NAN, 1.5, 1),
    (NAN, True, 1),
    (NAN, INF, 1),
    (NAN, -INF, 1),
    (NAN, 10**400, 1),
    (0, NAN, -1),
    (1.5, NAN, -1),
    (False, NAN, -1),
    (INF, NAN, -1),
    (-INF, NAN, -1),
    (10**400, NAN, -1),
]
INFINITY_CASES: list[tuple[Primitive, Primitive, int]] = [
    (-INF, -(10**100), -1),
    (INF, 10**100, 1),
    (-INF, -1e308, -1),
    (INF, 1e308, 1),
    (INF, INF, 0),
    (-INF, -INF, 0),
    (-INF, INF, -1),
]
NONE_CASES: list[tuple[Primitive, Primitive, int]] = [(None, None, 0)]
EMPTY_CASES: list[tuple[Primitive, Primitive, int]] = [
    ("", "", 0),
    ("", "a", -1),
    (b"", b"", 0),
    (b"", b"\x00", -1),
]
ALL_VALID = (
    LESS_EQUAL_GREATER
    + MIXED_NUMERICS
    + NAN_CASES
    + INFINITY_CASES
    + NONE_CASES
    + EMPTY_CASES
)
CROSS_FAMILY: list[tuple[Primitive, Primitive]] = [
    ("a", 1),
    (1, "a"),
    ("a", b"a"),
    (b"a", "a"),
    (None, 0),
    (0, None),
    (None, ""),
    ("", None),
    (None, b""),
    (True, "1"),
    (1.5, b"1"),
]
# Values outside the primitive families: compared through the ==/</> fallback.
FALLBACK_VALID: list[tuple[object, object, int]] = [
    ([1], [1], 0),
    ([1], [2], -1),
    ((2,), (1,), 1),
    ([], [], 0),
    ([], [0], -1),
    ((1, "a"), (1, "b"), -1),
    (frozenset({1}), frozenset({1, 2}), -1),
]
FALLBACK_UNORDERABLE: list[tuple[object, object]] = [
    (object(), object()),
    ([1], (1,)),
    (1, [1]),
    ([1], "a"),
    (None, [None]),
]
# Unequal, yet neither < nor >: partial orders and containers of distinct NaNs.
# float("nan") is called twice on purpose: two distinct NaN objects.
PARTIAL_ORDER: list[tuple[object, object]] = [
    (frozenset({1}), frozenset({2})),
    ({1}, {2}),
    ([float("nan")], [float("nan")]),
    ((float("nan"),), (float("nan"),)),
]


def _assert_compares(x: Primitive, y: Primitive, expected: int) -> None:
    result = Comparator.default_compare(x, y)
    assert type(result) is int
    assert result == expected


@pytest.mark.parametrize(("x", "y", "expected"), LESS_EQUAL_GREATER)
def test_default_compare_returns_minus_one_zero_one_for_less_equal_greater(
    x: Primitive, y: Primitive, expected: int
) -> None:
    _assert_compares(x, y, expected)


@pytest.mark.parametrize(("x", "y", "expected"), MIXED_NUMERICS)
def test_default_compare_mixed_numerics_compare_by_value(
    x: Primitive, y: Primitive, expected: int
) -> None:
    _assert_compares(x, y, expected)


@pytest.mark.parametrize(("x", "y", "expected"), NAN_CASES)
def test_default_compare_nan_equals_nan_and_is_greater_than_every_number(
    x: Primitive, y: Primitive, expected: int
) -> None:
    _assert_compares(x, y, expected)


@pytest.mark.parametrize(("x", "y", "expected"), INFINITY_CASES)
def test_default_compare_orders_infinities_against_huge_ints_and_floats(
    x: Primitive, y: Primitive, expected: int
) -> None:
    _assert_compares(x, y, expected)


def test_default_compare_none_equals_none() -> None:
    _assert_compares(None, None, 0)


@pytest.mark.parametrize(("x", "y"), CROSS_FAMILY)
def test_default_compare_cross_family_raises_type_error_naming_both_types(
    x: Primitive, y: Primitive
) -> None:
    with pytest.raises(TypeError) as excinfo:
        Comparator.default_compare(x, y)

    message = str(excinfo.value)
    assert type(x).__name__ in message
    assert type(y).__name__ in message


@pytest.mark.parametrize(("x", "y", "expected"), FALLBACK_VALID)
def test_default_compare_non_primitives_fall_back_to_eq_lt_gt(
    x: object, y: object, expected: int
) -> None:
    compare = Comparator[object]().compare

    result = compare(x, y)

    assert type(result) is int
    assert result == expected
    assert compare(y, x) == -expected


def test_default_compare_same_object_against_itself_is_zero() -> None:
    compare = Comparator[object]().compare
    value = object()

    assert compare(value, value) == 0


@pytest.mark.parametrize(("x", "y"), FALLBACK_UNORDERABLE)
def test_default_compare_unorderable_non_primitives_raise_type_error_naming_both(
    x: object, y: object
) -> None:
    compare = Comparator[object]().compare

    with pytest.raises(TypeError) as excinfo:
        compare(x, y)

    message = str(excinfo.value)
    assert type(x).__name__ in message
    assert type(y).__name__ in message


def test_comparator_equal_on_unequal_lists_is_false_without_raising() -> None:
    comparator = Comparator[list[int]]()

    assert not comparator.equal([1], [2])
    assert comparator.equal([1], [1])


@pytest.mark.parametrize(("x", "y", "expected"), EMPTY_CASES)
def test_default_compare_empty_values(
    x: Primitive, y: Primitive, expected: int
) -> None:
    _assert_compares(x, y, expected)


@pytest.mark.parametrize(("x", "y", "expected"), ALL_VALID)
def test_default_compare_is_antisymmetric(
    x: Primitive, y: Primitive, expected: int
) -> None:
    forward = Comparator.default_compare(x, y)
    backward = Comparator.default_compare(y, x)

    assert forward == expected
    assert forward == -backward


def test_default_compare_is_a_staticmethod_callable_without_instance() -> None:
    assert isinstance(
        inspect.getattr_static(Comparator, "default_compare"), staticmethod
    )
    assert Comparator.default_compare(1, 2) == -1


def test_default_compare_has_no_todo_left() -> None:
    assert "TODO" not in inspect.getsource(Comparator.default_compare)


def test_comparator_without_argument_uses_default_compare() -> None:
    comparator: Comparator[Primitive] = Comparator()

    assert comparator.compare is Comparator.default_compare
    assert comparator.equal(1, 1.0)
    assert comparator.equal(NAN, NAN)
    assert not comparator.equal(1, 2)
    assert not comparator.equal("a", "A")


def test_comparator_with_custom_compare_uses_it_for_equal() -> None:
    def case_insensitive(a: str, b: str) -> int:
        return Comparator.default_compare(a.casefold(), b.casefold())

    comparator = Comparator(case_insensitive)

    assert comparator.compare is case_insensitive
    assert comparator.equal("A", "a")
    assert not comparator.equal("A", "b")


def test_comparator_equal_on_non_primitives_with_custom_compare() -> None:
    def by_length(a: list[int], b: list[int]) -> int:
        return Comparator.default_compare(len(a), len(b))

    comparator = Comparator(by_length)

    assert comparator.equal([1, 2], [3, 4])
    assert not comparator.equal([1], [1, 2])


@pytest.mark.parametrize(("x", "y"), PARTIAL_ORDER)
def test_default_compare_partial_order_gets_antisymmetric_nonzero_tie_break(
    x: object, y: object
) -> None:
    compare = Comparator[object]().compare

    forward = compare(x, y)

    assert forward in {-1, 1}
    assert compare(y, x) == -forward
    assert compare(x, y) == forward
    assert compare(x, x) == 0


def test_comparator_equal_on_unequal_frozensets_is_false_without_raising() -> None:
    comparator = Comparator[frozenset[int]]()

    assert comparator.equal(frozenset({1}), frozenset({2})) is False
    assert comparator.equal(frozenset({1}), frozenset({1})) is True


def test_comparator_equal_on_lists_with_distinct_nan_is_false() -> None:
    comparator = Comparator[list[float]]()
    first, second = [float("nan")], [float("nan")]

    assert comparator.equal(first, second) is False
    assert comparator.equal(first, first) is True


class _Level(IntEnum):
    LOW = 1
    HIGH = 2


class _Colour(StrEnum):
    BLUE = "blue"
    RED = "red"


@pytest.mark.parametrize(
    ("x", "y", "expected"),
    [
        (_Level.LOW, _Level.HIGH, -1),
        (_Level.HIGH, 2, 0),
        (2.5, _Level.HIGH, 1),
        (_Colour.BLUE, _Colour.RED, -1),
        (_Colour.RED, "red", 0),
    ],
)
def test_default_compare_int_and_str_subclasses_compare_in_their_family(
    x: Primitive, y: Primitive, expected: int
) -> None:
    _assert_compares(x, y, expected)
    assert Comparator.default_compare(y, x) == -expected
