# NEAT Flappy Bird — Revision Notebook

> My single place to revise everything about this project: the theory behind NEAT,
> how each piece of my code works, and the "why" behind each design decision.
> Updated after every session.

**Progress:** Session 1 ✅ · Session 2 ✅ · Session 3 ✅ · Session 4 ⬜ · Session 5 ⬜ · Session 6 ⬜ · Session 7 ⬜ · Session 8 ⬜

---

## Table of Contents

1. [The Big Picture](#1-the-big-picture)
2. [NEAT Theory](#2-neat-theory)
3. [Project Architecture](#3-project-architecture)
4. [The Game (Week 1)](#4-the-game-week-1)
5. [Innovation Tracker](#5-innovation-tracker)
6. [Config — NEATConfig](#6-config--neatconfig)
7. [Genome (Session 3)](#7-genome-session-3)
8. [Mutations in Detail](#8-mutations-in-detail)
9. [Testing Strategy](#9-testing-strategy)
10. [Coming Next](#10-coming-next)
11. [Glossary](#11-glossary)
12. [Self-Check Questions](#12-self-check-questions)

---

## 1. The Big Picture

**Goal:** evolve neural networks that play Flappy Bird — with no backpropagation,
no gradient descent, no ML libraries. Only natural selection.

```
   ┌──────────────┐   inputs (5)    ┌──────────────┐   flap? (1)   ┌──────────┐
   │  Game state  │ ──────────────▶ │  Neural net  │ ────────────▶ │  Engine  │
   │ (bird, pipes)│                 │ (from genome)│               │ update() │
   └──────────────┘                 └──────────────┘               └────┬─────┘
          ▲                                                              │
          └──────────────────────── next frame ─────────────────────────┘

   When the bird dies → fitness = pipes³ + frames·0.01 → used for selection
```

Each generation:

```
 150 genomes ──▶ play the game ──▶ fitness ──▶ speciate ──▶ select + breed ──▶ 150 new genomes
      ▲                                                                              │
      └──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. NEAT Theory

**NEAT = NeuroEvolution of Augmenting Topologies** (Stanley & Miikkulainen, 2002).

A normal neural network has a *fixed* structure and learns its *weights* via
gradient descent. NEAT evolves **both the weights and the structure** (which nodes
exist, which are connected) using a genetic algorithm.

### 2.1 Genotype vs Phenotype

| Term | In NEAT | In my code |
|---|---|---|
| **Genotype** | The encoded "DNA": a list of node genes + connection genes | `Genome` (neat/genome.py) |
| **Phenotype** | The actual working network built from the DNA | `NeuralNetwork` (neat/network.py, Session 4) |

Evolution operates on genotypes; fitness is measured on phenotypes.

### 2.2 The three problems NEAT solves

Evolving network *topology* has three classic problems. NEAT has one idea for each.

#### Problem 1 — Competing Conventions → Solution: Innovation Numbers

Two networks can compute the same thing but list their genes in a different order,
or have different structures entirely. How do you line them up for crossover?

```
Parent A genes:  [in0→out]  [in1→out]  [in0→h1]  [h1→out]
Parent B genes:  [in0→out]  [in1→out]  [in1→h2]  [h2→out]
                                         ???        ???
```

**Fix:** every new structural gene gets a **globally unique innovation number** at the
moment it first appears. It's a historical marker — "this gene appeared at time 7".
Crossover lines genes up by that number. No graph matching required.

```
Innovation #:     1    2    3    4    5    6
Parent A:        [1]  [2]  [3]  [4]   -    -
Parent B:        [1]  [2]   -    -   [5]  [6]
                 match match disjoint     excess
```

#### Problem 2 — New structure gets killed too early → Solution: Speciation

Adding a node usually makes a network *worse* at first (its weights aren't tuned yet).
In one big pool it would be eliminated before it can improve.

**Fix:** group similar genomes into **species**. Genomes mostly compete inside their own
species, so a new structure gets a few generations to optimize. Similarity is measured
by the **compatibility distance**:

```
        c1·E     c2·D
  δ  =  ────  +  ────  +  c3·W̄
         N        N

  E  = number of excess genes      (beyond the other genome's highest innovation #)
  D  = number of disjoint genes    (missing in the middle)
  W̄  = average weight difference of matching genes
  N  = number of genes in the larger genome
  δ < dt (3.0)  →  same species
```

**Fitness sharing:** each genome's fitness is divided by its species size, so a single
big species can't take over the population.

#### Problem 3 — Searching huge networks is slow → Solution: Complexification

Start **minimal**: inputs wired straight to outputs, zero hidden nodes. Structure is only
added by mutation, and only survives if it helps. NEAT therefore tends to find the
*simplest* network that solves the problem.

```
Generation 0 (minimal)            Generation N (grown by mutation)

 x0 ─┐                             x0 ─────► h6 ─┐
 x1 ─┤                             x1 ─┐         │
 x2 ─┼──► out                      x2 ─┼──► out ◄┤
 x3 ─┤                             x3 ─┤         │
 x4 ─┘                             x4 ─────► h7 ─┘
```

### 2.3 The generation loop (what Session 6 will implement)

```
1. Evaluate      run every genome in the game, record fitness
2. Speciate      group genomes by δ
3. Share fitness divide fitness by species size
4. Cull          drop bottom 50% of each species
5. Reproduce     offspring ∝ species' average adjusted fitness
                 75% crossover + mutation, 25% mutation only
6. Elitism       copy each species' champion unchanged
7. Stagnation    remove species with no improvement in max_stagnation gens
8. Representatives  random member becomes next generation's species rep
9. Reset         InnovationTracker.reset()
```

### 2.4 Crossover rules (Session 5)

Assume parent 1 is the fitter one:

| Gene situation | Child gets |
|---|---|
| In both parents (matching) | random pick from either parent |
| Only in parent 1 (disjoint/excess) | inherited from parent 1 |
| Only in parent 2 (disjoint/excess) | skipped |
| Disabled in either parent | 75% chance stays disabled |

Why only from the fitter parent? Its extra structure is *proven* to be part of a
working network; the weaker parent's extra structure isn't.

---

## 3. Project Architecture

```
game/                     ← the environment (Week 1)
  constants.py            all magic numbers
  engine.py               GameEngine: physics, collisions, rendering
  sensors.py              GameState → 5 normalised inputs
  headless.py             run_episode(network) → fitness

neat/                     ← the algorithm (Weeks 2–3)
  innovation.py           InnovationTracker (global gene history)        ✅
  config.py               NEATConfig (all hyperparameters)               ✅
  genome.py               NodeGene, ConnectionGene, Genome + mutations    ✅
  network.py              NeuralNetwork: genome → feedforward net         ⬜
  species.py              compatibility distance, speciation              ⬜
  population.py           generation loop                                ⬜

visualizer/               ← live 4-panel pygame view (Week 4)            ⬜
tests/test1.py            game tests
tests/test2.py            innovation + genome tests
```

**The key contract between game and NEAT** is tiny — anything with an `evaluate` method
can play:

```python
class Network(Protocol):
    def evaluate(self, inputs: list[float]) -> list[float]: ...
```

That's why `main.py` can plug in a `RandomNetwork` today and a real `NeuralNetwork` later.

---

## 4. The Game (Week 1)

### 4.1 Physics (per frame)

```python
if self._flap_requested:
    self._player.vy = FLAP_STRENGTH        # -8.0: instant upward velocity
    self._flap_requested = False

self._player.vy += GRAVITY                 # +0.5 every frame
self._player.y += self._player.vy
```

Screen y grows **downwards**, so negative velocity = moving up.

### 4.2 Collision: circle vs rectangle

The bird is a circle, pipes are rectangles. Find the point on the rectangle closest to
the circle's centre; if it's within the radius, they collide.

```python
closest_x = max(rx, min(cx, rx + rw))     # clamp centre into the rect
closest_y = max(ry, min(cy, ry + rh))
dx = cx - closest_x
dy = cy - closest_y
return (dx * dx + dy * dy) < (r * r)      # compare squared → no sqrt needed
```

```
        ┌────────┐
        │  pipe  │
        │        ●←── closest point
        └────────┘ ╲
                    ╲ distance < r ?
                     ◯ bird
```

### 4.3 Sensors — what the network "sees"

```python
return [horiz_dist, dist_to_top, dist_to_bottom, velocity_norm, y_norm]
```

| # | Input | Range | Meaning |
|---|---|---|---|
| 0 | `horiz_dist` | [0, 1] | how far away the next pipe is |
| 1 | `dist_to_top` | [-1, 1] | bird y − gap top (negative = above the gap) |
| 2 | `dist_to_bottom` | [-1, 1] | bird y − gap bottom |
| 3 | `velocity_norm` | [-1, 1] | vertical speed |
| 4 | `y_norm` | [0, 1] | height on screen |

**Why normalise?** Raw pixel values (0–800) would saturate tanh/sigmoid immediately.
Keeping inputs small means random initial weights in [-1, 1] produce useful outputs.

### 4.4 Fitness function

```python
def fitness_from_game(pipes_cleared: int, time_alive: int) -> float:
    return float(pipes_cleared**3) + time_alive * 0.01
```

- **Cubic pipes:** 5 pipes = 125, 1 pipe = 1 → huge pressure to actually clear pipes.
- **Small time bonus:** separates "died instantly" from "survived but missed the first
  pipe", so generation 0 isn't all zeros and selection has something to work with.

### 4.5 Headless mode

```python
game = GameEngine(headless=True)   # pygame never imported
```

Training runs 150 genomes × hundreds of generations. Drawing would make that impossible.
Target: **150 episodes in < 10 s**.

---

## 5. Innovation Tracker

File: `neat/innovation.py`. Class-level state = one shared tracker for the whole program.

```python
@classmethod
def get_innovation(cls, in_node: int, out_node: int) -> int:
    key = (in_node, out_node)
    if key not in cls._history:
        cls._counter += 1
        cls._history[key] = cls._counter
    return cls._history[key]
```

### The two rules

1. **Same (in, out) pair in the same generation → same innovation number.**
   If two genomes independently add the connection 3→5 this generation, it's the *same
   gene* and must line up in crossover.
2. **`_counter` never goes backwards.** `reset()` clears only `_history` (once per
   generation). Numbers stay globally unique forever.

```
Gen 1:  genome A adds 3→5  → #6      genome B adds 3→5 → #6 (same!)
        reset()            → _history = {}, _counter stays 6
Gen 2:  genome C adds 3→5  → #7      (new number; history was cleared)
```

| Method | Clears history | Clears counter | Used by |
|---|---|---|---|
| `reset()` | ✅ | ❌ | population, once per generation |
| `full_reset()` | ✅ | ✅ | tests only |

### Split-node IDs (added in Session 3)

When a connection is split, the new hidden node needs an ID. That ID must *also* match
across genomes — otherwise two genomes splitting the same connection would create nodes
`6` and `9`, and then `0→6` and `0→9` would get different innovation numbers even though
they're the same structural change.

```python
@classmethod
def get_split_node_id(cls, innovation: int, first_free_id: int) -> int:
    if innovation not in cls._node_history:
        cls._node_counter = max(cls._node_counter, first_free_id)
        cls._node_history[innovation] = cls._node_counter
        cls._node_counter += 1
    return cls._node_history[innovation]
```

- Keyed by the **innovation number of the connection being split**.
- `first_free_id` = `inputs + outputs` (6 for Flappy Bird), so hidden IDs start at 6
  and never collide with input (0–4) or output (5) IDs.
- Follows the same reset rules as connections.

---

## 6. Config — NEATConfig

File: `neat/config.py`. Every hyperparameter in one dataclass, so tuning never means
hunting through code.

```python
@dataclass
class NEATConfig:
    pop_size: int = 150
    c1: float = 1.0                 # excess gene weight in δ
    c2: float = 1.0                 # disjoint gene weight in δ
    c3: float = 0.4                 # weight-difference weight in δ
    dt: float = 3.0                 # species threshold
    weight_mutate_rate: float = 0.8     # chance a genome's weights mutate at all
    weight_perturb_rate: float = 0.9    # per weight: nudge (90%) vs reset (10%)
    weight_perturb_power: float = 0.1   # std-dev of the gaussian nudge
    weight_init_range: float = 1.0      # reset weights land in [-1, 1]
    add_node_rate: float = 0.03
    add_conn_rate: float = 0.05
    toggle_conn_rate: float = 0.01
    max_stagnation: int = 20
```

Tuning cheat-sheet:

| Symptom | Change |
|---|---|
| Network never grows | `add_node_rate` 0.03 → 0.05 |
| Too many species (>15) | `dt` 3.0 → 4.0 |
| Species die too fast | `max_stagnation` 20 → 30 |
| Fitness oscillates | `weight_perturb_power` 0.1 → 0.05 |
| Slow convergence | `pop_size` 150 → 200, `dt` 3.0 → 2.5 |

---

## 7. Genome (Session 3)

File: `neat/genome.py`.

### 7.1 The genes

```python
@dataclass
class NodeGene:
    id: int
    type: str          # "input" | "hidden" | "output"
    activation: str    # "identity" | "tanh" | "sigmoid"

@dataclass
class ConnectionGene:
    in_node: int
    out_node: int
    weight: float
    enabled: bool = True
    innovation: int = 0
```

```python
@dataclass
class Genome:
    inputs: int
    outputs: int
    nodes: dict[int, NodeGene]               # keyed by node id
    connections: dict[int, ConnectionGene]   # keyed by innovation number
    fitness: float = 0.0
    species_id: int = -1
```

**Why are connections keyed by innovation number?** Because that's how crossover and
compatibility distance will look them up: `if innov in parent1.connections and innov in
parent2.connections` → matching gene. O(1) alignment.

### 7.2 Node ID layout

```
id:      0    1    2    3    4    5      6, 7, 8 ...
type:  input input input input input output  hidden (created by add_node)
act:   identity ────────────────►  sigmoid  tanh
```

| Node type | Activation | Why |
|---|---|---|
| input | identity | inputs are already normalised; just pass them through |
| hidden | tanh | output in [-1, 1], zero-centred, allows negative signals |
| output | sigmoid | output in [0, 1] → read as a probability: flap if > 0.5 |

### 7.3 The starting genome

```python
genome = Genome.create_initial(5, 1)
```

```python
for in_id in genome.input_ids():
    for out_id in genome.output_ids():
        weight = random.uniform(-weight_range, weight_range)
        genome._add_connection_gene(in_id, out_id, weight)
```

```
 x0 (0) ──#1──┐
 x1 (1) ──#2──┤
 x2 (2) ──#3──┼──► out (5)        6 nodes, 5 connections, 0 hidden
 x3 (3) ──#4──┤                   every genome in gen 0 has innovations 1–5
 x4 (4) ──#5──┘
```

Because all genomes call the tracker with the same pairs, they all get the same
innovation numbers 1–5 — they're perfectly aligned from the start.

### 7.4 `copy()`

```python
def copy(self) -> Genome:
    return copy.deepcopy(self)
```

A deep copy is essential. A shallow copy would share the same `ConnectionGene` objects,
so mutating a child's weight would silently mutate the parent (and elitism would break).

### 7.5 `add_node(conn)` — splitting a connection

```python
def add_node(self, conn: ConnectionGene) -> bool:
    if not conn.enabled:
        return False

    first_free_id = self.inputs + self.outputs
    new_id = InnovationTracker.get_split_node_id(conn.innovation, first_free_id)
    if new_id in self.nodes:
        return False

    conn.enabled = False
    self.nodes[new_id] = NodeGene(new_id, HIDDEN, "tanh")
    self._add_connection_gene(conn.in_node, new_id, 1.0)
    self._add_connection_gene(new_id, conn.out_node, conn.weight)
    return True
```

```
Before:   A ────── w ──────► B                (enabled)

After:    A ─ ─ ─ w ─ ─ ─ ─► B                (disabled, kept in genome)
          A ── 1.0 ──► H ── w ──► B           (two new genes)
```

**Why weight 1.0 in, old weight out?** The new path computes almost the same thing as the
old connection, so the network's behaviour barely changes. The new node isn't punished
on day one — it gets time to be tuned. (Not *exactly* the same because H applies tanh.)

**Why disable instead of delete?**
- The gene's history is preserved for crossover alignment (innovation # still exists).
- A later toggle mutation or crossover can re-enable it.
- Compatibility distance still counts it, so the genome's "ancestry" stays visible.

**Why `new_id in self.nodes` check?** If the same connection was split, re-enabled by a
toggle, and split again in the same generation, the tracker would return the same node
ID. We refuse rather than corrupt the genome.

### 7.6 `add_connection(in_id, out_id)` — and cycle detection

All rules live in one place:

```python
def _can_connect(self, in_id: int, out_id: int) -> bool:
    if in_id not in self.nodes or out_id not in self.nodes:
        return False
    if in_id == out_id:                                   # no self-loops
        return False
    if self.nodes[in_id].type == OUTPUT or self.nodes[out_id].type == INPUT:
        return False                                      # keep direction input → output
    if self._connection_exists(in_id, out_id):            # no duplicates
        return False
    return not self._creates_cycle(in_id, out_id)         # stay feedforward
```

**Cycle check:** adding `in → out` creates a cycle if `in` is already reachable *from*
`out`. Depth-first search from `out`:

```python
def _creates_cycle(self, in_id: int, out_id: int) -> bool:
    children: dict[int, list[int]] = {}
    for c in self.connections.values():
        children.setdefault(c.in_node, []).append(c.out_node)

    visited: set[int] = set()
    stack = [out_id]
    while stack:
        node = stack.pop()
        if node == in_id:
            return True
        if node in visited:
            continue
        visited.add(node)
        stack.extend(children.get(node, []))
    return False
```

```
Existing:   h6 ──► h7 ──► out
Try:        h7 ──► h6 ?

DFS from h6:  h6 → h7  ← found in_id (h7) → CYCLE → reject
```

**Why does it matter?** The network will be evaluated with a *topological sort* (Session 4):
each node is computed after all nodes feeding into it. A cycle means there's no valid
order — A needs B, B needs A — and the sort fails.

**Why include disabled connections in the check?** A disabled connection can be
re-enabled later by toggle mutation. If it would form a cycle at that point, the genome
breaks. Checking all connections keeps every genome feedforward no matter what's toggled.

---

## 8. Mutations in Detail

### 8.1 Overview

```python
def mutate(self, config: NEATConfig) -> None:
    if random.random() < config.weight_mutate_rate:    # 80%
        self.mutate_weights(config)
    if random.random() < config.add_conn_rate:         # 5%
        self.mutate_add_connection()
    if random.random() < config.add_node_rate:         # 3%
        self.mutate_add_node()
    if random.random() < config.toggle_conn_rate:      # 1%
        self.mutate_toggle_connection()
```

Each is an independent coin flip, so a genome can get several mutations at once.

| Mutation | Rate | Changes | Effect |
|---|---|---|---|
| weights | 80% | weight values | fine-tuning (most common) |
| add connection | 5% | new gene | new pathway between existing nodes |
| add node | 3% | new node + 2 genes | adds depth |
| toggle | 1% | enabled flag | switch a path on/off |

Structural rates are *low on purpose*: most generations should tune what exists; growth
should be rare and survive only if useful.

### 8.2 Weight mutation

```python
for conn in self.connections.values():
    if random.random() < config.weight_perturb_rate:             # 90%
        conn.weight += random.gauss(0.0, config.weight_perturb_power)
    else:                                                        # 10%
        conn.weight = random.uniform(-config.weight_init_range, config.weight_init_range)
```

- **Perturb** = small gaussian nudge → local search near a good solution.
- **Reset** = brand new random value → escape when a weight is stuck somewhere bad.

### 8.3 Add-connection mutation

```python
pairs = [(in_id, out_id) for in_id in self.nodes for out_id in self.nodes]
random.shuffle(pairs)

for in_id, out_id in pairs:
    if self.add_connection(in_id, out_id):
        return True
return False
```

Shuffle all pairs, take the first valid one. This picks uniformly among valid pairs but
stops early instead of validating every pair (each validation runs a DFS). In the
starting genome every valid pair already exists, so this returns `False`.

> 💡 Lesson learned: my first version validated *every* pair first, then picked one.
> With ~100 nodes that's 10,000 DFS runs per mutation — the test took 166 s. The shuffle
> version takes 0.5 s. Same behaviour, far less work.

---

## 9. Testing Strategy

Run all checks: `make check` (black + ruff + mypy + pytest).

| File | Covers |
|---|---|
| `tests/test1.py` | engine physics, collisions, sensors, fitness, headless speed |
| `tests/test2.py` | innovation numbers, split-node IDs, genome creation, copy, add_node, add_connection rules, mutations |

Every test in `test2.py` starts with a clean tracker:

```python
@pytest.fixture(autouse=True)
def _clean_tracker():
    InnovationTracker.full_reset()
    yield
    InnovationTracker.full_reset()
```

Without it, innovation numbers would depend on which tests ran before — tests would pass
alone and fail together.

A good example — proving cycle detection works:

```python
def test_rejects_cycle(self) -> None:
    genome = Genome.create_initial(5, 1)
    h1 = _split(genome, 0, 5)         # 0 → h1 → 5
    h2 = _split(genome, h1, 5)        # 0 → h1 → h2 → 5
    assert genome.add_connection(h2, h1) is False
```

And a stress test: 200 rounds of heavy mutation, then verify no connection forms a cycle.

---

## 10. Coming Next

### Session 4 — `neat/network.py`
- `NeuralNetwork(genome)`: build the phenotype from enabled connections only.
- Topological sort (Kahn's algorithm): repeatedly take nodes with no unprocessed inputs.
- `evaluate(inputs)`: set input values → walk nodes in sorted order →
  `value = activation(Σ weight · input_value)` → return output values.

### Session 5 — `neat/species.py` + crossover
### Session 6 — `neat/population.py` (the generation loop in §2.3)
### Session 7 — visualizer · Session 8 — tuning + release

---

## 11. Glossary

| Term | Meaning |
|---|---|
| **Genome** | The encoded network (nodes + connection genes) |
| **Gene** | One node or one connection |
| **Innovation number** | Global ID marking when a connection gene first appeared |
| **Matching gene** | Same innovation # in both genomes |
| **Disjoint gene** | Present in one genome, inside the other's innovation range |
| **Excess gene** | Present in one genome, beyond the other's max innovation # |
| **Species** | Group of genomes with δ < dt |
| **Compatibility distance (δ)** | How structurally different two genomes are |
| **Fitness sharing** | Fitness ÷ species size, to stop one species dominating |
| **Elitism** | Copying the best genome unchanged into the next generation |
| **Stagnation** | A species not improving for many generations |
| **Complexification** | Starting minimal and only growing structure when useful |
| **Feedforward** | Signals only flow input → output, no loops |
| **Topological sort** | An order of nodes where every node comes after its inputs |

---

## 12. Self-Check Questions

Try answering out loud before looking back.

1. What's the difference between a genotype and a phenotype in NEAT?
2. Why does the innovation counter never reset, but the history does?
3. Two genomes both add connection 2→5 in the same generation. What innovation numbers
   do they get? What about next generation?
4. Why does `add_node` set the incoming weight to 1.0 and the outgoing weight to the old
   weight?
5. Why is the old connection disabled rather than deleted?
6. Why must hidden node IDs from splitting be shared across genomes?
7. Draw a genome where adding `h7 → h6` would create a cycle. Why does a cycle break
   the network?
8. Why are disabled connections included in the cycle check?
9. Why is `copy()` a *deep* copy?
10. Why are structural mutation rates (3–5%) so much lower than weight mutation (80%)?
11. Why are inputs normalised to [-1, 1] / [0, 1]?
12. Why is the fitness function cubic in pipes cleared?
13. Why do we need speciation at all — what would happen without it?
