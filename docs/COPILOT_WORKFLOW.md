# Working with GitHub Copilot on NEAT Sprint

This guide explains **how to use Copilot** to build this project efficiently over 4 weeks.

## The Two-Strategy Approach

### Strategy A: File-Based (Better for Long Projects) ✅ RECOMMENDED

**What it is:** Keep a `.md` file in your repo that Copilot references.

**Setup:**
1. Save `docs/COPILOT_GUIDE.md` in your repo
2. Open it in VS Code **alongside** your code files
3. Copilot automatically sees it and uses context

**Workflow:**
```
1. Copy a weekly prompt from COPILOT_GUIDE.md
2. Paste it into Copilot Chat (Cmd+I in VS Code)
3. Copilot generates code
4. Review and accept changes
5. Commit to git
6. Next session: Copilot remembers previous context from the file
```

**Pros:**
- Accumulates context over 4 weeks
- One source of truth (the guide)
- You can update it as you learn
- Easy to reference specific sections
- Works across multiple sessions

**Cons:**
- Slightly longer setup time per prompt
- Requires keeping the guide file open

---

### Strategy B: Chat-Only (Faster for Individual Sessions)

**What it is:** Copy-paste prompts directly into Copilot Chat, one per session.

**Setup:**
1. Open Copilot Chat (Cmd+K in VS Code)
2. Open `COPILOT_GUIDE.md` in a split window
3. Copy a prompt

**Workflow:**
```
1. Paste prompt into Copilot Chat
2. Click "Use file..." to add current file context if needed
3. Let Copilot generate
4. Accept and commit
5. Start fresh next session (no cross-session memory)
```

**Pros:**
- Fast, no setup
- Self-contained sessions
- Good for focused coding sprints

**Cons:**
- Lost context between sessions
- Need to re-explain architecture each time
- Not ideal for 4-week project

---

## ✅ Recommended Workflow

**Hybrid approach — best of both:**

### Session Structure

```
BEFORE coding:
├─ Open VS Code
├─ Open docs/COPILOT_GUIDE.md in sidebar
├─ Open your working file (e.g., game/engine.py)
└─ Ready to go

DURING coding (per prompt):
1. Find your weekly prompt in COPILOT_GUIDE.md
2. Copy it (Cmd+C)
3. Open Copilot Chat (Cmd+K)
4. Paste the prompt
5. Add file context:
   - Copilot Chat can see open files
   - Mention specific files if needed: "@game/engine.py"
6. Review generated code:
   ✓ Does it match the prompt?
   ✓ Is it consistent with existing code?
   ✓ Are type hints present?
   ✓ Does it look efficient?
7. Accept or request changes
8. Test locally
9. Commit: git add . && git commit -m "Week X: [component]"

AFTER session:
└─ Leave COPILOT_GUIDE.md open for next time
```

---

## Specific Copilot Techniques

### 1. **File Context** — Tell Copilot What to Look At

❌ Bad:
```
Create a function to evaluate a network
```

✅ Good:
```
In game/sensors.py, create a function extract_inputs(game_state) that returns 
a list of 8 normalized floats. See game/constants.py for screen size and game/engine.py 
for GameState structure. Use the sensor definitions in the prompt above.
```

**How to do it in Copilot Chat:**
- Type `@filename.py` to reference a file
- Type `#` to reference a function/class
- Copilot will fetch the context

### 2. **Iterative Refinement** — Don't Accept Perfect Code First

Copilot rarely generates perfect code on first try. This is **expected**. Workflow:

```
Round 1:
You: [paste prompt]
Copilot: [generates code]
You: "This looks good but missing type hints. Add @dataclass decorator and 
       type hints for all parameters."

Round 2:
Copilot: [refines code]
You: "Now add docstrings for the copy() method explaining what it does."

Round 3:
Copilot: [adds docstrings]
You: ✓ Accept
```

This is **normal and expected**. Copilot is a co-pilot, not autopilot.

### 3. **Architecture Decisions** — Ask Copilot to Explain

```
Why use dict[int, NodeGene] instead of list[NodeGene] for storing nodes?
```

Copilot will explain:
- Lookup by ID is O(1) vs O(n)
- Gaps in ID sequence are fine
- Matches how NEAT papers describe genome

### 4. **Testing** — Ask Copilot to Write Tests

After Copilot generates a class:
```
Write pytest tests for the Genome class that verify:
1. copy() creates independent copies
2. add_node() increases node count and updates connections
3. add_connection() creates innovation numbers correctly
```

### 5. **Code Review** — Ask Copilot to Review Its Own Code

```
Review this code for bugs or inefficiencies:
[paste code from genome.py]

Specific things to check:
- Are there any off-by-one errors in the topological sort?
- Could any numpy operations be vectorized?
- Are there any missing edge cases?
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
I'm building a NEAT evolution system. This is Week 1 of 4, focusing on the game engine.
I have game/constants.py with screen size and physics constants.

REQUIREMENTS:
Create game/engine.py with a GameEngine class that:
- Runs at 60 FPS
- Handles jump/duck actions from a neural network
- Detects collisions with obstacles
- Returns current game state (for sensors)
- Works in both rendered and headless mode

CODE STYLE:
- Use type hints for all function signatures
- Add docstrings to public methods
- Use dataclass for GameState
- Keep constants in game/constants.py, don't hardcode

EXAMPLE:
class GameEngine:
    def update(self, dt: float) -> None:
        """Update game physics and state for dt seconds."""
        ...
```

This structure gets better results than vague requests.

---

## Common Copilot Pitfalls & How to Avoid

### Pitfall 1: "Generate the whole project"

❌ Don't:
```
Build the entire NEAT system
```

✅ Do:
```
Create game/engine.py with these methods: update(), render(), get_state(), 
set_actions(). Use this class skeleton...
```

**Why:** Copilot works best on scoped tasks (~100–200 lines). Asking for 2000 lines at once produces worse code.

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

### Week 1: Game Engine

- [ ] Read System Context section in COPILOT_GUIDE.md
- [ ] Copy Prompt 1.1 (Project Setup) → Copilot Chat
- [ ] Accept generated structure
- [ ] Copy Prompt 1.2 (Game Engine Core) → Copilot Chat
- [ ] Test game runs: `python main.py` (with random inputs)
- [ ] Copy Prompt 1.3 (Sensor Extraction) → Copilot Chat
- [ ] Copy Prompt 1.4 (Headless Mode) → Copilot Chat
- [ ] Run benchmark: 100 headless episodes in <5 seconds?
- [ ] Commit: `git commit -m "Week 1: Game engine complete"`

### Week 2: Neural Networks

- [ ] Copy Prompt 2.1 (Innovation Tracker) → Copilot Chat
- [ ] Copy Prompt 2.2 (Genomes) → Copilot Chat
- [ ] Copy Prompt 2.3 (Network Evaluation) → Copilot Chat
- [ ] Test network: `python test_week2.py`
- [ ] Network outputs in [0, 1]? Run 100 evals fast (<10ms)?
- [ ] Commit: `git commit -m "Week 2: Genomes and networks complete"`

### Week 3: NEAT Evolution

- [ ] Copy Prompt 3.1 (Species) → Copilot Chat
- [ ] Copy Prompt 3.2 (Speciation) → Copilot Chat
- [ ] Copy Prompt 3.3 (Crossover) → Copilot Chat
- [ ] Copy Prompt 3.4 (Population) → Copilot Chat
- [ ] Test evolution: `python test_week3.py` (5 generations)
- [ ] Best fitness increasing? Speciation working?
- [ ] Commit: `git commit -m "Week 3: NEAT evolution loop complete"`

### Week 4: Visualizer & Polish

- [ ] Copy Prompt 4.1 (Stats Tracker) → Copilot Chat
- [ ] Copy Prompt 4.2 (Network Visualizer) → Copilot Chat
- [ ] Copy Prompt 4.3 (Main Visualizer) → Copilot Chat
- [ ] Copy Prompt 4.4 (Integration) → Copilot Chat
- [ ] Run `python main.py` for 100 generations
- [ ] Watch fitness curve increase?
- [ ] Test controls: space (pause), R (reset), speed (arrows)
- [ ] Commit: `git commit -m "Week 4: Visualizer and final integration"`

---

## Tips for Faster Development

### Tip 1: Keep Your Git History Clean

```bash
# After each prompt, commit immediately
git add .
git commit -m "Week X: [what you just built]"

# This way, if something breaks, you can revert easily
git revert HEAD  # Undo last commit
```

### Tip 2: Test After Each Prompt

```python
# Create mini test files for each component
# test_week2.py — just check networks work
# Run after Prompt 2.3

from neat.network import NeuralNetwork
from neat.genome import Genome

g = Genome(inputs=8, outputs=2)
net = NeuralNetwork(g)
output = net.evaluate([0.5] * 8)
assert len(output) == 2
assert all(0 <= x <= 1 for x in output)
print("✓ Network works")
```

### Tip 3: Use Comments as Checkpoints

```python
class NeuralNetwork:
    def __init__(self, genome: Genome):
        # CHECKPOINT: Network built, nodes in topological order
        self.nodes = self._topological_sort()
        
    def evaluate(self, inputs: list[float]) -> list[float]:
        # CHECKPOINT: All inputs loaded into input layer
        # CHECKPOINT: All hidden nodes processed
        # CHECKPOINT: Outputs computed and returned
        ...
```

When you come back to code later, these checkpoints help you understand what's done.

### Tip 4: Ask Copilot to Help Debug

When something breaks:

```
This test is failing:
[paste error]

The function is in game/engine.py around line 45.
The test expects score to increase when obstacles are cleared.
Help me debug.
```

Copilot is surprisingly good at debugging. Paste error messages, it usually spots the issue.

---

## Session Length Recommendations

**Ideal session structure:**

```
📌 BEFORE: 5 min
   - Read the prompt in COPILOT_GUIDE.md
   - Review related code (existing modules)
   - Have a clear mental model

💬 COPILOT: 10 min
   - Paste prompt
   - Iterate 2–3 times if needed
   - Accept the code

✅ TEST: 10 min
   - Run your test
   - Make sure it works
   - No errors?

📝 COMMIT: 5 min
   - Stage changes
   - Write clear commit message
   - Done!

---
Total: ~30 min per prompt (can be faster with practice)
```

---

## Troubleshooting Copilot

### Issue: "Copilot is suggesting wrong code"

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

### Issue: "Copilot forgot what we built earlier"

**Solution:** This is normal. Tell Copilot what you already have:

```
I've already built game/engine.py and neat/genome.py. Now I need neat/network.py.
The Genome class has these fields: @dataclass class Genome:
    nodes: dict[int, NodeGene]
    connections: dict[int, ConnectionGene]

Create NeuralNetwork that takes a Genome and can evaluate it.
```

### Issue: "Generated code has bugs"

**Solution:** Ask Copilot to fix it:

```
This function has a bug — it returns None on line 23 instead of a list.
[paste function]

Also add type hints.
```

---

## Final Advice

1. **Use Copilot as a co-pilot, not a replacement.** You're still the architect; Copilot is the code generator.
2. **Never blindly accept code.** Read it, understand it, test it.
3. **Keep COPILOT_GUIDE.md in your workspace.** Copilot can reference it automatically.
4. **Commit frequently.** Each prompt = one commit. This saves you if something breaks.
5. **When stuck, ask for help differently.** If one prompt isn't working, rephrase it and try again.

---

**You've got this! 🚀**

Feel free to come back to this guide as you work through the 4 weeks. Update it with what works for you.
