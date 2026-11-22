from __future__ import annotations

from dataclasses import dataclass


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
    weight_init_range: float = 1.0

    add_node_rate: float = 0.03
    add_conn_rate: float = 0.05
    toggle_conn_rate: float = 0.01

    max_stagnation: int = 20
