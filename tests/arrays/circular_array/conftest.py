from __future__ import annotations

import pytest

from tests.arrays.circular_array.circular_array_backends import (
    BACKENDS,
    MakeCircularArray,
)


@pytest.fixture(params=list(BACKENDS))
def circular_array_backend(request: pytest.FixtureRequest) -> str:
    return request.param  # type: ignore[no-any-return]


@pytest.fixture
def make_circular_array(circular_array_backend: str) -> MakeCircularArray:
    return BACKENDS[circular_array_backend]
