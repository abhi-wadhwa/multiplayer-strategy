"""Axelrod-style iterated Prisoner's Dilemma tournament runner.

Runs a round-robin tournament where every strategy plays every other
strategy (and itself) in an iterated PD. Strategies are ranked by
total score across all matches.

References:
    - Axelrod, R. (1984). The Evolution of Cooperation.
"""

from __future__ import annotations

import structlog
from dataclasses import dataclass, field

from src.games.prisoners_dilemma import PrisonersDilemmaGame, PDMatchResult
from src.strategies.pd_strategies import STRATEGIES

logger = structlog.get_logger()


@dataclass
class TournamentEntry:
    """A strategy's performance in the tournament."""
    name: str
    total_score: float = 0.0
    matches_played: int = 0
    avg_score_per_match: float = 0.0
    avg_cooperation_rate: float = 0.0
    wins: int = 0
    losses: int = 0
    draws: int = 0


@dataclass
class TournamentResult:
    """Complete tournament results."""
    entries: list[TournamentEntry]
    match_results: list[PDMatchResult]
    rounds_per_match: int
    num_strategies: int
    payoff_matrix: dict[tuple[str, str], tuple[float, float]] = field(default_factory=dict)

    @property
    def rankings(self) -> list[TournamentEntry]:
        """Entries sorted by total score (descending)."""
        return sorted(self.entries, key=lambda e: e.total_score, reverse=True)

    def head_to_head(self, name_a: str, name_b: str) -> PDMatchResult | None:
        """Get the match result between two specific strategies."""
        for m in self.match_results:
            if m.player_a == name_a and m.player_b == name_b:
                return m
            if m.player_a == name_b and m.player_b == name_a:
                return m
        return None


class TournamentRunner:
    """Round-robin iterated PD tournament.

    Every strategy plays against every other strategy (and itself).
    Strategies are ranked by total cumulative score.

    Attributes:
        game: The PD game instance with payoff parameters.
        rounds_per_match: Number of rounds in each iterated match.
        strategies: Dict mapping strategy names to functions.
    """

    def __init__(
        self,
        rounds_per_match: int = 200,
        temptation: float = 5.0,
        reward: float = 3.0,
        punishment: float = 1.0,
        sucker: float = 0.0,
        strategy_names: list[str] | None = None,
    ) -> None:
        self.game = PrisonersDilemmaGame(
            temptation=temptation,
            reward=reward,
            punishment=punishment,
            sucker=sucker,
        )
        self.rounds_per_match = rounds_per_match

        if strategy_names is None:
            self.strategies = {name: info["fn"] for name, info in STRATEGIES.items()}
        else:
            self.strategies = {}
            for name in strategy_names:
                if name not in STRATEGIES:
                    raise ValueError(f"Unknown strategy: {name}")
                self.strategies[name] = STRATEGIES[name]["fn"]

    def run(self) -> TournamentResult:
        """Run the full round-robin tournament.

        Returns:
            TournamentResult with all match results and rankings.
        """
        names = list(self.strategies.keys())
        entries = {name: TournamentEntry(name=name) for name in names}
        match_results: list[PDMatchResult] = []
        payoff_matrix: dict[tuple[str, str], tuple[float, float]] = {}

        for i, name_a in enumerate(names):
            for j, name_b in enumerate(names):
                if j < i:
                    continue  # Already played (symmetric)

                logger.debug("match", player_a=name_a, player_b=name_b)

                result = self.game.play_match(
                    strategy_a=self.strategies[name_a],
                    strategy_b=self.strategies[name_b],
                    rounds=self.rounds_per_match,
                    name_a=name_a,
                    name_b=name_b,
                )
                match_results.append(result)
                payoff_matrix[(name_a, name_b)] = result.total_payoffs

                # Update scores
                score_a, score_b = result.total_payoffs
                entries[name_a].total_score += score_a
                entries[name_a].matches_played += 1
                entries[name_b].total_score += score_b
                entries[name_b].matches_played += 1

                # Track cooperation rates
                coop_a, coop_b = result.cooperation_rates
                entries[name_a].avg_cooperation_rate += coop_a
                entries[name_b].avg_cooperation_rate += coop_b

                # Win/loss/draw
                if name_a != name_b:
                    if score_a > score_b:
                        entries[name_a].wins += 1
                        entries[name_b].losses += 1
                    elif score_b > score_a:
                        entries[name_b].wins += 1
                        entries[name_a].losses += 1
                    else:
                        entries[name_a].draws += 1
                        entries[name_b].draws += 1

        # Compute averages
        for entry in entries.values():
            if entry.matches_played > 0:
                entry.avg_score_per_match = entry.total_score / entry.matches_played
                entry.avg_cooperation_rate /= entry.matches_played

        return TournamentResult(
            entries=list(entries.values()),
            match_results=match_results,
            rounds_per_match=self.rounds_per_match,
            num_strategies=len(names),
            payoff_matrix=payoff_matrix,
        )
