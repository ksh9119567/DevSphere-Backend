"""
Helper functions for working with slugs
"""

import re


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)   # remove special chars
    text = re.sub(r"[\s_-]+", "-", text)   # replace spaces/underscores with -
    text = re.sub(r"^-+|-+$", "", text)    # trim -
    return text