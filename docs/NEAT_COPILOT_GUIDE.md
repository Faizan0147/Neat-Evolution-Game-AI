# NEAT Neural Evolution Game AI — Copilot Agent Guide

**Status:** 4P-Sprint Project | Week 1-4 Build Plan | Python 3.9+

---

## How to Use This Document with GitHub Copilot

### Two Strategies:

**Option A: .md File in Repo (Recommended)**
- Save this as `docs/COPILOT_GUIDE.md` in your repo
- Copilot can see it and reference it automatically (in VS Code, it reads files in your workspace)
- Update it as you progress; Copilot learns from accumulated context
- **Best for:** Staying aligned over 4 weeks, iterating on feedback

**Option B: Copy-Paste Prompts (Quick Sessions)**
- Use the prompts below for individual chat sessions in Copilot Chat
- Paste one "Weekly Prompt" per session
- **Best for:** Short focused coding bursts, testing specific modules

**Recommendation:** Do both. Keep the .md in your repo. Copy-paste the weekly prompts into Copilot Chat when starting a new session.

---

## System Context — Give Copilot This First

**Paste this into a new Copilot Chat session to set expectations:**

```
I'm building a NEAT (NeuroEvolution of Augmenting Topologies) neural network 
from scratch to play a 2D game I'm also building from scratch. No ML libraries. 
Pure Python.

Project structure:
- game/        # Game engine, sensors, headless mode
- neat/        # Genome, network, population, evolution loop
- visualizer/  # Live pygame overlay showing best agent + stats
- main.py      # Wires everything

I'm a 2nd year CE student. I know Python, C++, Java, JS. Push me on architecture 
decisions — don't hand-hold.

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
- Tests optional but appreciated for core logic
```

---

## Project Requirements (Complete Spec)

### Game (Week 1)

**Pick one game** (recommendation: dino runner or flappy bird for speed):

#### Dino Runner
- Player sprite at fixed y position (or variable y for jumping)
- Obstacles: cacti (jump to clear) and birds (duck to clear)
- Ground scrolls left, obstacles spawn right
- Collision detection (AABB bounding boxes)
- Score = distance traveled (in pixels)
- Speed increases slightly per 500 distance

**Game Loop:**
- 60 FPS fixed timestep
- Input: jump, duck (from neural net)
- Physics: gravity, jump arc, collision checks
- Render mode (pygame) + headless mode (no rendering, return score)

**Sensor Inputs for Neural Net:**
1. Distance to next obstacle (pixels, normalized 0–1)
2. Obstacle width (0–1)
3. Obstacle height (0–1)
4. Obstacle type (0 = cactus, 1 = bird, one-hot or direct)
5. Player Y position (0–1)
6. Player Y velocity (−1 to 1)
7. Ground speed (0–1, increases over time)
8. Time since last obstacle (frames, normalized)

**Output:**
1. Jump action (sigmoid, threshold 0.5)
2. Duck action (sigmoid, threshold 0.5)

#### Alternative: Flappy Bird Clone
- Gravity pulls player downward
- Flap (from neural net) applies upward velocity
- Pipes scroll left, spawn right
- Collision: pipes or ceiling/floor = death
- Score = pipes cleared

**Sensor Inputs:**
1. Horizontal distance to next pipe pair (0–1)
2. Distance to top pipe bottom (−1 to 1, negative = above)
3. Distance to bottom pipe top (−1 to 1)
4. Player Y velocity (−1 to 1)
5. Player Y position (0–1)

**Output:**
1. Flap action (sigmoid, threshold 0.5)

**Code Requirements:**
- `game/engine.py` — main game class, update(), render(), collision logic
- `game/sensors.py` — extract neural network inputs from game state
- `game/headless.py` — GameHeadless class that runs without rendering, returns final score
- `game/constants.py` — all magic numbers (pipe spacing, gravity, speeds, etc.)

---

### NEAT Core (Weeks 2–3)

#### Week 2: Genome + Network

**Data Structures:**

```python
# NodeGene: represents a neuron
- id: int (unique)
- type: str ("input", "hidden", "output")
- activation: str ("tanh" or "sigmoid")

# ConnectionGene: represents a synapse
- in_node: int (source node id)
- out_node: int (target node id)
- weight: float
- enabled: bool (can be disabled by mutation)
- innovation: int (global unique ID for this connection)

# Genome: complete neural network genotype
- nodes: dict[int, NodeGene]
- connections: dict[int, ConnectionGene]
- fitness: float (assigned after game evaluation)
- species_id: int (assigned during speciation)

# NeuralNetwork: phenotype (built from genome)
- layers: list of node IDs, topologically sorted
- run(inputs: list[float]) -> list[float]
```

**Innovation Tracking:**
- Global singleton `InnovationTracker`
- Maps (in_node, out_node) → innovation_number
- Reset per generation, but same pair gets same number within generation
- Critical for crossover alignment

**Network Evaluation:**
- `network.evaluate(inputs)` does topological sort + feedforward pass
- Uses tanh/sigmoid activations
- Returns output layer values (list of floats)

#### Week 3: Population + Evolution

**Classes:**

```python
# Species: a group of similar genomes
- id: int
- representative: Genome (for compatibility distance)
- members: list[Genome]
- best_fitness: float (best in this species so far)
- stagnation_counter: int (generations with no improvement)

# Population: generation management
- genomes: list[Genome] (all agents current gen)
- species: list[Species]
- generation: int
- config: NEATConfig (hyperparameters)

# NEATConfig: all tunable parameters
- pop_size: int (default 150)
- c1, c2, c3: float (compatibility distance weights)
- dt: float (speciation threshold)
- mutation_rates: dict
- max_stagnation: int (kill species after N gens)
```

**Evolution Loop (each generation):**
1. Evaluate fitness: run each genome through game
2. Speciate: group by compatibility distance
3. Fitness sharing: divide by species size
4. Cull: remove bottom 50% per species
5. Reproduce: allocate offspring, crossover + mutate
6. Elitism: copy species champion unchanged
7. Stagnation check: kill stale species
8. Update reps: pick new representative per species

**Mutation Operators:**
- Perturb weights: (80%) add gaussian noise to random weights
- Reset weight: (20%) set weight to uniform random
- Add node: (3%) split a connection, insert new hidden node
- Add connection: (5%) add new random connection between nodes
- Toggle connection: (rare) enable/disable a connection

**Crossover:**
- Align by innovation number
- Matching genes: random parent
- Excess/disjoint: take from fitter parent
- Always inherit all genes, but disabled genes have 75% chance to stay disabled

---

### Fitness Function Design

**Rule: never reward only survival.**

Fitness should reward:
- **Primary:** Making progress (distance, pipes, height, etc.)
- **Secondary:** Efficiency (doing it fast)
- **Penalty:** Idling (−0.01 per frame if no progress)

**Example formulas:**

```python
# Dino runner
def fitness(distance, obstacles_cleared, time_alive):
    base = distance ** 2  # quadratic to encourage big improvements
    bonus = 10 * obstacles_cleared
    penalty = -0.01 * time_alive if distance == 0 else 0
    return base + bonus + penalty

# Flappy bird
def fitness(pipes_cleared, time_alive):
    return (pipes_cleared ** 3) + (time_alive * 0.01)
```

**Why quadratic?**
- Linear (distance) → going from 100 to 200 feels same as 1000 to 1100 → slow convergence
- Quadratic (distance²) → 200 is 4x better than 100, 1100 is 1.21x better than 1000 → creates gradient pressure to improve

---

### Visualizer (Week 4)

**Components:**

1. **Game window**: top-left, shows best agent playing (live each generation)
2. **Network graph**: bottom-left, draws neural net topology with weighted edges
   - Circle = node (color: input=blue, hidden=purple, output=green)
   - Line = connection (thickness = weight magnitude, color = sign)
3. **Stats panel**: right side
   - Best fitness this generation
   - Average fitness this generation
   - Species count
   - Generation number
   - Stagnation counters per species
4. **Fitness curve**: bottom-right, plot of best/avg fitness over generations

**Interactive:**
- Space to pause/resume
- R to reset
- Slider to speed up/slow down game playback
- Arrow keys to inspect different agents

---

## Weekly Prompts for Copilot

### **WEEK 1: Game Engine**

#### Prompt 1.1 — Project Setup & Game Architecture

```
I'm building a NEAT evolution system and need to start with the game.

Create the project structure with these directories:
- game/
- neat/
- visualizer/
- tests/

Then create game/constants.py with all magic numbers for a [DINO RUNNER / FLAPPY BIRD]:
- Screen size (800x600)
- Player dimensions
- Obstacle dimensions
- Spawn rates
- Physics (gravity, jump force, etc.)
- Speed scaling

Use dataclasses where it makes sense. Add type hints everywhere.
```

#### Prompt 1.2 — Game Engine Core

```
Create game/engine.py with a GameEngine class:

Methods needed:
- __init__(headless=False)
- update(dt) — apply physics, check collisions, spawn obstacles
- render() — draw to pygame surface (only if not headless)
- get_state() -> GameState — returns positions/velocities for sensors
- is_alive() -> bool
- get_score() -> float
- set_actions(jump: bool, duck: bool) — apply player actions this frame

Use AABB collision detection. Obstacles should recycle (off-screen → recycle to right).
Player should be represented as a simple rect with velocity.

Make sure the update loop is frame-rate independent (use dt parameter).
```

#### Prompt 1.3 — Sensor Extraction

```
Create game/sensors.py with a function:

def extract_inputs(game_state: GameState) -> list[float]:
    # Return normalized sensor inputs (all in range [0, 1] or [-1, 1])
    # For [DINO/FLAPPY], return these 8 / 5 inputs...
    
Inputs should be:
- [Dino: distance to obstacle, obstacle width, height, type, player y, player vy, speed, time since spawn]
- [Flappy: dist to pipes, dist to top, dist to bottom, player vy, player y]

Normalize everything to [-1, 1] or [0, 1]. Use constants from game/constants.py.
```

#### Prompt 1.4 — Headless Mode

```
Create game/headless.py with a GameHeadless class that runs the game without rendering.

class GameHeadless(GameEngine):
    def run_episode(self, network_controller) -> float:
        '''
        Run one full game episode.
        Each frame:
        1. Extract sensors
        2. Feed to network_controller (will pass a NeuralNetwork object in Week 2)
        3. Get actions (jump, duck)
        4. Update game
        5. Check death
        Return final score.
        '''

This should run at least 100x faster than rendered mode. Make sure there's no 
pygame drawing happening.
```

#### Prompt 1.5 — Main + Quick Test

```
Create main.py with a simple test:

from game.engine import GameEngine

game = GameEngine(headless=False)
for frame in range(60 * 5):  # 5 seconds at 60 FPS
    game.update(1/60)
    game.render()
    # Random actions for testing
    jump = random.random() > 0.7
    duck = random.random() > 0.8
    game.set_actions(jump, duck)

Print the final score. The game should run smoothly without crashes.
```

---

### **WEEK 2: Neural Network + Genome**

#### Prompt 2.1 — Innovation Tracker

```
Create neat/innovation.py with an InnovationTracker singleton:

class InnovationTracker:
    @classmethod
    def reset(cls):
        # Clear history, reset counter (called once per generation)
    
    @classmethod
    def get_innovation(cls, in_node: int, out_node: int) -> int:
        # If (in_node, out_node) pair already exists this generation, 
        # return its existing innovation number
        # Otherwise, increment counter and assign new number

Requirement: two mutations that add the same connection in the same generation
must receive the same innovation number. This is how crossover alignment works.
```

#### Prompt 2.2 — Node & Connection Genes

```
Create neat/genome.py with dataclasses:

@dataclass
class NodeGene:
    id: int
    type: str  # "input", "hidden", or "output"
    activation: str = "tanh"  # or "sigmoid"

@dataclass
class ConnectionGene:
    in_node: int
    out_node: int
    weight: float
    enabled: bool = True
    innovation: int = None

@dataclass
class Genome:
    inputs: int  # number of input nodes
    outputs: int  # number of output nodes
    nodes: dict[int, NodeGene]
    connections: dict[int, ConnectionGene]
    fitness: float = 0.0
    species_id: int = -1
    
    def copy(self) -> 'Genome':
        # Return a deep copy

Also add to Genome:
    def add_node(self, conn_to_split: ConnectionGene) -> NodeGene:
        # Split a connection: remove it, add new hidden node, add two new connections
        
    def add_connection(self, in_id: int, out_id: int) -> ConnectionGene:
        # Add new connection (get innovation number from InnovationTracker)
        
    def mutate_weights(self, mutate_rate=0.8, perturb_rate=0.9, perturb_power=0.1):
        # 80% of connections get mutation
        # Of those, 90% get perturbed (gaussian noise), 10% reset to random
```

#### Prompt 2.3 — Neural Network Evaluation

```
Create neat/network.py with a NeuralNetwork class:

class NeuralNetwork:
    def __init__(self, genome: Genome):
        # Build from genome
        # Topologically sort nodes (inputs → hidden → outputs)
        # Store activation functions
    
    def evaluate(self, inputs: list[float]) -> list[float]:
        # Forward pass
        # 1. Load inputs into input nodes
        # 2. Process hidden nodes (in topological order)
        # 3. Return output values
        
        Activations:
        - input: identity (no activation)
        - hidden: tanh
        - output: sigmoid (for binary decisions like jump/duck)

Use numpy for efficiency if evaluating many times per second, but pure Python 
is acceptable.
```

#### Prompt 2.4 — Manual Testing

```
Create a test script (test_week2.py):

1. Create a simple Genome with 8 inputs, 2 outputs
2. Add a few hidden nodes and connections manually
3. Create a NeuralNetwork from it
4. Feed random inputs and verify outputs are in [0, 1] range
5. Mutate the genome (add node, add connection, perturb weights)
6. Verify the network still runs
7. Time it: evaluate 100 times, should take <10ms

Print a network diagram (simple text representation) showing 
nodes and their connections.
```

---

### **WEEK 3: NEAT Evolution Loop**

#### Prompt 3.1 — Species Management

```
Create neat/species.py:

@dataclass
class Species:
    id: int
    representative: Genome
    members: list[Genome]
    best_fitness: float = 0.0
    stagnation_counter: int = 0
    
    def compute_adjusted_fitness(self):
        # For each member, divide fitness by species size
        # Returns list of adjusted fitnesses
        # This prevents one species from dominating

def compatibility_distance(g1: Genome, g2: Genome, c1=1.0, c2=1.0, c3=0.4) -> float:
    '''
    Calculate genetic distance between two genomes.
    d = (c1 * E + c2 * D) / N + c3 * W̄
    where:
    - E = excess genes (in g1 but not g2, or vice versa)
    - D = disjoint genes (in both but different structure)
    - N = max genes between them
    - W̄ = average weight difference of matching genes
    '''
    # Align by innovation number
    # Count excess/disjoint
    # Compute avg weight delta
    # Return distance
```

#### Prompt 3.2 — Speciation

```
Create a Speciation class in neat/species.py:

class Speciation:
    def speciate(self, genomes: list[Genome], existing_species: list[Species], 
                 threshold: float = 3.0) -> list[Species]:
        '''
        Assign each genome to a species.
        
        Algorithm:
        1. For each genome, compare to representative of each existing species
        2. If distance < threshold, add to that species
        3. If no match, create new species with this genome as representative
        4. Return updated species list
        '''
```

#### Prompt 3.3 — Crossover & Reproduction

```
Add to neat/genome.py:

def crossover(parent1: Genome, parent2: Genome) -> Genome:
    '''
    Assume parent1 is fitter (or equal).
    
    1. Align by innovation number
    2. For matching connections: random pick from parent1 or parent2
    3. For excess/disjoint: take from fitter parent (parent1)
    4. Copy inherited nodes
    5. Return child
    '''

def mutate(self, config: NEATConfig) -> None:
    '''
    Apply mutations in order:
    1. Mutate weights
    2. Add connection with probability config.add_conn_rate
    3. Add node with probability config.add_node_rate
    
    This is in-place mutation.
    '''
```

#### Prompt 3.4 — Population & Generation Loop

```
Create neat/population.py:

@dataclass
class NEATConfig:
    pop_size: int = 150
    c1: float = 1.0
    c2: float = 1.0
    c3: float = 0.4
    dt: float = 3.0  # speciation threshold
    weight_mutate_rate: float = 0.8
    weight_perturb_rate: float = 0.9
    weight_perturb_power: float = 0.1
    add_node_rate: float = 0.03
    add_conn_rate: float = 0.05
    max_stagnation: int = 20
    elitism: bool = True

class Population:
    def __init__(self, num_inputs: int, num_outputs: int, config: NEATConfig):
        self.genomes: list[Genome] = [create_initial_genome(...) for _ in range(config.pop_size)]
        self.species: list[Species] = []
        self.generation: int = 0
        self.config = config
        self.innovation_tracker = InnovationTracker()
    
    def evolve_one_generation(self, fitness_values: list[float]) -> None:
        '''
        Core evolution loop:
        
        1. Assign fitness to genomes
        2. InnovationTracker.reset()
        3. Speciate
        4. Compute adjusted fitness (fitness sharing)
        5. Cull bottom 50% per species
        6. Determine offspring allocation (proportional to avg adjusted fitness)
        7. Reproduce: elitism, crossover, mutation
        8. Check stagnation, kill stale species
        9. Update species reps
        10. Increment generation
        '''
    
    def get_best_genome(self) -> Genome:
        return max(self.genomes, key=lambda g: g.fitness)
```

#### Prompt 3.5 — Integration Test

```
Create test_week3.py:

1. Initialize Population with 8 inputs, 2 outputs
2. Run 5 generations:
   a. Create networks from genomes
   b. Assign random fitness (or use headless game from Week 1)
   c. Call evolve_one_generation(fitness_list)
3. Print stats each generation:
   - Best fitness
   - Avg fitness
   - Num species
   - Stagnation counts
4. Verify best fitness increases over generations (not guaranteed, but likely)

If you have the game from Week 1 integrated:
- Run each genome through headless game
- Use returned score as fitness
- Watch NEAT learn to play
```

---

### **WEEK 4: Visualizer & Polish**

#### Prompt 4.1 — Stats Tracker

```
Create visualizer/stats.py:

class GenerationStats:
    generation: int
    best_fitness: float
    avg_fitness: float
    num_species: int
    stagnation_counters: dict[int, int]  # species_id -> counter
    timestamp: float

class StatsHistory:
    def __init__(self):
        self.history: list[GenerationStats] = []
    
    def record(self, population: Population) -> None:
        # Compute stats from population, append to history
    
    def get_best_fitnesses(self) -> list[float]:
        return [s.best_fitness for s in self.history]
    
    def get_avg_fitnesses(self) -> list[float]:
        return [s.avg_fitness for s in self.history]
```

#### Prompt 4.2 — Network Visualizer

```
Create visualizer/network_viz.py:

class NetworkVisualizer:
    def __init__(self, width=300, height=400):
        # Will draw neural network graph on pygame surface
    
    def draw_network(self, network: NeuralNetwork, surface: pygame.Surface) -> None:
        '''
        Draw the network topology:
        1. Position nodes in layers (x by layer, y by rank within layer)
        2. Draw connections (thickness ∝ weight, darker if disabled)
        3. Color: input=blue, hidden=purple, output=green
        4. Label each node with activation type
        '''
```

#### Prompt 4.3 — Main Visualizer

```
Create visualizer/main_viz.py:

class NEATVisualizer:
    def __init__(self, game_engine: GameHeadless, population: Population):
        self.game = game_engine
        self.population = population
        self.stats = StatsHistory()
        self.paused = False
        self.speed_mult = 1.0
    
    def run(self):
        # Pygame window with:
        # - Top-left: best agent playing (live)
        # - Bottom-left: network graph of best agent
        # - Right: stats panel (best_fit, avg_fit, species_count, generation)
        # - Bottom-right: fitness curve plot
        
        # Main loop:
        # 1. Get user input (space=pause, R=reset, arrow keys, etc.)
        # 2. Run one evolution generation
        # 3. Render game for best genome
        # 4. Draw stats + network
        # 5. Draw fitness curve
```

#### Prompt 4.4 — Integration & Tuning

```
Update main.py to tie everything together:

from game.headless import GameHeadless
from neat.population import Population, NEATConfig
from visualizer.main_viz import NEATVisualizer

config = NEATConfig(
    pop_size=150,
    dt=3.0,
    max_stagnation=20
)

game = GameHeadless()
population = Population(num_inputs=8, num_outputs=2, config=config)
visualizer = NEATVisualizer(game, population)

# Main evolution loop with visualization
for generation in range(500):
    # Evaluate all genomes
    fitness_values = []
    for genome in population.genomes:
        network = NeuralNetwork(genome)
        score = game.run_episode(network)
        fitness_values.append(score)
    
    population.evolve_one_generation(fitness_values)
    visualizer.stats.record(population)
    visualizer.render()  # Draw one frame
    
    if generation % 10 == 0:
        print(f"Gen {generation}: best={max(fitness_values):.2f}, "
              f"avg={sum(fitness_values)/len(fitness_values):.2f}, "
              f"species={len(population.species)}")

print("Evolution complete!")
```

---

## Checkpoints & Testing

### Week 1 Checkpoint
- [ ] Game runs without crashing (human can play with arrow keys or space)
- [ ] Score increases as player progresses
- [ ] Obstacles spawn and move correctly
- [ ] Collision detection works (test by hitting obstacle)
- [ ] Headless mode runs 100 episodes in <5 seconds
- [ ] Sensors return normalized values (all in [−1, 1] or [0, 1])

### Week 2 Checkpoint
- [ ] InnovationTracker returns same number for same (in, out) pair within generation
- [ ] Genome can be created, mutated (weights, node, connection)
- [ ] Network evaluates correctly (outputs in [0, 1] for sigmoid)
- [ ] Topological sort works (no cycles in network)
- [ ] Network evaluation is deterministic (same inputs → same outputs)

### Week 3 Checkpoint
- [ ] Compatibility distance < threshold for two very similar genomes
- [ ] Compatibility distance > threshold for two very different genomes
- [ ] Speciation assigns genomes to species
- [ ] Crossover produces valid offspring (no broken connections)
- [ ] Evolution loop runs 5 generations without crashing
- [ ] Best fitness increases (or at least doesn't decrease rapidly)

### Week 4 Checkpoint
- [ ] Visualizer window opens and displays game
- [ ] Network graph renders without distortion
- [ ] Stats panel updates each generation
- [ ] Fitness curve plots correctly
- [ ] Can pause/resume and adjust speed
- [ ] Record best agent and save video (optional but impressive)

---

## Git Workflow Suggestions

```bash
# Week 1
git checkout -b week/1-game-engine
# ... commit game/constants.py, game/engine.py, game/sensors.py ...
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

## Hyperparameter Tuning (Week 4)

Start with these and tweak based on results:

```python
config = NEATConfig(
    pop_size=150,              # 100–200 is typical
    c1=1.0,                    # excess gene penalty
    c2=1.0,                    # disjoint gene penalty
    c3=0.4,                    # weight difference penalty
    dt=3.0,                    # speciation threshold (lower = more species)
    weight_mutate_rate=0.8,    # % of conns that mutate
    weight_perturb_rate=0.9,   # of those, % that get perturbed vs reset
    weight_perturb_power=0.1,  # gaussian std dev
    add_node_rate=0.03,        # low, rarely split connections
    add_conn_rate=0.05,        # slightly higher
    max_stagnation=20          # kill species after 20 gens with no improvement
)
```

**If convergence is too slow:** increase `pop_size`, decrease `dt` (more species = more innovation)
**If overfitting:** increase `max_stagnation`, decrease mutation rates
**If agents look random:** increase fitness rewards in game (fitness signal too weak)

---

## Common Pitfalls to Avoid

1. **Innovation numbers not aligned:** Crossover breaks if two genomes use different numbers for the same connection. Use global tracker.
2. **Fitness function too weak:** Agents learn to survive by doing nothing. Always reward progress, not just time alive.
3. **Network has cycles:** Topological sort will hang. Add cycle detection in network evaluation.
4. **Headless mode is slow:** Make sure you're not rendering. Remove pygame calls in headless path.
5. **Speciation threshold too low/high:** <1 = no species, all unique. >10 = one giant species (no speciation). Start at 3.
6. **Excess/disjoint genes flipped:** In crossover, both parents might be "fitter" if fitness is tied. Break ties by species age or genome size.
7. **Disabled genes not inherited:** Children of two parents should inherit disabled genes at higher rate (75% of disabled stays disabled even in child).

---

## What Success Looks Like

- **Gen 1–10:** Agents move randomly, score ~10–50
- **Gen 10–50:** Some agents accidentally beat obstacles, scores drift upward
- **Gen 50–100:** Visible improvement, strategy emerges (e.g., jump at specific range)
- **Gen 100–200:** Agents play almost perfectly, may plateau
- **Gen 200+:** Fine-tuning or overfitting (depends on game complexity)

By Week 4 (full month), you should have agents that:
- Play noticeably better than random (easily 5–10x higher score)
- Show learned behavior (consistent strategy, not luck)
- Have a diverse population (multiple species)
- Have stable fitness curves (not crashing, not random oscillation)

---

## Running Incrementally with Copilot

**Session 1 (30 min):** Run Prompt 1.1 + 1.2. You'll have a working game engine.

**Session 2 (30 min):** Run Prompt 1.3 + 1.4. Headless mode works.

**Session 3 (20 min):** Run Prompt 2.1 + 2.2. Genomes exist.

**Session 4 (30 min):** Run Prompt 2.3 + 2.4. Networks work.

**Session 5 (40 min):** Run Prompt 3.1 + 3.2. Speciation works.

**Session 6 (40 min):** Run Prompt 3.3 + 3.4. Full NEAT loop.

**Session 7 (30 min):** Run Prompt 4.1 + 4.2. Visualizer foundations.

**Session 8 (40 min):** Run Prompt 4.3 + 4.4. Full integration + tuning.

Each session can be a focused GitHub Copilot Chat. Paste the prompt, let it write the code, review and refine.

---

**Good luck with the sprint! Come back to this doc if you get stuck.**
