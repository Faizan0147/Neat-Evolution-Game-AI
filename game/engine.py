"""
Flappy Bird game engine with optional pygame rendering.

GameEngine is the single source of truth for all game logic:
    - Physics:     gravity + flap impulse on the player circle
    - Pipes:       spawning, scrolling, gap placement, pipe-cleared counting
    - Collision:   player vs pipe columns, ceiling, floor
    - Rendering:   optional pygame draw calls (skipped in headless mode)

Public API
----------
    engine = GameEngine(headless=True)
    engine.set_action(flap=True)
    engine.update()          # advance one frame (uses internal FPS dt)
    state = engine.get_state()
    alive = engine.is_alive()
    score = engine.get_score()   # pipes cleared
    time  = engine.get_time_alive()
    engine.reset()
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from game.constants import (
    COLOR_GROUND,
    COLOR_PIPE,
    COLOR_PIPE_OUTLINE,
    COLOR_PLAYER,
    COLOR_PLAYER_OUTLINE,
    COLOR_SKY,
    COLOR_TEXT,
    FPS,
    FLAP_STRENGTH,
    GRAVITY,
    PIPE_FIRST_SPAWN_X,
    PIPE_GAP,
    PIPE_SPACING,
    PIPE_SPEED,
    PIPE_WIDTH,
    PLAYER_RADIUS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)

if TYPE_CHECKING:
    import pygame


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclass
class PipePair:
    """A pair of upper and lower pipe columns sharing the same x position."""

    x: float
    gap_y: float      # y-coordinate of the TOP of the gap opening
    passed: bool = False  # set to True once the player clears this pair

    @property
    def gap_bottom(self) -> float:
        """Y coordinate of the bottom of the gap opening."""
        return self.gap_y + PIPE_GAP

    def top_rect(self) -> tuple[float, float, float, float]:
        """(x, y, w, h) of the top pipe column (extends from ceiling to gap_y)."""
        return (self.x, 0.0, float(PIPE_WIDTH), self.gap_y)

    def bottom_rect(self) -> tuple[float, float, float, float]:
        """(x, y, w, h) of the bottom pipe column (extends from gap_bottom to floor)."""
        return (
            self.x,
            self.gap_bottom,
            float(PIPE_WIDTH),
            float(SCREEN_HEIGHT) - self.gap_bottom,
        )


@dataclass
class GameState:
    """
    Snapshot of the game at one frame.  Consumed by sensors and tests.

    player_x / player_y   : centre-point of the circular player (pixels)
    player_vy              : vertical velocity (positive = downward)
    pipes                  : list of all on-screen PipePair objects
    pipes_cleared          : how many pipe pairs the player has passed
    frames_alive           : total frames the player has survived
    alive                  : False once a collision or boundary is hit
    """

    player_x: float
    player_y: float
    player_vy: float
    pipes: list[PipePair]
    pipes_cleared: int
    frames_alive: int
    alive: bool


# ── Internal player state ──────────────────────────────────────────────────────

@dataclass
class _Player:
    x: float = float(SCREEN_WIDTH) * 0.25  # fixed horizontal position
    y: float = float(SCREEN_HEIGHT) * 0.5   # start vertically centred
    vy: float = 0.0


# ── Main engine ───────────────────────────────────────────────────────────────

class GameEngine:
    """
    Flappy Bird game engine.

    Parameters
    ----------
    headless : bool
        When True, no pygame window is created and render() is a no-op.
        Always True during NEAT training for maximum speed.
    """

    def __init__(self, headless: bool = False) -> None:
        self.headless = headless

        # Mutable game state
        self._player = _Player()
        self._pipes: list[PipePair] = []
        self._pipes_cleared: int = 0
        self._frames_alive: int = 0
        self._alive: bool = True
        self._flap_requested: bool = False

        # Pygame handles (None in headless mode)
        self._screen: pygame.Surface | None = None  # type: ignore[name-defined]
        self._clock: pygame.time.Clock | None = None  # type: ignore[name-defined]
        self._pygame = None
        self._font = None

        if not headless:
            import pygame as pg

            self._pygame = pg
            pg.init()
            self._screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pg.display.set_caption("NEAT Flappy Bird")
            self._clock = pg.time.Clock()
            self._font = pg.font.SysFont("monospace", 24, bold=True)

        # Spawn initial pipes
        self._spawn_initial_pipes()

    # ── Public API ────────────────────────────────────────────────────────────

    def set_action(self, flap: bool) -> None:
        """Queue a flap impulse for the next update() call."""
        if flap:
            self._flap_requested = True

    def update(self) -> None:
        """
        Advance the simulation by exactly one frame (1/FPS seconds).

        Order of operations per frame:
          1. Apply flap impulse (if requested)
          2. Apply gravity to vy, then move player vertically
          3. Scroll all pipes left
          4. Spawn new pipe if needed
          5. Check pipe-clear events (score update)
          6. Check collisions (pipe columns, ceiling, floor)
        """
        if not self._alive:
            return

        dt = 1.0 / FPS  # fixed timestep — physics are frame-rate independent
        self._frames_alive += 1

        # 1. Flap
        if self._flap_requested:
            self._player.vy = FLAP_STRENGTH
            self._flap_requested = False

        # 2. Gravity + vertical movement
        self._player.vy += GRAVITY
        self._player.y += self._player.vy

        # 3. Scroll pipes
        for pipe in self._pipes:
            pipe.x -= PIPE_SPEED

        # 4. Remove off-screen pipes and spawn replacements
        self._pipes = [p for p in self._pipes if p.x + PIPE_WIDTH > -50]
        self._maybe_spawn_pipe()

        # 5. Score: count pipes the player has passed
        player_cx = self._player.x
        for pipe in self._pipes:
            if not pipe.passed and pipe.x + PIPE_WIDTH < player_cx:
                pipe.passed = True
                self._pipes_cleared += 1

        # 6. Collision detection
        self._check_collisions()

    def render(self) -> None:
        """Draw the current frame. No-op when headless=True."""
        if self.headless or self._screen is None or self._pygame is None:
            return

        pg = self._pygame
        screen = self._screen

        # Background sky
        screen.fill(COLOR_SKY)

        # Ground strip
        ground_h = 40
        pg.draw.rect(
            screen,
            COLOR_GROUND,
            (0, SCREEN_HEIGHT - ground_h, SCREEN_WIDTH, ground_h),
        )

        # Pipes
        for pipe in self._pipes:
            top_x, top_y, top_w, top_h = pipe.top_rect()
            bot_x, bot_y, bot_w, bot_h = pipe.bottom_rect()

            pg.draw.rect(screen, COLOR_PIPE, (int(top_x), int(top_y), int(top_w), int(top_h)))
            pg.draw.rect(screen, COLOR_PIPE_OUTLINE, (int(top_x), int(top_y), int(top_w), int(top_h)), 2)
            pg.draw.rect(screen, COLOR_PIPE, (int(bot_x), int(bot_y), int(bot_w), int(bot_h)))
            pg.draw.rect(screen, COLOR_PIPE_OUTLINE, (int(bot_x), int(bot_y), int(bot_w), int(bot_h)), 2)

        # Player circle
        px = int(self._player.x)
        py = int(self._player.y)
        pg.draw.circle(screen, COLOR_PLAYER, (px, py), PLAYER_RADIUS)
        pg.draw.circle(screen, COLOR_PLAYER_OUTLINE, (px, py), PLAYER_RADIUS, 2)

        # HUD
        if self._font is not None:
            score_surf = self._font.render(
                f"Pipes: {self._pipes_cleared}  Frames: {self._frames_alive}",
                True,
                COLOR_TEXT,
            )
            screen.blit(score_surf, (10, 10))

        pg.display.flip()
        if self._clock is not None:
            self._clock.tick(FPS)

    def get_state(self) -> GameState:
        """Return a sensor-friendly snapshot of the current frame."""
        return GameState(
            player_x=self._player.x,
            player_y=self._player.y,
            player_vy=self._player.vy,
            pipes=list(self._pipes),
            pipes_cleared=self._pipes_cleared,
            frames_alive=self._frames_alive,
            alive=self._alive,
        )

    def is_alive(self) -> bool:
        """Whether the player is still alive."""
        return self._alive

    def get_score(self) -> int:
        """Return the number of pipe pairs cleared (primary score)."""
        return self._pipes_cleared

    def get_time_alive(self) -> int:
        """Return total frames survived."""
        return self._frames_alive

    def reset(self) -> None:
        """Reset game to its initial state for a fresh episode."""
        self._player = _Player()
        self._pipes = []
        self._pipes_cleared = 0
        self._frames_alive = 0
        self._alive = True
        self._flap_requested = False
        self._spawn_initial_pipes()

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _spawn_initial_pipes(self) -> None:
        """Pre-populate the pipe list so the first pipe is already on screen."""
        x = float(PIPE_FIRST_SPAWN_X)
        for _ in range(3):
            self._pipes.append(self._create_pipe(x))
            x += PIPE_SPACING

    def _maybe_spawn_pipe(self) -> None:
        """Spawn a new pipe if the rightmost existing pipe has scrolled far enough."""
        if not self._pipes:
            self._pipes.append(self._create_pipe(float(SCREEN_WIDTH + PIPE_WIDTH)))
            return

        rightmost_x = max(p.x for p in self._pipes)
        if rightmost_x < SCREEN_WIDTH + PIPE_SPACING - PIPE_SPEED:
            self._pipes.append(self._create_pipe(rightmost_x + PIPE_SPACING))

    @staticmethod
    def _create_pipe(x: float) -> PipePair:
        """
        Create a pipe pair at position x with a random gap position.

        The gap top is constrained so the gap never appears too close
        to the ceiling or floor, giving the player a fair challenge.
        """
        min_gap_y = PLAYER_RADIUS * 4          # at least 4 radii from ceiling
        max_gap_y = SCREEN_HEIGHT - PIPE_GAP - PLAYER_RADIUS * 4  # space above floor
        gap_y = float(random.randint(min_gap_y, max(min_gap_y + 1, max_gap_y)))
        return PipePair(x=x, gap_y=gap_y)

    def _check_collisions(self) -> None:
        """
        Kill the player if:
          - Circle centre hits the ceiling (y - radius <= 0)
          - Circle centre hits the floor   (y + radius >= SCREEN_HEIGHT)
          - Circle overlaps any pipe column rectangle (AABB + circle check)
        """
        px = self._player.x
        py = self._player.y
        r = float(PLAYER_RADIUS)

        # Ceiling
        if py - r <= 0:
            self._alive = False
            return

        # Floor (allow a small buffer so the bird can skim the bottom)
        if py + r >= SCREEN_HEIGHT - 5:
            self._alive = False
            return

        # Pipe collision (AABB between pipe rectangles and bounding box of circle)
        for pipe in self._pipes:
            if self._circle_rect_collision(px, py, r, *pipe.top_rect()):
                self._alive = False
                return
            if self._circle_rect_collision(px, py, r, *pipe.bottom_rect()):
                self._alive = False
                return

    @staticmethod
    def _circle_rect_collision(
        cx: float,
        cy: float,
        r: float,
        rx: float,
        ry: float,
        rw: float,
        rh: float,
    ) -> bool:
        """
        Axis-aligned bounding box vs circle collision.

        Finds the closest point on the rectangle to the circle centre,
        then checks if that distance is less than the circle radius.
        """
        # Clamp circle centre to rect bounds to get closest point
        closest_x = max(rx, min(cx, rx + rw))
        closest_y = max(ry, min(cy, ry + rh))

        dx = cx - closest_x
        dy = cy - closest_y
        return (dx * dx + dy * dy) < (r * r)
