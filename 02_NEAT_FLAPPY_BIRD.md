# Project 2 — NEAT Neural Evolution Game AI (Flappy Bird)
> Complete plan. Paste this file at the start of any new chat for full context.

---

## One-Line Description
Implement NEAT (NeuroEvolution of Augmenting Topologies) completely from scratch
in Python — no ML libraries — to evolve a population of neural networks that
learn to play a custom-built Flappy Bird clone through natural selection alone.

## Who I Am
2nd-year Computer Engineering student, Pakistan. AI/ML internship ongoing.
Languages: Python (primary), C++. IDE: Cursor. Platform: local machine (no GPU
needed — NEAT runs on CPU). Part of 4P-Sprint. Game: Flappy Bird (not dino runner).

---

## Theory (understand this before coding)

### What NEAT Is
Genetic algorithm that evolves both weights AND topology of neural networks.
Published: Kenneth Stanley & Risto Miikkulainen, 2002.
Key difference from standard NNs: no backpropagation, no gradient descent.
Networks are the "genome." Fitness in the game is the selection pressure.
Better networks reproduce more. Worse ones die. Topology grows via mutation.

### Three Core Innovations in NEAT

**1. Historical Markings (Innovation Numbers)**
Problem: how do you cross over two networks with different structures?
```
Parent A: [in→h1→out] [in→out]
Parent B: [in→h2→out] [in→h3→out]
How do you align these for crossover?
```
Solution: every new connection or node gets a globally unique innovation number
assigned at the moment it first appears. Innovation numbers are historical —
they mark *when* a gene appeared, not *where* it is structurally.
Crossover aligns genes by innovation number. Matching genes → random pick.
Excess/disjoint genes → from fitter parent. Works regardless of topology diff.

**2. Speciation (Protecting Innovation)**
Problem: a useful mutation initially performs worse (the network needs time to
adapt to the new structure). In a shared gene pool it gets eliminated too fast.
Solution: group similar genomes into species. Species compete internally first.
A new structure gets time to optimise within its species before competing globally.
Compatibility distance: δ = (c1·E + c2·D)/N + c3·W̄
where E=excess genes, D=disjoint genes, N=max genes, W̄=avg weight diff.
If δ < threshold (dt=3.0), same species.

**3. Complexification (Start Small, Grow)**
Networks start minimal — only direct connections from inputs to outputs.
Nodes and connections are added via mutation over generations.
Complexity only increases when it's beneficial to survival.
Result: the algorithm finds the simplest structure that solves the problem.

### The Evolution Loop (each generation)
```
1. Evaluate fitness    — run every genome through Flappy Bird, record score
2. Speciate            — group genomes by compatibility distance δ
3. Fitness sharing     — divide each genome's fitness by species size
                         (prevents one species dominating the population)
4. Cull                — remove bottom 50% of members per species
5. Reproduce           — allocate offspring proportional to avg adjusted fitness
                         75% crossover + mutation, 25% mutation only
6. Elitism             — copy species champion unchanged to next generation
7. Stagnation check    — kill species with no improvement for max_stagnation gens
8. Update reps         — pick random member as new species representative
9. Reset innovation    — InnovationTracker.reset() for next generation
```

### Crossover (align by innovation number)
```python
# Assume parent1 is fitter
for innov_num in all_innovations:
    if in both parents:   child takes random pick
    if only in parent1:   child inherits (parent1 is fitter, keep its genes)
    if only in parent2:   child skips    (disjoint from weaker parent)
# Disabled genes: 75% chance to stay disabled in child
```

### Mutations
```
Perturb weights    80% probability — gaussian noise on random connections
Reset weight       20% of weight mutations — uniform random new value
Add connection     5% probability — new synapse between two existing nodes
Add node           3% probability — split existing connection, insert new node
Toggle connection  rare — enable/disable a connection
```

### Neural Network Evaluation (feedforward only)
Genome → topological sort of nodes → feedforward pass
No recurrent connections in this implementation.
Hidden activations: tanh. Output activations: sigmoid.
Cycle detection required — add_connection() must reject cycles.

---

## Game: Flappy Bird

### Mechanics
- Gravity pulls player downward each frame
- One action: flap (upward velocity impulse)
- Pipes scroll left, spawn right at random gap heights
- Death: hit pipe, hit ceiling, hit floor
- Score: number of pipes cleared

### Neural Network Interface
```
Inputs (5 values, all normalised to [-1, 1] or [0, 1]):
  1. Horizontal distance to next pipe pair       [0, 1]
  2. Vertical distance from player to top pipe   [-1, 1]  (negative = above gap)
  3. Vertical distance from player to bottom pipe [-1, 1]
  4. Player Y velocity                           [-1, 1]
  5. Player Y position                           [0, 1]

Output (1 value, sigmoid):
  1. Flap if > 0.5, do nothing otherwise
```

### Fitness Function
```python
fitness = (pipes_cleared ** 3) + (time_alive * 0.01)
# Cubic pipes: going from 1 pipe to 5 pipes is 125x better than 1
# This creates massive pressure to actually clear pipes
# Small time bonus prevents instant-death from being equally bad as dying at pipe 1
```

### Game Constants
```python
SCREEN_WIDTH    = 800
SCREEN_HEIGHT   = 600
GRAVITY         = 0.5           # pixels/frame²
FLAP_STRENGTH   = -8            # upward velocity impulse
PIPE_SPEED      = 3             # pixels/frame leftward
PIPE_SPACING    = 250           # horizontal gap between pipe pairs
PIPE_GAP        = 150           # vertical opening height
PIPE_WIDTH      = 80
PLAYER_RADIUS   = 15
FPS             = 60
```

---

## Repository Structure
```
neat-flappy/
├── game/
│   ├── __init__.py
│   ├── constants.py
│   ├── engine.py              GameEngine class
│   ├── sensors.py             extract_inputs(state) → list[float]
│   └── headless.py            GameHeadless.run_episode(network) → float
├── neat/
│   ├── __init__.py
│   ├── config.py              NEATConfig dataclass
│   ├── innovation.py          InnovationTracker singleton
│   ├── genome.py              NodeGene, ConnectionGene, Genome
│   ├── network.py             NeuralNetwork (topological sort + feedforward)
│   ├── species.py             Species + compatibility_distance + Speciation
│   └── population.py          Population + generation loop
├── visualizer/
│   ├── __init__.py
│   ├── stats.py               GenerationStats, StatsHistory
│   ├── network_viz.py         draw neural net topology on pygame surface
│   └── main_viz.py            full 4-panel pygame window
├── tests/
│   ├── conftest.py            shared fixtures, reset InnovationTracker
│   ├── test_week1.py
│   ├── test_week2.py
│   ├── test_week3.py
│   └── test_week4.py
├── docs/
│   ├── 02_NEAT_FLAPPY_BIRD.md     this file
│   ├── NEAT_COPILOT_GUIDE.md      full Cursor prompts per session
│   ├── DEVOPS_GUIDE.md            CI/CD, Docker, GitHub Actions
│   └── QUICK_REFERENCE.md
├── .github/workflows/
│   └── ci.yml
├── Makefile
├── pyproject.toml
├── .pre-commit-config.yaml
└── main.py
```

---

## Core Data Structures
```python
@dataclass
class NodeGene:
    id: int
    type: str        # "input" | "hidden" | "output"
    activation: str  # "tanh" for hidden, "sigmoid" for output

@dataclass
class ConnectionGene:
    in_node: int
    out_node: int
    weight: float
    enabled: bool = True
    innovation: int = 0

@dataclass
class Genome:
    inputs: int               # 5 for Flappy Bird
    outputs: int              # 1 for Flappy Bird
    nodes: dict[int, NodeGene]
    connections: dict[int, ConnectionGene]
    fitness: float = 0.0
    species_id: int = -1

@dataclass
class Species:
    id: int
    representative: Genome
    members: list[Genome]
    best_fitness: float = 0.0
    stagnation_counter: int = 0

@dataclass
class NEATConfig:
    pop_size: int = 150
    c1: float = 1.0
    c2: float = 1.0
    c3: float = 0.4
    dt: float = 3.0
    weight_mutate_rate: float = 0.8
    weight_perturb_rate: float = 0.9
    weight_perturb_power: float = 0.1
    add_node_rate: float = 0.03
    add_conn_rate: float = 0.05
    max_stagnation: int = 20
```

---

## Innovation Tracker (critical — read carefully)
```python
class InnovationTracker:
    _counter: int = 0
    _history: dict[tuple[int,int], int] = {}

    @classmethod
    def get_innovation(cls, in_node: int, out_node: int) -> int:
        key = (in_node, out_node)
        if key not in cls._history:
            cls._counter += 1
            cls._history[key] = cls._counter
        return cls._history[key]

    @classmethod
    def reset(cls) -> None:
        # Call ONCE per generation before any mutations
        # Do NOT reset _counter — innovation numbers must be globally unique
        cls._history = {}
```
Rule: same (in_node, out_node) pair in same generation → same innovation number.
This is what makes crossover alignment work. Do not reset _counter between gens.

---

## Week-by-Week + Session Plan

### Week 1 — Game Engine + DevOps

**Session 1 (~45 min): Repo + DevOps scaffold**
```
Cursor prompts (from NEAT_COPILOT_GUIDE.md):
1. Create pyproject.toml (black, ruff, mypy, pytest, pygame, numpy)
2. Create Makefile (make run, make test, make check, make headless)
3. Create .pre-commit-config.yaml (black, ruff, no-commit-to-main)
4. Create .github/workflows/ci.yml (Python 3.9 + 3.11 matrix)
5. pip install -e ".[dev]" && pre-commit install
6. git commit -m "chore: devops scaffold, CI"
Push → verify GitHub Actions goes green
```

**Session 2 (~60 min): Game engine + sensors + headless**
```
Cursor prompts:
1. Create game/constants.py (all magic numbers above)
2. Create game/engine.py:
   - GameEngine(headless=False)
   - update(dt): gravity, flap physics, pipe movement, collision
   - render(): pygame draw calls (skip if headless)
   - get_state() → GameState dataclass
   - set_action(flap: bool)
   - is_alive() → bool, get_score() → float, reset()
3. Create game/sensors.py:
   - extract_inputs(state: GameState) → list[float]
   - 5 normalised inputs
4. Create game/headless.py:
   - run_episode(network) → float fitness score
   - Must run 150 episodes in under 10 seconds
5. Test: python main.py (game opens, bird falls, dies at first pipe)
Commit: "feat(game): flappy bird engine, sensors, headless mode"
```

---

### Week 2 — Genome + Neural Network

**Session 3 (~50 min): Innovation tracker + genome**
```
Cursor prompts:
1. Create neat/innovation.py (InnovationTracker singleton — see above)
2. Create neat/genome.py:
   - NodeGene, ConnectionGene, Genome dataclasses
   - Genome.copy() → deep copy
   - Genome.add_node(conn) → split connection, new node
   - Genome.add_connection(in_id, out_id) → new connection + cycle check
   - Genome.mutate_weights(rates)
   - Genome.mutate(config: NEATConfig)
   - Initial genome: 5 inputs → 1 output, direct connections

Ask Cursor to EXPLAIN (highlight + Ask):
  "Why does add_node() disable the original connection instead of deleting it?"
  "What is the purpose of cycle detection in add_connection()?"
Commit: "feat(neat): innovation tracker and genome dataclasses"
```

**Session 4 (~50 min): Neural network + integration test**
```
Cursor prompts:
1. Create neat/network.py:
   - NeuralNetwork(genome: Genome)
   - _topological_sort() → list[int] (node processing order)
   - evaluate(inputs: list[float]) → list[float]
   - Input nodes: identity. Hidden: tanh. Output: sigmoid.

Ask Cursor to EXPLAIN:
  "Trace evaluate() with 5 inputs, 1 hidden node, 1 output — show each step"
  "Why does topological sort break if there are cycles?"

2. Wire it all together: genome → network → headless game, print score
3. Run: random network plays flappy bird, score is (usually) 0
Commit: "feat(neat): feedforward neural network from genome"
```

---

### Week 3 — Full NEAT Evolution

**Session 5 (~60 min): Speciation + crossover**
```
Cursor prompts:
1. Create neat/species.py:
   - compatibility_distance(g1, g2, c1, c2, c3) → float
     Align by innovation number. Count E (excess), D (disjoint), W̄ (avg weight diff)
     δ = (c1·E + c2·D)/N + c3·W̄
   - Species dataclass
   - Speciation.speciate(genomes, existing_species, threshold) → list[Species]

Ask Cursor to EXPLAIN:
  "Give me a concrete example of two genomes — show me which genes are
   excess vs disjoint and how the distance is calculated step by step"

2. Add to neat/genome.py:
   - crossover(parent1: Genome, parent2: Genome) → Genome
     (parent1 assumed fitter, or equal fitness → random)

Ask Cursor to EXPLAIN:
  "Why do excess/disjoint genes only come from the fitter parent?"
Commit: "feat(neat): species, compatibility distance, crossover"
```

**Session 6 (~60 min): Population + generation loop**
```
Cursor prompts:
1. Create neat/population.py:
   - NEATConfig dataclass
   - Population(num_inputs=5, num_outputs=1, config)
   - Population.evolve_one_generation(fitness_values: list[float])
     Steps 1-9 from the evolution loop above
   - Population.get_best_genome() → Genome

2. Integration test: 5 full generations, print stats each gen
   Expected: best fitness increases, species count changes
   If fitness stays at 0: fitness function bug — check pipes_cleared count

3. Let it run 20 generations — birds should start clearing 1-2 pipes
Commit: "feat(neat): population and full generation loop"
```

---

### Week 4 — Visualizer + Polish

**Session 7 (~60 min): Stats + network graph + visualizer**
```
Cursor prompts:
1. Create visualizer/stats.py:
   - GenerationStats dataclass
   - StatsHistory.record(population) and history getters

2. Create visualizer/network_viz.py:
   - NetworkVisualizer.draw_network(network, surface)
   - Node positions by layer (x) and rank within layer (y)
   - Nodes: input=blue, hidden=purple, output=green
   - Connections: thickness ∝ |weight|, colour = sign (green/red)

3. Create visualizer/main_viz.py:
   4-panel pygame window:
   - Top-left:     best agent playing Flappy Bird live
   - Bottom-left:  neural network graph of best agent
   - Top-right:    stats panel (gen, best fit, avg fit, species)
   - Bottom-right: fitness curve (best + avg over all generations)
   Controls: Space=pause, R=reset, +/-=speed, arrows=inspect agents

Test: python main.py — window opens, birds visible, network draws
Commit: "feat(visualizer): 4-panel live evolution view"
```

**Session 8 (~45 min): Tuning + demo + release**
```
Run 200 generations. Expected behaviour:
  Gen 1-10:    all birds die immediately (score ~0)
  Gen 10-50:   some start clearing 1-2 pipes
  Gen 50-150:  consistent 3-5 pipe clears, population stabilising
  Gen 150-200: best agent clearing 10+ pipes, network diagram settling

If agents plateau early: increase add_node_rate to 0.05
If too many species (>15): increase dt to 4.0
If species dying too fast: increase max_stagnation to 30

Record a video of the best agent (gen 100+) playing
git tag -a v0.1.0 -m "Working NEAT Flappy Bird"

LinkedIn post structure:
  Hook:      "I wrote the algorithm that made 'AI learns to play X' videos famous."
  What NEAT: Evolves the network structure, not just the weights
  The cool part: Networks start with ZERO hidden neurons and grow complexity
  Visual:    GIF of generation 1 (all dying) vs generation 200 (clearing pipes)
  Technical: Innovation numbers and why they solve the competing conventions problem
  Tags:      #NEAT #NeuroEvolution #MachineLearning #Python #GameAI
```

---

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

## Hyperparameter Tuning Reference
```
Too slow convergence:  increase pop_size (150→200), decrease dt (3.0→2.5)
Too many species:      increase dt (3.0→4.0)
Species collapsing:    increase max_stagnation (20→30)
Agents not improving:  check fitness function — is pipes_cleared updating?
Network not growing:   increase add_node_rate (0.03→0.05)
Fitness oscillating:   reduce weight_perturb_power (0.1→0.05)
```

## DevOps Stack
GitHub Actions CI (every push) + pre-commit (black, ruff) + pytest + Makefile
Semantic versioning: v0.1.0. Conventional commits. Docker optional Week 4.
```
make run       → python main.py (visualizer)
make headless  → python main.py --headless --generations 500
make test      → pytest
make check     → ruff + black --check + mypy + pytest
```

## What You'll Deeply Understand
- NEAT crossover alignment (the competing conventions problem)
- Why speciation protects structural innovation
- Topological sort for feedforward networks (and why cycles break it)
- Fitness sharing: explicit protection against species domination
- Innovation numbers: history as the key to structural alignment
- Why evolution finds simple solutions (minimal network structures)
- The difference between weight evolution and topology evolution

## What I Am NOT Using
No neat-python. No ML libraries. No physics engine. Pure Python + pygame + numpy.

## Context for Agent
- Game: Flappy Bird specifically (NOT dino runner)
- Inputs: 5 (not 8) — horiz dist to pipe, dist to top, dist to bottom, vy, y
- Output: 1 — flap if sigmoid output > 0.5
- Fitness: pipes_cleared**3 + time_alive*0.01
- Platform: local machine (no GPU needed), Cursor IDE
- Do NOT use neat-python or any ML library for NEAT logic
- InnovationTracker._history resets each gen, _counter never resets
- Full Cursor prompts in: docs/NEAT_COPILOT_GUIDE.md
- DevOps setup in: docs/DEVOPS_GUIDE.md
