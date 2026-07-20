"""Shared Decimal money rounding with explicit approved-policy inputs."""

from decimal import (
    Decimal,
    ROUND_DOWN,
    ROUND_HALF_DOWN,
    ROUND_HALF_EVEN,
    ROUND_HALF_UP,
    ROUND_UP,
)


ROUNDING_MODES = {
    "half_up": ROUND_HALF_UP,
    "half_even": ROUND_HALF_EVEN,
    "half_down": ROUND_HALF_DOWN,
    "down": ROUND_DOWN,
    "up": ROUND_UP,
}


def round_monetary(value, *, mode, precision, boundary):
    """Round money once under a complete, supported approved policy."""
    try:
        approved_precision = Decimal(precision)
    except (TypeError, ValueError):
        approved_precision = None
    if mode not in ROUNDING_MODES or approved_precision != Decimal("0.01"):
        raise ValueError("The approved monetary rounding policy is unsupported.")
    if boundary != "whole_decision":
        raise ValueError("The approved monetary rounding boundary is unsupported.")
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUNDING_MODES[mode])
