try:
    import numexpr
except Exception:  # pragma: no cover - handled at runtime
    numexpr = None


def run(args: str) -> str:
    """Safely evaluate a mathematical expression.

    Uses ``numexpr`` to compute the result. If the expression is invalid or
    contains unsupported operations, an informative message is returned
    instead of raising an exception.
    """

    if numexpr is None:
        return "\u26A0\uFE0F Math error: numexpr library is not installed"

    try:
        result = numexpr.evaluate(args)
        return f"\U0001F9EE Result: {result.item()}"
    except Exception as e:
        return f"\u26A0\uFE0F Math error: {str(e)}"
