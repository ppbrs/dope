"""
Run linters as regular tests.
"""
import logging
import pathlib
import subprocess

_logger = logging.getLogger(__name__)


def test_lint_isort() -> None:
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


def test_lint_pylint() -> None:
    """Run pylint on all files in the package."""

    completed_process = subprocess.run(
        "pylint --recursive=true --verbose --rc-file=pyproject.toml *.py", shell=True,
        check=False,
        capture_output=True, text=True,
    )
    for line in completed_process.stdout.splitlines():
        if line:
            _logger.info("%s", line)
    if completed_process.returncode != 0:
        for line in completed_process.stderr.splitlines():
            _logger.error("%s", line)
        assert False, "pylint failed"


def test_lint_mypy() -> None:
    """Run mypy on all files in the package."""

    cwd = pathlib.Path.cwd()
    files = " ".join(str(path.relative_to(cwd)) for path in cwd.rglob("*.py"))
    cmd = f"mypy  --config-file=pyproject.toml {files}"
    completed_process = subprocess.run(
        cmd, shell=True,
        check=False,
        capture_output=True, text=True,
    )
    for line in completed_process.stdout.splitlines():
        if line:
            _logger.info("%s", line)
    if completed_process.returncode != 0:
        for line in completed_process.stderr.splitlines():
            _logger.error("%s", line)
        assert False, "mypy failed"
