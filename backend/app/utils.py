"""Shared utility functions."""


def escape_like_pattern(value: str) -> str:
    """Escape special LIKE pattern characters to prevent SQL injection.

    Args:
        value: The string to escape for use in a LIKE pattern.

    Returns:
        The escaped string safe for LIKE queries.
    """
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
