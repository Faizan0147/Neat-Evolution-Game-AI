# NEAT Sprint — DevOps Setup & Deployment Guide

> **For AI Agent use:** This file defines the complete DevOps infrastructure for the NEAT Neural Evolution Game AI project. Follow these specifications when setting up tooling, CI/CD pipelines, Docker, deployment, and monitoring. Do not deviate from the structure defined here.

---

## Table of Contents

1. [Project Metadata](#1-project-metadata)
2. [Local Development Setup](#2-local-development-setup)
3. [Code Quality Tooling](#3-code-quality-tooling)
4. [Git Workflow](#4-git-workflow)
5. [Testing Pipeline](#5-testing-pipeline)
6. [GitHub Actions CI/CD](#6-github-actions-cicd)
7. [Docker & Containerization](#7-docker--containerization)
8. [Deployment](#8-deployment)
9. [Monitoring & Error Tracking](#9-monitoring--error-tracking)
10. [Security](#10-security)
11. [Documentation](#11-documentation)
12. [Makefile Commands](#12-makefile-commands)
13. [Environment Variables](#13-environment-variables)
14. [Versioning & Releases](#14-versioning--releases)
15. [Agent Prompt Templates](#15-agent-prompt-templates)

---

## 1. Project Metadata

```
Project:     NEAT Neural Evolution Game AI
Language:    Python 3.11
Framework:   pygame 2.1+, numpy 1.21+
Repo:        github.com/USERNAME/neural-evolution-game-ai
License:     MIT
Python min:  3.9
```

**Stack summary:**
- Runtime: Python 3.11
- Game: pygame
- Math: numpy
- Tests: pytest + pytest-cov
- Lint: ruff
- Format: black
- Types: mypy
- CI: GitHub Actions
- Container: Docker
- Deploy: Render (or Railway)
- Errors: Sentry
- Docs: MkDocs

---

## 2. Local Development Setup

### 2.1 Required Files in Root

```
neat-sprint/
├── .github/
│   └── workflows/
│       ├── ci.yml               ← runs on every push
│       └── release.yml          ← runs on version tags
├── docs/
│   ├── NEAT_COPILOT_GUIDE.md
│   ├── COPILOT_WORKFLOW.md
│   ├── QUICK_REFERENCE.md
│   ├── FILE_STRUCTURE.md
│   └── DEVOPS_GUIDE.md          ← this file
├── game/
├── neat/
├── visualizer/
├── tests/
├── .dockerignore
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── mkdocs.yml
├── pyproject.toml
├── README.md
└── main.py
```

### 2.2 pyproject.toml (Single Config File for Everything)

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "neat-sprint"
version = "0.1.0"
description = "NEAT neuroevolution from scratch — evolves neural networks to play a 2D game"
authors = [{ name = "YOUR_NAME", email = "YOUR_EMAIL" }]
license = { text = "MIT" }
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
    "pygame>=2.1.0",
    "numpy>=1.21.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
    "pre-commit>=3.0",
    "sentry-sdk>=1.0",
    "mkdocs>=1.5",
    "mkdocs-material>=9.0",
    "mkdocstrings[python]>=0.24",
]

[tool.black]
line-length = 88
target-version = ["py39", "py310", "py311"]

[tool.ruff]
line-length = 88
select = ["E", "W", "F", "I", "N", "UP", "ANN", "B", "A"]
ignore = ["ANN101", "ANN102"]
target-version = "py39"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true
strict = false

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=. --cov-report=term-missing --cov-report=xml -v"
filterwarnings = ["ignore::DeprecationWarning"]

[tool.coverage.run]
omit = ["tests/*", "visualizer/*", "main.py"]

[tool.coverage.report]
fail_under = 60
```

### 2.3 Setup Commands (run once after cloning)

```bash
# Clone repo
git clone https://github.com/USERNAME/neural-evolution-game-ai.git
cd neural-evolution-game-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# Install all dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Verify everything works
make check
```

---

## 3. Code Quality Tooling

### 3.1 Pre-commit Config (.pre-commit-config.yaml)

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-json
      - id: check-merge-conflict
      - id: check-added-large-files
        args: ["--maxkb=500"]
      - id: debug-statements      # catches leftover print() in commits
      - id: no-commit-to-branch
        args: ["--branch", "main"]  # forces PR workflow

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

**How pre-commit works:**
- Runs automatically on `git commit`
- If any hook fails, commit is blocked
- Fix the issues, `git add` again, then commit
- Run manually: `pre-commit run --all-files`

### 3.2 Ruff Rules Explained

```toml
select = [
  "E",    # pycodestyle errors
  "W",    # pycodestyle warnings
  "F",    # pyflakes (unused imports, undefined names)
  "I",    # isort (import ordering)
  "N",    # pep8-naming conventions
  "UP",   # pyupgrade (modernize syntax)
  "ANN",  # type annotation enforcement
  "B",    # flake8-bugbear (common bugs)
  "A",    # flake8-builtins (shadowing builtins)
]
```

---

## 4. Git Workflow

### 4.1 Branch Naming Convention

```
main              ← production, protected, never push directly
dev               ← integration branch, PRs merge here first

Feature branches:
  feat/week1-game-engine
  feat/week2-genome-network
  feat/week3-neat-evolution
  feat/week4-visualizer

Fix branches:
  fix/topological-sort-cycles
  fix/innovation-tracker-reset

Documentation:
  docs/add-devops-guide
  docs/update-readme

Experiments (won't be merged):
  exp/recurrent-networks
  exp/alternative-fitness
```

### 4.2 Conventional Commits (Required Format)

```
<type>(<scope>): <short description>

Types:
  feat      New feature
  fix       Bug fix
  docs      Documentation only
  style     Formatting (no logic change)
  refactor  Code restructure (no feature/fix)
  test      Adding or fixing tests
  chore     Build, CI, dependencies
  perf      Performance improvement

Examples:
  feat(neat): add speciation by compatibility distance
  fix(genome): innovation tracker not resetting between generations
  test(week2): add unit tests for NeuralNetwork.evaluate()
  chore(ci): add pytest coverage threshold to GitHub Actions
  docs(readme): add project structure diagram
  perf(headless): vectorize feedforward with numpy for 3x speedup

Rules:
  - Subject line max 72 characters
  - Use imperative mood ("add" not "added")
  - No period at end
  - Reference issues: feat(neat): add crossover (#12)
```

### 4.3 PR Workflow

```
1. Create branch from dev
   git checkout dev
   git pull origin dev
   git checkout -b feat/week3-neat-evolution

2. Work on feature (multiple commits OK)
   git add .
   git commit -m "feat(neat): add compatibility distance function"

3. Push and open PR → dev
   git push origin feat/week3-neat-evolution
   # Open PR on GitHub: feat/week3-neat-evolution → dev

4. PR checklist:
   ✓ CI passes (all tests green)
   ✓ Coverage didn't drop
   ✓ No lint errors
   ✓ Commit messages follow convention

5. Merge to dev, then dev → main for releases
```

### 4.4 Git Aliases (add to ~/.gitconfig)

```ini
[alias]
  s = status
  co = checkout
  br = branch
  cm = commit -m
  lg = log --oneline --graph --decorate --all
  undo = reset --soft HEAD~1
  unstage = restore --staged .
```

---

## 5. Testing Pipeline

### 5.1 Test Structure

```
tests/
├── conftest.py          ← shared fixtures for all tests
├── test_week1.py        ← game engine tests
├── test_week2.py        ← genome + network tests
├── test_week3.py        ← evolution loop tests
└── test_week4.py        ← integration + visualizer tests
```

### 5.2 conftest.py (Shared Fixtures)

```python
# tests/conftest.py
import pytest
from neat.config import NEATConfig
from neat.genome import Genome, NodeGene, ConnectionGene
from neat.network import NeuralNetwork
from neat.innovation import InnovationTracker


@pytest.fixture(autouse=True)
def reset_innovation_tracker():
    """Reset global innovation tracker before every test."""
    InnovationTracker.reset()
    yield
    InnovationTracker.reset()


@pytest.fixture
def default_config() -> NEATConfig:
    return NEATConfig(
        pop_size=10,          # Small for tests
        dt=3.0,
        max_stagnation=5,
        add_node_rate=0.03,
        add_conn_rate=0.05,
    )


@pytest.fixture
def minimal_genome() -> Genome:
    """Genome with 3 inputs, 2 outputs, no hidden nodes."""
    nodes = {
        0: NodeGene(id=0, type="input"),
        1: NodeGene(id=1, type="input"),
        2: NodeGene(id=2, type="input"),
        10: NodeGene(id=10, type="output", activation="sigmoid"),
        11: NodeGene(id=11, type="output", activation="sigmoid"),
    }
    conns = {
        1: ConnectionGene(in_node=0, out_node=10, weight=0.5, innovation=1),
        2: ConnectionGene(in_node=1, out_node=11, weight=-0.3, innovation=2),
    }
    return Genome(inputs=3, outputs=2, nodes=nodes, connections=conns)


@pytest.fixture
def trained_network(minimal_genome) -> NeuralNetwork:
    return NeuralNetwork(minimal_genome)
```

### 5.3 Test Naming Convention

```python
# Pattern: test_<what>_<condition>_<expected>

def test_evaluate_valid_inputs_returns_sigmoid_outputs(): ...
def test_compatibility_distance_identical_genomes_returns_zero(): ...
def test_speciate_assigns_all_genomes_to_species(): ...
def test_crossover_offspring_has_valid_nodes(): ...
def test_innovation_tracker_same_pair_same_generation_same_number(): ...
```

### 5.4 Coverage Targets

```
Overall:          60% minimum (enforced in CI)
neat/genome.py:   80% target
neat/network.py:  80% target
neat/species.py:  70% target
neat/population.py: 65% target
game/engine.py:   50% target (pygame makes full coverage hard)
visualizer/*:     exempt (UI code, hard to test automatically)
```

Run coverage locally:
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html    # Visual coverage report
```

---

## 6. GitHub Actions CI/CD

### 6.1 CI Workflow (.github/workflows/ci.yml)

```yaml
name: CI

on:
  push:
    branches: ["**"]          # Every branch push
  pull_request:
    branches: [main, dev]     # PRs to main or dev

jobs:
  test:
    name: Test (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.11"]   # Test on multiple versions

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"           # Cache pip downloads

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run linter (ruff)
        run: ruff check .

      - name: Run formatter check (black)
        run: black --check .

      - name: Run type checker (mypy)
        run: mypy neat/ game/
        continue-on-error: true  # Don't fail CI on type errors (yet)

      - name: Run tests with coverage
        run: pytest
        env:
          SENTRY_DSN: ""         # Disable Sentry in CI

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: false

  lint-commits:
    name: Check Commit Messages
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: wagoid/commitlint-action@v5
        with:
          configFile: .commitlintrc.json
```

### 6.2 Commitlint Config (.commitlintrc.json)

```json
{
  "extends": ["@commitlint/config-conventional"],
  "rules": {
    "type-enum": [2, "always", [
      "feat", "fix", "docs", "style",
      "refactor", "test", "chore", "perf"
    ]],
    "subject-max-length": [2, "always", 72],
    "subject-case": [2, "always", "lower-case"]
  }
}
```

### 6.3 Release Workflow (.github/workflows/release.yml)

```yaml
name: Release

on:
  push:
    tags:
      - "v*.*.*"        # Triggers on v1.0.0, v0.2.1, etc.

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t neat-sprint:${{ github.ref_name }} .

      - name: Push to GitHub Container Registry
        run: |
          echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          docker tag neat-sprint:${{ github.ref_name }} ghcr.io/${{ github.repository }}:${{ github.ref_name }}
          docker push ghcr.io/${{ github.repository }}:${{ github.ref_name }}

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true   # Auto-generates from commit messages
          files: |
            requirements.txt
```

### 6.4 GitHub Repository Settings

```
Branch protection rules for main:
  ✓ Require pull request before merging
  ✓ Require status checks to pass (select: test)
  ✓ Require branches to be up to date before merging
  ✓ Do not allow bypassing (not even you)

Branch protection rules for dev:
  ✓ Require status checks to pass
  ✗ Require PR (optional — you can push directly to dev)
```

---

## 7. Docker & Containerization

### 7.1 Dockerfile

```dockerfile
# ─────────────────────────────────────────
# Stage 1: Builder (installs deps)
# ─────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python deps
COPY pyproject.toml .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -e ".[dev]"

# ─────────────────────────────────────────
# Stage 2: Runtime (lean final image)
# ─────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install SDL2 for pygame (headless mode needs this)
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Set display for headless pygame (needed in containers)
ENV SDL_VIDEODRIVER=offscreen
ENV SDL_AUDIODRIVER=dummy
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default: run headless evolution
CMD ["python", "main.py", "--headless", "--generations", "500"]
```

### 7.2 docker-compose.yml

```yaml
version: "3.9"

services:
  neat:
    build: .
    container_name: neat-evolution
    environment:
      - SENTRY_DSN=${SENTRY_DSN}
      - HEADLESS=true
      - GENERATIONS=500
      - POP_SIZE=150
    volumes:
      - ./checkpoints:/app/checkpoints    # Persist saved genomes
      - ./logs:/app/logs                  # Persist logs
    restart: unless-stopped

  neat-dev:
    build: .
    container_name: neat-dev
    environment:
      - HEADLESS=true
      - GENERATIONS=10             # Short run for dev testing
      - POP_SIZE=20
    volumes:
      - .:/app                     # Live code reloading
    command: python main.py --headless --generations 10
    profiles: ["dev"]              # Only starts with: docker compose --profile dev up
```

### 7.3 .dockerignore

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
env/
.env
.git/
.github/
.pytest_cache/
htmlcov/
*.mp4
checkpoints/
logs/
.DS_Store
*.egg-info/
dist/
build/
```

### 7.4 Docker Commands Reference

```bash
# Build image
docker build -t neat-sprint .

# Run headless evolution
docker run --rm neat-sprint

# Run with environment variables
docker run --rm \
  -e SENTRY_DSN=your_dsn_here \
  -e GENERATIONS=1000 \
  -v $(pwd)/checkpoints:/app/checkpoints \
  neat-sprint

# Start with docker-compose
docker compose up

# Start dev profile
docker compose --profile dev up neat-dev

# View logs
docker compose logs -f neat

# Stop everything
docker compose down

# Remove everything including volumes
docker compose down -v
```

---

## 8. Deployment

### 8.1 Platform: Render (Recommended for Beginners)

Render is the simplest deployment platform for Python projects. Free tier available.

**render.yaml (Infrastructure as Code for Render):**

```yaml
services:
  - type: worker                    # Background worker (no HTTP needed)
    name: neat-evolution
    runtime: python
    buildCommand: pip install -e ".[dev]"
    startCommand: python main.py --headless --generations 500
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SENTRY_DSN
        sync: false                 # Set manually in Render dashboard
      - key: GENERATIONS
        value: 500
      - key: POP_SIZE
        value: 150
    disk:
      name: checkpoints
      mountPath: /opt/render/project/src/checkpoints
      sizeGB: 1
```

**Deployment steps:**
```
1. Push code to GitHub
2. Go to render.com → New → Background Worker
3. Connect your GitHub repo
4. Set environment variables (SENTRY_DSN, etc.)
5. Deploy — Render auto-deploys on every push to main
```

### 8.2 Platform: Railway (Alternative)

```
1. railway.app → New Project → Deploy from GitHub
2. Select repo
3. Set environment variables in Railway dashboard
4. railway up (or auto-deploys from GitHub)
```

### 8.3 Platform: VPS (Manual — DigitalOcean, Linode)

For learning the full stack:

```bash
# On your server (Ubuntu 22.04)

# 1. Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 2. Clone your repo
git clone https://github.com/USERNAME/neural-evolution-game-ai.git
cd neural-evolution-game-ai

# 3. Create .env file
cp .env.example .env
nano .env    # Set your real values

# 4. Start with docker-compose
docker compose up -d

# 5. View logs
docker compose logs -f

# 6. Auto-update on new pushes (simple approach)
# Add this to cron (crontab -e):
*/5 * * * * cd /path/to/repo && git pull && docker compose up -d --build
```

### 8.4 Deployment Environments

```
Local:      Your machine. Uses .env file. Full pygame rendering.
CI:         GitHub Actions runners. Headless. No real GPU.
Staging:    dev branch deploys here. Same as prod but separate.
Production: main branch. Auto-deploys after CI passes.
```

---

## 9. Monitoring & Error Tracking

### 9.1 Sentry (Error Tracking)

Free tier: 5,000 errors/month. Set up in 5 minutes.

**Install:**
```bash
pip install sentry-sdk
```

**Initialize in main.py:**
```python
import sentry_sdk
import os

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", ""),      # Empty string = Sentry disabled
    traces_sample_rate=0.1,               # 10% of transactions traced
    environment=os.getenv("ENVIRONMENT", "development"),
    release=os.getenv("RELEASE", "0.0.0"),
)
```

**Captures automatically:**
- All unhandled exceptions
- Stack traces with local variables
- Release version
- Environment (dev/staging/prod)

**Manual error capture:**
```python
import sentry_sdk

try:
    risky_operation()
except Exception as e:
    sentry_sdk.capture_exception(e)
    raise
```

### 9.2 Structured Logging

```python
# neat/logger.py
import logging
import json
import sys
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for machine-readable output."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    return logger


# Usage in any module:
# from neat.logger import get_logger
# logger = get_logger(__name__)
# logger.info("Generation complete", extra={"generation": 5, "best_fitness": 1234.5})
```

### 9.3 Evolution Metrics Logging

```python
# Log these every generation for analysis
def log_generation_stats(population: Population, generation: int) -> None:
    fitnesses = [g.fitness for g in population.genomes]
    logger.info(
        "generation_complete",
        extra={
            "generation": generation,
            "best_fitness": max(fitnesses),
            "avg_fitness": sum(fitnesses) / len(fitnesses),
            "min_fitness": min(fitnesses),
            "num_species": len(population.species),
            "population_size": len(population.genomes),
            "stagnation_counts": {
                s.id: s.stagnation_counter
                for s in population.species
            },
        }
    )
```

---

## 10. Security

### 10.1 Secret Management

**Never commit secrets. Ever.**

```bash
# .env.example (commit this — it's a template with no real values)
SENTRY_DSN=your_sentry_dsn_here
ENVIRONMENT=development
RELEASE=0.0.0
POP_SIZE=150
GENERATIONS=500

# .env (NEVER commit this — real values live here)
# Add .env to .gitignore
SENTRY_DSN=https://abc123@o123.ingest.sentry.io/456789
ENVIRONMENT=production
RELEASE=v0.3.0
POP_SIZE=150
GENERATIONS=500
```

**Load .env in code:**
```python
# main.py
from dotenv import load_dotenv
import os

load_dotenv()   # Loads .env if it exists (ignored in production — env vars set directly)

SENTRY_DSN = os.getenv("SENTRY_DSN", "")
POP_SIZE = int(os.getenv("POP_SIZE", "150"))
GENERATIONS = int(os.getenv("GENERATIONS", "500"))
```

**Install python-dotenv:**
Add `python-dotenv>=1.0` to pyproject.toml dependencies.

### 10.2 Dependabot (Auto-update Dependencies)

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

Dependabot auto-opens PRs when a dependency has a security fix. Merge them.

### 10.3 GitHub Secrets Setup

```
GitHub repo → Settings → Secrets and variables → Actions → New repository secret

Required secrets:
  SENTRY_DSN          ← your Sentry project DSN
  RENDER_DEPLOY_HOOK  ← Render deploy webhook URL (for manual triggers)
```

---

## 11. Documentation

### 11.1 MkDocs Setup (Auto-generate Docs from Docstrings)

**mkdocs.yml:**
```yaml
site_name: NEAT Sprint Docs
site_description: NEAT Neural Evolution Game AI — From-scratch implementation
repo_url: https://github.com/USERNAME/neural-evolution-game-ai

theme:
  name: material
  palette:
    scheme: slate          # Dark theme
    primary: deep purple
    accent: purple
  features:
    - navigation.tabs
    - navigation.sections
    - content.code.copy

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
            show_root_heading: true

nav:
  - Home: index.md
  - DevOps Guide: DEVOPS_GUIDE.md
  - Copilot Guide: NEAT_COPILOT_GUIDE.md
  - File Structure: FILE_STRUCTURE.md
  - Quick Reference: QUICK_REFERENCE.md
  - API Reference:
      - Game: api/game.md
      - NEAT: api/neat.md
      - Visualizer: api/visualizer.md

markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - admonition
```

**Build and serve docs:**
```bash
mkdocs serve          # Local preview at http://127.0.0.1:8000
mkdocs build          # Build static site to site/ directory
mkdocs gh-deploy      # Deploy to GitHub Pages (free hosting)
```

### 11.2 Docstring Format (Google Style)

```python
def compatibility_distance(
    g1: Genome,
    g2: Genome,
    c1: float = 1.0,
    c2: float = 1.0,
    c3: float = 0.4,
) -> float:
    """Calculate genetic compatibility distance between two genomes.

    Uses the formula: δ = (c1·E + c2·D) / N + c3·W̄
    where E = excess genes, D = disjoint genes,
    N = max genes, W̄ = avg weight difference.

    Args:
        g1: First genome to compare.
        g2: Second genome to compare.
        c1: Weight for excess gene distance. Defaults to 1.0.
        c2: Weight for disjoint gene distance. Defaults to 1.0.
        c3: Weight for weight difference. Defaults to 0.4.

    Returns:
        Float compatibility distance. Lower = more similar.
        Returns 0.0 for identical genomes.

    Raises:
        ValueError: If either genome has no connections.

    Example:
        >>> g1 = Genome(inputs=3, outputs=2, ...)
        >>> g2 = Genome(inputs=3, outputs=2, ...)
        >>> dist = compatibility_distance(g1, g2)
        >>> assert 0.0 <= dist
    """
```

---

## 12. Makefile Commands

```makefile
# Makefile — one place for all common commands

.PHONY: help install setup test lint format typecheck check clean build run docker-build docker-run docs

# Default target
help:
	@echo "NEAT Sprint — Available commands:"
	@echo ""
	@echo "  make install      Install all dependencies"
	@echo "  make setup        Full dev environment setup"
	@echo "  make run          Run evolution with pygame visualizer"
	@echo "  make headless     Run headless evolution (no pygame)"
	@echo "  make test         Run test suite with coverage"
	@echo "  make lint         Run ruff linter"
	@echo "  make format       Auto-format with black"
	@echo "  make typecheck    Run mypy type checker"
	@echo "  make check        Run all quality checks (lint + format + typecheck + test)"
	@echo "  make clean        Remove build artifacts and caches"
	@echo "  make docker-build Build Docker image"
	@echo "  make docker-run   Run headless evolution in Docker"
	@echo "  make docs         Serve docs locally at localhost:8000"
	@echo "  make docs-deploy  Deploy docs to GitHub Pages"
	@echo "  make release      Tag and push a new release (VERSION=x.y.z)"

install:
	pip install --upgrade pip
	pip install -e ".[dev]"

setup: install
	pre-commit install
	cp -n .env.example .env || true
	@echo "✓ Dev environment ready. Edit .env with your values."

run:
	python main.py

headless:
	python main.py --headless --generations 500

test:
	pytest

test-fast:
	pytest -x --no-cov     # Stop on first failure, no coverage (fast)

lint:
	ruff check .

format:
	black .

format-check:
	black --check .

typecheck:
	mypy neat/ game/

check: format-check lint typecheck test
	@echo "✓ All checks passed"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage coverage.xml dist build *.egg-info

docker-build:
	docker build -t neat-sprint .

docker-run:
	docker run --rm \
		--env-file .env \
		-v $(PWD)/checkpoints:/app/checkpoints \
		neat-sprint

docs:
	mkdocs serve

docs-build:
	mkdocs build

docs-deploy:
	mkdocs gh-deploy

release:
	@if [ -z "$(VERSION)" ]; then echo "Usage: make release VERSION=x.y.z"; exit 1; fi
	git tag -a v$(VERSION) -m "Release v$(VERSION)"
	git push origin v$(VERSION)
	@echo "✓ Tagged v$(VERSION) — GitHub Actions will create the release"
```

---

## 13. Environment Variables

### 13.1 Complete Variable Reference

```bash
# .env.example — copy to .env and fill in real values

# ─────────────────────────────────────
# Monitoring
# ─────────────────────────────────────
SENTRY_DSN=                        # From Sentry project settings
ENVIRONMENT=development            # development | staging | production
RELEASE=0.0.0                      # Updated by CI on release

# ─────────────────────────────────────
# NEAT Configuration
# ─────────────────────────────────────
POP_SIZE=150                       # Population size (100-300)
GENERATIONS=500                    # Number of generations to run
GAME_TYPE=dino                     # dino | flappy | snake | platform
HEADLESS=false                     # true = no pygame window
CHECKPOINT_DIR=checkpoints         # Where to save best genomes
CHECKPOINT_EVERY=50                # Save checkpoint every N generations

# ─────────────────────────────────────
# NEAT Hyperparameters
# ─────────────────────────────────────
DT=3.0                             # Speciation threshold
C1=1.0                             # Excess gene weight
C2=1.0                             # Disjoint gene weight
C3=0.4                             # Weight difference factor
MAX_STAGNATION=20                  # Kill species after N gens no improvement
WEIGHT_MUTATE_RATE=0.8
WEIGHT_PERTURB_RATE=0.9
WEIGHT_PERTURB_POWER=0.1
ADD_NODE_RATE=0.03
ADD_CONN_RATE=0.05
```

### 13.2 Loading Config from Environment

```python
# neat/config.py
import os
from dataclasses import dataclass, field


@dataclass
class NEATConfig:
    pop_size: int = int(os.getenv("POP_SIZE", "150"))
    dt: float = float(os.getenv("DT", "3.0"))
    c1: float = float(os.getenv("C1", "1.0"))
    c2: float = float(os.getenv("C2", "1.0"))
    c3: float = float(os.getenv("C3", "0.4"))
    max_stagnation: int = int(os.getenv("MAX_STAGNATION", "20"))
    weight_mutate_rate: float = float(os.getenv("WEIGHT_MUTATE_RATE", "0.8"))
    weight_perturb_rate: float = float(os.getenv("WEIGHT_PERTURB_RATE", "0.9"))
    weight_perturb_power: float = float(os.getenv("WEIGHT_PERTURB_POWER", "0.1"))
    add_node_rate: float = float(os.getenv("ADD_NODE_RATE", "0.03"))
    add_conn_rate: float = float(os.getenv("ADD_CONN_RATE", "0.05"))
```

---

## 14. Versioning & Releases

### 14.1 Semantic Versioning (SemVer)

```
Format: MAJOR.MINOR.PATCH
         v1.2.3

MAJOR — Breaking changes (restructured API, different inputs/outputs)
MINOR — New features, backwards compatible (new game type, new mutation)
PATCH — Bug fixes (fixed innovation tracker, fixed crossover alignment)

Examples:
  v0.1.0  First working game engine
  v0.2.0  NEAT evolution loop working
  v0.3.0  Full visualizer complete
  v0.3.1  Fixed compatibility distance calculation
  v1.0.0  Polished, documented, deployed
```

### 14.2 CHANGELOG.md Format

```markdown
# Changelog

All notable changes to this project will be documented here.
Format based on [Keep a Changelog](https://keepachangelog.com).
Versioning follows [Semantic Versioning](https://semver.org).

## [Unreleased]
### Added
- Network topology graph renderer in visualizer

## [0.2.0] — 2024-01-21
### Added
- Full NEAT evolution loop with speciation
- Compatibility distance function
- Crossover aligned by innovation number
- Stagnation-based species culling

### Fixed
- Innovation tracker not resetting between generations

## [0.1.0] — 2024-01-14
### Added
- Dino runner game engine with pygame
- Headless mode for fast evaluation
- Sensor extraction (8 normalized inputs)
- Basic genome and feedforward network
```

### 14.3 Release Process

```bash
# 1. Update version in pyproject.toml
# 2. Update CHANGELOG.md
# 3. Commit
git add pyproject.toml CHANGELOG.md
git commit -m "chore(release): bump version to 0.2.0"

# 4. Tag and push (GitHub Actions creates the release automatically)
make release VERSION=0.2.0

# OR manually:
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

---

## 15. Agent Prompt Templates

> **For Copilot:** Use these prompts when the user asks to set up specific DevOps components.

### Setup GitHub Actions CI

```
Set up GitHub Actions CI for this Python project.

Create .github/workflows/ci.yml that:
1. Triggers on every push and PR to main/dev
2. Tests on Python 3.9 and 3.11 (matrix)
3. Caches pip installs
4. Runs: ruff, black --check, mypy, pytest
5. Uploads coverage to Codecov

Use the configuration from DEVOPS_GUIDE.md Section 6.1.
The project uses pyproject.toml for all tool config.
```

### Setup pre-commit hooks

```
Set up pre-commit for this project.

Create .pre-commit-config.yaml using:
- pre-commit-hooks: trailing whitespace, end-of-file-fixer, check-yaml,
  check-merge-conflict, no-commit-to-branch (main)
- black 23.11.0
- ruff with --fix
- mypy

After creating the file, show the commands to:
1. Install pre-commit
2. Install the hooks
3. Run against all files to test

Follow DEVOPS_GUIDE.md Section 3.1 exactly.
```

### Setup Docker

```
Create Docker setup for this Python NEAT project.

Files needed:
1. Dockerfile — multi-stage build (builder + runtime)
   - Use python:3.11-slim
   - Install SDL2 libraries for headless pygame
   - Set SDL_VIDEODRIVER=offscreen for headless
2. docker-compose.yml — with neat and neat-dev services
3. .dockerignore

Follow DEVOPS_GUIDE.md Section 7 exactly.
The app runs: python main.py --headless --generations 500
```

### Setup Sentry

```
Add Sentry error tracking to this project.

1. Add sentry-sdk to pyproject.toml optional dev dependencies
2. Initialize Sentry in main.py using SENTRY_DSN env var
3. Add SENTRY_DSN to .env.example (empty value)
4. Disable Sentry when SENTRY_DSN is empty (don't error if not set)
5. Add SENTRY_DSN: "" to GitHub Actions env so CI doesn't use Sentry

Follow DEVOPS_GUIDE.md Section 9.1.
```

### Setup Makefile

```
Create a Makefile for this project with these targets:
help, install, setup, run, headless, test, test-fast, lint, format,
format-check, typecheck, check, clean, docker-build, docker-run,
docs, docs-deploy, release

Follow DEVOPS_GUIDE.md Section 12 exactly.
Make sure `make check` runs all quality gates in order.
```

### Setup MkDocs

```
Set up MkDocs with the Material theme for this project.

1. Create mkdocs.yml with dark theme (slate + deep purple)
2. Enable mkdocstrings for auto-generating API docs from docstrings
3. Add nav structure: Home, DevOps Guide, Copilot Guide, API Reference
4. Add mkdocs + mkdocs-material + mkdocstrings to pyproject.toml dev deps
5. Add docs and docs-deploy targets to Makefile

Follow DEVOPS_GUIDE.md Section 11.1.
```

### Setup Logging

```
Add structured JSON logging to this project.

1. Create neat/logger.py with JSONFormatter and get_logger() function
2. Add a log_generation_stats() function
3. Update main.py to use the logger instead of print()
4. Log each generation: generation number, best/avg/min fitness, num_species

Follow DEVOPS_GUIDE.md Section 9.2 and 9.3 exactly.
Use the Google-style docstring format from Section 11.2.
```

---

## Quick Reference — DevOps Commands

```bash
# DAILY USE
make run              # Run with visualizer
make test             # Run all tests
make check            # All quality checks
git add . && git commit -m "feat(neat): description"

# WEEKLY
make release VERSION=x.y.z    # Tag a release
mkdocs gh-deploy               # Update docs

# DEBUGGING
docker compose logs -f         # View container logs
pytest -x --no-cov -v         # Stop on first failure
mypy neat/ --show-error-codes  # Type errors with codes
ruff check . --show-fixes      # See what ruff can auto-fix

# CLEANUP
make clean             # Remove all build artifacts
git stash              # Temporarily save uncommitted changes
git stash pop          # Restore stashed changes
```

---

*Last updated: Week 1 of 4P-Sprint*
*Agent: Reference this file for all DevOps setup. Always prefer the configuration in this file over general knowledge.*
