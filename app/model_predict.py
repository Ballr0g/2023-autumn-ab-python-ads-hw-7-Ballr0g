import string
from itertools import groupby
from typing import Final


def constant_fraud(message: str) -> str:  # pylint: disable=unused-argument
    """
    Constant fraud method.
    :param message: Message checked for fraud.
    :return: fraud or clean.
    """
    result: Final[str] = "fraud"

    # Проверка на то, что ваша функция возвращает валидное значение.
    assert result in ["fraud", "clean"]

    return result


def constant_clean(message: str) -> str:  # pylint: disable=unused-argument
    """
    Constant clean method.
    :param message: Message checked for fraud.
    :return: fraud or clean.
    """
    result = "clean"

    # проверка на то, что ваша функция возвращает валидное значение
    assert result in ["fraud", "clean"]

    return result


def remove_consecutive_duplicates(s: str) -> str:
    return "".join(i for i, _ in groupby(s))


def tokenize_message(s: str) -> list[str]:
    """
    Разбивает строку с предварительной нормализацией:
        - Переводит в нижний регистр;
        - Удаляет последовательные дублирующиеся символы;
        - Удаляет все символы из string.punctuation;
        - Разделяет строку по пробелам.

    :param s: входное сообщение с разделяемым текстом
    :return: список слов, разделённый по пробелам. В каждом слове удалены подряд идущие повторы букв
    """
    s = remove_consecutive_duplicates(s.lower())
    table = str.maketrans("", "", string.punctuation)
    s = s.translate(table)
    return s.split()


def damerau_levenshtein_distance(s1: str, s2: str) -> int:
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in range(-1, lenstr1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, lenstr2 + 1):
        d[(-1, j)] = j + 1

    for i in range(lenstr1):
        for j in range(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,  # deletion
                d[(i, j - 1)] + 1,  # insertion
                d[(i - 1, j - 1)] + cost,  # substitution
            )
            if i and j and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + cost)  # transposition
    return d[lenstr1 - 1, lenstr2 - 1]


def is_token_fraud(token: str) -> bool:
    blacklisted_constant_tokens = ["тг"]
    whitelisted_constant_tokens = ["тележка"]
    checked_telegram_letters = ["т", "л", "г"]
    telegram_tokens_with_count = {
        "телеграм": 2,
        "телега": 3,
    }

    if token in blacklisted_constant_tokens:
        return True

    # Костыль на обработку слова 'тележка' в форме инфинитива
    # (остальные не попадают под false-positive).
    if token in whitelisted_constant_tokens:
        return False

    # Слишком длинные и слишком короткие строки не сравниваем.
    if len(token) < 5 or len(token) > 10:
        return False

    # Максимальное расстояние Дамерау-Левенштейна, при котором токен является фродом.
    fraud_suspicion_distance = 3

    for telegram_token, checked_count in telegram_tokens_with_count.items():
        # Смотрим, какие из ключевых букв слова телеграм есть в данном токене:
        present_telegram_chars = [char for char in checked_telegram_letters if char in token]
        # Если в слове достаточно много букв для похожести на телеграм, используем алгоритм
        if len(present_telegram_chars) >= checked_count:
            distance_to_fraud = damerau_levenshtein_distance(telegram_token, token)
            if distance_to_fraud <= fraud_suspicion_distance:
                return True

    return False


def first_hypothesis(message: str) -> str:
    """
    First hypothesis method.
    :param message: Message checked for fraud.
    :return: fraud or clean.
    """
    # напишите ваш код здесь и положите результат в переменную result
    tokenized_message = tokenize_message(message)

    result = "clean"
    for token in tokenized_message:
        if is_token_fraud(token):
            result = "fraud"
            break

    # проверка на то, что ваша функция возвращает валидное значение
    assert result in ["fraud", "clean"]

    return result
