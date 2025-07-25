"""Utils for creating MP3 and MP4 files."""
import logging
import pathlib
import subprocess as sp


def extract_mp3_segment(
    input_file: pathlib.PosixPath,
    output_file: pathlib.PosixPath,
    time_from: str,
    time_to: str,
) -> None:
    """
    Extract a segment from an MP3 file.
    """
    logger = logging.getLogger(__name__)
    assert input_file.exists() and input_file.is_file() and input_file.suffix == ".mp3"

    if output_file.suffix != ".mp3":
        logger.warning(
            "Adding '.mp3' suffix to '%s': '%s'",
            output_file.name,
            (output_file := output_file.with_suffix(".mp3")).name,
        )

    if not output_file.parent.exists():
        logger.warning("'%s' doesn't exist, creating.", output_file.parent)
        output_file.parent.mkdir(parents=True, exist_ok=True)

    assert isinstance(time_from, str)
    assert isinstance(time_to, str)

    time_from_parts = [int(x) for x in time_from.split(":")]
    match len(time_from_parts):
        case 3:
            time_from_hh, time_from_mm, time_from_ss = time_from_parts
        case 2:
            time_from_hh, time_from_mm, time_from_ss = (0, *time_from_parts)
        case 1:
            time_from_hh, time_from_mm, time_from_ss = (0, 0, *time_from_parts)
        case _:
            raise ValueError

    time_to_parts = [int(x) for x in time_to.split(":")]
    match len(time_to_parts):
        case 3:
            time_to_hh, time_to_mm, time_to_ss = time_to_parts
        case 2:
            time_to_hh, time_to_mm, time_to_ss = (0, *time_to_parts)
        case 1:
            time_to_hh, time_to_mm, time_to_ss = (0, 0, *time_to_parts)
        case _:
            raise ValueError

    logger.info("Segment start: %s", time_from)
    logger.info("Segment end: %s", time_to)

    time_from_seconds = time_from_ss + 60 * time_from_mm + 3600 * time_from_hh
    time_to_seconds = time_to_ss + 60 * time_to_mm + 3600 * time_to_hh

    assert time_from_seconds < time_to_seconds
    time_diff_seconds = time_to_seconds - time_from_seconds

    time_diff_ss = time_diff_seconds % 60
    time_diff_seconds -= time_diff_ss
    time_diff_mm = (time_diff_seconds // 60) % 60
    time_diff_seconds -= time_diff_mm * 60
    time_diff_hh = time_diff_seconds // 3600
    assert time_diff_seconds == time_diff_hh * 3600
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
            str(output_file)
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
