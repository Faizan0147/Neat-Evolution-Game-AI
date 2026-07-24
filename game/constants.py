"""
Game constants for the Flappy Bird NEAT implementation.

All magic numbers live here. Import from this module everywhere else.
"""

# ── Display ────────────────────────────────────────────────────────────────────
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
FPS: int = 60

# ── Physics ────────────────────────────────────────────────────────────────────
GRAVITY: float = 0.5          # pixels / frame²  (added to vy each frame)
FLAP_STRENGTH: float = -8.0   # upward velocity impulse on flap (negative = up)

# ── Pipes ──────────────────────────────────────────────────────────────────────
PIPE_SPEED: float = 3.0       # pixels / frame  (leftward scroll)
PIPE_SPACING: int = 250       # horizontal gap between pipe pairs (px)
PIPE_GAP: int = 150           # vertical opening height (px)
PIPE_WIDTH: int = 80          # pixel width of each pipe column

# ── Player ─────────────────────────────────────────────────────────────────────
PLAYER_RADIUS: int = 15       # circle radius (px) — used for collision & drawing

# ── Pipe spawn X ───────────────────────────────────────────────────────────────
# First pipe spawns this many pixels to the right of the screen edge
PIPE_FIRST_SPAWN_X: int = SCREEN_WIDTH + 100

# ── Sensor normalisation ceilings ──────────────────────────────────────────────
# Maximum meaningful horizontal distance to the next pipe (full screen width)
MAX_PIPE_DISTANCE: float = float(SCREEN_WIDTH)

# Maximum meaningful vertical distance (full screen height, signed range)
MAX_VERT_DISTANCE: float = float(SCREEN_HEIGHT)

# Maximum meaningful vertical velocity (cap for normalisation)
MAX_VELOCITY: float = 20.0

# ── Colour palette (RGB) ───────────────────────────────────────────────────────
COLOR_SKY = (135, 206, 235)
COLOR_PIPE = (34, 139, 34)
COLOR_PIPE_OUTLINE = (0, 100, 0)
COLOR_PLAYER = (255, 220, 50)
COLOR_PLAYER_OUTLINE = (200, 160, 0)
COLOR_GROUND = (210, 180, 140)
COLOR_TEXT = (30, 30, 30)
