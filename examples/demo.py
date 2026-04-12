"""Demo script showcasing all three games."""

from __future__ import annotations

import numpy as np

from src.games.blotto import BlottoGame
from src.games.public_goods import PublicGoodsGame
from src.tournament.runner import TournamentRunner


def demo_blotto():
    print("=" * 60)
    print("COLONEL BLOTTO")
    print("=" * 60)
    game = BlottoGame(num_battlefields=5, num_troops=100)
    rng = np.random.default_rng(42)

    concentrate = [100, 0, 0, 0, 0]
    spread = [20, 20, 20, 20, 20]
    result = game.play([concentrate, spread])
    print(f"\nConcentrate {concentrate} vs Spread {spread}")
    print(f"Winners per BF: {result.battlefield_winners}")
    print(f"Score: {result.wins[0]}-{result.wins[1]} -> {'Concentrate' if result.winner == 0 else 'Spread'} wins!")

    p1_wins = sum(1 for _ in range(1000)
                  if game.play([game.random_allocation(rng), game.random_allocation(rng)]).winner == 0)
    print(f"\n1000 random games: P1 wins {p1_wins}, P2 wins {1000 - p1_wins} (approx 50/50)")


def demo_public_goods():
    print("\n" + "=" * 60)
    print("PUBLIC GOODS GAME")
    print("=" * 60)
    game = PublicGoodsGame(num_players=4, endowment=100, multiplier=2.0)
    print(f"MPCR: {game.marginal_per_capita_return():.2f}")
    print(f"Social dilemma: {game.is_social_dilemma}")

    for name, contribs in [
        ("Full cooperation", [100, 100, 100, 100]),
        ("Nash equilibrium", [0, 0, 0, 0]),
        ("One free-rider", [100, 100, 100, 0]),
    ]:
        result = game.play(contribs)
        print(f"\n{name}: contributions={contribs}")
        print(f"  Payoffs: {[f'{p:.0f}' for p in result.payoffs]}, Efficiency: {result.efficiency:.0%}")


def demo_tournament():
    print("\n" + "=" * 60)
    print("PD TOURNAMENT (Axelrod-style)")
    print("=" * 60)
    runner = TournamentRunner(rounds_per_match=200)
    result = runner.run()

    print(f"\n{'Rank':<5} {'Strategy':<20} {'Score':<12} {'Coop Rate':<12}")
    print("-" * 55)
    for rank, entry in enumerate(result.rankings, 1):
        print(f"{rank:<5} {entry.name:<20} {entry.total_score:<12.0f} {entry.avg_cooperation_rate:<12.1%}")


if __name__ == "__main__":
    demo_blotto()
    demo_public_goods()
    demo_tournament()
