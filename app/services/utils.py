def to_absolute_media_url(image_url: str, base_url: str) -> str:
    """
    Prepend the configured base URL to a root-relative media path.

    Args:
        image_url (str): The stored root-relative path, e.g.
            ``/media/products/<uuid>``.
        base_url (str): The public origin, e.g. ``https://api.example.com``.
            When empty, the path is returned unchanged.

    Returns:
        str: The absolute URL.
    """
    return f"{base_url.rstrip('/')}{image_url}"


def to_relative_media_url(image_url: str, base_url: str) -> str:
    """
    Strip the configured base URL so the value stays root-relative.

    Args:
        image_url (str): The incoming URL, absolute or already relative.
        base_url (str): The public origin to strip. When empty, the value is
            returned unchanged.

    Returns:
        str: The root-relative path.
    """
    prefix = base_url.rstrip("/")
    if image_url.startswith(prefix):
        return image_url[len(prefix) :]

    raise ValueError(
        f"image_url '{image_url}' has unexpected base URL prefix '{prefix}'"
    )


def escape_like_operator_value(value: str) -> str:
    """
    Escape special characters for use in a LIKE/ILIKE query.

    Args:
        value (str): The string to escape.

    Returns:
        str: The escaped string.
    """
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
