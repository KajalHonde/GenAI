"""Shared pytest fixtures for AapdaMitra.

The RAG cache and the metrics store are module-level singletons, so reset
them before and after every test to keep tests independent.
"""

import pytest

from app.observability import cache_clear, metrics_clear


@pytest.fixture(autouse=True)
def _reset_observability():
    cache_clear()
    metrics_clear()
    yield
    cache_clear()
    metrics_clear()
