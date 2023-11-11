import json
import os
from pathlib import Path
from typing import Final

from app.model_estimate import (
    calculate_money_loss_per_function,
    calculate_rate_for_hypothesis_function,
)
from app.model_predict import constant_clean, constant_fraud, first_hypothesis
from dotenv import load_dotenv

load_dotenv()

FRAUD_SAMPLES_PATH: Final[str | None] = os.getenv("FRAUD_SAMPLES_PATH")
assert (
    FRAUD_SAMPLES_PATH is not None
), "FRAUD_SAMPLES_PATH must be present, consider adding it to .env."

CLEAN_SAMPLES_PATH: Final[str | None] = os.getenv("CLEAN_SAMPLES_PATH")
assert (
    CLEAN_SAMPLES_PATH is not None
), "CLEAN_SAMPLES_PATH must be present, consider adding it to .env."

# считываем 1000 фродовых сообщений
if (Path(__file__).parent.parent / FRAUD_SAMPLES_PATH).is_file():
    with open(Path(__file__).parent.parent / FRAUD_SAMPLES_PATH, "r", encoding="utf-8") as handler:
        FRAUD_MESSAGES: Final[list[str]] = json.load(handler)

# считываем 1000 чистых сообщений
if (Path(__file__).parent.parent / CLEAN_SAMPLES_PATH).is_file():
    with open(Path(__file__).parent.parent / CLEAN_SAMPLES_PATH, "r", encoding="utf-8") as handler:
        CLEAN_MESSAGES: Final[list[str]] = json.load(handler)

FALSE_POSITIVE_COST: Final[int] = int(os.getenv("FALSE_POSITIVE_COST") or "")
FALSE_NEGATIVE_COST: Final[int] = int(os.getenv("FALSE_NEGATIVE_COST") or "")
DAILY_PURCHASES: Final[int] = int(os.getenv("DAILY_PURCHASES") or "")
FRAUD_SHARE: Final[float] = float(os.getenv("FRAUD_SHARE") or "")

# следующие две строки проверяют, что считанные списки сообщений имеют
# правильную длину
assert len(FRAUD_MESSAGES) == 1000
assert len(CLEAN_MESSAGES) == 1000

constant_fraud_false_positive: float = calculate_rate_for_hypothesis_function(
    constant_fraud, CLEAN_MESSAGES, "clean"
)
constant_fraud_false_negative: float = calculate_rate_for_hypothesis_function(
    constant_fraud, FRAUD_MESSAGES, "fraud"
)
constant_clean_false_positive: float = calculate_rate_for_hypothesis_function(
    constant_clean, CLEAN_MESSAGES, "clean"
)
constant_clean_false_negative: float = calculate_rate_for_hypothesis_function(
    constant_clean, FRAUD_MESSAGES, "fraud"
)
first_hypothesis_false_positive: float = calculate_rate_for_hypothesis_function(
    first_hypothesis, CLEAN_MESSAGES, "clean"
)
first_hypothesis_false_negative: float = calculate_rate_for_hypothesis_function(
    first_hypothesis, FRAUD_MESSAGES, "fraud"
)

constant_fraud_loss: float = calculate_money_loss_per_function(
    false_positive_rate=constant_fraud_false_positive,
    false_negative_rate=constant_fraud_false_negative,
    false_positive_cost=FALSE_POSITIVE_COST,
    false_negative_cost=FALSE_NEGATIVE_COST,
    purchases_per_day=DAILY_PURCHASES,
    fraud_share=FRAUD_SHARE,
)
constant_clean_loss: float = calculate_money_loss_per_function(
    false_positive_rate=constant_clean_false_positive,
    false_negative_rate=constant_clean_false_negative,
    false_positive_cost=FALSE_POSITIVE_COST,
    false_negative_cost=FALSE_NEGATIVE_COST,
    purchases_per_day=DAILY_PURCHASES,
    fraud_share=FRAUD_SHARE,
)
first_hypothesis_loss: float = calculate_money_loss_per_function(
    false_positive_rate=first_hypothesis_false_positive,
    false_negative_rate=first_hypothesis_false_negative,
    false_positive_cost=FALSE_POSITIVE_COST,
    false_negative_cost=FALSE_NEGATIVE_COST,
    purchases_per_day=DAILY_PURCHASES,
    fraud_share=FRAUD_SHARE,
)
