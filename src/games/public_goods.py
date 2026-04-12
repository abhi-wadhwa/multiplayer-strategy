"""Public Goods Game implementation.

Players secretly choose how much to contribute to a shared pool.
The pool is multiplied by a factor and divided equally among all players.
This creates a social dilemma: the group benefits from full contribution,
but each individual is tempted to free-ride.

Nash Equilibrium (one-shot): Contribute nothing (0).
Social Optimum: Contribute everything (endowment).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PublicGoodsResult:
    """Result of one round of the Public Goods Game."""

    contributions: list[float]  # Each player's contribution
    endowments: list[float]  # Each player's starting endowment
    pool: float  # Total contributions
    multiplied_pool: float  # Pool after multiplication
    share: float  # Each player's equal share of the multiplied pool
    payoffs: list[float]  # Final payoff per player
    efficiency: float  # Ratio of total payoff to social optimum


class PublicGoodsGame:
    """Public Goods Game engine.

    N players each receive an endowment E. They simultaneously choose
    a contribution c_i in [0, E]. The total contributions are multiplied
    by a factor M and divided equally among all N players.

    Payoff for player i: (E - c_i) + M * sum(c_j) / N

    The multiplier M must satisfy 1 < M < N for the social dilemma to exist:
    - M > 1: group benefits from contributions (social optimum = contribute all)
    - M < N: individual marginal return < 1 (NE = contribute nothing)

    Attributes:
        num_players: Number of players (N).
        endowment: Starting endowment for each player (E).
        multiplier: Pool multiplication factor (M).
    """

    def __init__(
        self,
        num_players: int = 4,
        endowment: float = 100.0,
        multiplier: float = 2.0,
    ) -> None:
        if num_players < 2:
            raise ValueError("Must have at least 2 players")
        if endowment <= 0:
            raise ValueError("Endowment must be positive")
        if multiplier <= 0:
            raise ValueError("Multiplier must be positive")
        self.num_players = num_players
        self.endowment = endowment
        self.multiplier = multiplier

    @property
    def is_social_dilemma(self) -> bool:
        """Check if the game parameters create a genuine social dilemma."""
        return 1.0 < self.multiplier < self.num_players

    def validate_contribution(self, contribution: float) -> bool:
        """Check if a contribution is valid."""
        return 0 <= contribution <= self.endowment

    def play(
        self,
        contributions: list[float],
        endowments: list[float] | None = None,
    ) -> PublicGoodsResult:
        """Play one round of the Public Goods Game.

        Args:
            contributions: List of contributions, one per player.
            endowments: Optional per-player endowments (default: self.endowment for all).

        Returns:
            PublicGoodsResult with payoffs and game statistics.
        """
        if len(contributions) != self.num_players:
            raise ValueError(
                f"Expected {self.num_players} contributions, got {len(contributions)}"
            )

        if endowments is None:
            endowments = [self.endowment] * self.num_players

        for i, (c, e) in enumerate(zip(contributions, endowments)):
            if c < 0 or c > e + 1e-9:
                raise ValueError(
                    f"Player {i} contribution {c} not in [0, {e}]"
                )

        pool = sum(contributions)
        multiplied_pool = pool * self.multiplier
        share = multiplied_pool / self.num_players

        payoffs = [(e - c) + share for c, e in zip(contributions, endowments)]

        # Social optimum: everyone contributes everything
        social_optimum = sum(endowments) * self.multiplier / self.num_players * self.num_players
        total_payoff = sum(payoffs)
        # Minimum total payoff: no one contributes
        min_total = sum(endowments)
        efficiency = (total_payoff - min_total) / (social_optimum - min_total) if social_optimum != min_total else 1.0

        return PublicGoodsResult(
            contributions=contributions,
            endowments=endowments,
            pool=pool,
            multiplied_pool=multiplied_pool,
            share=share,
            payoffs=payoffs,
            efficiency=efficiency,
        )

    def nash_payoff(self) -> float:
        """Payoff at Nash equilibrium (all contribute 0)."""
        return self.endowment

    def social_optimum_payoff(self) -> float:
        """Payoff at social optimum (all contribute endowment)."""
        return self.endowment * self.multiplier / self.num_players * self.num_players / self.num_players

    def marginal_per_capita_return(self) -> float:
        """MPCR: the return per dollar contributed, per player.

        MPCR = M / N. When MPCR < 1, free-riding is individually rational.
        """
        return self.multiplier / self.num_players

    def play_iterated(
        self,
        rounds: int,
        strategy_fn: list,  # list of callables: (round, history) -> contribution
    ) -> list[PublicGoodsResult]:
        """Play multiple rounds with strategy functions.

        Args:
            rounds: Number of rounds.
            strategy_fn: List of strategy functions, one per player.
                Each takes (round_number, history_of_results) and returns a contribution.

        Returns:
            List of PublicGoodsResult for each round.
        """
        history: list[PublicGoodsResult] = []
        for r in range(rounds):
            contributions = [fn(r, history) for fn in strategy_fn]
            result = self.play(contributions)
            history.append(result)
        return history
