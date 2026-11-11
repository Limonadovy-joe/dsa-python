import pytest

from dsa.arrays import DynamicArray


def test_append_and_index() -> None:
    array: DynamicArray[int] = DynamicArray()
    for value in range(3):
        array.append(value)
    assert len(array) == 3
    assert [array[i] for i in range(3)] == [0, 1, 2]


def test_constructed_from_iterable() -> None:
    assert list(DynamicArray("abc")) == ["a", "b", "c"]


def test_grows_by_doubling() -> None:
    array: DynamicArray[int] = DynamicArray()
    assert array.capacity == 4
    for value in range(5):
        array.append(value)
    assert array.capacity == 8
    assert list(array) == [0, 1, 2, 3, 4]


def test_negative_index_and_setitem() -> None:
    array = DynamicArray([1, 2, 3])
    array[-1] = 99
    assert array[2] == 99


def test_insert_shifts_right() -> None:
    array = DynamicArray([1, 3])
    array.insert(1, 2)
    array.insert(3, 4)
    assert list(array) == [1, 2, 3, 4]


def test_pop_returns_and_shrinks() -> None:
    array = DynamicArray([1, 2, 3])
    assert array.pop() == 3
    assert array.pop(0) == 1
    assert list(array) == [2]


@pytest.mark.parametrize("index", [0, -1, 5])
def test_out_of_range_raises(index: int) -> None:
    with pytest.raises(IndexError):
        DynamicArray[int]()[index]


def test_equality() -> None:
    assert DynamicArray([1, 2]) == DynamicArray([1, 2])
    assert DynamicArray([1, 2]) != DynamicArray([1])
