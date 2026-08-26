from fastapi import APIRouter
import pandas as pd

router = APIRouter(
    prefix="/players",
    tags=["players"]
)

player_metrics = pd.read_parquet(
    "data/player_metrics_2025.parquet"
)

@router.get("/")
def get_players(
    limit: int = 25,
    sort_by: str = "xFP",
    signal: str | None = None
):
    valid_sort_columns = [
        "xFP",
        "actual_fp",
        "regression_delta",
        "xFP_per_game",
        "actual_fp_per_game"
    ]

    if sort_by not in valid_sort_columns:
        sort_by = "xFP"

    filtered_players = player_metrics.copy()

    if signal:
        filtered_players = filtered_players[
            filtered_players["signal"].str.upper() == signal.upper()
        ]

    sorted_players = filtered_players.sort_values(
        sort_by,
        ascending=False
    )

    return sorted_players.head(limit).to_dict(orient="records")

@router.get("/market-map")
def get_market_map():
    columns = [
        "player_id",
        "player_name",
        "posteam",
        "actual_fp_per_game",
        "xFP_per_game",
        "regression_delta_per_game",
        "signal"
    ]

    return player_metrics[columns].to_dict(orient="records")

@router.get("/{player_id}")
def get_player(player_id: str):
    player = player_metrics[
        player_metrics["player_id"] == player_id
    ]

    if player.empty:
        return {
            "error": "Player not found"
        }

    return player.iloc[0].to_dict()

@router.get("/signals/buy-low")
def get_buy_low(limit: int = 10):
    buy_low_players = player_metrics[
        player_metrics["signal"].isin(["BUY", "STRONG BUY"])
    ].sort_values(
        "regression_delta_per_game",
        ascending=True
    )

    return buy_low_players.head(limit).to_dict(orient="records")

@router.get("/signals/sell-high")
def get_sell_high(limit: int = 10):
    sell_high_players = player_metrics[
        player_metrics["signal"].isin(["SELL", "STRONG SELL"])
    ].sort_values(
        "regression_delta_per_game",
        ascending=False
    )

    return sell_high_players.head(limit).to_dict(orient="records")