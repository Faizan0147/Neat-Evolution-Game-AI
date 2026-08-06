# NEAT Flappy Bird — Antigravity Agent Guide

**Status:** 4P-Sprint Project | Week 1-4 (8 sessions) | Python 3.9+ | IDE: Antigravity

> Full session-by-session Antigravity prompts for `docs/02_NEAT_FLAPPY_BIRD.md`, the source-of-truth plan. Paste that file into a new Antigravity chat for full context before starting Session 1.

---

## How to Use This Document with Antigravity

### Two Strategies

**Option A: .md File in Repo (Recommended)**
- Keep this file (and `02_NEAT_FLAPPY_BIRD.md`) open in Antigravity alongside your code
- Antigravity reads open files in your workspace as context automatically
- Update it as you progress; Antigravity picks up accumulated context each session
- **Best for:** staying aligned over 4 weeks, iterating on feedback

**Option B: Copy-Paste Prompts (Quick Sessions)**
- Use the "Session N" prompts below for individual Antigravity Chat sessions
- Paste one session's prompts at a time
- **Best for:** short, focused coding bursts

**Recommendation:** Do both. Keep the docs open in Antigravity. Copy-paste the session prompts into Antigravity Chat when starting a new sitting.

---

## System Context — Give Antigravity This First

**Paste this into a new Antigravity Chat session to set expectations:**

```
I'm building NEAT (NeuroEvolution of Augmenting Topologies) completely from
scratch in Python to play a custom Flappy Bird clone I'm also building from
scratch. No ML libraries. Pure Python + pygame + numpy.

Project structure:
- game/        # Flappy Bird engine, sensors, headless mode
- neat/        # Genome, network, population, evolution loop
- visualizer/  # Live pygame overlay showing best agent + stats
- main.py      # Wires everything

I'm a 2nd-year Computer Engineering student (Pakistan), currently doing an
AI/ML internship. I know Python and C++. Push me on architecture decisions —
don't hand-hold.

Constraints:
- Week 1: Game engine + headless mode (no NEAT yet)
- Week 2: Genome + neural net (can evaluate one agent)
- Week 3: Full NEAT (speciation, crossover, evolution loop)
- Week 4: Visualizer + tuning + live demo

Do not use external ML libraries (no neat-python, sklearn, tensorflow).
Build NEAT from first principles.

Code style:
- Type hints for all functions
- Dataclasses for genome/nodes/connections
- Clear variable names (avoid single letters except i, j, x, y)
- Docstrings on public methods
- Tests appreciated for core logic (pytest)
```

---

## Project Requirements (Complete Spec)

### The Game — Flappy Bird Only

This project builds one game: a Flappy Bird clone. (Not a dino runner, not a
configurable multi-game engine — see `02_NEAT_FLAPPY_BIRD.md` if that ever
changes.)

- Gravity pulls the player downward each frame
- One action: flap (upward velocity impulse)
- Pipes scroll left, spawn right at random gap heights
- Death: hit a pipe, hit the ceiling, hit the floor
- Score: number of pipes cleared

**Game constants:**

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

**Sensor inputs (5 values):**

```
1. Horizontal distance to next pipe pair       [0, 1]
2. Vertical distance from player to top pipe   [-1, 1]  (negative = above gap)
3. Vertical distance from player to bottom pipe [-1, 1]
4. Player Y velocity                           [-1, 1]
5. Player Y position                           [0, 1]
```

**Output (1 value, sigmoid):**

```
1. Flap if > 0.5, do nothing otherwise
```

**Code requirements:**
- `game/engine.py` — GameEngine class, `update()`, `render()`, collision logic
- `game/sensors.py` — `extract_inputs(state) -> list[float]`, 5 normalised inputs
- `game/headless.py` — `GameHeadless.run_episode(network) -> float`; must run 150 episodes in under 10 seconds
- `game/constants.py` — all magic numbers above

---

### NEAT Core (Weeks 2–3)

#### Week 2: Genome + Network

**Data Structures:**

```python
@dataclass
class NodeGene:
    id: int
    type: str        # "input" | "hidden" | "output"
    activation: str   # "tanh" for hidden, "sigmoid" for output

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
```

**Innovation Tracking:**
- Global singleton `InnovationTracker`
- Maps `(in_node, out_node) → innovation_number`
- `reset()` clears the history dict once per generation — the counter itself is **never** reset
- Same pair in the same generation always gets the same number — this is what makes crossover alignment work

**Network Evaluation:**
- `network.evaluate(inputs)` does topological sort + feedforward pass
- Input nodes: identity. Hidden: tanh. Output: sigmoid.
- No recurrent connections — `add_connection()` must reject cycles

#### Week 3: Population + Evolution

```python
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

**Evolution Loop (each generation):**
1. Evaluate fitness — run every genome through Flappy Bird, record score
2. Speciate — group genomes by compatibility distance δ
3. Fitness sharing — divide each genome's fitness by species size
4. Cull — remove bottom 50% of members per species
5. Reproduce — allocate offspring proportional to avg adjusted fitness (75% crossover + mutation, 25% mutation only)
6. Elitism — copy species champion unchanged to next generation
7. Stagnation check — kill species with no improvement for `max_stagnation` gens
8. Update reps — pick a random member as new species representative
9. Reset innovation — `InnovationTracker.reset()` for next generation

**Mutation Operators:**
- Perturb weights (80%) — gaussian noise on random connections
- Reset weight (20% of weight mutations) — uniform random new value
- Add connection (5%) — new synapse between two existing nodes
- Add node (3%) — split existing connection, insert new node
- Toggle connection (rare) — enable/disable a connection

**Crossover:**
- Align by innovation number, assume parent1 is fitter
- Matching genes → random pick
- Excess/disjoint → from fitter parent only
- Disabled genes: 75% chance to stay disabled in child

---

### Fitness Function Design

**Rule: never reward only survival.**

```python
fitness = (pipes_cleared ** 3) + (time_alive * 0.01)
```

**Why cubic on pipes?** Going from 1 pipe to 5 pipes is 125x better than 1 — this creates massive pressure to actually clear pipes rather than just survive. The small time bonus prevents instant-death scoring the same as dying at pipe 1.

---

### Visualizer (Week 4)

- **Top-left:** best agent playing Flappy Bird live
- **Bottom-left:** neural network graph of best agent (input=blue, hidden=purple, output=green; connection thickness ∝ |weight|, colour = sign)
- **Top-right:** stats panel (generation, best fitness, avg fitness, species count)
- **Bottom-right:** fitness curve (best + avg over all generations)
- **Controls:** Space = pause/resume, R = reset, +/- = speed, arrow keys = inspect agents

---

## Session-by-Session Prompts for Antigravity

### WEEK 1 — Game Engine + DevOps

#### Session 1 (~45 min): Repo + DevOps scaffold

```
1. Create pyproject.toml (black, ruff, mypy, pytest, pygame, numpy)
2. Create Makefile (make run, make test, make check, make headless)
3. Create .pre-commit-config.yaml (black, ruff, no-commit-to-main)
4. Create .github/workflows/ci.yml (Python 3.9 + 3.11 matrix)
5. pip install -e ".[dev]" && pre-commit install
6. git commit -m "chore: devops scaffold, CI"
Push → verify GitHub Actions goes green
```

See `docs/DEVOPS_GUIDE.md` for exact file contents to hand Antigravity.

#### Session 2 (~60 min): Game engine + sensors + headless

```
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
   - 5 normalised inputs (see spec above)
4. Create game/headless.py:
   - run_episode(network) → float fitness score
   - Must run 150 episodes in under 10 seconds
5. Test: python main.py (game opens, bird falls, dies at first pipe)
Commit: "feat(game): flappy bird engine, sensors, headless mode"
```

---

### WEEK 2 — Genome + Neural Network

#### Session 3 (~50 min): Innovation tracker + genome

```
1. Create neat/innovation.py (InnovationTracker singleton — see spec above)
2. Create neat/genome.py:
   - NodeGene, ConnectionGene, Genome dataclasses
   - Genome.copy() → deep copy
   - Genome.add_node(conn) → split connection, new node
   - Genome.add_connection(in_id, out_id) → new connection + cycle check
   - Genome.mutate_weights(rates)
   - Genome.mutate(config: NEATConfig)
   - Initial genome: 5 inputs → 1 output, direct connections
```

**Ask Antigravity to EXPLAIN (highlight + Ask):**
```
"Why does add_node() disable the original connection instead of deleting it?"
"What is the purpose of cycle detection in add_connection()?"
```

Commit: `"feat(neat): innovation tracker and genome dataclasses"`

#### Session 4 (~50 min): Neural network + integration test

```
1. Create neat/network.py:
   - NeuralNetwork(genome: Genome)
   - _topological_sort() → list[int] (node processing order)
   - evaluate(inputs: list[float]) → list[float]
   - Input nodes: identity. Hidden: tanh. Output: sigmoid.
```

**Ask Antigravity to EXPLAIN:**
```
"Trace evaluate() with 5 inputs, 1 hidden node, 1 output — show each step"
"Why does topological sort break if there are cycles?"
```

```
2. Wire it all together: genome → network → headless game, print score
3. Run: random network plays flappy bird, score is (usually) 0
```

Commit: `"feat(neat): feedforward neural network from genome"`

---

### WEEK 3 — Full NEAT Evolution

#### Session 5 (~60 min): Speciation + crossover

```
1. Create neat/species.py:
   - compatibility_distance(g1, g2, c1, c2, c3) → float
     Align by innovation number. Count E (excess), D (disjoint), W̄ (avg weight diff)
     δ = (c1·E + c2·D)/N + c3·W̄
   - Species dataclass
   - Speciation.speciate(genomes, existing_species, threshold) → list[Species]
```

**Ask Antigravity to EXPLAIN:**
```
"Give me a concrete example of two genomes — show me which genes are
 excess vs disjoint and how the distance is calculated step by step"
```

```
2. Add to neat/genome.py:
   - crossover(parent1: Genome, parent2: Genome) → Genome
     (parent1 assumed fitter, or equal fitness → random)
```

**Ask Antigravity to EXPLAIN:**
```
"Why do excess/disjoint genes only come from the fitter parent?"
```

Commit: `"feat(neat): species, compatibility distance, crossover"`

#### Session 6 (~60 min): Population + generation loop

```
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
```

Commit: `"feat(neat): population and full generation loop"`

---

### WEEK 4 — Visualizer + Polish

#### Session 7 (~60 min): Stats + network graph + visualizer

```
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
```

Commit: `"feat(visualizer): 4-panel live evolution view"`

#### Session 8 (~45 min): Tuning + demo + release

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
```

**LinkedIn post structure:**
```
Hook:      "I wrote the algorithm that made 'AI learns to play X' videos famous."
What NEAT: Evolves the network structure, not just the weights
The cool part: Networks start with ZERO hidden neurons and grow complexity
Visual:    GIF of generation 1 (all dying) vs generation 200 (clearing pipes)
Technical: Innovation numbers and why they solve the competing conventions problem
Tags:      #NEAT #NeuroEvolution #MachineLearning #Python #GameAI
```

---

## Checkpoints & Testing

### Week 1 Checkpoint
- [ ] Game runs without crashing
- [ ] Score increases as pipes are cleared
- [ ] Pipes spawn and move correctly
- [ ] Collision detection works (test by hitting a pipe)
- [ ] Headless mode runs 150 episodes in <10 seconds
- [ ] Sensors return normalised values (all in [-1, 1] or [0, 1])

### Week 2 Checkpoint
- [ ] `InnovationTracker` returns the same number for the same (in, out) pair within a generation
- [ ] Genome can be created and mutated (weights, node, connection)
- [ ] Network evaluates correctly (output in [0, 1] for sigmoid)
- [ ] Topological sort works (no cycles reach it)
- [ ] Network evaluation is deterministic (same inputs → same outputs)

### Week 3 Checkpoint
- [ ] Compatibility distance is small for two very similar genomes
- [ ] Compatibility distance is large for two very different genomes
- [ ] Speciation assigns genomes to species
- [ ] Crossover produces valid offspring (no broken connections)
- [ ] Evolution loop runs 5 generations without crashing
- [ ] Best fitness increases (or at least doesn't decrease rapidly)

### Week 4 Checkpoint
- [ ] Visualizer window opens and displays the game
- [ ] Network graph renders without distortion
- [ ] Stats panel updates each generation
- [ ] Fitness curve plots correctly
- [ ] Can pause/resume and adjust speed

---

## Git Workflow Suggestions

```bash
# Week 1
git checkout -b week/1-game-engine
# ... commit game/constants.py, game/engine.py, game/sensors.py, game/headless.py ...
git push origin week/1-game-engine
git checkout main && git merge week/1-game-engine

# Week 2
git checkout -b week/2-neural-genome
# ... commit neat/innovation.py, neat/genome.py, neat/network.py ...
git push origin week/2-neural-genome
git checkout main && git merge week/2-neural-genome

# Week 3
git checkout -b week/3-neat-evolution
# ... commit neat/species.py, neat/population.py ...
git push origin week/3-neat-evolution
git checkout main && git merge week/3-neat-evolution

# Week 4
git checkout -b week/4-visualizer-polish
# ... commit visualizer/, update main.py ...
git push origin week/4-visualizer-polish
git checkout main && git merge week/4-visualizer-polish
```

---

## Hyperparameter Tuning Reference

Start with the defaults in `NEATConfig` and tweak based on results:

```
Too slow convergence:  increase pop_size (150→200), decrease dt (3.0→2.5)
Too many species:      increase dt (3.0→4.0)
Species collapsing:    increase max_stagnation (20→30)
Agents not improving:  check fitness function — is pipes_cleared updating?
Network not growing:   increase add_node_rate (0.03→0.05)
Fitness oscillating:   reduce weight_perturb_power (0.1→0.05)
```

---

## Common Pitfalls to Avoid

1. **Innovation numbers not aligned:** crossover breaks if two genomes use different numbers for the same connection. Use the global tracker, and reset only the history — never the counter.
2. **Fitness function too weak:** agents learn to survive by doing nothing. Reward pipes cleared, not just time alive.
3. **Network has cycles:** topological sort will hang. Reject cycles in `add_connection()`.
4. **Headless mode is slow:** make sure there's no pygame rendering happening in the headless path.
5. **Speciation threshold too low/high:** `dt` < 1 → no species, all unique. `dt` > 10 → one giant species (no speciation). Start at 3.0.
6. **Excess/disjoint genes flipped:** if fitness is tied between parents, break ties consistently (e.g. by species age or genome size).
7. **Disabled genes not inherited:** children should inherit disabled genes at a higher rate — 75% stay disabled even in the child.

---

## What Success Looks Like

```
Gen 1-10:    all birds die immediately (score ~0)
Gen 10-50:   some start clearing 1-2 pipes
Gen 50-150:  consistent 3-5 pipe clears, population stabilising
Gen 150-200: best agent clearing 10+ pipes, network diagram settling
```

By the end of Week 4, you should have agents that:
- Consistently clear multiple pipes (not luck — repeatable across runs)
- Show a diverse population (multiple species)
- Have stable fitness curves (not crashing, not random oscillation)
- A network that grew hidden structure beyond the initial direct connections

---

## Running Incrementally with Antigravity

**Session 1 (~45 min):** Repo + DevOps scaffold. CI goes green.

**Session 2 (~60 min):** Game engine + sensors + headless. Bird falls, dies at first pipe.

**Session 3 (~50 min):** Innovation tracker + genome. Genomes exist and mutate.

**Session 4 (~50 min):** Neural network + integration test. Random network plays (badly).

**Session 5 (~60 min):** Speciation + crossover.

**Session 6 (~60 min):** Population + generation loop. 20 generations, birds start clearing pipes.

**Session 7 (~60 min):** Stats + network graph + visualizer.

**Session 8 (~45 min):** Tuning + demo + release (v0.1.0 tag).

Each session is one focused Antigravity Chat sitting. Paste the session's prompts, let it write the code, review and refine before committing. (These techniques apply just as well if you're using GitHub Copilot or another AI pair-programmer — Antigravity is this project's IDE of choice, not a hard requirement.)

---

**Good luck with the sprint! Come back to this doc if you get stuck.**
