"""File utility helpers."""
from __future__ import annotations

import hashlib
import mimetypes
import os
from pathlib import Path

ALLOWED_EXTENSIONS = {
    ".pdf", ".txt", ".doc", ".docx", ".rtf",
    ".mp3", ".wav", ".ogg", ".flac", ".m4a",
    ".mp4", ".avi", ".mkv", ".mov", ".webm",
    ".png", ".jpg", ".jpeg", ".gif", ".webp",
}

MAX_FILENAME_LENGTH = 255


def get_file_extension(filename: str) -> str:
    """Return the lowercase file extension including the dot."""
    return Path(filename).suffix.lower()


def is_allowed_extension(filename: str) -> bool:
    """Check if the file extension is in the allowed set."""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def get_mime_type(filename: str) -> str:
    """Guess MIME type from filename."""
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"


def sanitize_filename(filename: str) -> str:
    """Remove path separators and limit length."""
    name = os.path.basename(filename)
    # Remove any non-printable characters
    name = "".join(c for c in name if c.isprintable())
    if len(name) > MAX_FILENAME_LENGTH:
        ext = get_file_extension(name)
        name = name[: MAX_FILENAME_LENGTH - len(ext)] + ext
    return name


def compute_file_hash(content: bytes) -> str:
    """Compute SHA-256 hash of file content."""
    return hashlib.sha256(content).hexdigest()


def human_readable_size(size_bytes: int) -> str:
    """Convert bytes to human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
