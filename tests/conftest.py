"""
Shared test fixtures for all NEAT Flappy Bird test suites.

Conventions
-----------
- All fixtures that touch InnovationTracker call reset() in teardown so
  tests are order-independent.
- headless_game() creates a fresh GameHeadless for each test that needs it.
- random_network() provides a stub implementing the Network protocol.
"""

from __future__ import annotations

import random

import pytest

from game.engine import GameEngine
from game.headless import GameHeadless


class _RandomNetwork:
    """Minimal stub satisfying the Network protocol — used across test suites."""

    def evaluate(self, inputs: list[float]) -> list[float]:  # noqa: ARG002
        return [random.random()]


@pytest.fixture()
def headless_engine() -> GameEngine:
    """Fresh headless GameEngine for low-level engine tests."""
    return GameEngine(headless=True)


@pytest.fixture()
def headless_game() -> GameHeadless:
    """Reusable GameHeadless runner for episode-level tests."""
    return GameHeadless()


@pytest.fixture()
def random_network() -> _RandomNetwork:
    """Stub network that outputs a random activation each frame."""
    return _RandomNetwork()
