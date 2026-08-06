from __future__ import annotations

import argparse
import random
import sys
import time

from game.constants import FPS
from game.engine import GameEngine
from game.headless import GameHeadless, fitness_from_game
from game.sensors import extract_inputs


class RandomNetwork:
    def evaluate(self, inputs: list[float]) -> list[float]:  # noqa: ARG002
        return [random.random()]


def run_visual_demo(max_seconds: float = 30.0) -> None:
    import pygame  # noqa: PLC0415

    game = GameEngine(headless=False)
    network = RandomNetwork()
    deadline = int(max_seconds * FPS)

    print("Flappy Bird visual demo — close the window or wait for bird to die.\n")

    running = True
    for frame in range(deadline):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game.set_action(flap=True)

        if not running or not game.is_alive():
            break

        state = game.get_state()
        inputs = extract_inputs(state)
        outputs = network.evaluate(inputs)
        flap = outputs[0] > 0.5
        game.set_action(flap=flap)
        game.update()
        game.render()

    pipes = game.get_score()
    frames = game.get_time_alive()
    fitness = fitness_from_game(pipes, frames)
    print(f"Episode ended — pipes cleared: {pipes}, frames: {frames}, fitness: {fitness:.2f}")
    pygame.quit()


def run_headless_benchmark(episodes: int = 150) -> None:
    runner = GameHeadless()
    network = RandomNetwork()

    print(f"Running {episodes} headless episodes …")
    start = time.perf_counter()

    scores: list[float] = []
    for _ in range(episodes):
        fitness = runner.run_episode(network)
        scores.append(fitness)

    elapsed = time.perf_counter() - start
    avg = sum(scores) / len(scores)
    best = max(scores)

    print(f"  Done in {elapsed:.3f}s  ({elapsed / episodes * 1000:.1f} ms/episode)")
    print(f"  Avg fitness : {avg:.4f}")
    print(f"  Best fitness: {best:.4f}")

    if elapsed < 10.0:
        print("  [PASS] Performance target MET  (< 10 s for 150 episodes)")
    else:
        print("  [FAIL] Performance target MISSED")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="NEAT Flappy Bird")
    p.add_argument("--headless", action="store_true")
    p.add_argument("--episodes", type=int, default=150)
    p.add_argument("--generations", type=int, default=0)
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.headless:
        run_headless_benchmark(args.episodes)
    else:
        run_visual_demo()

    return 0


if __name__ == "__main__":
    sys.exit(main())
