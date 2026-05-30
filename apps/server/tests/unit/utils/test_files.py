"""Unit tests for app.utils.files helpers."""
from __future__ import annotations

import hashlib

import pytest

from app.utils import files as file_utils


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("doc.PDF", ".pdf"),
        ("clip.MP4", ".mp4"),
        ("archive.tar.gz", ".gz"),
        ("noext", ""),
    ],
)
def test_get_file_extension(filename, expected):
    assert file_utils.get_file_extension(filename) == expected


@pytest.mark.parametrize(
    "filename,allowed",
    [
        ("a.pdf", True),
        ("a.mp3", True),
        ("a.mov", True),
        ("a.exe", False),
        ("a.zip", False),
    ],
)
def test_is_allowed_extension(filename, allowed):
    assert file_utils.is_allowed_extension(filename) is allowed


def test_get_mime_type_known_and_fallback():
    assert file_utils.get_mime_type("a.pdf") == "application/pdf"
    assert file_utils.get_mime_type("a.unknownext") == "application/octet-stream"


def test_sanitize_filename_strips_paths():
    assert file_utils.sanitize_filename("/etc/passwd") == "passwd"
    assert file_utils.sanitize_filename("..\\..\\evil.txt") in {"evil.txt", "..\\..\\evil.txt".split("\\")[-1]}


def test_sanitize_filename_truncates_long_names():
    long_name = "a" * 300 + ".pdf"
    out = file_utils.sanitize_filename(long_name)
    assert len(out) <= file_utils.MAX_FILENAME_LENGTH
    assert out.endswith(".pdf")


def test_compute_file_hash_matches_hashlib():
    content = b"hello world"
    assert file_utils.compute_file_hash(content) == hashlib.sha256(content).hexdigest()


@pytest.mark.parametrize(
    "size,expected",
    [
        (512, "512 B"),
        (1536, "1.5 KB"),
        (1024 * 1024, "1.0 MB"),
        (2 * 1024 * 1024 * 1024, "2.00 GB"),
    ],
)
def test_human_readable_size(size, expected):
    assert file_utils.human_readable_size(size) == expected
