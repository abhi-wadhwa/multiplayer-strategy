"""Tests for PD strategies."""

from src.games.prisoners_dilemma import Action, PrisonersDilemmaGame
from src.strategies.pd_strategies import (
    always_cooperate,
    always_defect,
    tit_for_tat,
    grim_trigger,
    pavlov,
    tit_for_two_tats,
    list_strategies,
    get_strategy,
    STRATEGIES,
)


class TestStrategies:
    def test_always_cooperate(self):
        for r in range(10):
            assert always_cooperate(r, [], []) == Action.COOPERATE

    def test_always_defect(self):
        for r in range(10):
            assert always_defect(r, [], []) == Action.DEFECT

    def test_tft_starts_cooperate(self):
        assert tit_for_tat(0, [], []) == Action.COOPERATE

    def test_tft_copies_opponent(self):
        assert tit_for_tat(1, [Action.COOPERATE], [Action.DEFECT]) == Action.DEFECT
        assert tit_for_tat(1, [Action.COOPERATE], [Action.COOPERATE]) == Action.COOPERATE

    def test_grim_trigger_cooperates_first(self):
        assert grim_trigger(0, [], []) == Action.COOPERATE

    def test_grim_trigger_retaliates_forever(self):
        opp = [Action.COOPERATE, Action.DEFECT]
        assert grim_trigger(2, [Action.COOPERATE, Action.COOPERATE], opp) == Action.DEFECT
        # Still defects even after cooperating
        opp2 = [Action.COOPERATE, Action.DEFECT, Action.COOPERATE]
        assert grim_trigger(3, [Action.COOPERATE, Action.COOPERATE, Action.DEFECT], opp2) == Action.DEFECT

    def test_pavlov_win_stay(self):
        # Both cooperated -> cooperate again
        assert pavlov(1, [Action.COOPERATE], [Action.COOPERATE]) == Action.COOPERATE
        # Both defected -> cooperate (same action = "win")
        assert pavlov(1, [Action.DEFECT], [Action.DEFECT]) == Action.COOPERATE

    def test_pavlov_lose_shift(self):
        # I cooperated, they defected -> shift to defect
        assert pavlov(1, [Action.COOPERATE], [Action.DEFECT]) == Action.DEFECT

    def test_tft2_tolerates_one_defection(self):
        assert tit_for_two_tats(2, [Action.COOPERATE] * 2, [Action.COOPERATE, Action.DEFECT]) == Action.COOPERATE

    def test_tft2_retaliates_after_two(self):
        assert tit_for_two_tats(2, [Action.COOPERATE] * 2, [Action.DEFECT, Action.DEFECT]) == Action.DEFECT

    def test_list_strategies(self):
        names = list_strategies()
        assert len(names) >= 6
        assert "Tit-for-Tat" in names

    def test_get_strategy(self):
        fn = get_strategy("Tit-for-Tat")
        assert fn is tit_for_tat

    def test_strategy_metadata(self):
        for name, info in STRATEGIES.items():
            assert "fn" in info
            assert "description" in info
            assert "nice" in info
            assert callable(info["fn"])

    def test_tft_vs_tft_mutual_cooperation(self):
        game = PrisonersDilemmaGame()
        result = game.play_match(tit_for_tat, tit_for_tat, rounds=100)
        assert result.cooperation_rates[0] == 1.0
        assert result.cooperation_rates[1] == 1.0
