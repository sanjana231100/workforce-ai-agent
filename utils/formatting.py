def format_currency(value: float) -> str:
    """Format a number as USD currency string."""
    return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    """Format a number as a percentage string."""
    return f"{round(value, 2)}%"


def truncate(text: str, max_length: int = 300) -> str:
    """Truncate long strings for display in the UI."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."