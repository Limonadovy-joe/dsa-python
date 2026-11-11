from __future__ import annotations

import pytest

from tests.queues.queue.queue_backends import BACKENDS, MakeQueue


@pytest.fixture(params=list(BACKENDS))
def queue_backend(request: pytest.FixtureRequest) -> str:
    return request.param  # type: ignore[no-any-return]


@pytest.fixture
def make_queue(queue_backend: str) -> MakeQueue:
    return BACKENDS[queue_backend]
