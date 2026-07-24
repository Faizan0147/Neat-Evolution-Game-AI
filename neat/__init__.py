"""
NEAT (NeuroEvolution of Augmenting Topologies) package.

Implemented from scratch — no ML libraries used.

Modules (built across weeks 2–3):
    config       — NEATConfig dataclass with all hyperparameters
    innovation   — InnovationTracker singleton (global innovation numbers)
    genome       — NodeGene, ConnectionGene, Genome + mutation / crossover
    network      — NeuralNetwork: topological sort + feedforward evaluation
    species      — Species dataclass + compatibility_distance + Speciation
    population   — Population + full generation loop
"""
