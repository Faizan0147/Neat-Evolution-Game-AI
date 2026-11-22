from __future__ import annotations


class InnovationTracker:
    _counter: int = 0
    _history: dict[tuple[int, int], int] = {}

    _node_counter: int = 0
    _node_history: dict[int, int] = {}

    @classmethod
    def get_innovation(cls, in_node: int, out_node: int) -> int:
        key = (in_node, out_node)
        if key not in cls._history:
            cls._counter += 1
            cls._history[key] = cls._counter
        return cls._history[key]

    @classmethod
    def get_split_node_id(cls, innovation: int, first_free_id: int) -> int:
        if innovation not in cls._node_history:
            cls._node_counter = max(cls._node_counter, first_free_id)
            cls._node_history[innovation] = cls._node_counter
            cls._node_counter += 1
        return cls._node_history[innovation]

    @classmethod
    def reset(cls) -> None:
        cls._history = {}
        cls._node_history = {}

    @classmethod
    def full_reset(cls) -> None:
        cls._counter = 0
        cls._history = {}
        cls._node_counter = 0
        cls._node_history = {}
