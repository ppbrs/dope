"""
Run linters as regular tests.
"""
import logging
import subprocess

_logger = logging.getLogger(__name__)


def test_isort() -> None:
    """Run isort on all files in the package."""

    completed_process = subprocess.run(
        "isort . --check", shell=True,
        check=False,
        capture_output=True, text=True,
    )
    if completed_process.returncode != 0:
        for line in completed_process.stderr.splitlines():
            _logger.error("%s", line)
        assert False, "isort failed"
