"""Decide whether every figure in a claim appears in a retrieved snippet.

The check is deterministic. A missing figure is unsupported, and a later model
call must not upgrade that result to supported. Spelled-out numbers such as
"thirty" are ignored. Thousands separators use commas, and the decimal mark is
a dot.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

Status = Literal["not_applicable", "numbers_present", "unsupported"]

_MINUS = str.maketrans({"−": "-", "–": "-"})
_TOKEN = re.compile(
    r"""
    (?<![A-Za-z0-9_])
    (?P<sign>[-+])?
    (?P<currency>[$€£])?
    (?P<body>
        \d{1,3}(?:,\d{3})+(?:\.\d+)?
        |
        \d+\.\d+
        |
        \d+
    )
    \s?%?
    (?![A-Za-z0-9_])
    """,
    re.VERBOSE,
)


@dataclass(frozen=True)
class NumberCheck:
    """Result of comparing claim figures with a retrieved snippet."""

    status: Status
    model_may_set_support: bool
    claim_numbers: tuple[str, ...]
    missing_numbers: tuple[str, ...]


def check_numbers(claim: str, snippet: str) -> NumberCheck:
    """Return unsupported when any claim figure is absent from the snippet."""

    if not isinstance(claim, str) or not isinstance(snippet, str):
        raise TypeError("claim and snippet must be strings")

    claim_numbers = _unique(_extract(claim))
    if not claim_numbers:
        return NumberCheck("not_applicable", True, (), ())

    snippet_numbers = set(_extract(snippet))
    missing = tuple(number for number in claim_numbers if number not in snippet_numbers)
    if missing:
        return NumberCheck("unsupported", False, claim_numbers, missing)
    return NumberCheck("numbers_present", True, claim_numbers, ())


def _extract(text: str) -> list[str]:
    normalized = text.translate(_MINUS)
    return [
        _canonical(match.group("sign"), match.group("body"))
        for match in _TOKEN.finditer(normalized)
    ]


def _canonical(sign: str | None, body: str) -> str:
    digits = body.replace(",", "")
    whole, dot, frac = digits.partition(".")
    frac = frac.rstrip("0")
    number = str(int(whole)) if not dot or not frac else f"{int(whole)}.{frac}"
    if sign == "-" and number != "0":
        return f"-{number}"
    return number


def _unique(numbers: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for number in numbers:
        if number in seen:
            continue
        seen.add(number)
        ordered.append(number)
    return tuple(ordered)
