"""Classic Prisoner's Dilemma strategies for iterated play.

Each strategy is a callable: (round, my_history, opponent_history) -> Action

References:
    - Axelrod, R. (1984). The Evolution of Cooperation.
    - Nowak, M. A. (2006). Five rules for the evolution of cooperation.
"""

from __future__ import annotations

import random

from src.games.prisoners_dilemma import Action


def always_cooperate(round_num: int, my_history: list[Action], opp_history: list[Action]) -> Action:
    """Always cooperate regardless of opponent's actions."""
    return Action.COOPERATE


def always_defect(round_num: int, my_history: list[Action], opp_history: list[Action]) -> Action:
    """Always defect regardless of opponent's actions."""
    return Action.DEFECT


def tit_for_tat(round_num: int, my_history: list[Action], opp_history: list[Action]) -> Action:
    """Start with cooperation, then copy opponent's last action.

    The most famous and robust strategy from Axelrod's tournaments.
    Properties: Nice (never defects first), Retaliatory, Forgiving, Clear.
    """
    if round_num == 0:
        return Action.COOPERATE
    return opp_history[-1]


def suspicious_tit_for_tat(round_num: int, my_history: list[Action], opp_history: list[Action]) -> Action:
    """Like TFT but starts with defection."""
    if round_num == 0:
        return Action.DEFECT
    return opp_history[-1]


def grim_trigger(round_num: int, my_history: list[Action], opp_history: list[Action]) -> Action:
    """Cooperate until opponent defects, then defect forever.

    Also known as "Friedman" strategy. Enforces cooperation through
    the threat of permanent punishment.
    """
    if round_num == 0:
        return Action.COOPERATE
    if Action.DEFECT in opp_history:
        return Action.DEFECT
    return Action.COOPERATE


def random_strategy(round_num: int, my_history: list[Action], opp_history: list[Action]) -> Action:
    """Cooperate or defect with equal probability."""
    return Action.COOPERATE if random.random() < 0.5 else Action.DEFECT


def pavlov(round_num: int, my_history: list[Action], opp_history: list[Action]) -> Action:
    """Win-stay, lose-shift strategy.

    Cooperate if both players chose the same action last round,
    defect otherwise. Starts with cooperation.

    Also known as "Win-Stay, Lose-Shift" (WSLS).
    """
    if round_num == 0:
        return Action.COOPERATE
    # "Win" = both same action (mutual C or mutual D)
    if my_history[-1] == opp_history[-1]:
        return Action.COOPERATE
    return Action.DEFECT


def tit_for_two_tats(round_num: int, my_history: list[Action], opp_history: list[Action]) -> Action:
    """Only defect if opponent defected in both of the last two rounds.

    More forgiving than TFT — tolerates a single defection.
    """
    if round_num < 2:
        return Action.COOPERATE
    if opp_history[-1] == Action.DEFECT and opp_history[-2] == Action.DEFECT:
        return Action.DEFECT
    return Action.COOPERATE


def generous_tit_for_tat(round_num: int, my_history: list[Action], opp_history: list[Action]) -> Action:
    """TFT but occasionally forgives a defection (10% chance).

    Helps break cycles of mutual retaliation.
    """
    if round_num == 0:
        return Action.COOPERATE
    if opp_history[-1] == Action.DEFECT:
        return Action.COOPERATE if random.random() < 0.1 else Action.DEFECT
    return Action.COOPERATE


# Registry of all strategies with metadata
STRATEGIES: dict[str, dict] = {
    "Always Cooperate": {
        "fn": always_cooperate,
        "description": "Always cooperates regardless of opponent",
        "nice": True,
    },
    "Always Defect": {
        "fn": always_defect,
        "description": "Always defects regardless of opponent",
        "nice": False,
    },
    "Tit-for-Tat": {
        "fn": tit_for_tat,
        "description": "Cooperate first, then copy opponent's last action",
        "nice": True,
    },
    "Suspicious TFT": {
        "fn": suspicious_tit_for_tat,
        "description": "Like TFT but starts with defection",
        "nice": False,
    },
    "Grim Trigger": {
        "fn": grim_trigger,
        "description": "Cooperate until opponent defects, then defect forever",
        "nice": True,
    },
    "Random": {
        "fn": random_strategy,
        "description": "Cooperate or defect with equal probability",
        "nice": False,
    },
    "Pavlov": {
        "fn": pavlov,
        "description": "Win-stay, lose-shift",
        "nice": True,
    },
    "Tit-for-Two-Tats": {
        "fn": tit_for_two_tats,
        "description": "Only retaliate after two consecutive defections",
        "nice": True,
    },
    "Generous TFT": {
        "fn": generous_tit_for_tat,
        "description": "TFT with 10% chance of forgiving a defection",
        "nice": True,
    },
}


def get_strategy(name: str):
    """Get a strategy function by name."""
    if name not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {name}. Available: {list(STRATEGIES.keys())}")
    return STRATEGIES[name]["fn"]


def list_strategies() -> list[str]:
    """List all available strategy names."""
    return list(STRATEGIES.keys())
