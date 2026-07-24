"""Template-friendly number formatting helpers."""


def compact_number(value, decimals=1):
    """Format large numbers compactly: 2500000 -> 2.5M, 6800000000 -> 6.8B."""
    if value is None:
        return "—"

    try:
        number = float(value)
    except (TypeError, ValueError):
        return "—"

    if number != number:  # NaN
        return "—"

    sign = "-" if number < 0 else ""
    number = abs(number)

    thresholds = (
        (1_000_000_000_000, "T"),
        (1_000_000_000, "B"),
        (1_000_000, "M"),
        (1_000, "K"),
    )

    for threshold, suffix in thresholds:
        if number >= threshold:
            scaled = number / threshold
            formatted = f"{scaled:.{decimals}f}".rstrip("0").rstrip(".")
            return f"{sign}{formatted}{suffix}"

    if number == int(number):
        return f"{sign}{int(number)}"

    formatted = f"{number:.{decimals}f}".rstrip("0").rstrip(".")
    return f"{sign}{formatted}"


def compact_usd(value, decimals=1):
    """Prefix a compact number with $."""
    formatted = compact_number(value, decimals)
    if formatted == "—":
        return formatted
    return f"${formatted}"
