"""Prisoner's Dilemma game implementation.

Two players simultaneously choose to Cooperate (C) or Defect (D).
Payoff matrix (row player):
    C,C -> R,R (mutual cooperation reward)
    C,D -> S,T (sucker's payoff vs. temptation)
    D,C -> T,S (temptation vs. sucker's)
    D,D -> P,P (mutual defection punishment)

For a Prisoner's Dilemma: T > R > P > S and 2R > T + S.

Nash Equilibrium (one-shot): Both defect (D,D).
Iterated: Cooperation can emerge via strategies like Tit-for-Tat.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Action(Enum):
    """Prisoner's Dilemma actions."""
    COOPERATE = "C"
    DEFECT = "D"


@dataclass
class PDResult:
    """Result of one round of the Prisoner's Dilemma."""
    actions: tuple[Action, Action]
    payoffs: tuple[float, float]


@dataclass
class PDMatchResult:
    """Result of an iterated PD match between two players."""
    player_a: str
    player_b: str
    rounds: list[PDResult]
    total_payoffs: tuple[float, float]
    cooperation_rates: tuple[float, float]


class PrisonersDilemmaGame:
    """Prisoner's Dilemma game engine.

    Supports both one-shot and iterated play with configurable payoffs.

    Default payoffs (classic):
        T=5 (temptation), R=3 (reward), P=1 (punishment), S=0 (sucker)

    Attributes:
        temptation: Payoff for defecting against cooperator (T).
        reward: Payoff for mutual cooperation (R).
        punishment: Payoff for mutual defection (P).
        sucker: Payoff for cooperating against defector (S).
    """

    def __init__(
        self,
        temptation: float = 5.0,
        reward: float = 3.0,
        punishment: float = 1.0,
        sucker: float = 0.0,
    ) -> None:
        self.temptation = temptation
        self.reward = reward
        self.punishment = punishment
        self.sucker = sucker

        if not (temptation > reward > punishment > sucker):
            raise ValueError("Must have T > R > P > S for a valid Prisoner's Dilemma")
        if not (2 * reward > temptation + sucker):
            raise ValueError("Must have 2R > T + S for iterated PD cooperation to be efficient")

    def payoff(self, action_a: Action, action_b: Action) -> tuple[float, float]:
        """Compute payoffs for a single round.

        Args:
            action_a: Player A's action.
            action_b: Player B's action.

        Returns:
            Tuple of (player_a_payoff, player_b_payoff).
        """
        if action_a == Action.COOPERATE and action_b == Action.COOPERATE:
            return (self.reward, self.reward)
        elif action_a == Action.COOPERATE and action_b == Action.DEFECT:
            return (self.sucker, self.temptation)
        elif action_a == Action.DEFECT and action_b == Action.COOPERATE:
            return (self.temptation, self.sucker)
        else:  # Both defect
            return (self.punishment, self.punishment)

    def play_round(self, action_a: Action, action_b: Action) -> PDResult:
        """Play a single round."""
        payoffs = self.payoff(action_a, action_b)
        return PDResult(actions=(action_a, action_b), payoffs=payoffs)

    def play_match(
        self,
        strategy_a,  # callable: (round, my_history, opp_history) -> Action
        strategy_b,  # callable: (round, my_history, opp_history) -> Action
        rounds: int = 200,
        name_a: str = "Player A",
        name_b: str = "Player B",
    ) -> PDMatchResult:
        """Play an iterated PD match between two strategies.

        Args:
            strategy_a: Strategy function for player A.
            strategy_b: Strategy function for player B.
            rounds: Number of rounds to play.
            name_a: Display name for player A.
            name_b: Display name for player B.

        Returns:
            PDMatchResult with full round history and totals.
        """
        results: list[PDResult] = []
        history_a: list[Action] = []
        history_b: list[Action] = []

        for r in range(rounds):
            action_a = strategy_a(r, history_a, history_b)
            action_b = strategy_b(r, history_b, history_a)
            result = self.play_round(action_a, action_b)
            results.append(result)
            history_a.append(action_a)
            history_b.append(action_b)

        total_a = sum(r.payoffs[0] for r in results)
        total_b = sum(r.payoffs[1] for r in results)

        coop_a = sum(1 for a in history_a if a == Action.COOPERATE) / len(history_a) if history_a else 0
        coop_b = sum(1 for a in history_b if a == Action.COOPERATE) / len(history_b) if history_b else 0

        return PDMatchResult(
            player_a=name_a,
            player_b=name_b,
            rounds=results,
            total_payoffs=(total_a, total_b),
            cooperation_rates=(coop_a, coop_b),
        )
