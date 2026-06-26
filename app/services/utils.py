def escape_like_operator_value(value: str) -> str:
    """
    Escape special characters for use in a LIKE/ILIKE query.

    Args:
        value (str): The string to escape.

    Returns:
        str: The escaped string.
    """
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
