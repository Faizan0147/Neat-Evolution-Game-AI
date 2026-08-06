# NEAT Flappy Bird — Neural Evolution Game AI

> A from-scratch implementation of NeuroEvolution of Augmenting Topologies (NEAT) evolved to play a custom Flappy Bird clone. No ML libraries. Pure Python. Built in 4 weeks / 8 sessions.

![Status](https://img.shields.io/badge/status-in%20progress-yellow) ![Python](https://img.shields.io/badge/python-3.9%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## What is this?

This project implements NEAT — Kenneth Stanley & Risto Miikkulainen's foundational neuroevolution algorithm (2002) — **completely from first principles**. You'll find:

- **Genome representation** with innovation-numbered connections
- **Speciation** by compatibility distance (prevents premature convergence)
- **Adaptive topology evolution** (networks grow new nodes and connections via mutation, starting minimal)
- **Crossover** aligned by innovation number
- **Fitness-proportional reproduction** with explicit fitness sharing

All wired to evolve a population of neural networks that learn to play a custom-built **Flappy Bird** clone through natural selection alone — no supervision, no backpropagation, no gradient descent.

## Why build NEAT from scratch?

- **Understand the algorithm**, not just call a library function
- **Optimize for the specific game** (no generic ML framework overhead)
- **Learn how networks grow** (adding nodes/connections is inherently interesting)
- **SEE evolution happen** in real time with a live visualizer

## Project Structure

```
neat-flappy/
├── game/
│   ├── __init__.py
│   ├── constants.py        # All magic numbers (screen size, gravity, pipe speed, etc.)
│   ├── engine.py            # GameEngine class — physics, collisions, render
│   ├── sensors.py           # extract_inputs(state) → list[float]
│   └── headless.py          # GameHeadless.run_episode(network) → float
├── neat/
│   ├── __init__.py
│   ├── config.py             # NEATConfig dataclass
│   ├── innovation.py         # InnovationTracker singleton
│   ├── genome.py             # NodeGene, ConnectionGene, Genome
│   ├── network.py            # NeuralNetwork (topological sort + feedforward)
│   ├── species.py            # Species + compatibility_distance + Speciation
│   └── population.py         # Population + generation loop
├── visualizer/
│   ├── __init__.py
│   ├── stats.py               # GenerationStats, StatsHistory
│   ├── network_viz.py         # draw neural net topology on pygame surface
│   └── main_viz.py            # full 4-panel pygame window
├── tests/
│   ├── conftest.py            # shared fixtures, resets InnovationTracker
│   ├── test_week1.py
│   ├── test_week2.py
│   ├── test_week3.py
│   └── test_week4.py
├── docs/
│   ├── 02_NEAT_FLAPPY_BIRD.md   # the complete plan (source of truth)
│   ├── NEAT_COPILOT_GUIDE.md    # full Antigravity prompts, session by session
│   ├── COPILOT_WORKFLOW.md      # how to work with Antigravity effectively
│   ├── DEVOPS_GUIDE.md          # CI/CD, Docker, GitHub Actions
│   └── QUICK_REFERENCE.md
├── .github/workflows/
│   └── ci.yml
├── Makefile
├── pyproject.toml
├── .pre-commit-config.yaml
└── main.py
```

## Quick Start

### Prerequisites

- Python 3.9+
- pygame (for rendering and visualization)
- Antigravity (or any editor) — the build plan is written as Antigravity prompts, but works with any AI pair-programmer

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/neat-flappy.git
cd neat-flappy
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
pre-commit install
```

### Run Evolution

```bash
make run        # python main.py — opens the live 4-panel visualizer
make headless    # python main.py --headless --generations 500 — no rendering, much faster
```

This will:
1. Initialize a population of 150 random neural networks (minimal topology — direct input→output connections only)
2. Run generations of evolution against the Flappy Bird engine
3. Display a live visualizer (in `make run` mode) showing:
   - The best agent playing Flappy Bird
   - Its neural network topology
   - Fitness curves and species stats

### Tuning Hyperparameters

Edit `NEATConfig` in `main.py` (see `neat/config.py`):

```python
config = NEATConfig(
    pop_size=150,               # Population size
    c1=1.0,                     # excess gene weight
    c2=1.0,                     # disjoint gene weight
    c3=0.4,                     # weight-difference weight
    dt=3.0,                     # speciation threshold (lower = more species)
    weight_mutate_rate=0.8,
    weight_perturb_rate=0.9,
    weight_perturb_power=0.1,
    add_node_rate=0.03,         # probability of adding a node mutation
    add_conn_rate=0.05,         # probability of adding a connection mutation
    max_stagnation=20,          # kill species with no improvement for N gens
)
```

See `docs/02_NEAT_FLAPPY_BIRD.md` and `docs/QUICK_REFERENCE.md` for the full tuning reference.

## How It Works

### 1. Genome Representation

Each network is encoded as a genome — 5 inputs, 1 output, growing hidden structure:

```python
genome.nodes = {
    0: NodeGene(id=0, type="input"),   # horizontal distance to next pipe
    1: NodeGene(id=1, type="input"),   # vertical distance to top pipe
    2: NodeGene(id=2, type="input"),   # vertical distance to bottom pipe
    3: NodeGene(id=3, type="input"),   # player Y velocity
    4: NodeGene(id=4, type="input"),   # player Y position
    10: NodeGene(id=10, type="hidden", activation="tanh"),   # added by mutation
    20: NodeGene(id=20, type="output", activation="sigmoid"),  # flap
}

genome.connections = {
    0: ConnectionGene(in_node=0, out_node=20, weight=0.5, innovation=1),
    1: ConnectionGene(in_node=1, out_node=20, weight=-0.3, innovation=2),
    # ...
}
```

### 2. Neural Network Interface

```
Inputs (5 values, normalised to [-1, 1] or [0, 1]):
  1. Horizontal distance to next pipe pair       [0, 1]
  2. Vertical distance from player to top pipe   [-1, 1]  (negative = above gap)
  3. Vertical distance from player to bottom pipe [-1, 1]
  4. Player Y velocity                           [-1, 1]
  5. Player Y position                           [0, 1]

Output (1 value, sigmoid):
  1. Flap if > 0.5, do nothing otherwise
```

```python
network = NeuralNetwork(genome)
output = network.evaluate(inputs)   # [0.73] → flap
```

### 3. Fitness Function

```python
fitness = (pipes_cleared ** 3) + (time_alive * 0.01)
# Cubic pipes: going from 1 pipe to 5 pipes is 125x better than 1 pipe
# This creates massive pressure to actually clear pipes.
# The small time bonus prevents instant-death from scoring the same as
# surviving a while before dying at pipe 1.
```

### 4. Evolution Loop (each generation)

1. **Evaluate:** Run every genome through the game, record fitness
2. **Speciate:** Group genomes using compatibility distance δ
3. **Fitness sharing:** Divide each genome's fitness by species size (prevents one species from dominating)
4. **Cull:** Remove bottom 50% per species
5. **Reproduce:** Allocate offspring proportional to avg adjusted fitness — 75% crossover + mutation, 25% mutation only
6. **Elitism:** Copy each species champion unchanged to the next generation
7. **Stagnation check:** Kill species with no improvement for `max_stagnation` generations
8. **Update reps:** Pick a random member as the new species representative
9. **Reset innovation:** `InnovationTracker.reset()` for the next generation

### 5. Mutation Operators

- **Perturb weights** (80%): gaussian noise on random connections
- **Reset weight** (20% of weight mutations): uniform random new value
- **Add connection** (5%): new synapse between two existing nodes (rejects cycles)
- **Add node** (3%): split an existing connection, insert new hidden node
- **Toggle connection** (rare): enable/disable a connection

### 6. Crossover (75% of reproduction)

Align parents by innovation number, assuming parent1 is fitter:
- **Matching genes:** randomly pick from either parent
- **Excess/disjoint:** inherit from the fitter parent only
- **Disabled genes:** 75% chance to stay disabled in the child

### 7. Speciation (prevent premature convergence)

Compatibility distance between two genomes:

```
δ = (c1·E + c2·D) / N + c3·W̄

where:
  E = excess genes
  D = disjoint genes
  N = max(genes in parent1, genes in parent2)
  W̄ = average weight difference of matching connections
  c1, c2, c3 = tunable weights
```

If δ < dt (default 3.0), the genomes belong to the same species.

## Expected Progression

```
Gen 1-10:    all birds die immediately (score ~0)
Gen 10-50:   some birds start clearing 1-2 pipes
Gen 50-150:  consistent 3-5 pipe clears, population stabilising
Gen 150-200: best agent clearing 10+ pipes, network diagram settling
```

If agents plateau early, increase `add_node_rate` to 0.05. If there are too many species (>15), increase `dt` to 4.0. If species are dying too fast, increase `max_stagnation` to 30. Full tuning table in `docs/02_NEAT_FLAPPY_BIRD.md`.

## Building with Antigravity

See `docs/NEAT_COPILOT_GUIDE.md` for the complete session-by-session build plan (8 sessions across 4 weeks), and `docs/COPILOT_WORKFLOW.md` for how to work with Antigravity's AI chat effectively.

**Recommended approach:**
1. Keep `docs/NEAT_COPILOT_GUIDE.md` open alongside your code
2. Copy one session's prompts into Antigravity Chat per sitting
3. Ask Antigravity to **explain** the tricky bits (innovation numbers, cycle detection, crossover alignment) — don't just accept the code
4. Review and refine generated code before committing

## Testing

```bash
make test        # pytest
make check        # ruff + black --check + mypy + pytest
```

Individual tests per week:
```bash
python -m pytest tests/test_week1.py -v   # Game engine
python -m pytest tests/test_week2.py -v   # Genomes and networks
python -m pytest tests/test_week3.py -v   # Evolution loop
python -m pytest tests/test_week4.py -v   # Visualizer / integration
```

## Key Implementation Details

### Innovation Number Tracking

The `InnovationTracker` is a global singleton that ensures two mutations adding the same connection in the same generation receive the same innovation number. This is **critical** for crossover alignment.

```python
InnovationTracker.reset()   # Call ONCE per generation, before any mutations
                              # Do NOT reset the counter — innovation numbers stay globally unique
innovation_id = InnovationTracker.get_innovation(in_node=5, out_node=10)
# A second call with the same args in the same generation returns the same ID
```

### Topological Sort

```python
# Valid order: inputs → hidden (sorted by depth) → outputs
# No recurrent connections in this implementation — cycles are rejected at
# add_connection() time, so the topological sort never has to break a cycle.
layers = network._topological_sort()
```

### Fitness Function Design

The fitness function is the **most critical hyperparameter** — it shapes the entire evolutionary landscape.

```python
fitness = (pipes_cleared ** 3) + (time_alive * 0.01)
```

- Cubic reward on pipes creates strong pressure to actually clear pipes, not just survive
- The small time bonus stops instant-death scoring the same as dying at pipe 1

## Visualizer Layout

```
+------------------------+------------------+
|                        |  Gen: 47         |
|   FLAPPY BIRD          |  Best: 12847.3   |
|   (best agent live)    |  Avg:  892.1     |
|                        |  Species: 8      |
|                        |                  |
+------------------------+  [fitness curve] |
|                        |                  |
|   NETWORK GRAPH        |                  |
|   (best agent's net)   |                  |
|                        |                  |
+------------------------+------------------+
```

**Controls:** Space = pause/resume, R = reset, +/- = speed up/slow down, arrow keys = inspect agents.

## Known Limitations

- **No recurrent connections:** pure feedforward only (extensions exist for LSTM-like recurrence)
- **Fixed topology inputs/outputs:** NEAT only evolves hidden structure (5 in, 1 out)
- **Single game:** built and tuned specifically for Flappy Bird
- **Single-objective:** only optimizes one fitness value (no multi-objective like NSGA-II)

## Further Reading

- **Original NEAT paper:** Stanley & Miikkulainen, "Evolving Neural Networks through Augmenting Topologies" (2002)
- **HyperNEAT:** extends NEAT to evolve substrate geometry (cool but complex)

## Contributing

This is a learning project, but ideas for extending it once the core is working:
- Swap in a different game (dino runner, snake) by writing new `sensors.py` + `constants.py`
- Enhanced visualizers (better network graphs, 3D projection)
- Recurrent networks (LSTM-like nodes)
- Multi-objective fitness (NSGA-II variant)

## License

MIT — use freely, credit appreciated.

## Author

2nd-year Computer Engineering student, Pakistan. Built as part of a 4P-Sprint (4 projects in 4 weeks, 25% effort each week) alongside an ongoing AI/ML internship.

---

**Next steps:**

1. Read `docs/02_NEAT_FLAPPY_BIRD.md` — the full plan
2. Read `docs/NEAT_COPILOT_GUIDE.md` — Session 1 prompts
3. `pip install -e ".[dev]" && pre-commit install`
4. `make run` once the game engine exists, to see evolution in action
5. Tune hyperparameters and watch agents improve

Enjoy! 🚀
