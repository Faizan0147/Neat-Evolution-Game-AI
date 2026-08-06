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


@dataclass
class PipePair:
    x: float
    gap_y: float
    passed: bool = False

    @property
    def gap_bottom(self) -> float:
        return self.gap_y + PIPE_GAP

    def top_rect(self) -> tuple[float, float, float, float]:
        return (self.x, 0.0, float(PIPE_WIDTH), self.gap_y)

    def bottom_rect(self) -> tuple[float, float, float, float]:
        return (
            self.x,
            self.gap_bottom,
            float(PIPE_WIDTH),
            float(SCREEN_HEIGHT) - self.gap_bottom,
        )


@dataclass
class GameState:
    player_x: float
    player_y: float
    player_vy: float
    pipes: list[PipePair]
    pipes_cleared: int
    frames_alive: int
    alive: bool


@dataclass
class _Player:
    x: float = float(SCREEN_WIDTH) * 0.25
    y: float = float(SCREEN_HEIGHT) * 0.5
    vy: float = 0.0


class GameEngine:
    def __init__(self, headless: bool = False) -> None:
        self.headless = headless

        self._player = _Player()
        self._pipes: list[PipePair] = []
        self._pipes_cleared: int = 0
        self._frames_alive: int = 0
        self._alive: bool = True
        self._flap_requested: bool = False

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

        self._spawn_initial_pipes()

    def set_action(self, flap: bool) -> None:
        if flap:
            self._flap_requested = True

    def update(self) -> None:
        if not self._alive:
            return

        dt = 1.0 / FPS
        self._frames_alive += 1

        if self._flap_requested:
            self._player.vy = FLAP_STRENGTH
            self._flap_requested = False

        self._player.vy += GRAVITY
        self._player.y += self._player.vy

        for pipe in self._pipes:
            pipe.x -= PIPE_SPEED

        self._pipes = [p for p in self._pipes if p.x + PIPE_WIDTH > -50]
        self._maybe_spawn_pipe()

        player_cx = self._player.x
        for pipe in self._pipes:
            if not pipe.passed and pipe.x + PIPE_WIDTH < player_cx:
                pipe.passed = True
                self._pipes_cleared += 1

        self._check_collisions()

    def render(self) -> None:
        if self.headless or self._screen is None or self._pygame is None:
            return

        pg = self._pygame
        screen = self._screen

        screen.fill(COLOR_SKY)

        ground_h = 40
        pg.draw.rect(
            screen,
            COLOR_GROUND,
            (0, SCREEN_HEIGHT - ground_h, SCREEN_WIDTH, ground_h),
        )

        for pipe in self._pipes:
            top_x, top_y, top_w, top_h = pipe.top_rect()
            bot_x, bot_y, bot_w, bot_h = pipe.bottom_rect()

            pg.draw.rect(screen, COLOR_PIPE, (int(top_x), int(top_y), int(top_w), int(top_h)))
            pg.draw.rect(screen, COLOR_PIPE_OUTLINE, (int(top_x), int(top_y), int(top_w), int(top_h)), 2)
            pg.draw.rect(screen, COLOR_PIPE, (int(bot_x), int(bot_y), int(bot_w), int(bot_h)))
            pg.draw.rect(screen, COLOR_PIPE_OUTLINE, (int(bot_x), int(bot_y), int(bot_w), int(bot_h)), 2)

        px = int(self._player.x)
        py = int(self._player.y)
        pg.draw.circle(screen, COLOR_PLAYER, (px, py), PLAYER_RADIUS)
        pg.draw.circle(screen, COLOR_PLAYER_OUTLINE, (px, py), PLAYER_RADIUS, 2)

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
        return self._alive

    def get_score(self) -> int:
        return self._pipes_cleared

    def get_time_alive(self) -> int:
        return self._frames_alive

    def reset(self) -> None:
        self._player = _Player()
        self._pipes = []
        self._pipes_cleared = 0
        self._frames_alive = 0
        self._alive = True
        self._flap_requested = False
        self._spawn_initial_pipes()

    def _spawn_initial_pipes(self) -> None:
        x = float(PIPE_FIRST_SPAWN_X)
        for _ in range(3):
            self._pipes.append(self._create_pipe(x))
            x += PIPE_SPACING

    def _maybe_spawn_pipe(self) -> None:
        if not self._pipes:
            self._pipes.append(self._create_pipe(float(SCREEN_WIDTH + PIPE_WIDTH)))
            return

        rightmost_x = max(p.x for p in self._pipes)
        if rightmost_x < SCREEN_WIDTH + PIPE_SPACING - PIPE_SPEED:
            self._pipes.append(self._create_pipe(rightmost_x + PIPE_SPACING))

    @staticmethod
    def _create_pipe(x: float) -> PipePair:
        min_gap_y = PLAYER_RADIUS * 4
        max_gap_y = SCREEN_HEIGHT - PIPE_GAP - PLAYER_RADIUS * 4
        gap_y = float(random.randint(min_gap_y, max(min_gap_y + 1, max_gap_y)))
        return PipePair(x=x, gap_y=gap_y)

    def _check_collisions(self) -> None:
        px = self._player.x
        py = self._player.y
        r = float(PLAYER_RADIUS)

        if py - r <= 0:
            self._alive = False
            return

        if py + r >= SCREEN_HEIGHT - 5:
            self._alive = False
            return

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
        closest_x = max(rx, min(cx, rx + rw))
        closest_y = max(ry, min(cy, ry + rh))

        dx = cx - closest_x
        dy = cy - closest_y
        return (dx * dx + dy * dy) < (r * r)
