from fastapi import APIRouter
import pandas as pd

from backend.app.schemas.trade import TradeRequest

router = APIRouter(
    prefix="/trades",
    tags=["trades"]
)

player_metrics = pd.read_parquet(
    "data/player_metrics_2025.parquet"
)


@router.post("/analyze")
def analyze_trade(trade: TradeRequest):
    side_a_players = player_metrics[
        player_metrics["player_id"].isin(trade.side_a)
    ]

    side_b_players = player_metrics[
        player_metrics["player_id"].isin(trade.side_b)
    ]

    # xFP per game totals
    side_a_xfp = float(
        pd.to_numeric(
            side_a_players["xFP_per_game"],
            errors="coerce"
        ).fillna(0).sum()
    )

    side_b_xfp = float(
        pd.to_numeric(
            side_b_players["xFP_per_game"],
            errors="coerce"
        ).fillna(0).sum()
    )

    # Temporary VORP placeholders
    side_a_vorp = side_a_xfp
    side_b_vorp = side_b_xfp

    # Regression context
    side_a_delta = float(
        pd.to_numeric(
            side_a_players["regression_delta_per_game"],
            errors="coerce"
        ).fillna(0).sum()
    )

    side_b_delta = float(
        pd.to_numeric(
            side_b_players["regression_delta_per_game"],
            errors="coerce"
        ).fillna(0).sum()
    )

    # Winner
    if side_a_xfp > side_b_xfp:
        winner = "SIDE_A"
    elif side_b_xfp > side_a_xfp:
        winner = "SIDE_B"
    else:
        winner = "TIE"

    # Margin
    trade_margin = abs(side_a_xfp - side_b_xfp)

    # Grade
    if trade_margin < 1:
        trade_grade = "EVEN"
    elif trade_margin < 3:
        trade_grade = "SLIGHT EDGE"
    elif trade_margin < 6:
        trade_grade = "CLEAR EDGE"
    else:
        trade_grade = "LOPSIDED"

    # Explanation
    if winner == "SIDE_A":
        explanation = f"Side A wins by {trade_margin:.2f} xFP per game."
    elif winner == "SIDE_B":
        explanation = f"Side B wins by {trade_margin:.2f} xFP per game."
    else:
        explanation = "The trade is effectively even based on xFP per game."

    if side_a_delta < side_b_delta:
        explanation += " Side A has more positive regression upside."
    elif side_b_delta < side_a_delta:
        explanation += " Side B has more positive regression upside."

    return {
        "side_a": side_a_players.to_dict(orient="records"),
        "side_b": side_b_players.to_dict(orient="records"),
        "side_a_xfp": side_a_xfp,
        "side_b_xfp": side_b_xfp,
        "side_a_vorp": side_a_vorp,
        "side_b_vorp": side_b_vorp,
        "side_a_regression_delta": side_a_delta,
        "side_b_regression_delta": side_b_delta,
        "winner": winner,
        "trade_margin": trade_margin,
        "trade_grade": trade_grade,
        "explanation": explanation
    }