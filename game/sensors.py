from __future__ import annotations

from game.constants import MAX_PIPE_DISTANCE, MAX_VELOCITY, SCREEN_HEIGHT
from game.engine import GameState, PipePair


def _next_pipe(state: GameState) -> PipePair | None:
    ahead = [
        pipe
        for pipe in state.pipes
        if not pipe.passed or (pipe.x + 80 >= state.player_x)
    ]
    if not ahead:
        return None
    return min(ahead, key=lambda p: p.x)


def _clip(value: float, lo: float, hi: float) -> float:
    return max(lo, min(value, hi))


def extract_inputs(state: GameState) -> list[float]:
    next_pipe = _next_pipe(state)

    if next_pipe is None:
        horiz_dist = 1.0
    else:
        raw = next_pipe.x - state.player_x
        horiz_dist = _clip(raw / MAX_PIPE_DISTANCE, 0.0, 1.0)

    if next_pipe is None:
        dist_to_top = 0.0
    else:
        raw = state.player_y - next_pipe.gap_y
        dist_to_top = _clip(raw / SCREEN_HEIGHT, -1.0, 1.0)

    if next_pipe is None:
        dist_to_bottom = 0.0
    else:
        raw = state.player_y - next_pipe.gap_bottom
        dist_to_bottom = _clip(raw / SCREEN_HEIGHT, -1.0, 1.0)

    velocity_norm = _clip(state.player_vy / MAX_VELOCITY, -1.0, 1.0)

    y_norm = _clip(state.player_y / float(SCREEN_HEIGHT), 0.0, 1.0)

    return [horiz_dist, dist_to_top, dist_to_bottom, velocity_norm, y_norm]
