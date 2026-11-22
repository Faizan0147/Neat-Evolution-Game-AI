from __future__ import annotations

import copy
import random
from dataclasses import dataclass, field

from neat.config import NEATConfig
from neat.innovation import InnovationTracker

INPUT = "input"
HIDDEN = "hidden"
OUTPUT = "output"


@dataclass
class NodeGene:
    id: int
    type: str
    activation: str


@dataclass
class ConnectionGene:
    in_node: int
    out_node: int
    weight: float
    enabled: bool = True
    innovation: int = 0


@dataclass
class Genome:
    inputs: int
    outputs: int
    nodes: dict[int, NodeGene] = field(default_factory=dict)
    connections: dict[int, ConnectionGene] = field(default_factory=dict)
    fitness: float = 0.0
    species_id: int = -1

    @classmethod
    def create_initial(
        cls, inputs: int, outputs: int, weight_range: float = 1.0
    ) -> Genome:
        genome = cls(inputs=inputs, outputs=outputs)

        for node_id in range(inputs):
            genome.nodes[node_id] = NodeGene(node_id, INPUT, "identity")
        for node_id in range(inputs, inputs + outputs):
            genome.nodes[node_id] = NodeGene(node_id, OUTPUT, "sigmoid")

        for in_id in genome.input_ids():
            for out_id in genome.output_ids():
                weight = random.uniform(-weight_range, weight_range)
                genome._add_connection_gene(in_id, out_id, weight)

        return genome

    def input_ids(self) -> list[int]:
        return [n.id for n in self.nodes.values() if n.type == INPUT]

    def output_ids(self) -> list[int]:
        return [n.id for n in self.nodes.values() if n.type == OUTPUT]

    def hidden_ids(self) -> list[int]:
        return [n.id for n in self.nodes.values() if n.type == HIDDEN]

    def copy(self) -> Genome:
        return copy.deepcopy(self)

    def add_connection(
        self, in_id: int, out_id: int, weight: float | None = None
    ) -> bool:
        if not self._can_connect(in_id, out_id):
            return False

        if weight is None:
            weight = random.uniform(-1.0, 1.0)
        self._add_connection_gene(in_id, out_id, weight)
        return True

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

    def mutate(self, config: NEATConfig) -> None:
        if random.random() < config.weight_mutate_rate:
            self.mutate_weights(config)
        if random.random() < config.add_conn_rate:
            self.mutate_add_connection()
        if random.random() < config.add_node_rate:
            self.mutate_add_node()
        if random.random() < config.toggle_conn_rate:
            self.mutate_toggle_connection()

    def mutate_weights(self, config: NEATConfig) -> None:
        for conn in self.connections.values():
            if random.random() < config.weight_perturb_rate:
                conn.weight += random.gauss(0.0, config.weight_perturb_power)
            else:
                conn.weight = random.uniform(
                    -config.weight_init_range, config.weight_init_range
                )

    def mutate_add_connection(self) -> bool:
        pairs = [(in_id, out_id) for in_id in self.nodes for out_id in self.nodes]
        random.shuffle(pairs)

        for in_id, out_id in pairs:
            if self.add_connection(in_id, out_id):
                return True
        return False

    def mutate_add_node(self) -> bool:
        enabled = [c for c in self.connections.values() if c.enabled]
        if not enabled:
            return False
        return self.add_node(random.choice(enabled))

    def mutate_toggle_connection(self) -> bool:
        if not self.connections:
            return False
        conn = random.choice(list(self.connections.values()))
        conn.enabled = not conn.enabled
        return True

    def _add_connection_gene(self, in_id: int, out_id: int, weight: float) -> None:
        innovation = InnovationTracker.get_innovation(in_id, out_id)
        self.connections[innovation] = ConnectionGene(
            in_node=in_id,
            out_node=out_id,
            weight=weight,
            enabled=True,
            innovation=innovation,
        )

    def _can_connect(self, in_id: int, out_id: int) -> bool:
        if in_id not in self.nodes or out_id not in self.nodes:
            return False
        if in_id == out_id:
            return False
        if self.nodes[in_id].type == OUTPUT or self.nodes[out_id].type == INPUT:
            return False
        if self._connection_exists(in_id, out_id):
            return False
        return not self._creates_cycle(in_id, out_id)

    def _connection_exists(self, in_id: int, out_id: int) -> bool:
        return any(
            c.in_node == in_id and c.out_node == out_id
            for c in self.connections.values()
        )

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
