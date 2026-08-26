from pydantic import BaseModel


class TradeRequest(BaseModel):
    side_a: list[str]
    side_b: list[str]