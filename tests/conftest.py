from __future__ import annotations

import random

import pytest

from game.engine import GameEngine
from game.headless import GameHeadless


class _RandomNetwork:
    def evaluate(self, inputs: list[float]) -> list[float]:  # noqa: ARG002
        return [random.random()]


@pytest.fixture()
def headless_engine() -> GameEngine:
    return GameEngine(headless=True)


@pytest.fixture()
def headless_game() -> GameHeadless:
    return GameHeadless()


@pytest.fixture()
def random_network() -> _RandomNetwork:
    return _RandomNetwork()
