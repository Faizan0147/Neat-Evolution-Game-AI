# NEAT Sprint — Quick Reference

## Files You Need to Keep Open

1. **COPILOT_GUIDE.md** — Full specs and prompts (reference while coding)
2. **COPILOT_WORKFLOW.md** — How to use Copilot effectively (read once)
3. **This file** — Paste shortcuts and architecture overview

---

## Quick Links

| Task | Where |
|------|-------|
| Get a weekly prompt | COPILOT_GUIDE.md → "Weekly Prompts for Copilot" |
| Understand NEAT algorithm | COPILOT_GUIDE.md → "NEAT Algorithm" tab |
| Architecture decisions | COPILOT_GUIDE.md → "Data Structures" |
| Hyperparameter tuning | COPILOT_GUIDE.md → bottom section |
| Test checklist | COPILOT_GUIDE.md → "Checkpoints & Testing" |

---

## Weekly Prompts (Ctrl+F Find These)

```
WEEK 1 (Game Engine):
  Prompt 1.1 — Project Setup & Game Architecture
  Prompt 1.2 — Game Engine Core
  Prompt 1.3 — Sensor Extraction
  Prompt 1.4 — Headless Mode
  Prompt 1.5 — Main + Quick Test

WEEK 2 (Genome & Network):
  Prompt 2.1 — Innovation Tracker
  Prompt 2.2 — Node & Connection Genes
  Prompt 2.3 — Neural Network Evaluation
  Prompt 2.4 — Manual Testing

WEEK 3 (NEAT Evolution):
  Prompt 3.1 — Species Management
  Prompt 3.2 — Speciation
  Prompt 3.3 — Crossover & Reproduction
  Prompt 3.4 — Population & Generation Loop
  Prompt 3.5 — Integration Test

WEEK 4 (Visualizer):
  Prompt 4.1 — Stats Tracker
  Prompt 4.2 — Network Visualizer
  Prompt 4.3 — Main Visualizer
  Prompt 4.4 — Integration & Tuning
```

---

## Copy-Paste Ready Prompts

### When You're Lost

```
I'm building NEAT from scratch. I'm on [WEEK X] working on [COMPONENT].

Here's what I've built so far:
[paste your current code]

Here's what I need to build next:
[copy from COPILOT_GUIDE.md Prompt X.X]

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
# GENOME LAYER (Week 2)
NodeGene          → id, type (input/hidden/output), activation
ConnectionGene    → in_node, out_node, weight, enabled, innovation
Genome            → nodes dict, connections dict, fitness
NeuralNetwork     → feedforward from genome

# NEAT LAYER (Week 3)
InnovationTracker → global singleton, get_innovation(in, out)
Species           → representative, members, best_fitness, stagnation
Population        → genomes, species, generation, config
NEATConfig        → all hyperparameters in one place

# EVOLUTION LOOP (Week 3)
population.evolve_one_generation(fitness_values)
  1. Assign fitness
  2. Speciate (by compatibility distance)
  3. Fitness sharing (divide by species size)
  4. Cull bottom 50% per species
  5. Reproduce (elitism + crossover + mutation)
  6. Check stagnation
  7. Update representatives
```

---

## File Structure

```
neat-sprint/
├── game/
│   ├── constants.py         # All magic numbers
│   ├── engine.py            # Game loop
│   ├── sensors.py           # Extract inputs
│   └── headless.py          # Fast game runner
├── neat/
│   ├── innovation.py        # Global tracker
│   ├── genome.py            # Genome + mutations
│   ├── network.py           # Neural net from genome
│   ├── species.py           # Species + compatibility
│   └── population.py        # Evolution loop
├── visualizer/
│   ├── stats.py             # Stats tracker
│   ├── network_viz.py       # Network graph
│   └── main_viz.py          # Full visualizer
├── tests/
│   ├── test_week1.py
│   ├── test_week2.py
│   └── test_week3.py
├── main.py                  # Wire everything
├── requirements.txt
├── README.md
├── COPILOT_GUIDE.md         # ← Keep this open
├── COPILOT_WORKFLOW.md      # ← Read this once
└── .gitignore
```

---

## Copilot Usage Pattern

```
Every Session:
  1. Open COPILOT_GUIDE.md
  2. Find your prompt (Ctrl+F)
  3. Copy it
  4. Paste into Copilot Chat (Cmd+K)
  5. Add context: @file.py if needed
  6. Review code
  7. Test locally
  8. Commit: git commit -m "Week X: description"
```

---

## Testing Checklist

### Week 1 ✓
- [ ] Game runs smooth (60 FPS)
- [ ] Collision detection works
- [ ] Score increases
- [ ] Sensors return [−1, 1] or [0, 1]
- [ ] Headless mode runs 100 episodes in <5s

### Week 2 ✓
- [ ] Innovation tracker returns same number for same pair
- [ ] Genome mutations work
- [ ] Network outputs are [0, 1] (sigmoid)
- [ ] Topological sort works (no cycles)
- [ ] Network is deterministic

### Week 3 ✓
- [ ] Speciation groups similar genomes
- [ ] Crossover produces valid offspring
- [ ] Evolution loop runs 5 generations
- [ ] Best fitness increases (usually)
- [ ] Species count changes over time

### Week 4 ✓
- [ ] Visualizer renders
- [ ] Stats panel updates
- [ ] Network graph draws
- [ ] Fitness curve plots
- [ ] Can pause/resume

---

## Common Errors & Fixes

| Error | Likely Cause | Fix |
|-------|------|-----|
| `KeyError: innovation (X, Y) not found` | InnovationTracker not reset per generation | Add `InnovationTracker.reset()` at start of generate |
| `RecursionError in topological sort` | Cycle in network | Check `add_connection()` doesn't create cycles |
| `fitness is NaN` | Division by zero in fitness sharing | Check species size > 0 |
| `Network outputs are [-5, 5]` | Wrong activation function | Use sigmoid/tanh, not ReLU |
| `Fitness doesn't increase` | Fitness function too weak | Make rewards quadratic: `distance**2` |
| `Speciation not working` | Threshold too high or low | Try dt=3.0 (change if too many/few species) |

---

## Performance Targets

| Component | Target |
|-----------|--------|
| Headless game eval | 100 evals/sec |
| Network forward pass | <0.1ms |
| Speciation | <50ms for 150 genomes |
| Full generation | <10s for 150 pop |

If slower, profile with `python -m cProfile main.py`

---

## Git Workflow

```bash
# Each week
git checkout -b week/X-component

# Each prompt
git add .
git commit -m "Week X: [what you built]"

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

# Or go back to specific commit
git reset --hard COMMIT_HASH
```

---

## Resources Inside the Repo

- **COPILOT_GUIDE.md** — Everything about architecture and prompts
- **COPILOT_WORKFLOW.md** — How to work with Copilot effectively
- **README.md** — Project overview and quick start

---

## Your First Steps

```bash
# 1. Clone repo
git clone https://github.com/YOUR_USERNAME/neat-sprint.git
cd neat-sprint

# 2. Install dependencies
pip install -r requirements.txt

# 3. Open VS Code
code .

# 4. Open these files in tabs:
#    - game/engine.py (or constants.py)
#    - COPILOT_GUIDE.md (keep visible)
#    - COPILOT_WORKFLOW.md (read once)

# 5. Start Week 1, Prompt 1.1
#    Copy prompt into Copilot Chat (Cmd+K)
#    Let it generate
#    Test: python main.py
```

---

**You're ready! Start with Prompt 1.1 in COPILOT_GUIDE.md. 🚀**
