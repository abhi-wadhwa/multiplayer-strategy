"""Colonel Blotto game implementation.

Players allocate a fixed number of troops across battlefields.
The player who deploys more troops to a battlefield wins it.
The player winning the most battlefields wins the game.

Nash Equilibrium: In the symmetric case, the unique NE involves
randomizing uniformly over all allocations (for continuous troops)
or over a specific support set (for discrete troops).
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass


@dataclass
class BlottoResult:
    """Result of a Colonel Blotto game."""

    allocations: list[list[int]]  # Each player's allocation
    battlefield_winners: list[int | None]  # Winner index per battlefield (None = tie)
    wins: list[int]  # Number of battlefields won per player
    ties: int  # Number of tied battlefields
    winner: int | None  # Overall winner index (None = tie)


class BlottoGame:
    """Colonel Blotto game engine.

    Two or more players allocate T troops across B battlefields.
    Each battlefield is won by the player with the most troops there.
    Ties on a battlefield result in neither player winning it.
    The player winning the most battlefields wins the overall game.

    Attributes:
        num_battlefields: Number of battlefields (B).
        num_troops: Total troops each player must allocate (T).
        num_players: Number of players (default 2).
    """

    def __init__(
        self,
        num_battlefields: int = 5,
        num_troops: int = 100,
        num_players: int = 2,
    ) -> None:
        if num_battlefields < 1:
            raise ValueError("Must have at least 1 battlefield")
        if num_troops < 1:
            raise ValueError("Must have at least 1 troop")
        if num_players < 2:
            raise ValueError("Must have at least 2 players")
        self.num_battlefields = num_battlefields
        self.num_troops = num_troops
        self.num_players = num_players

    def validate_allocation(self, allocation: list[int]) -> bool:
        """Check if an allocation is valid (correct length, non-negative, sums to num_troops)."""
        if len(allocation) != self.num_battlefields:
            return False
        if any(t < 0 for t in allocation):
            return False
        if sum(allocation) != self.num_troops:
            return False
        return True

    def play(self, allocations: list[list[int]]) -> BlottoResult:
        """Play a round of Colonel Blotto.

        Args:
            allocations: List of allocations, one per player.
                Each allocation is a list of troop counts per battlefield.

        Returns:
            BlottoResult with battlefield outcomes and overall winner.

        Raises:
            ValueError: If allocations are invalid.
        """
        if len(allocations) != self.num_players:
            raise ValueError(f"Expected {self.num_players} allocations, got {len(allocations)}")

        for i, alloc in enumerate(allocations):
            if not self.validate_allocation(alloc):
                raise ValueError(
                    f"Invalid allocation for player {i}: {alloc}. "
                    f"Must have {self.num_battlefields} non-negative values summing to {self.num_troops}"
                )

        battlefield_winners: list[int | None] = []
        for bf in range(self.num_battlefields):
            troops = [allocations[p][bf] for p in range(self.num_players)]
            max_troops = max(troops)
            winners = [p for p in range(self.num_players) if troops[p] == max_troops]
            if len(winners) == 1:
                battlefield_winners.append(winners[0])
            else:
                battlefield_winners.append(None)  # Tie

        wins = [0] * self.num_players
        ties = 0
        for w in battlefield_winners:
            if w is not None:
                wins[w] += 1
            else:
                ties += 1

        max_wins = max(wins)
        overall_winners = [p for p in range(self.num_players) if wins[p] == max_wins]
        winner = overall_winners[0] if len(overall_winners) == 1 else None

        return BlottoResult(
            allocations=allocations,
            battlefield_winners=battlefield_winners,
            wins=wins,
            ties=ties,
            winner=winner,
        )

    def random_allocation(self, rng: np.random.Generator | None = None) -> list[int]:
        """Generate a random valid allocation using the stars-and-bars method.

        Uniformly samples from all ways to distribute num_troops
        across num_battlefields.
        """
        if rng is None:
            rng = np.random.default_rng()

        # Use the "breaks" method: choose B-1 break points in [0, T]
        breaks = sorted(rng.choice(
            self.num_troops + self.num_battlefields - 1,
            size=self.num_battlefields - 1,
            replace=False,
        ))

        allocation = []
        prev = 0
        for b in breaks:
            allocation.append(int(b - prev))
            prev = b + 1
        allocation.append(int(self.num_troops + self.num_battlefields - 1 - prev))

        # Adjust for the bars-and-stars offset
        # Simpler approach: multinomial-like
        allocation = []
        remaining = self.num_troops
        for i in range(self.num_battlefields - 1):
            if remaining == 0:
                allocation.append(0)
            else:
                t = int(rng.integers(0, remaining + 1))
                allocation.append(t)
                remaining -= t
        allocation.append(remaining)
        return allocation

    def evaluate_strategy_matchup(
        self,
        strategy_a: list[list[int]],
        strategy_b: list[list[int]],
    ) -> tuple[float, float]:
        """Evaluate two mixed strategies (lists of pure allocations) against each other.

        Returns average win rates for each strategy (player A, player B).
        """
        a_wins = 0
        b_wins = 0
        total = 0

        for alloc_a in strategy_a:
            for alloc_b in strategy_b:
                result = self.play([alloc_a, alloc_b])
                if result.winner == 0:
                    a_wins += 1
                elif result.winner == 1:
                    b_wins += 1
                total += 1

        return a_wins / total if total > 0 else 0.0, b_wins / total if total > 0 else 0.0

    @staticmethod
    def nash_equilibrium_note() -> str:
        """Return a description of the Nash equilibrium for Colonel Blotto."""
        return (
            "In the continuous symmetric Colonel Blotto game with B battlefields "
            "and T troops per player, the unique Nash equilibrium involves each "
            "player independently drawing each battlefield's allocation from a "
            "uniform distribution on [0, 2T/B], subject to the budget constraint. "
            "For discrete versions, the equilibrium support is the set of all "
            "permutations of certain 'balanced' allocations."
        )
