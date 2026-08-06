from __future__ import annotations

from typing import Protocol

from game.engine import GameEngine
from game.sensors import extract_inputs


class Network(Protocol):
    def evaluate(self, inputs: list[float]) -> list[float]: ...


def fitness_from_game(pipes_cleared: int, time_alive: int) -> float:
    return float(pipes_cleared**3) + time_alive * 0.01


def run_episode(network: Network, max_frames: int = 10_000) -> float:
    game = GameEngine(headless=True)

    for _ in range(max_frames):
        if not game.is_alive():
            break

        state = game.get_state()
        inputs = extract_inputs(state)
        outputs = network.evaluate(inputs)

        flap = len(outputs) > 0 and outputs[0] > 0.5
        game.set_action(flap=flap)
        game.update()

    return fitness_from_game(game.get_score(), game.get_time_alive())


class GameHeadless:
    def __init__(self) -> None:
        self._engine = GameEngine(headless=True)

    def run_episode(self, network: Network, max_frames: int = 10_000) -> float:
        self._engine.reset()

        for _ in range(max_frames):
            if not self._engine.is_alive():
                break

            state = self._engine.get_state()
            inputs = extract_inputs(state)
            outputs = network.evaluate(inputs)

            flap = len(outputs) > 0 and outputs[0] > 0.5
            self._engine.set_action(flap=flap)
            self._engine.update()

        return fitness_from_game(
            self._engine.get_score(),
            self._engine.get_time_alive(),
        )
