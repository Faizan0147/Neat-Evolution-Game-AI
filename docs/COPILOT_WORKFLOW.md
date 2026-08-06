# Working with Antigravity on NEAT Flappy Bird

This guide explains **how to use Antigravity** to build this project efficiently over 4 weeks / 8 sessions. (The techniques here apply just as well to GitHub Copilot or another AI pair-programmer — Antigravity is simply this project's IDE of choice, per `docs/02_NEAT_FLAPPY_BIRD.md`.)

## The Two-Strategy Approach

### Strategy A: File-Based (Better for Long Projects) ✅ RECOMMENDED

**What it is:** Keep the `.md` plan files in your repo that Antigravity references.

**Setup:**
1. Save `docs/02_NEAT_FLAPPY_BIRD.md` and `docs/NEAT_COPILOT_GUIDE.md` in your repo
2. Open them in Antigravity **alongside** your code files
3. Antigravity automatically sees open files and uses them as context

**Workflow:**
```
1. Copy a session's prompts from NEAT_COPILOT_GUIDE.md
2. Paste it into Antigravity Chat
3. Antigravity generates code
4. Review and accept changes
5. Commit to git
6. Next session: Antigravity picks up context from the open docs again
```

**Pros:**
- Accumulates context over 4 weeks
- One source of truth (`02_NEAT_FLAPPY_BIRD.md`)
- You can update it as you learn
- Easy to reference specific sections
- Works across multiple sessions

**Cons:**
- Slightly longer setup time per prompt
- Requires keeping the docs open

---

### Strategy B: Chat-Only (Faster for Individual Sessions)

**What it is:** Copy-paste prompts directly into Antigravity Chat, one session at a time.

**Setup:**
1. Open Antigravity Chat
2. Open `NEAT_COPILOT_GUIDE.md` in a split pane
3. Copy a session's prompts

**Workflow:**
```
1. Paste the session's prompts into Antigravity Chat
2. Reference relevant files (@filename) for extra context if needed
3. Let Antigravity generate
4. Accept and commit
5. Start fresh next session (no cross-session memory unless you keep the docs open)
```

**Pros:**
- Fast, no setup
- Self-contained sessions
- Good for focused coding sprints

**Cons:**
- Lost context between sessions
- Need to re-explain architecture each time
- Not ideal for a 4-week project

---

## ✅ Recommended Workflow

**Hybrid approach — best of both:**

### Session Structure

```
BEFORE coding:
├─ Open Antigravity
├─ Open docs/02_NEAT_FLAPPY_BIRD.md and docs/NEAT_COPILOT_GUIDE.md in the sidebar
├─ Open your working file (e.g., game/engine.py)
└─ Ready to go

DURING coding (per session):
1. Find your session's prompts in NEAT_COPILOT_GUIDE.md (Session 1-8)
2. Copy them
3. Open Antigravity Chat
4. Paste the prompts
5. Add file context:
   - Antigravity Chat can see open files
   - Reference specific files if needed: "@game/engine.py"
6. Review generated code:
   ✓ Does it match the prompt?
   ✓ Is it consistent with existing code?
   ✓ Are type hints present?
   ✓ Does it look efficient?
7. Accept or request changes
8. Test locally
9. Commit: git add . && git commit -m "feat(scope): what you just built"

AFTER session:
└─ Leave the docs open for next time
```

---

## Specific Antigravity Techniques

### 1. **File Context** — Tell Antigravity What to Look At

❌ Bad:
```
Create a function to evaluate a network
```

✅ Good:
```
In game/sensors.py, create a function extract_inputs(game_state) that returns
a list of 5 normalized floats (see docs/02_NEAT_FLAPPY_BIRD.md → "Neural
Network Interface"). See game/constants.py for screen size and game/engine.py
for the GameState structure.
```

**How to do it in Antigravity Chat:**
- Type `@filename.py` to reference a file
- Type `@` then a symbol name to reference a specific function/class
- Antigravity will pull in that context automatically

### 2. **Iterative Refinement** — Don't Accept Perfect Code First

Antigravity rarely generates perfect code on the first try. This is **expected**. Workflow:

```
Round 1:
You: [paste session prompt]
Antigravity: [generates code]
You: "This looks good but missing type hints. Add @dataclass decorator and
       type hints for all parameters."

Round 2:
Antigravity: [refines code]
You: "Now add docstrings for the copy() method explaining what it does."

Round 3:
Antigravity: [adds docstrings]
You: ✓ Accept
```

This is **normal and expected**. Antigravity is a pair-programmer, not autopilot.

### 3. **Architecture Decisions** — Ask Antigravity to Explain

Both `02_NEAT_FLAPPY_BIRD.md` and `NEAT_COPILOT_GUIDE.md` call out specific "Ask Antigravity to EXPLAIN" prompts per session, e.g.:

```
Why does add_node() disable the original connection instead of deleting it?
What is the purpose of cycle detection in add_connection()?
Why do excess/disjoint genes only come from the fitter parent?
```

Highlight the relevant code, then ask — Antigravity will explain:
- The design tradeoff (e.g. dict[int, NodeGene] gives O(1) lookup by innovation-stable ID)
- How it maps back to the NEAT paper's concepts
- Edge cases you might be missing

### 4. **Testing** — Ask Antigravity to Write Tests

After Antigravity generates a class:
```
Write pytest tests for the Genome class that verify:
1. copy() creates independent copies
2. add_node() increases node count and updates connections
3. add_connection() creates innovation numbers correctly and rejects cycles
```

### 5. **Code Review** — Ask Antigravity to Review Its Own Code

```
Review this code for bugs or inefficiencies:
[paste code from genome.py]

Specific things to check:
- Are there any off-by-one errors in the topological sort?
- Could any numpy operations be vectorized?
- Are there any missing edge cases (e.g. innovation counter reset)?
```

---

## Prompt Structure That Works Best

Every prompt should have:

```
CONTEXT:
[What you're building, why, where it fits in the project]

REQUIREMENTS:
[What the code should do, bullet points]

CODE STYLE:
[Specific expectations: type hints, docstrings, etc.]

EXAMPLE:
[Show format/pattern if not obvious]
```

**Example:**

```
CONTEXT:
I'm building NEAT from scratch. This is Session 2 of 8, focusing on the
Flappy Bird game engine. I have game/constants.py with screen size and
physics constants already.

REQUIREMENTS:
Create game/engine.py with a GameEngine class that:
- Runs at 60 FPS
- Handles the flap action from a neural network
- Detects collisions with pipes, ceiling, and floor
- Returns current game state (for sensors)
- Works in both rendered and headless mode

CODE STYLE:
- Use type hints for all function signatures
- Add docstrings to public methods
- Use a dataclass for GameState
- Keep constants in game/constants.py, don't hardcode

EXAMPLE:
class GameEngine:
    def update(self, dt: float) -> None:
        """Update game physics and state for dt seconds."""
        ...
```

This structure gets better results than vague requests.

---

## Common Pitfalls & How to Avoid Them

### Pitfall 1: "Generate the whole project"

❌ Don't:
```
Build the entire NEAT system
```

✅ Do:
```
Create game/engine.py with these methods: update(), render(), get_state(),
set_action(). Use this class skeleton...
```

**Why:** Antigravity works best on scoped tasks (~100–200 lines). Asking for 2000 lines at once produces worse code.

### Pitfall 2: Forgetting to Give Context

❌ Don't:
```
Add a mutate() method
```

✅ Do:
```
Add a mutate() method to the Genome class that:
1. Mutates weights with 80% probability (use weight_mutate_rate from config)
2. Adds a new node with 3% probability (use add_node() method)
3. Adds a new connection with 5% probability
The method should be in-place (modify self, don't return)
```

### Pitfall 3: Not Specifying Output Format

❌ Don't:
```
Compute compatibility distance between genomes
```

✅ Do:
```
Implement def compatibility_distance(g1: Genome, g2: Genome) -> float:
The formula is: δ = (c1·E + c2·D) / N + c3·W̄
where E=excess, D=disjoint, N=max genes, W̄=avg weight diff.
Return a float in range [0, ∞).
```

---

## Weekly Checklist

### Week 1: Game Engine + DevOps

- [ ] Read System Context section in `NEAT_COPILOT_GUIDE.md`
- [ ] Session 1 — repo + DevOps scaffold (pyproject.toml, Makefile, pre-commit, CI)
- [ ] Push → verify GitHub Actions goes green
- [ ] Session 2 — game engine + sensors + headless mode
- [ ] Test game runs: `python main.py` (bird falls, dies at first pipe)
- [ ] Run benchmark: 150 headless episodes in <10 seconds
- [ ] Commit: `git commit -m "feat(game): flappy bird engine, sensors, headless mode"`

### Week 2: Genome + Neural Network

- [ ] Session 3 — innovation tracker + genome
- [ ] Ask Antigravity to explain `add_node()` and cycle detection
- [ ] Commit: `git commit -m "feat(neat): innovation tracker and genome dataclasses"`
- [ ] Session 4 — neural network + integration test
- [ ] Network outputs in [0, 1]? Runs fast?
- [ ] Commit: `git commit -m "feat(neat): feedforward neural network from genome"`

### Week 3: NEAT Evolution

- [ ] Session 5 — speciation + crossover
- [ ] Commit: `git commit -m "feat(neat): species, compatibility distance, crossover"`
- [ ] Session 6 — population + generation loop
- [ ] Test evolution: 5 generations, then 20 (birds start clearing 1-2 pipes)
- [ ] Best fitness increasing? Speciation working?
- [ ] Commit: `git commit -m "feat(neat): population and full generation loop"`

### Week 4: Visualizer & Polish

- [ ] Session 7 — stats + network graph + main visualizer
- [ ] Run `python main.py` — window opens, birds visible, network draws
- [ ] Commit: `git commit -m "feat(visualizer): 4-panel live evolution view"`
- [ ] Session 8 — tuning + demo + release
- [ ] Run 200 generations, tag `v0.1.0`
- [ ] Record a video of the best agent (gen 100+) playing

---

## Tips for Faster Development

### Tip 1: Keep Your Git History Clean

```bash
# After each session, commit immediately
git add .
git commit -m "feat(scope): what you just built"

# This way, if something breaks, you can revert easily
git revert HEAD  # Undo last commit
```

### Tip 2: Test After Each Session

```python
# Mini test files per week — see tests/test_week1.py .. test_week4.py
from neat.network import NeuralNetwork
from neat.genome import Genome

g = Genome(inputs=5, outputs=1)
net = NeuralNetwork(g)
output = net.evaluate([0.5] * 5)
assert len(output) == 1
assert 0 <= output[0] <= 1
print("✓ Network works")
```

### Tip 3: Use Comments as Checkpoints

```python
class NeuralNetwork:
    def __init__(self, genome: Genome):
        # CHECKPOINT: Network built, nodes in topological order
        self.nodes = self._topological_sort()

    def evaluate(self, inputs: list[float]) -> list[float]:
        # CHECKPOINT: All 5 inputs loaded into input layer
        # CHECKPOINT: All hidden nodes processed
        # CHECKPOINT: Output computed and returned
        ...
```

When you come back to code later, these checkpoints help you understand what's done.

### Tip 4: Ask Antigravity to Help Debug

When something breaks:

```
This test is failing:
[paste error]

The function is in game/engine.py around line 45.
The test expects score to increase when pipes are cleared.
Help me debug.
```

---

## Session Length Recommendations

Actual session lengths per `02_NEAT_FLAPPY_BIRD.md`:

```
Session 1: ~45 min   Session 5: ~60 min
Session 2: ~60 min   Session 6: ~60 min
Session 3: ~50 min   Session 7: ~60 min
Session 4: ~50 min   Session 8: ~45 min
```

**Ideal structure within a session:**

```
📌 BEFORE: 5 min   — read the prompts, review related code, have a mental model
💬 CURSOR: bulk of the time — paste prompts, iterate 2–3 times, accept the code
✅ TEST: — run your test, make sure it works, no errors
📝 COMMIT: — stage changes, write a clear commit message
```

---

## Troubleshooting Antigravity

### Issue: "Antigravity is suggesting wrong code"

**Solution:** Be more specific. Add examples, show similar code from your project.

```
Looking at game/engine.py, I need another method like update() but for physics.
Create a _apply_physics() method that:
1. Updates velocity from gravity (use GRAVITY constant)
2. Updates position from velocity
3. Clamps Y to screen bounds

Here's update() for reference:
[show your update() method]
```

### Issue: "Antigravity forgot what we built earlier"

**Solution:** This is normal. Tell Antigravity what you already have, or make sure the relevant files are open in your workspace so it picks them up as context.

```
I've already built game/engine.py and neat/genome.py. Now I need neat/network.py.
The Genome class has these fields:
@dataclass
class Genome:
    nodes: dict[int, NodeGene]
    connections: dict[int, ConnectionGene]

Create NeuralNetwork that takes a Genome and can evaluate it.
```

### Issue: "Generated code has bugs"

**Solution:** Ask Antigravity to fix it:

```
This function has a bug — it returns None on line 23 instead of a list.
[paste function]

Also add type hints.
```

---

## Final Advice

1. **Use Antigravity as a pair-programmer, not a replacement.** You're still the architect; Antigravity is the code generator.
2. **Never blindly accept code.** Read it, understand it, test it.
3. **Keep `02_NEAT_FLAPPY_BIRD.md` and `NEAT_COPILOT_GUIDE.md` open in your workspace.** Antigravity references them automatically.
4. **Commit frequently.** Each session ≈ one or two commits. This saves you if something breaks.
5. **When stuck, ask for help differently.** If one prompt isn't working, rephrase it and try again.

---

**You've got this! 🚀**

Feel free to come back to this guide as you work through the 4 weeks. Update it with what works for you.
