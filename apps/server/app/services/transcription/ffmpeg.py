"""Pure ffmpeg/ffprobe helpers used by the transcription pipeline.

Side-effect free except for the subprocess shells. No state, no instance —
import-and-use.
"""
from __future__ import annotations

import math
import subprocess
from pathlib import Path
from typing import Any

DEFAULT_SEGMENT_SECONDS = 10 * 60


def _run_ffmpeg(args: list[str]) -> None:
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *args]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {proc.stderr.decode(errors='ignore')}")


def probe_duration(path: str | Path) -> float:
    """Return media duration in seconds via ffprobe (0.0 on failure)."""
    proc = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=nokey=1:noprint_wrappers=1",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    try:
        return float(proc.stdout.strip())
    except (TypeError, ValueError):
        return 0.0


def extract_audio_track(video_path: str | Path, out_path: str | Path) -> str:
    """Extract a mono 16kHz mp3 audio track from a video file."""
    _run_ffmpeg(
        ["-i", str(video_path), "-vn", "-ac", "1", "-ar", "16000", "-b:a", "64k", str(out_path)]
    )
    return str(out_path)


def split_audio(
    audio_path: str | Path,
    work_dir: str | Path,
    segment_seconds: int = DEFAULT_SEGMENT_SECONDS,
) -> list[dict[str, Any]]:
    """Split audio into time-bounded segments.

    Returns a list of `{path, start, end}` dicts. If the source is shorter
    than `segment_seconds`, returns a single-element list pointing at the
    original file.
    """
    audio_path = Path(audio_path)
    work = Path(work_dir)
    work.mkdir(parents=True, exist_ok=True)

    duration = probe_duration(audio_path)
    if duration <= segment_seconds:
        return [{"path": str(audio_path), "start": 0.0, "end": duration}]

    out: list[dict[str, Any]] = []
    n = int(math.ceil(duration / segment_seconds))
    for i in range(n):
        start = i * segment_seconds
        end = min(duration, start + segment_seconds)
        seg_path = work / f"chunk_{i:03d}.mp3"
        _run_ffmpeg(
            ["-i", str(audio_path), "-ss", f"{start}", "-to", f"{end}", "-c", "copy", str(seg_path)]
        )
        out.append({"path": str(seg_path), "start": float(start), "end": float(end)})
    return out
