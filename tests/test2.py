from __future__ import annotations

import pytest

from neat.config import NEATConfig
from neat.genome import Genome
from neat.innovation import InnovationTracker


@pytest.fixture(autouse=True)
def _clean_tracker():
    InnovationTracker.full_reset()
    yield
    InnovationTracker.full_reset()


class TestInnovationBasics:
    def test_first_call_returns_1(self) -> None:
        assert InnovationTracker.get_innovation(0, 5) == 1

    def test_second_unique_pair_returns_2(self) -> None:
        InnovationTracker.get_innovation(0, 5)
        assert InnovationTracker.get_innovation(1, 5) == 2

    def test_counter_increments_sequentially(self) -> None:
        for i in range(5):
            assert InnovationTracker.get_innovation(i, 10) == i + 1


class TestInnovationSameGeneration:
    def test_same_pair_same_generation_returns_same_number(self) -> None:
        first = InnovationTracker.get_innovation(2, 7)
        second = InnovationTracker.get_innovation(2, 7)
        assert first == second

    def test_different_pairs_get_different_numbers(self) -> None:
        a = InnovationTracker.get_innovation(0, 5)
        b = InnovationTracker.get_innovation(1, 5)
        assert a != b

    def test_order_matters(self) -> None:
        a = InnovationTracker.get_innovation(2, 7)
        b = InnovationTracker.get_innovation(7, 2)
        assert a != b


class TestInnovationReset:
    def test_reset_clears_history(self) -> None:
        before = InnovationTracker.get_innovation(2, 7)
        InnovationTracker.reset()
        after = InnovationTracker.get_innovation(2, 7)
        assert after > before

    def test_counter_continues_after_reset(self) -> None:
        InnovationTracker.get_innovation(0, 5)  # → 1
        InnovationTracker.get_innovation(1, 5)  # → 2
        InnovationTracker.reset()
        result = InnovationTracker.get_innovation(0, 5)  # → 3, not 1
        assert result == 3

    def test_multiple_resets_counter_keeps_climbing(self) -> None:
        InnovationTracker.get_innovation(0, 1)  # → 1
        InnovationTracker.reset()
        InnovationTracker.get_innovation(0, 1)  # → 2
        InnovationTracker.reset()
        InnovationTracker.get_innovation(0, 1)  # → 3
        assert InnovationTracker.get_innovation(0, 1) == 3


class TestSplitNodeIds:
    def test_first_split_uses_first_free_id(self) -> None:
        assert InnovationTracker.get_split_node_id(1, 6) == 6

    def test_same_split_same_generation_same_id(self) -> None:
        a = InnovationTracker.get_split_node_id(3, 6)
        b = InnovationTracker.get_split_node_id(3, 6)
        assert a == b

    def test_different_splits_get_different_ids(self) -> None:
        a = InnovationTracker.get_split_node_id(1, 6)
        b = InnovationTracker.get_split_node_id(2, 6)
        assert a != b

    def test_node_ids_keep_climbing_after_reset(self) -> None:
        before = InnovationTracker.get_split_node_id(1, 6)
        InnovationTracker.reset()
        after = InnovationTracker.get_split_node_id(1, 6)
        assert after > before


def _split(genome: Genome, in_id: int, out_id: int) -> int:
    conn = next(
        c
        for c in genome.connections.values()
        if c.in_node == in_id and c.out_node == out_id
    )
    genome.add_node(conn)
    return max(genome.hidden_ids())


class TestInitialGenome:
    def test_node_counts(self) -> None:
        genome = Genome.create_initial(5, 1)
        assert len(genome.input_ids()) == 5
        assert len(genome.output_ids()) == 1
        assert genome.hidden_ids() == []

    def test_fully_connected_inputs_to_outputs(self) -> None:
        genome = Genome.create_initial(5, 1)
        assert len(genome.connections) == 5
        assert all(c.enabled for c in genome.connections.values())
        assert all(c.out_node == 5 for c in genome.connections.values())

    def test_activations(self) -> None:
        genome = Genome.create_initial(5, 1)
        assert genome.nodes[0].activation == "identity"
        assert genome.nodes[5].activation == "sigmoid"

    def test_two_genomes_share_innovation_numbers(self) -> None:
        a = Genome.create_initial(5, 1)
        b = Genome.create_initial(5, 1)
        assert set(a.connections) == set(b.connections) == {1, 2, 3, 4, 5}

    def test_weights_within_range(self) -> None:
        genome = Genome.create_initial(5, 1, weight_range=0.5)
        assert all(-0.5 <= c.weight <= 0.5 for c in genome.connections.values())


class TestGenomeCopy:
    def test_copy_is_independent(self) -> None:
        original = Genome.create_initial(5, 1)
        clone = original.copy()
        clone.connections[1].weight = 99.0
        clone.nodes[0].activation = "changed"
        assert original.connections[1].weight != 99.0
        assert original.nodes[0].activation == "identity"


class TestAddNode:
    def test_disables_original_connection(self) -> None:
        genome = Genome.create_initial(5, 1)
        conn = genome.connections[1]
        genome.add_node(conn)
        assert conn.enabled is False
        assert 1 in genome.connections

    def test_creates_hidden_node_and_two_connections(self) -> None:
        genome = Genome.create_initial(5, 1)
        conn = genome.connections[1]
        assert genome.add_node(conn)

        new_id = genome.hidden_ids()[0]
        assert genome.nodes[new_id].activation == "tanh"
        assert len(genome.connections) == 7

        incoming = [c for c in genome.connections.values() if c.out_node == new_id]
        outgoing = [c for c in genome.connections.values() if c.in_node == new_id]
        assert incoming[0].in_node == conn.in_node
        assert incoming[0].weight == 1.0
        assert outgoing[0].out_node == conn.out_node
        assert outgoing[0].weight == conn.weight

    def test_rejects_disabled_connection(self) -> None:
        genome = Genome.create_initial(5, 1)
        conn = genome.connections[1]
        conn.enabled = False
        assert genome.add_node(conn) is False

    def test_same_split_in_two_genomes_matches(self) -> None:
        a = Genome.create_initial(5, 1)
        b = Genome.create_initial(5, 1)
        a.add_node(a.connections[2])
        b.add_node(b.connections[2])
        assert a.hidden_ids() == b.hidden_ids()
        assert set(a.connections) == set(b.connections)


class TestAddConnection:
    def test_rejects_existing_connection(self) -> None:
        genome = Genome.create_initial(5, 1)
        assert genome.add_connection(0, 5) is False

    def test_rejects_into_input(self) -> None:
        genome = Genome.create_initial(5, 1)
        hidden = _split(genome, 0, 5)
        assert genome.add_connection(hidden, 1) is False

    def test_rejects_from_output(self) -> None:
        genome = Genome.create_initial(5, 1)
        hidden = _split(genome, 0, 5)
        assert genome.add_connection(5, hidden) is False

    def test_rejects_self_loop(self) -> None:
        genome = Genome.create_initial(5, 1)
        hidden = _split(genome, 0, 5)
        assert genome.add_connection(hidden, hidden) is False

    def test_rejects_cycle(self) -> None:
        genome = Genome.create_initial(5, 1)
        h1 = _split(genome, 0, 5)
        h2 = _split(genome, h1, 5)
        assert genome.add_connection(h2, h1) is False

    def test_accepts_valid_connection(self) -> None:
        genome = Genome.create_initial(5, 1)
        hidden = _split(genome, 0, 5)
        assert genome.add_connection(1, hidden, weight=0.3)
        new = [c for c in genome.connections.values() if c.in_node == 1]
        assert any(c.out_node == hidden and c.weight == 0.3 for c in new)

    def test_add_connection_mutation_fails_when_full(self) -> None:
        genome = Genome.create_initial(5, 1)
        assert genome.mutate_add_connection() is False


class TestMutation:
    def test_perturb_changes_weights_slightly(self) -> None:
        config = NEATConfig(weight_perturb_rate=1.0, weight_perturb_power=0.1)
        genome = Genome.create_initial(5, 1)
        before = {k: c.weight for k, c in genome.connections.items()}
        genome.mutate_weights(config)
        for k, c in genome.connections.items():
            assert c.weight != before[k]
            assert abs(c.weight - before[k]) < 1.0

    def test_reset_keeps_weights_in_init_range(self) -> None:
        config = NEATConfig(weight_perturb_rate=0.0, weight_init_range=0.5)
        genome = Genome.create_initial(5, 1)
        genome.mutate_weights(config)
        assert all(-0.5 <= c.weight <= 0.5 for c in genome.connections.values())

    def test_add_node_rate_one_grows_network(self) -> None:
        config = NEATConfig(add_node_rate=1.0)
        genome = Genome.create_initial(5, 1)
        genome.mutate(config)
        assert len(genome.hidden_ids()) == 1

    def test_many_mutations_never_create_cycles(self) -> None:
        config = NEATConfig(add_node_rate=0.5, add_conn_rate=0.8)
        genome = Genome.create_initial(5, 1)
        for _ in range(200):
            genome.mutate(config)
        for c in genome.connections.values():
            assert not genome._creates_cycle(c.in_node, c.out_node)
