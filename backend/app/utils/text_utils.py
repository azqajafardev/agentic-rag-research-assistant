"""Text normalization helpers used before chunking."""

import re

_MULTIPLE_SPACES = re.compile(r"[ \t]+")
_MULTIPLE_BLANK_LINES = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    """Normalize whitespace while preserving meaningful paragraph structure."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _MULTIPLE_SPACES.sub(" ", text)
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = _MULTIPLE_BLANK_LINES.sub("\n\n", text)
    return text.strip()
