from typing import Callable


def calculate_rate_for_hypothesis_function(
    hypothesis_function: Callable[[str], str], input_messages: list[str], expected_result: str
) -> float:
    mismatch_count = 0
    for input_message in input_messages:
        if hypothesis_function(input_message) != expected_result:
            mismatch_count += 1

    return mismatch_count / len(input_messages)


def calculate_money_loss_per_function(
    *,
    false_positive_rate: float,
    false_negative_rate: float,
    false_positive_cost: int,
    false_negative_cost: int,
    purchases_per_day: int,
    fraud_share: float,
) -> float:
    false_positive_loss = (
        purchases_per_day * (1.0 - fraud_share) * false_positive_cost * false_positive_rate
    )
    false_negative_loss = (
        purchases_per_day * fraud_share * false_negative_cost * false_negative_rate
    )

    return false_positive_loss + false_negative_loss
