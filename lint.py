"""
Run linters as regular tests.
"""

import logging
import pathlib
import subprocess

import pytest

_logger = logging.getLogger(__name__)


def _get_all_python_modules() -> list[str]:
    """
    Return a list of paths all python modules.

    The output function must be determenistic because it will be used by both 'argvalues' and 'ids'
    of the same pytest.parametrize decorator.

    This function outputs strings instead of pathlib.Path because there is no value in those as
    they would have been converted to strings anyways.
    """
    attr_name = "cache"
    if not hasattr(_get_all_python_modules, attr_name):
        cwd = pathlib.PosixPath.cwd()
        cache = sorted(str(path.relative_to(cwd)) for path in cwd.rglob("*.py"))
        setattr(_get_all_python_modules, attr_name, cache)
    return getattr(_get_all_python_modules, attr_name)  # type: ignore[no-any-return]


def test_lint_isort() -> None:
    """Run isort on all files in the package."""

    completed_process = subprocess.run(
        "isort . --check",
        shell=True,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed_process.returncode != 0:
        for line in completed_process.stderr.splitlines():
            _logger.error("%s", line)
        assert False, "isort failed"


def test_lint_pylint() -> None:
    """Run pylint on all files in the package."""

    completed_process = subprocess.run(
        "pylint --recursive=true --verbose --rc-file=pyproject.toml *.py",
        shell=True,
        check=False,
        capture_output=True,
        text=True,
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
        cmd,
        shell=True,
        check=False,
        capture_output=True,
        text=True,
    )
    for line in completed_process.stdout.splitlines():
        if line:
            _logger.info("%s", line)
    if completed_process.returncode != 0:
        for line in completed_process.stderr.splitlines():
            _logger.error("%s", line)
        assert False, "mypy failed"


def test_lint_pyright() -> None:
    """Run pyright on all files in the package."""

    cmd = "pyright"
    completed_process = subprocess.run(
        cmd,
        shell=True,
        check=False,
        capture_output=True,
        text=True,
    )
    for line in completed_process.stdout.splitlines():
        if line:
            _logger.info("%s", line)
    if completed_process.returncode != 0:
        for line in completed_process.stderr.splitlines():
            _logger.error("%s", line)
        assert False, "pyright failed"


@pytest.mark.parametrize(
    argnames="path",
    argvalues=_get_all_python_modules(),
    ids=_get_all_python_modules(),
)
def test_lint_ruff_format(
    path: str,
) -> None:
    """Check that a python module is properly formatted."""
    completed_process = subprocess.run(
        ["ruff", "format", "--diff", path],
        check=False,
        capture_output=True,
        text=True,
    )
    for line in completed_process.stdout.splitlines():
        if line:
            _logger.info(line)
    if completed_process.returncode != 0:
        for line in completed_process.stderr.splitlines():
            _logger.error(line)
        err_msg = f"Ruff thinks '{path}' needs reformatting."
        raise AssertionError(err_msg)
