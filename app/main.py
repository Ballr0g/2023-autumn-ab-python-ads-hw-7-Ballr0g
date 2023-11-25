"""
Main module of the Anti-Fraud application.
"""
from datetime import datetime
from typing import Any, Callable, Generator

from app import (
    FALSE_NEGATIVE_COST,
    FALSE_POSITIVE_COST,
    constant_clean_loss,
    constant_fraud_loss,
    first_hypothesis_loss,
    models,
)
from app.database import SessionLocal, engine
from app.model_predict import constant_clean, constant_fraud, first_hypothesis
from app.models import Message
from app.schemas import (
    BaseLine,
    ClassifiedTextTypes,
    ErrorType,
    MessageEntry,
    POSTPredictByBaselineInput,
)
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

app: FastAPI = FastAPI()


if __name__ == "__main__":
    models.Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, Any, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root() -> dict[str, str]:
    """Returns welcome message for the fraud detector"""

    return {"message": "Hello! This is the fraud detector."}


@app.get("/cost/{error_type}")
async def get_cost_by_error_type(error_type: ErrorType) -> dict[str, int]:
    result_value: int = (
        FALSE_POSITIVE_COST if error_type == "false-positive" else FALSE_NEGATIVE_COST
    )

    return {"errorCost": result_value}


@app.get("/loss/{baseline}")
async def get_loss_by_baseline(baseline: BaseLine) -> dict[str, float]:
    if baseline == "constant_fraud":
        return {"baseDailyLineLoss": constant_fraud_loss}

    if baseline == "constant_clean":
        return {"baseDailyLineLoss": constant_clean_loss}

    return {"baseDailyLineLoss": first_hypothesis_loss}


def get_prediction_by_baseline(baseline: BaseLine) -> Callable[[str], str]:
    match baseline:
        case "constant_fraud":
            return constant_fraud
        case "constant_clean":
            return constant_clean

    return first_hypothesis


@app.post("/predict/{baseline}")
async def post_predict_by_baseline(
    baseline: BaseLine, checked_info: POSTPredictByBaselineInput, db: Session = Depends(get_db)
) -> dict[str, ClassifiedTextTypes]:
    prediction_func: Callable[[str], str] = get_prediction_by_baseline(baseline)
    prediction_result: str = prediction_func(checked_info.text)
    execution_time: datetime = datetime.now()

    new_message: Message = Message(
        input_text=checked_info.text,
        result_prediction=prediction_result,
        baseline_used=baseline,
        execution_date=execution_time,
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return {"result": ClassifiedTextTypes(prediction_result)}


@app.get("/latest_entry/{baseline}")
async def get_latest_entry(baseline: BaseLine, db: Session = Depends(get_db)) -> MessageEntry:
    latest_baseline_entry: Message | None = (
        db.query(Message)
        .filter(Message.baseline_used == baseline)
        .order_by(Message.execution_date.desc())
        .first()
    )

    if latest_baseline_entry is None:
        raise HTTPException(status_code=404, detail=f"No requests for baseline {baseline} found.")

    return MessageEntry(
        checked_text=latest_baseline_entry.input_text,
        prediction_result=latest_baseline_entry.result_prediction,
        baseline_used=latest_baseline_entry.baseline_used,
        execution_date=latest_baseline_entry.execution_date,
    )


@app.get("/number_of_entries")
async def get_number_of_entries(db: Session = Depends(get_db)) -> dict[str, int]:
    response: dict[str, int] = {}
    for i, j in db.query(Message.baseline_used, func.count()).group_by(Message.baseline_used).all():
        response[i] = j

    return response
