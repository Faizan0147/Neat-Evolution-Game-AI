"""
Sensor extraction for the Flappy Bird NEAT neural network.

extract_inputs(state) → list[float]

Returns exactly 5 normalised float values.  All values are clipped to their
stated ranges so the neural network always receives valid inputs even at the
extremes (ceiling, floor, no pipes visible).

Inputs
------
1. Horizontal distance to the next pipe pair, normalised to [0, 1]
   - 0.0  = pipe is right at the player
   - 1.0  = pipe is a full screen-width away

2. Vertical distance from player centre to TOP of the gap, normalised to [-1, 1]
   - Negative  = player is ABOVE the top of the gap (needs to drop)
   - Positive  = player is BELOW the top of the gap

3. Vertical distance from player centre to BOTTOM of the gap, normalised [-1, 1]
   - Negative  = player is ABOVE the bottom of the gap (safe)
   - Positive  = player is BELOW the bottom of the gap (crashed)

4. Player Y velocity normalised to [-1, 1]
   - Negative  = moving upward
   - Positive  = moving downward (falling)

5. Player Y position normalised to [0, 1]
   - 0.0 = at the ceiling
   - 1.0 = at the floor
"""

from __future__ import annotations

from game.constants import MAX_PIPE_DISTANCE, MAX_VELOCITY, SCREEN_HEIGHT
from game.engine import GameState, PipePair


def _next_pipe(state: GameState) -> PipePair | None:
    """
    Return the first pipe pair that the player has NOT yet passed.

    'Not yet passed' means the right edge of the pipe is still ahead of or
    level with the player's x position.  We use the right edge so the sensor
    still sees the pipe during the moment the bird is inside the gap.
    """
    ahead = [
        pipe
        for pipe in state.pipes
        if not pipe.passed or (pipe.x + 80 >= state.player_x)  # 80 = PIPE_WIDTH
    ]
    if not ahead:
        return None
    return min(ahead, key=lambda p: p.x)


def _clip(value: float, lo: float, hi: float) -> float:
    """Clamp value to [lo, hi]."""
    return max(lo, min(value, hi))


def extract_inputs(state: GameState) -> list[float]:
    """
    Return 5 normalised sensor values describing the current game state.

    Parameters
    ----------
    state : GameState
        Snapshot returned by GameEngine.get_state()

    Returns
    -------
    list[float]
        [horiz_dist, dist_to_top, dist_to_bottom, velocity_norm, y_norm]
    """
    next_pipe = _next_pipe(state)

    # ── Input 1: Horizontal distance to next pipe ─────────────────────────────
    if next_pipe is None:
        horiz_dist = 1.0  # no pipe visible → treat as maximum distance
    else:
        raw = next_pipe.x - state.player_x
        horiz_dist = _clip(raw / MAX_PIPE_DISTANCE, 0.0, 1.0)

    # ── Input 2: Vertical distance to top of gap ──────────────────────────────
    # Negative  → player is above the gap top (needs to descend)
    # Positive  → player is below the gap top (still in safe zone above, or crashed)
    if next_pipe is None:
        dist_to_top = 0.0
    else:
        raw = state.player_y - next_pipe.gap_y
        dist_to_top = _clip(raw / SCREEN_HEIGHT, -1.0, 1.0)

    # ── Input 3: Vertical distance to bottom of gap ───────────────────────────
    # Negative  → player is above the gap bottom (safe)
    # Positive  → player is below the gap bottom (should not happen → crash)
    if next_pipe is None:
        dist_to_bottom = 0.0
    else:
        raw = state.player_y - next_pipe.gap_bottom
        dist_to_bottom = _clip(raw / SCREEN_HEIGHT, -1.0, 1.0)

    # ── Input 4: Player Y velocity ────────────────────────────────────────────
    velocity_norm = _clip(state.player_vy / MAX_VELOCITY, -1.0, 1.0)

    # ── Input 5: Player Y position ────────────────────────────────────────────
    y_norm = _clip(state.player_y / float(SCREEN_HEIGHT), 0.0, 1.0)

    return [horiz_dist, dist_to_top, dist_to_bottom, velocity_norm, y_norm]
