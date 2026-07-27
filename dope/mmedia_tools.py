"""Utils for creating MP3 and MP4 files."""

import logging
import pathlib
import subprocess as sp


def extract_mp3_segment(
    input_file: pathlib.PosixPath,
    output_file: pathlib.PosixPath,
    time_from: str | int,
    time_to: str | int,
) -> None:
    """
    Extract a segment from an MP3 file.

    :param input_file: File to extract segments from.
    :param output_file: .mp3 suffix will be added automatically when missing.
    :param time_from: Start time of the segment. It can be a string or an integer.
        Examples: "03:51:21" = 35121
    :param time_to: End time of the segment. It can be a string or an integer.
    """
    logger = logging.getLogger(__name__)
    assert input_file.exists(), f"'{input_file}' is not found"
    assert input_file.is_file(), f"'{input_file}' is not a file"
    assert input_file.suffix == ".mp3", f"'{input_file}' is not MP3"

    if output_file.suffix != ".mp3":
        logger.warning(
            "Adding '.mp3' suffix to '%s': '%s'",
            output_file.name,
            (output_file := output_file.with_suffix(".mp3")).name,
        )

    if not output_file.parent.exists():
        logger.warning("'%s' doesn't exist, creating.", output_file.parent)
        output_file.parent.mkdir(parents=True, exist_ok=True)

    time_from_hh, time_from_mm, time_from_ss = _get_time_parts(time_from)
    time_to_hh, time_to_mm, time_to_ss = _get_time_parts(time_to)

    time_from = f"{time_from_hh:02d}:{time_from_mm:02d}:{time_from_ss:02d}"
    time_to = f"{time_to_hh:02d}:{time_to_mm:02d}:{time_to_ss:02d}"
    logger.info("Segment start: %s", time_from)
    logger.info("Segment end: %s", time_to)

    time_from_seconds = time_from_ss + 60 * time_from_mm + 3600 * time_from_hh
    time_to_seconds = time_to_ss + 60 * time_to_mm + 3600 * time_to_hh
    assert time_from_seconds < time_to_seconds
    time_diff_seconds = time_to_seconds - time_from_seconds

    time_diff_ss = time_diff_seconds % 60
    time_diff_minutes = time_diff_seconds // 60
    time_diff_mm = time_diff_minutes % 60
    time_diff_hours = time_diff_minutes // 60
    time_diff_hh = time_diff_hours // 3600
    assert time_diff_seconds == time_diff_hh * 3600 + time_diff_mm * 60 + time_diff_ss
    time_diff: str = f"{time_diff_hh:02d}:{time_diff_mm:02d}:{time_diff_ss:02d}"
    logger.info("Segment duration: %s", time_diff)

    proc: sp.CompletedProcess[str] = sp.run(
        [
            "ffmpeg",
            "-y",  # overwrite
            "-i",
            str(input_file),
            "-acodec",
            "copy",  # to instruct FFmpeg to copy the audio stream from the input file directly to the output without re-encoding
            "-ss",
            time_from,
            "-to",
            time_to,
            str(output_file),
        ],
        shell=False,
        check=False,
        text=True,
        stdout=sp.PIPE,
        stderr=sp.PIPE,
    )
    if proc.returncode:
        logger.warning("ffmpeg returned %d", proc.returncode)
        for line in proc.stdout.splitlines():
            logger.info("stdout: %s", line)
        for line in proc.stderr.splitlines():
            logger.info("stderr: %s", line)
        proc.check_returncode()
    else:
        logger.info("ffmpeg returned 0, '%s' is ready.", output_file.name)


def _get_time_parts(time_arg: str | int) -> tuple[int, int, int]:
    """Convert time_from or time_to argument to a tuple (hours, minutes, seconds)."""
    assert isinstance(time_arg, str | int)

    if isinstance(time_arg, str):
        time_arg_parts = tuple(int(x) for x in time_arg.split(":", 3))
        match len(time_arg_parts):
            case 3:
                assert len(time_arg_parts) == 3
                return time_arg_parts
            case 2:
                assert len(time_arg_parts) == 2
                return (0, *time_arg_parts)
            case 1:
                assert len(time_arg_parts) == 1
                return (0, 0, *time_arg_parts)
            case _:
                raise ValueError

    if isinstance(time_arg, int):
        ss = time_arg % 100
        time_arg //= 100
        mm = time_arg % 100
        time_arg //= 100
        hh = time_arg
        return (hh, mm, ss)


def test_get_time_parts() -> None:
    """Test _get_time_parts() function."""
    assert _get_time_parts("00:00:00") == (0, 0, 0)
    assert _get_time_parts("03:45:50") == (3, 45, 50)
    assert _get_time_parts("57:58:59") == (57, 58, 59)

    assert _get_time_parts(0) == (0, 0, 0)
    assert _get_time_parts(34550) == (3, 45, 50)
    assert _get_time_parts(9995959) == (999, 59, 59)
