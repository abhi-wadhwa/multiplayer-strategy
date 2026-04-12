"""Streamlit web interface for multiplayer strategy games."""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Multiplayer Strategy Games", layout="wide")
st.title("Multiplayer Strategy Games")

game_choice = st.sidebar.selectbox("Select Game", ["Colonel Blotto", "Public Goods Game", "PD Tournament"])

if game_choice == "Colonel Blotto":
    st.header("Colonel Blotto")
    st.markdown("""
    Allocate your troops across battlefields. Win more battlefields than your opponent!

    **Nash Equilibrium**: In the symmetric continuous case, the equilibrium involves
    randomizing uniformly over balanced allocations.
    """)

    col1, col2 = st.columns(2)
    with col1:
        num_bf = st.slider("Battlefields", 3, 10, 5)
    with col2:
        num_troops = st.slider("Total Troops", 10, 200, 100)

    from src.games.blotto import BlottoGame
    game = BlottoGame(num_battlefields=num_bf, num_troops=num_troops)

    st.subheader("Your Allocation")
    allocation = []
    cols = st.columns(num_bf)
    remaining = num_troops
    for i, c in enumerate(cols):
        with c:
            if i < num_bf - 1:
                val = st.number_input(f"BF {i+1}", 0, remaining, 0, key=f"bf_{i}")
                allocation.append(val)
                remaining -= val
            else:
                st.write(f"BF {i+1}: {remaining}")
                allocation.append(remaining)

    if st.button("Play vs Random Bot"):
        rng = np.random.default_rng()
        bot_alloc = game.random_allocation(rng)
        if sum(allocation) == num_troops and all(a >= 0 for a in allocation):
            result = game.play([allocation, bot_alloc])

            fig = go.Figure()
            x = [f"BF {i+1}" for i in range(num_bf)]
            fig.add_trace(go.Bar(name="You", x=x, y=allocation, marker_color="blue"))
            fig.add_trace(go.Bar(name="Bot", x=x, y=bot_alloc, marker_color="red"))
            fig.update_layout(barmode="group", title="Troop Allocations")
            st.plotly_chart(fig, use_container_width=True)

            winners_text = []
            for i, w in enumerate(result.battlefield_winners):
                if w == 0:
                    winners_text.append(f"BF {i+1}: **You win**")
                elif w == 1:
                    winners_text.append(f"BF {i+1}: **Bot wins**")
                else:
                    winners_text.append(f"BF {i+1}: Tie")
            st.markdown(" | ".join(winners_text))

            if result.winner == 0:
                st.success(f"You win! {result.wins[0]}-{result.wins[1]}")
            elif result.winner == 1:
                st.error(f"Bot wins! {result.wins[1]}-{result.wins[0]}")
            else:
                st.warning(f"Tie! {result.wins[0]}-{result.wins[1]}")
        else:
            st.error(f"Invalid allocation. Must sum to {num_troops}.")

    # Simulation
    st.subheader("Monte Carlo Simulation (Random vs Random)")
    if st.button("Run 1000 Random Games"):
        rng = np.random.default_rng(42)
        p1_wins, p2_wins, ties = 0, 0, 0
        for _ in range(1000):
            a1 = game.random_allocation(rng)
            a2 = game.random_allocation(rng)
            res = game.play([a1, a2])
            if res.winner == 0:
                p1_wins += 1
            elif res.winner == 1:
                p2_wins += 1
            else:
                ties += 1
        st.write(f"P1 wins: {p1_wins}, P2 wins: {p2_wins}, Ties: {ties}")
        st.write("(Approximately equal, confirming symmetric equilibrium)")


elif game_choice == "Public Goods Game":
    st.header("Public Goods Game")
    st.markdown("""
    Each player secretly contributes to a shared pool.
    The pool is multiplied and divided equally.

    **Social Dilemma**: Contributing benefits everyone, but free-riding benefits the individual.

    **Nash Equilibrium**: Contribute nothing. **Social Optimum**: Contribute everything.
    """)

    from src.games.public_goods import PublicGoodsGame

    col1, col2, col3 = st.columns(3)
    with col1:
        n_players = st.slider("Players", 2, 8, 4)
    with col2:
        endowment = st.slider("Endowment", 10, 500, 100)
    with col3:
        multiplier = st.slider("Multiplier", 1.1, float(n_players) - 0.1, 2.0, 0.1)

    game = PublicGoodsGame(num_players=n_players, endowment=endowment, multiplier=multiplier)
    st.info(f"MPCR = {game.marginal_per_capita_return():.2f} ({'< 1: free-riding temptation' if game.marginal_per_capita_return() < 1 else '>= 1: always contribute'})")

    st.subheader("Your Contribution")
    your_contribution = st.slider("How much do you contribute?", 0.0, float(endowment), float(endowment) / 2)

    bot_strategy = st.selectbox("Bot Strategy", ["Nash (0)", "Cooperate (all)", "Half", "Random"])

    if st.button("Play Round"):
        rng = np.random.default_rng()
        bot_contributions = []
        for _ in range(n_players - 1):
            if bot_strategy == "Nash (0)":
                bot_contributions.append(0.0)
            elif bot_strategy == "Cooperate (all)":
                bot_contributions.append(float(endowment))
            elif bot_strategy == "Half":
                bot_contributions.append(float(endowment) / 2)
            else:
                bot_contributions.append(float(rng.uniform(0, endowment)))

        all_contributions = [your_contribution] + bot_contributions
        result = game.play(all_contributions)

        fig = go.Figure()
        labels = ["You"] + [f"Bot {i+1}" for i in range(n_players - 1)]
        colors = ["blue"] + ["red"] * (n_players - 1)
        fig.add_trace(go.Bar(x=labels, y=all_contributions, marker_color=colors, name="Contributions"))
        fig.add_hline(y=result.share, line_dash="dash", annotation_text=f"Equal Share: {result.share:.1f}")
        fig.update_layout(title="Contributions & Equal Share")
        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Your Payoff", f"{result.payoffs[0]:.1f}")
        c2.metric("Pool", f"{result.multiplied_pool:.1f}")
        c3.metric("Efficiency", f"{result.efficiency:.1%}")


elif game_choice == "PD Tournament":
    st.header("Iterated Prisoner's Dilemma Tournament")
    st.markdown("""
    Classic Axelrod-style round-robin tournament.
    Each strategy plays every other (and itself) in iterated PD matches.

    **Key Insight**: Nice strategies (those that never defect first) tend to do well,
    with Tit-for-Tat being famously robust.
    """)

    from src.tournament.runner import TournamentRunner
    from src.strategies.pd_strategies import STRATEGIES

    rounds = st.slider("Rounds per match", 50, 500, 200)

    available = list(STRATEGIES.keys())
    selected = st.multiselect("Select strategies", available, default=available[:6])

    if len(selected) < 2:
        st.warning("Select at least 2 strategies")
    elif st.button("Run Tournament"):
        with st.spinner("Running tournament..."):
            runner = TournamentRunner(rounds_per_match=rounds, strategy_names=selected)
            result = runner.run()

        rankings = result.rankings
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[e.name for e in rankings],
            y=[e.total_score for e in rankings],
            marker_color=["green" if STRATEGIES[e.name]["nice"] else "red" for e in rankings],
            text=[f"Coop: {e.avg_cooperation_rate:.0%}" for e in rankings],
            textposition="outside",
        ))
        fig.update_layout(title="Tournament Rankings (Green=Nice, Red=Not Nice)", yaxis_title="Total Score")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Detailed Results")
        for rank, entry in enumerate(rankings, 1):
            st.write(f"**{rank}. {entry.name}** — Score: {entry.total_score:.0f}, "
                     f"Avg/match: {entry.avg_score_per_match:.1f}, "
                     f"Cooperation: {entry.avg_cooperation_rate:.1%}, "
                     f"W-L-D: {entry.wins}-{entry.losses}-{entry.draws}")
