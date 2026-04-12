"""Tests for PD Tournament."""

from src.tournament.runner import TournamentRunner


class TestTournament:
    def test_tournament_runs(self):
        runner = TournamentRunner(rounds_per_match=50, strategy_names=["Tit-for-Tat", "Always Defect", "Always Cooperate"])
        result = runner.run()
        assert result.num_strategies == 3
        assert len(result.entries) == 3
        assert all(e.matches_played > 0 for e in result.entries)

    def test_rankings_sorted(self):
        runner = TournamentRunner(rounds_per_match=100, strategy_names=["Tit-for-Tat", "Always Defect", "Always Cooperate"])
        result = runner.run()
        rankings = result.rankings
        for i in range(len(rankings) - 1):
            assert rankings[i].total_score >= rankings[i + 1].total_score

    def test_always_defect_vs_always_cooperate(self):
        runner = TournamentRunner(rounds_per_match=100, strategy_names=["Always Defect", "Always Cooperate"])
        result = runner.run()
        # Always Defect exploits Always Cooperate
        h2h = result.head_to_head("Always Defect", "Always Cooperate")
        assert h2h is not None
        # Defect gets T=5 each round, Cooperate gets S=0
        assert h2h.total_payoffs[0] > h2h.total_payoffs[1]

    def test_cooperation_rates(self):
        runner = TournamentRunner(rounds_per_match=100, strategy_names=["Always Cooperate", "Always Defect"])
        result = runner.run()
        for entry in result.entries:
            if entry.name == "Always Cooperate":
                assert entry.avg_cooperation_rate > 0.9
            elif entry.name == "Always Defect":
                assert entry.avg_cooperation_rate < 0.1

    def test_all_strategies(self):
        runner = TournamentRunner(rounds_per_match=50)
        result = runner.run()
        assert result.num_strategies >= 6  # At least the default strategies
