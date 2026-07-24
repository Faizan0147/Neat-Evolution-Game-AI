"""
Entry point for the NEAT Flappy Bird project.

Modes
-----
    python main.py                        → pygame window, bird falls with random actions
    python main.py --headless             → headless benchmark (150 episodes)
    python main.py --headless --episodes 500
    python main.py --headless --generations 500   → (used in Week 3+ with population)

Week 1 goal: open the pygame window, see the bird fall under gravity,
             die at the first pipe. Then verify headless runs 150 episodes
             in under 10 seconds.
"""

from __future__ import annotations

import argparse
import random
import sys
import time

from game.constants import FPS
from game.engine import GameEngine
from game.headless import GameHeadless, fitness_from_game
from game.sensors import extract_inputs


# ── Dummy network for testing before NEAT is wired up ─────────────────────────

class RandomNetwork:
    """
    A dummy 'network' that outputs a random flap decision.

    Used in Week 1 to verify the game loop without any real NEAT code.
    Implements the Network protocol expected by GameHeadless.run_episode().
    """

    def evaluate(self, inputs: list[float]) -> list[float]:  # noqa: ARG002
        # 30% chance to flap each frame — roughly playable randomness
        return [random.random()]


# ── Visual demo ───────────────────────────────────────────────────────────────

def run_visual_demo(max_seconds: float = 30.0) -> None:
    """
    Open a pygame window and run until the bird dies or time runs out.

    The bird uses a random network so it will almost certainly die quickly
    in Week 1. This is expected — it just proves the renderer works.
    """
    import pygame  # noqa: PLC0415  (local import — only needed in visual mode)

    game = GameEngine(headless=False)
    network = RandomNetwork()
    deadline = int(max_seconds * FPS)

    print("Flappy Bird visual demo — close the window or wait for bird to die.")
    print("Week 1: bird will die quickly. That's expected!\n")

    running = True
    for frame in range(deadline):
        # Handle pygame events so the window stays responsive
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game.set_action(flap=True)

        if not running or not game.is_alive():
            break

        # Get sensor inputs, decide action, step, draw
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


# ── Headless benchmark ────────────────────────────────────────────────────────

def run_headless_benchmark(episodes: int = 150) -> None:
    """
    Run N headless episodes with a random network and print timing stats.

    Week 1 success criterion: 150 episodes in under 10 seconds.
    """
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
        print("  [FAIL] Performance target MISSED -- check game/headless.py max_frames")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="NEAT Flappy Bird — Week 1 demo")
    p.add_argument("--headless", action="store_true", help="Skip pygame, run benchmarks only")
    p.add_argument("--episodes", type=int, default=150, help="Episodes for headless benchmark")
    p.add_argument("--generations", type=int, default=0, help="(Week 3+) NEAT generations to run")
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
