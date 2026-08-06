from __future__ import annotations

from neat.innovation import InnovationTracker

import pytest




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
