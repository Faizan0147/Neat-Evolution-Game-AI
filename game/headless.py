"""
Headless game runner for fast NEAT fitness evaluation.

GameHeadless.run_episode(network) → float fitness

The fitness function is:
    fitness = pipes_cleared ** 3 + time_alive * 0.01

Why cubic pipes?
    Going from 1 to 5 pipes is 125× better (not just 5×).
    This creates massive evolutionary pressure to actually clear pipes.

Why the time bonus?
    Without it, a bird dying instantly and a bird dying at the first pipe
    have equal fitness (0). The time term creates a gradient so early
    generations learn to survive longer even before clearing any pipe.

Performance target: 150 episodes in under 10 seconds.
"""

from __future__ import annotations

from typing import Protocol

from game.engine import GameEngine
from game.sensors import extract_inputs


class Network(Protocol):
    """Minimal interface expected from a NEAT neural network."""

    def evaluate(self, inputs: list[float]) -> list[float]:
        """Forward pass: inputs → output activations."""
        ...


def fitness_from_game(pipes_cleared: int, time_alive: int) -> float:
    """
    Compute the NEAT fitness score from raw game outcomes.

    Parameters
    ----------
    pipes_cleared : int
        Number of pipe pairs successfully passed.
    time_alive : int
        Number of frames the bird survived.

    Returns
    -------
    float
        Fitness score.  Higher is always better.
    """
    return float(pipes_cleared**3) + time_alive * 0.01


def run_episode(network: Network, max_frames: int = 10_000) -> float:
    """
    Run one complete Flappy Bird episode with the given network and
    return the fitness score.

    Parameters
    ----------
    network : Network
        Any object with an evaluate(inputs) → list[float] method.
        Typically a NeuralNetwork built from a NEAT Genome.
    max_frames : int
        Hard cap on episode length.  Prevents immortal birds from
        running indefinitely in headless training.

    Returns
    -------
    float
        Fitness score for this episode.
    """
    game = GameEngine(headless=True)

    for _ in range(max_frames):
        if not game.is_alive():
            break

        state = game.get_state()
        inputs = extract_inputs(state)
        outputs = network.evaluate(inputs)

        # Output is sigmoid ∈ [0, 1]. Flap if > 0.5
        flap = len(outputs) > 0 and outputs[0] > 0.5
        game.set_action(flap=flap)
        game.update()

    return fitness_from_game(game.get_score(), game.get_time_alive())


class GameHeadless:
    """
    Reusable headless game runner.

    Holds a single GameEngine instance and resets it between episodes
    to avoid the overhead of constructing a new engine every time.
    This is the recommended way to run many episodes during NEAT training.

    Example
    -------
        runner = GameHeadless()
        fitness = runner.run_episode(my_network)
    """

    def __init__(self) -> None:
        self._engine = GameEngine(headless=True)

    def run_episode(self, network: Network, max_frames: int = 10_000) -> float:
        """
        Run one episode, reset the engine, return fitness.

        Parameters
        ----------
        network : Network
            Neural network to evaluate.
        max_frames : int
            Frame cap per episode.

        Returns
        -------
        float
            Fitness score.
        """
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
