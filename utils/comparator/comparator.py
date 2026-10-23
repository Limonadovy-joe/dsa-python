from typing import Callable, TypeVar, Optional

T = TypeVar("T")

ComparatorFunc = Callable[[T, T], int]


class Comparator[T]:
    compare: ComparatorFunc

    @staticmethod
    def default_compare(x: str | int, y: str | int) -> int:
        # TODO
        # handle case where x:str, y: int
        if x == y:
            return 0
        return -1 if x < y else 1

    def __init__(self, compare_fun: Optional[ComparatorFunc[T]] = None):
        if compare_fun is not None:
            self.compare = compare_fun
        else:
            self.compare = Comparator.default_compare

    def equal(self, x: T, y: T) -> bool:
        return self.compare(x, y) == 0
