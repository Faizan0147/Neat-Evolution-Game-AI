from __future__ import annotations

import time

import pytest

from game.constants import (
    FPS,
    GRAVITY,
    PIPE_GAP,
    PIPE_WIDTH,
    PLAYER_RADIUS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from game.engine import GameEngine, PipePair
from game.headless import GameHeadless, fitness_from_game
from game.sensors import extract_inputs


class TestEngineInitialState:
    def test_starts_alive(self, headless_engine: GameEngine) -> None:
        assert headless_engine.is_alive()

    def test_score_zero_at_start(self, headless_engine: GameEngine) -> None:
        assert headless_engine.get_score() == 0

    def test_time_alive_zero_at_start(self, headless_engine: GameEngine) -> None:
        assert headless_engine.get_time_alive() == 0

    def test_pipes_spawned_at_start(self, headless_engine: GameEngine) -> None:
        state = headless_engine.get_state()
        assert len(state.pipes) >= 1

    def test_player_starts_in_middle_of_screen(self, headless_engine: GameEngine) -> None:
        state = headless_engine.get_state()
        assert 0 < state.player_x < SCREEN_WIDTH * 0.5
        assert SCREEN_HEIGHT * 0.2 < state.player_y < SCREEN_HEIGHT * 0.8


class TestEnginePhysics:
    def test_gravity_pulls_bird_downward(self, headless_engine: GameEngine) -> None:
        state_before = headless_engine.get_state()
        headless_engine.update()
        state_after = headless_engine.get_state()
        assert state_after.player_vy > state_before.player_vy

    def test_gravity_magnitude_matches_constant(self, headless_engine: GameEngine) -> None:
        headless_engine.update()
        state = headless_engine.get_state()
        assert abs(state.player_vy - GRAVITY) < 1e-6

    def test_flap_gives_upward_velocity(self, headless_engine: GameEngine) -> None:
        headless_engine.set_action(flap=True)
        headless_engine.update()
        state = headless_engine.get_state()
        assert state.player_vy < 0

    def test_frame_counter_increments(self, headless_engine: GameEngine) -> None:
        for _ in range(10):
            headless_engine.update()
        assert headless_engine.get_time_alive() == 10

    def test_update_is_noop_when_dead(self, headless_engine: GameEngine) -> None:
        headless_engine._player.y = float(SCREEN_HEIGHT) + 100
        headless_engine.update()
        assert not headless_engine.is_alive()

        frames_at_death = headless_engine.get_time_alive()
        headless_engine.update()
        assert headless_engine.get_time_alive() == frames_at_death


class TestEngineCollision:
    def test_floor_collision_kills_player(self, headless_engine: GameEngine) -> None:
        headless_engine._player.y = float(SCREEN_HEIGHT) + 10
        headless_engine.update()
        assert not headless_engine.is_alive()

    def test_ceiling_collision_kills_player(self, headless_engine: GameEngine) -> None:
        headless_engine._player.y = -float(PLAYER_RADIUS) - 5
        headless_engine.update()
        assert not headless_engine.is_alive()

    def test_pipe_collision_kills_player(self, headless_engine: GameEngine) -> None:
        px = headless_engine._player.x
        py = headless_engine._player.y
        pipe = PipePair(
            x=px - float(PIPE_WIDTH) / 2,
            gap_y=py + float(PLAYER_RADIUS) + 10,
        )
        headless_engine._pipes = [pipe]
        headless_engine.update()
        assert not headless_engine.is_alive()

    def test_surviving_through_gap_does_not_kill(self, headless_engine: GameEngine) -> None:
        px = headless_engine._player.x
        gap_y = 200.0
        pipe = PipePair(
            x=px - float(PIPE_WIDTH) / 2,
            gap_y=gap_y,
        )
        headless_engine._player.y = gap_y + float(PIPE_GAP) / 2
        headless_engine._pipes = [pipe]
        headless_engine.update()
        state = headless_engine.get_state()
        assert state.player_y > 0


class TestEngineScoring:
    def test_passing_pipe_increments_score(self, headless_engine: GameEngine) -> None:
        px = headless_engine._player.x
        pipe = PipePair(
            x=px - float(PIPE_WIDTH) - 10,
            gap_y=float(SCREEN_HEIGHT) / 2 - float(PIPE_GAP) / 2,
            passed=False,
        )
        headless_engine._pipes = [pipe]
        headless_engine.update()
        assert headless_engine.get_score() == 1

    def test_same_pipe_not_counted_twice(self, headless_engine: GameEngine) -> None:
        px = headless_engine._player.x
        pipe = PipePair(
            x=px - float(PIPE_WIDTH) - 10,
            gap_y=float(SCREEN_HEIGHT) / 2 - float(PIPE_GAP) / 2,
            passed=False,
        )
        headless_engine._pipes = [pipe]
        headless_engine.update()
        headless_engine.update()
        assert headless_engine.get_score() == 1


class TestEngineReset:
    def test_reset_restores_alive(self, headless_engine: GameEngine) -> None:
        headless_engine._player.y = float(SCREEN_HEIGHT) + 100
        headless_engine.update()
        assert not headless_engine.is_alive()
        headless_engine.reset()
        assert headless_engine.is_alive()

    def test_reset_clears_score(self, headless_engine: GameEngine) -> None:
        px = headless_engine._player.x
        pipe = PipePair(
            x=px - float(PIPE_WIDTH) - 10,
            gap_y=float(SCREEN_HEIGHT) / 2 - float(PIPE_GAP) / 2,
            passed=False,
        )
        headless_engine._pipes = [pipe]
        headless_engine.update()
        assert headless_engine.get_score() == 1
        headless_engine.reset()
        assert headless_engine.get_score() == 0

    def test_reset_clears_time(self, headless_engine: GameEngine) -> None:
        for _ in range(30):
            headless_engine.update()
        headless_engine.reset()
        assert headless_engine.get_time_alive() == 0


class TestSensors:
    def test_returns_exactly_five_inputs(self, headless_engine: GameEngine) -> None:
        inputs = extract_inputs(headless_engine.get_state())
        assert len(inputs) == 5

    def test_input_1_horiz_dist_in_zero_one(self, headless_engine: GameEngine) -> None:
        inputs = extract_inputs(headless_engine.get_state())
        assert 0.0 <= inputs[0] <= 1.0

    def test_input_2_dist_to_top_in_neg1_to_1(self, headless_engine: GameEngine) -> None:
        inputs = extract_inputs(headless_engine.get_state())
        assert -1.0 <= inputs[1] <= 1.0

    def test_input_3_dist_to_bottom_in_neg1_to_1(self, headless_engine: GameEngine) -> None:
        inputs = extract_inputs(headless_engine.get_state())
        assert -1.0 <= inputs[2] <= 1.0

    def test_input_4_velocity_in_neg1_to_1(self, headless_engine: GameEngine) -> None:
        inputs = extract_inputs(headless_engine.get_state())
        assert -1.0 <= inputs[3] <= 1.0

    def test_input_5_y_pos_in_zero_one(self, headless_engine: GameEngine) -> None:
        inputs = extract_inputs(headless_engine.get_state())
        assert 0.0 <= inputs[4] <= 1.0

    def test_all_inputs_are_finite(self, headless_engine: GameEngine) -> None:
        import math

        for _ in range(60):
            headless_engine.update()
        inputs = extract_inputs(headless_engine.get_state())
        assert all(math.isfinite(v) for v in inputs)


class TestFitnessFunction:
    def test_zero_pipes_zero_time(self) -> None:
        assert fitness_from_game(0, 0) == 0.0

    def test_cubic_pipes_weight(self) -> None:
        assert fitness_from_game(5, 0) == 125.0

    def test_time_bonus(self) -> None:
        assert abs(fitness_from_game(0, 100) - 1.0) < 1e-9

    def test_combined(self) -> None:
        result = fitness_from_game(3, 1000)
        expected = 27.0 + 10.0
        assert abs(result - expected) < 1e-9

    def test_more_pipes_always_better(self) -> None:
        assert fitness_from_game(5, 300) > fitness_from_game(4, 300)


class TestHeadlessRunner:
    def test_run_episode_returns_float(self, headless_game: GameHeadless, random_network) -> None:
        result = headless_game.run_episode(random_network)
        assert isinstance(result, float)

    def test_run_episode_returns_nonnegative(self, headless_game: GameHeadless, random_network) -> None:
        result = headless_game.run_episode(random_network)
        assert result >= 0.0

    def test_always_flap_network_survives_some_frames(self, headless_game: GameHeadless) -> None:
        class AlwaysFlap:
            def evaluate(self, inputs: list[float]) -> list[float]:
                return [1.0]

        result = headless_game.run_episode(AlwaysFlap())
        assert result >= 0.0

    def test_never_flap_network_survives_some_frames(self, headless_game: GameHeadless) -> None:
        class NeverFlap:
            def evaluate(self, inputs: list[float]) -> list[float]:
                return [0.0]

        result = headless_game.run_episode(NeverFlap())
        assert result >= 0.0

    def test_150_episodes_under_10_seconds(self) -> None:
        import random as rng

        class RandomNet:
            def evaluate(self, inputs: list[float]) -> list[float]:
                return [rng.random()]

        runner = GameHeadless()
        net = RandomNet()

        start = time.perf_counter()
        for _ in range(150):
            runner.run_episode(net)
        elapsed = time.perf_counter() - start

        assert elapsed < 10.0, f"150 episodes took {elapsed:.2f}s — must be < 10s."

    def test_reset_between_episodes_clears_state(self, headless_game: GameHeadless) -> None:
        class NeverFlap:
            def evaluate(self, inputs: list[float]) -> list[float]:
                return [0.0]

        net = NeverFlap()
        scores = [headless_game.run_episode(net) for _ in range(3)]
        assert all(s >= 0.0 for s in scores)
