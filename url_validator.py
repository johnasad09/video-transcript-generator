"""
url_validator.py - URL validation utilities.
"""

from urllib.parse import urlparse


def is_valid_url(url: str) -> tuple[bool, str]:
    """
    Validates a URL string.
    Returns (is_valid, error_message). error_message is empty string if valid.
    """
    url = url.strip()

    if not url:
        return False, "URL cannot be empty."

    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Could not parse the URL."

    if parsed.scheme not in ("http", "https"):
        return False, "URL must start with http:// or https://"

    if not parsed.netloc:
        return False, "URL is missing a domain."

    return True, ""
