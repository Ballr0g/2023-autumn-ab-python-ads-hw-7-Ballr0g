"""Define schemas"""
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel

ErrorType = Literal["false-positive", "false-negative"]
BaseLine = Literal["constant_fraud", "constant_clean", "first_hypothesis"]


class POSTPredictByBaselineInput(BaseModel):
    """
    Input data for predict body
    """

    text: str


class MessageEntry(BaseModel):
    """
    Response representing a message checked for fraud.
    """

    checked_text: str
    prediction_result: str
    baseline_used: str
    execution_date: datetime


class ClassifiedTextTypes(Enum):
    """Text check results"""

    CLEAN = "clean"
    FRAUD = "fraud"
