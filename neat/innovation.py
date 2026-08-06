from __future__ import annotations


class InnovationTracker:
    _counter: int = 0
    _history: dict[tuple[int, int], int] = {}

    @classmethod
    def get_innovation(cls, in_node: int, out_node: int) -> int:
        key = (in_node, out_node)
        if key not in cls._history:
            cls._counter += 1
            cls._history[key] = cls._counter
        return cls._history[key]

    @classmethod
    def reset(cls) -> None:
        cls._history = {}

    @classmethod
    def full_reset(cls) -> None:
        cls._counter = 0
        cls._history = {}
