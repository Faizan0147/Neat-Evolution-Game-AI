# NEAT Flappy Bird — Quick Reference

## Files You Need to Keep Open

1. **02_NEAT_FLAPPY_BIRD.md** — the complete plan (source of truth)
2. **NEAT_COPILOT_GUIDE.md** — full session-by-session Antigravity prompts
3. **COPILOT_WORKFLOW.md** — how to work with Antigravity effectively (read once)
4. **This file** — paste shortcuts and architecture overview

---

## Quick Links

| Task | Where |
|------|-------|
| Get a session's prompt | NEAT_COPILOT_GUIDE.md → "Session-by-Session Prompts for Antigravity" |
| Understand NEAT algorithm | 02_NEAT_FLAPPY_BIRD.md → "Theory" |
| Architecture / data structures | 02_NEAT_FLAPPY_BIRD.md → "Core Data Structures" |
| Hyperparameter tuning | 02_NEAT_FLAPPY_BIRD.md → "Hyperparameter Tuning Reference" |
| Test checklist | NEAT_COPILOT_GUIDE.md → "Checkpoints & Testing" |
| CI/CD, Docker, DevOps | DEVOPS_GUIDE.md |

---

## Sessions (Ctrl+F Find These)

```
WEEK 1 (Game Engine + DevOps):
  Session 1 (~45 min) — Repo + DevOps scaffold
  Session 2 (~60 min) — Game engine + sensors + headless mode

WEEK 2 (Genome & Network):
  Session 3 (~50 min) — Innovation tracker + genome
  Session 4 (~50 min) — Neural network + integration test

WEEK 3 (NEAT Evolution):
  Session 5 (~60 min) — Speciation + crossover
  Session 6 (~60 min) — Population + generation loop

WEEK 4 (Visualizer):
  Session 7 (~60 min) — Stats + network graph + main visualizer
  Session 8 (~45 min) — Tuning + demo + release
```

---

## Copy-Paste Ready Prompts

### When You're Lost

```
I'm building NEAT from scratch for Flappy Bird. I'm on [WEEK X / Session N]
working on [COMPONENT].

Here's what I've built so far:
[paste your current code]

Here's what I need to build next:
[copy from NEAT_COPILOT_GUIDE.md Session N]

Help me.
```

### When Code Is Broken

```
This is failing:
[paste error]

The code is in [filename.py] around line [N].
The expected behavior is [describe what should happen].
What's wrong?
```

### When You Want to Understand

```
Explain why we use [concept]:
- Innovation numbers
- Compatibility distance
- Speciation
- Explicit fitness sharing
- Topological sort
```

---

## Key Classes to Know

```python
# GAME LAYER (Week 1)
GameEngine        → update(), render(), get_state(), set_action(), is_alive(), get_score()
GameHeadless       → run_episode(network) -> float
extract_inputs     → GameState -> list[float]  (5 normalised inputs)

# GENOME LAYER (Week 2)
NodeGene           → id, type (input/hidden/output), activation
ConnectionGene     → in_node, out_node, weight, enabled, innovation
Genome             → nodes dict, connections dict, fitness, species_id
NeuralNetwork      → feedforward from genome (topological sort)

# NEAT LAYER (Week 3)
InnovationTracker  → global singleton, get_innovation(in, out), reset()
Species            → representative, members, best_fitness, stagnation_counter
Population         → genomes, species, generation, config
NEATConfig         → all hyperparameters in one place (see below)

# EVOLUTION LOOP (Week 3)
population.evolve_one_generation(fitness_values)
  1. Assign fitness
  2. InnovationTracker.reset()
  3. Speciate (by compatibility distance)
  4. Fitness sharing (divide by species size)
  5. Cull bottom 50% per species
  6. Reproduce (elitism + crossover + mutation)
  7. Stagnation check, kill stale species
  8. Update representatives
  9. Increment generation
```

### NEATConfig defaults

```python
NEATConfig(
    pop_size=150,
    c1=1.0, c2=1.0, c3=0.4,
    dt=3.0,
    weight_mutate_rate=0.8,
    weight_perturb_rate=0.9,
    weight_perturb_power=0.1,
    add_node_rate=0.03,
    add_conn_rate=0.05,
    max_stagnation=20,
)
```

### Sensor inputs / output (5 → 1)

```
1. Horizontal distance to next pipe pair       [0, 1]
2. Vertical distance to top pipe               [-1, 1]
3. Vertical distance to bottom pipe            [-1, 1]
4. Player Y velocity                           [-1, 1]
5. Player Y position                           [0, 1]

Output: flap if sigmoid > 0.5, else do nothing
```

### Fitness formula

```python
fitness = (pipes_cleared ** 3) + (time_alive * 0.01)
```

---

## File Structure

```
neat-flappy/
├── game/
│   ├── constants.py          # All magic numbers
│   ├── engine.py              # Game loop
│   ├── sensors.py             # Extract inputs
│   └── headless.py            # Fast game runner
├── neat/
│   ├── config.py               # NEATConfig dataclass
│   ├── innovation.py           # Global tracker
│   ├── genome.py                # Genome + mutations
│   ├── network.py               # Neural net from genome
│   ├── species.py                # Species + compatibility
│   └── population.py             # Evolution loop
├── visualizer/
│   ├── stats.py                  # Stats tracker
│   ├── network_viz.py             # Network graph
│   └── main_viz.py                # Full visualizer
├── tests/
│   ├── conftest.py
│   ├── test_week1.py
│   ├── test_week2.py
│   ├── test_week3.py
│   └── test_week4.py
├── docs/
│   ├── 02_NEAT_FLAPPY_BIRD.md    # ← the plan, keep this open
│   ├── NEAT_COPILOT_GUIDE.md     # ← Antigravity prompts per session
│   ├── COPILOT_WORKFLOW.md       # ← how to work with Antigravity
│   ├── DEVOPS_GUIDE.md
│   └── QUICK_REFERENCE.md
├── .github/workflows/ci.yml
├── main.py
├── pyproject.toml
├── .pre-commit-config.yaml
└── Makefile
```

---

## Antigravity Usage Pattern

```
Every Session:
  1. Open docs/02_NEAT_FLAPPY_BIRD.md and docs/NEAT_COPILOT_GUIDE.md
  2. Find your session (Ctrl+F "Session N")
  3. Copy it
  4. Paste into Antigravity Chat
  5. Add context: @file.py if needed
  6. Review code
  7. Test locally
  8. Commit: git commit -m "feat(scope): description"
```

---

## Testing Checklist

### Week 1 ✓
- [ ] Game runs smooth (60 FPS)
- [ ] Collision detection works (pipe, ceiling, floor)
- [ ] Score increases as pipes are cleared
- [ ] Sensors return 5 values in [−1, 1] or [0, 1]
- [ ] Headless mode runs 150 episodes in <10s

### Week 2 ✓
- [ ] Innovation tracker returns same number for same pair, same generation
- [ ] Genome mutations work (weights, add node, add connection)
- [ ] Network output is in [0, 1] (sigmoid)
- [ ] Topological sort works (no cycles reach it)
- [ ] Network is deterministic

### Week 3 ✓
- [ ] Speciation groups similar genomes
- [ ] Crossover produces valid offspring
- [ ] Evolution loop runs 5, then 20, generations
- [ ] Best fitness increases (usually)
- [ ] Species count changes over time

### Week 4 ✓
- [ ] Visualizer renders (4 panels)
- [ ] Stats panel updates
- [ ] Network graph draws
- [ ] Fitness curve plots
- [ ] Can pause/resume, adjust speed, inspect agents

---

## Common Errors & Fixes

| Error | Likely Cause | Fix |
|-------|------|-----|
| `KeyError: innovation (X, Y) not found` | `InnovationTracker` not reset per generation | Call `InnovationTracker.reset()` at the start of each generation |
| `RecursionError in topological sort` | Cycle in network | Check `add_connection()` rejects cycles |
| `fitness is NaN` | Division by zero in fitness sharing | Check species size > 0 |
| `Network output out of [0, 1]` | Wrong activation function | Output layer must use sigmoid, hidden layer tanh |
| `Fitness doesn't increase` | Fitness function too weak, or pipes_cleared not updating | Verify `fitness = pipes_cleared**3 + time_alive*0.01` and that the counter increments |
| `Speciation not working` | Threshold too high or low | Try `dt=3.0` (raise if too many species, lower if too few) |

---

## Performance Targets

| Component | Target |
|-----------|--------|
| Headless game eval | 150 episodes in <10s |
| Network forward pass | <0.1ms |
| Speciation | <50ms for 150 genomes |
| Full generation | fast enough to run 200+ gens in one sitting |

If slower, profile with `python -m cProfile main.py`

---

## Git Workflow

```bash
# Each week
git checkout -b week/X-component

# Each session
git add .
git commit -m "feat(scope): [what you built]"

# At end of week
git checkout main
git merge week/X-component
```

---

## Emergency Restore

If you break something:

```bash
# See recent commits
git log --oneline

# Revert last commit
git reset --hard HEAD~1

# Or go back to a specific commit
git reset --hard COMMIT_HASH
```

---

## Resources Inside the Repo

- **02_NEAT_FLAPPY_BIRD.md** — the complete plan, paste at the start of any new chat
- **NEAT_COPILOT_GUIDE.md** — everything about architecture and session prompts
- **COPILOT_WORKFLOW.md** — how to work with Antigravity effectively
- **DEVOPS_GUIDE.md** — CI/CD, tooling, Docker (optional, Week 4)
- **README.md** — project overview and quick start

---

## Your First Steps

```bash
# 1. Clone repo
git clone https://github.com/YOUR_USERNAME/neat-flappy.git
cd neat-flappy

# 2. Install dependencies
pip install -e ".[dev]"
pre-commit install

# 3. Open Antigravity and open this folder as your project

# 4. Open these files in tabs:
#    - docs/02_NEAT_FLAPPY_BIRD.md (keep visible)
#    - docs/NEAT_COPILOT_GUIDE.md (keep visible)
#    - docs/COPILOT_WORKFLOW.md (read once)

# 5. Start Session 1 (repo + DevOps scaffold)
#    Copy the prompts into Antigravity Chat
#    Let it generate
#    Push, verify CI is green
```

---

**You're ready! Start with Session 1 in NEAT_COPILOT_GUIDE.md. 🚀**
