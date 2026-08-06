# Learning Mode — How to Actually Understand NEAT While Building This

> Companion to `NEAT_COPILOT_GUIDE.md`. Read this first if your goal is to
> *understand* NEAT deeply, not just end up with a working repo. Use this
> guide instead of the raw session prompts for Sessions 3, 4, 5, and 6 — the
> sessions where the actual NEAT algorithm lives.

---

## Why This Exists

`NEAT_COPILOT_GUIDE.md` is written as agent instructions: paste a session's
prompt, the agent generates a working file. That's great for shipping fast.
It's bad for learning, because nothing forces you to engage with *why* the
code works — you can watch 150 correct lines appear and understand none of
them.

**The rule for this project:** infrastructure gets built by the agent.
Algorithm gets built by you, with the agent as a tutor, not an author.

| Category | Sessions | Who writes it |
|---|---|---|
| Game engine, pygame rendering, DevOps/CI | 1, 2 (game part), 7 (drawing code), 8 | Agent — not the point of this project |
| **The NEAT algorithm itself** | **2 (sensors), 3, 4, 5, 6** | **You, with the agent reviewing** |

Sessions 3, 4, 5, 6 are where every core NEAT idea from `02_NEAT_FLAPPY_BIRD.md`
actually lives: innovation numbers, genome mutation, feedforward evaluation,
compatibility distance, crossover, the generation loop. Slow down there.

---

## The Atomic Learning Loop

Instead of running a whole session in one sitting, break it into loops of
**~15-20 minutes, one concept each.** Each loop looks like this:

```
1. READ    — the one relevant paragraph in 02_NEAT_FLAPPY_BIRD.md. Not the
             whole session. One concept.

2. ATTEMPT — write it yourself. Pseudocode is fine. Wrong code is fine.
             Timebox it — 10 minutes, then move to step 3 regardless.

3. REVIEW  — bring the agent in, but as a reviewer, not an author.
             Use the tutor-mode prompts below. Never "write X for me"
             for this part.

4. TEST    — run it. A 3-line manual test, or the relevant tests/test_weekN.py.

5. EXPLAIN — say out loud (or write one sentence) why it works. If you
             can't, you skipped step 2 — go back.
```

If step 5 fails, that's not a setback — it's the signal doing its job. Redo
step 2 before moving on.

---

## Tutor-Mode Prompts (use these instead of "build X")

**Before writing anything:**
```
Don't write the code yet. Explain [concept] conceptually — walk me through
it like I'm implementing it by hand.
```

**After you've made an attempt:**
```
Here's my attempt at [thing]. Don't rewrite it. Tell me what's wrong or
missing, and ask me a question that'll help me find it myself rather than
just telling me the answer.
```

**When you want a starting point but not the answer:**
```
Give me the function signature, docstring, and TODO comments only — no
implementation. I want to write the body myself.
```

**When you're stuck after a real attempt (this one's fine to ask directly):**
```
I've tried [X] for 15 minutes and I'm stuck on [specific thing]. Here's my
code. What am I missing?
```

**After it's working, to check you actually understand it:**
```
Quiz me on this: what would break if I removed the cycle check in
add_connection()? What would break if InnovationTracker reset the counter
instead of just the history dict?
```

---

## Session 3 — Innovation Tracker + Genome, Broken Down

Don't paste the whole Session 3 prompt. Work through these loops instead.

**Loop 3a — Innovation numbers (~15 min)**
- Read: "Historical Markings (Innovation Numbers)" in `02_NEAT_FLAPPY_BIRD.md`
- Attempt: write `InnovationTracker` yourself — just `get_innovation()` and
  `reset()`. It's genuinely ~10 lines. Try before looking at the spec's code.
- Review: ask the agent to check your version, not replace it
- Test: call `get_innovation(0, 5)` twice in the same "generation" — same
  number? Call `reset()`, call it again — new number, but does the *next*
  new connection continue from the old counter, or restart at 1? (It must
  continue — that's the one bug that breaks everything downstream.)
- Explain: why would two mutations creating the same connection in the same
  generation need the same innovation number?

**Loop 3b — NodeGene / ConnectionGene / Genome shape (~10 min)**
- Read: "Core Data Structures"
- Attempt: write the three dataclasses from memory, no lookup
- Review: compare field-by-field against the spec, not the agent's own version
- Explain: why is `nodes` a `dict[int, NodeGene]` instead of a `list`?

**Loop 3c — `add_connection()` and cycle detection (~20 min)**
- Read: "Cycle detection required — add_connection() must reject cycles"
- Attempt: before coding, describe in words how you'd check if adding
  `in_id → out_id` creates a cycle, given the existing connections
- Review: ask the agent to poke holes in your algorithm *before* you code it
- Attempt again: now implement it
- Test: try to add a connection that would create a cycle — does it get rejected?
- Explain: what's the smallest example network where this bug would bite you
  if you skipped the check?

**Loop 3d — `add_node()` — why disable, not delete (~15 min)**
- Read: the mutation section
- Attempt: write `add_node()` — split a connection, insert a hidden node,
  add two new connections. What happens to the original connection?
- Review: this is explicitly called out as a question to ask the agent —
  use it: *"Why does add_node() disable the original connection instead of
  deleting it?"* — but only after you've formed your own guess first.
- Explain: what would go wrong for genomes with different history if the
  original connection were deleted instead of disabled?

**Loop 3e — weight mutation (~10 min)**
- This one's mechanical (gaussian perturb vs. reset) — fine to move faster,
  but still write it yourself before checking.

By the end of Session 3 you should be able to explain innovation numbers,
cycle rejection, and the disable-don't-delete rule to someone else without
looking at the file.

---

## Session 4 — Neural Network, Broken Down

**Loop 4a — Topological sort (~20 min)**
- Read: "topological sort of nodes"
- Attempt: on paper, sort a tiny example genome (2 inputs, 1 hidden, 1
  output) into evaluation order by hand *before* writing any code
- Attempt: now write `_topological_sort()`
- Explain: why does a cycle break this, concretely — what would the
  algorithm do if one existed? (This connects directly back to Loop 3c —
  that's the whole reason the cycle check exists.)

**Loop 4b — `evaluate()` — the forward pass (~20 min)**
- Attempt: trace through evaluate() by hand for a genome with 5 inputs, 1
  hidden node, 1 output, using made-up weights — write down every
  intermediate value on paper first
- Attempt: now write the actual `evaluate()`
- Test: does your hand-traced numbers match what your code outputs for the
  same genome and inputs?
- Explain: why identity for inputs, tanh for hidden, sigmoid for output —
  what would break if hidden used sigmoid too?

---

## Session 5 — Speciation + Crossover, Broken Down

**Loop 5a — Compatibility distance (~25 min)**
- Read: the δ formula
- Attempt: take two small made-up genomes (write out their connections with
  innovation numbers) and calculate excess, disjoint, and δ **by hand** —
  this is the single most important exercise in the whole project for
  understanding NEAT
- Attempt: now write `compatibility_distance()`
- Test: does it match your hand calculation?
- Explain: in your own words, what's the difference between an excess gene
  and a disjoint gene?

**Loop 5b — Speciation assignment (~15 min)**
- Attempt: write `speciate()` — for each genome, compare to existing
  species reps, threshold check, else new species
- Explain: why does a genome compare only to the *representative*, not to
  every member of a species?

**Loop 5c — Crossover (~20 min)**
- Attempt: using the same two genomes from 5a, decide by hand which genes
  the child should inherit if genome A is fitter
- Attempt: now write `crossover()`
- Explain (use the suggested "Ask Cursor/Antigravity to EXPLAIN" prompt from
  the guide, but only after your own attempt): why do excess/disjoint genes
  only come from the fitter parent?

---

## Session 6 — Population + Generation Loop, Broken Down

This session is mostly *orchestration* of things you already understand from
3-5, so it's lower-risk to let it move faster — but still write the 9-step
loop yourself from the numbered list in `02_NEAT_FLAPPY_BIRD.md` before
looking at any generated code.

**Loop 6a — the loop skeleton (~15 min)**
- Attempt: write `evolve_one_generation()` as just comments — the 9 steps,
  in order, nothing else
- Review: check your ordering against the spec. Order matters here — e.g.
  fitness sharing has to happen before culling, and `InnovationTracker.reset()`
  has to happen before any mutation in the new generation.

**Loop 6b — wire it up (~30 min)**
- Now let the agent help you fill in each step — but call out any step you
  don't fully understand yet and stop to explain-back before continuing.

**Loop 6c — watch it run (~15 min)**
- Run 5, then 20, generations. Before checking the stats, predict: will best
  fitness go up, down, or stay flat? Were you right? If not, why not?

---

## A Note on Pace

This will make the project take noticeably longer than the raw 4-week plan.
That's expected and fine — the 4-week estimate assumes the agent is doing
the thinking. If you only have limited time, prioritize Loops 3a, 3c, 4a,
4b, 5a, and 5c — those five cover the ideas that make NEAT *NEAT* (innovation
numbers, cycle safety, feedforward evaluation, compatibility distance, and
crossover alignment). Sessions 1, 2 (game), 7, and 8 can go back to the
normal agent-generates-it workflow in `COPILOT_WORKFLOW.md` without losing
much of what you came here to learn.
