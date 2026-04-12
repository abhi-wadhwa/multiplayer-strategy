"""Tests for Public Goods Game."""

import pytest

from src.games.public_goods import PublicGoodsGame


class TestPublicGoodsGame:
    def test_full_cooperation(self):
        game = PublicGoodsGame(num_players=4, endowment=100, multiplier=2.0)
        result = game.play([100, 100, 100, 100])
        assert result.pool == 400
        assert result.multiplied_pool == 800
        assert result.share == 200
        # Payoff = (100 - 100) + 200 = 200
        assert all(abs(p - 200.0) < 1e-9 for p in result.payoffs)

    def test_full_defection_nash(self):
        game = PublicGoodsGame(num_players=4, endowment=100, multiplier=2.0)
        result = game.play([0, 0, 0, 0])
        assert result.pool == 0
        assert result.multiplied_pool == 0
        assert result.share == 0
        # Payoff = 100 - 0 + 0 = 100
        assert all(abs(p - 100.0) < 1e-9 for p in result.payoffs)

    def test_free_rider_advantage(self):
        game = PublicGoodsGame(num_players=4, endowment=100, multiplier=2.0)
        result = game.play([100, 100, 100, 0])
        # Free rider gets: 100 - 0 + (300*2/4) = 100 + 150 = 250
        assert result.payoffs[3] > result.payoffs[0]

    def test_social_dilemma_property(self):
        game = PublicGoodsGame(num_players=4, endowment=100, multiplier=2.0)
        assert game.is_social_dilemma
        assert game.marginal_per_capita_return() == 0.5  # 2/4 < 1

    def test_not_social_dilemma(self):
        game = PublicGoodsGame(num_players=2, endowment=100, multiplier=3.0)
        assert not game.is_social_dilemma  # M=3 > N=2

    def test_efficiency(self):
        game = PublicGoodsGame(num_players=4, endowment=100, multiplier=2.0)
        full_coop = game.play([100, 100, 100, 100])
        assert abs(full_coop.efficiency - 1.0) < 1e-9

        full_defect = game.play([0, 0, 0, 0])
        assert abs(full_defect.efficiency - 0.0) < 1e-9

    def test_invalid_contribution(self):
        game = PublicGoodsGame(num_players=2, endowment=100, multiplier=2.0)
        with pytest.raises(ValueError):
            game.play([150, 50])  # Exceeds endowment

    def test_wrong_player_count(self):
        game = PublicGoodsGame(num_players=4, endowment=100, multiplier=2.0)
        with pytest.raises(ValueError):
            game.play([50, 50])

    def test_nash_payoff(self):
        game = PublicGoodsGame(num_players=4, endowment=100, multiplier=2.0)
        assert game.nash_payoff() == 100.0

    def test_constructor_validation(self):
        with pytest.raises(ValueError):
            PublicGoodsGame(num_players=1)
        with pytest.raises(ValueError):
            PublicGoodsGame(endowment=-10)
