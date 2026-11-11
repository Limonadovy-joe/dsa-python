from __future__ import annotations

import pytest

from tests.queues.deque.deque_backends import BACKENDS, MakeDeque


@pytest.fixture(params=list(BACKENDS))
def deque_backend(request: pytest.FixtureRequest) -> str:
    return request.param  # type: ignore[no-any-return]


@pytest.fixture
def make_deque(deque_backend: str) -> MakeDeque:
    return BACKENDS[deque_backend]
