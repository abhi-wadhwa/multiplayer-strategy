"""CLI entrypoint for multiplayer strategy games."""

from __future__ import annotations

import typer

app = typer.Typer(help="Multiplayer Strategy Games CLI")


@app.command()
def blotto(
    battlefields: int = typer.Option(5, help="Number of battlefields"),
    troops: int = typer.Option(100, help="Total troops per player"),
    rounds: int = typer.Option(10, help="Number of random matchups to simulate"),
) -> None:
    """Simulate Colonel Blotto games with random allocations."""
    from src.games.blotto import BlottoGame

    game = BlottoGame(num_battlefields=battlefields, num_troops=troops)
    import numpy as np

    rng = np.random.default_rng(42)
    p1_wins, p2_wins, ties = 0, 0, 0

    for i in range(rounds):
        a1 = game.random_allocation(rng)
        a2 = game.random_allocation(rng)
        result = game.play([a1, a2])
        if result.winner == 0:
            p1_wins += 1
        elif result.winner == 1:
            p2_wins += 1
        else:
            ties += 1
        typer.echo(f"Round {i+1}: {a1} vs {a2} -> Winner: {'P1' if result.winner == 0 else 'P2' if result.winner == 1 else 'Tie'} ({result.wins[0]}-{result.wins[1]})")

    typer.echo(f"\nResults: P1={p1_wins}, P2={p2_wins}, Ties={ties}")


@app.command()
def public_goods(
    players: int = typer.Option(4, help="Number of players"),
    endowment: float = typer.Option(100.0, help="Endowment per player"),
    multiplier: float = typer.Option(2.0, help="Pool multiplier"),
) -> None:
    """Run a Public Goods Game demonstration."""
    from src.games.public_goods import PublicGoodsGame

    game = PublicGoodsGame(num_players=players, endowment=endowment, multiplier=multiplier)

    scenarios = {
        "Full cooperation": [endowment] * players,
        "Full defection (Nash)": [0.0] * players,
        "Half contribution": [endowment / 2] * players,
        "One free-rider": [endowment] * (players - 1) + [0.0],
    }

    for name, contributions in scenarios.items():
        result = game.play(contributions)
        typer.echo(f"\n{name}:")
        typer.echo(f"  Contributions: {contributions}")
        typer.echo(f"  Pool: {result.pool:.1f} -> {result.multiplied_pool:.1f}")
        typer.echo(f"  Payoffs: {[f'{p:.1f}' for p in result.payoffs]}")
        typer.echo(f"  Efficiency: {result.efficiency:.1%}")


@app.command()
def tournament(
    rounds: int = typer.Option(200, help="Rounds per match"),
) -> None:
    """Run an Axelrod-style iterated PD tournament."""
    from src.tournament.runner import TournamentRunner

    runner = TournamentRunner(rounds_per_match=rounds)
    result = runner.run()

    typer.echo("\n=== PD Tournament Results ===\n")
    typer.echo(f"{'Rank':<5} {'Strategy':<20} {'Total Score':<15} {'Avg/Match':<12} {'Coop Rate':<12} {'W-L-D'}")
    typer.echo("-" * 80)

    for rank, entry in enumerate(result.rankings, 1):
        wld = f"{entry.wins}-{entry.losses}-{entry.draws}"
        typer.echo(
            f"{rank:<5} {entry.name:<20} {entry.total_score:<15.0f} "
            f"{entry.avg_score_per_match:<12.1f} {entry.avg_cooperation_rate:<12.1%} {wld}"
        )


@app.command()
def ui() -> None:
    """Launch the Streamlit web interface."""
    import subprocess
    import sys

    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/viz/app.py"])


if __name__ == "__main__":
    app()
