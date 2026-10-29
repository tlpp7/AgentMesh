"""Composable, offline text constraints."""
from .core import Constraint

def nonempty() -> Constraint:
    return Constraint("nonempty", lambda text: bool(text.strip()))

def min_length(n: int) -> Constraint:
    if n < 0:
        raise ValueError("minimum length must be nonnegative")
    return Constraint(f"min_length:{n}", lambda text: len(text) >= n)

def contains(term: str, case_sensitive: bool = False) -> Constraint:
    if not term:
        raise ValueError("term must not be empty")
    if case_sensitive:
        return Constraint(f"contains:{term}", lambda text: term in text)
    return Constraint(f"contains:{term}", lambda text: term.casefold() in text.casefold())

def max_length(n: int) -> Constraint:
    if n < 0:
        raise ValueError("maximum length must be nonnegative")
    return Constraint(f"max_length:{n}", lambda text: len(text) <= n)
