"""Text helpers shared across the site."""

import re
import unicodedata


def slugify(text):
    """Return a lowercase ASCII slug: accents folded, other runs of characters become one hyphen."""
    folded = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", folded.lower()).strip("-")
