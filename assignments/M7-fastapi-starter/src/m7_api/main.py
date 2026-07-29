from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(title="Учебный сервис прогнозов", version="0.1.0")


class PredictionRequest(BaseModel):
    value: float = Field(ge=0, le=1)


class PredictionResponse(BaseModel):
    label: Literal["низкий", "высокий"]
    confidence: float


@app.get("/health", tags=["служебные"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse, tags=["прогноз"])
def predict(payload: PredictionRequest) -> PredictionResponse:
    label: Literal["низкий", "высокий"] = "высокий" if payload.value >= 0.5 else "низкий"
    return PredictionResponse(label=label, confidence=abs(payload.value - 0.5) * 2)
