"""Tests for Colonel Blotto game."""

import numpy as np
import pytest

from src.games.blotto import BlottoGame


class TestBlottoGame:
    def test_basic_game(self):
        game = BlottoGame(num_battlefields=3, num_troops=10)
        result = game.play([[5, 3, 2], [2, 4, 4]])
        assert result.battlefield_winners[0] == 0  # 5 > 2
        assert result.battlefield_winners[1] == 1  # 3 < 4
        assert result.battlefield_winners[2] == 1  # 2 < 4
        assert result.wins == [1, 2]
        assert result.winner == 1

    def test_tie_battlefield(self):
        game = BlottoGame(num_battlefields=3, num_troops=9)
        result = game.play([[3, 3, 3], [3, 3, 3]])
        assert all(w is None for w in result.battlefield_winners)
        assert result.ties == 3
        assert result.winner is None

    def test_sweep(self):
        game = BlottoGame(num_battlefields=3, num_troops=10)
        result = game.play([[4, 4, 2], [3, 3, 4]])
        assert result.wins[0] == 2
        assert result.wins[1] == 1
        assert result.winner == 0

    def test_invalid_allocation_wrong_sum(self):
        game = BlottoGame(num_battlefields=3, num_troops=10)
        with pytest.raises(ValueError):
            game.play([[5, 5, 5], [3, 3, 4]])  # First player has 15 troops

    def test_invalid_allocation_negative(self):
        game = BlottoGame(num_battlefields=3, num_troops=10)
        assert not game.validate_allocation([-1, 5, 6])

    def test_invalid_allocation_wrong_length(self):
        game = BlottoGame(num_battlefields=3, num_troops=10)
        assert not game.validate_allocation([5, 5])

    def test_random_allocation_valid(self):
        game = BlottoGame(num_battlefields=5, num_troops=100)
        rng = np.random.default_rng(42)
        for _ in range(100):
            alloc = game.random_allocation(rng)
            assert len(alloc) == 5
            assert sum(alloc) == 100
            assert all(a >= 0 for a in alloc)

    def test_wrong_player_count(self):
        game = BlottoGame(num_battlefields=3, num_troops=10)
        with pytest.raises(ValueError):
            game.play([[3, 3, 4]])  # Only 1 player

    def test_strategy_matchup(self):
        game = BlottoGame(num_battlefields=3, num_troops=6)
        strat_a = [[6, 0, 0], [0, 6, 0], [0, 0, 6]]  # Concentrate
        strat_b = [[2, 2, 2]]  # Spread evenly
        win_a, win_b = game.evaluate_strategy_matchup(strat_a, strat_b)
        assert win_a + win_b <= 1.0  # Plus possible ties

    def test_constructor_validation(self):
        with pytest.raises(ValueError):
            BlottoGame(num_battlefields=0)
        with pytest.raises(ValueError):
            BlottoGame(num_troops=0)
        with pytest.raises(ValueError):
            BlottoGame(num_players=1)
