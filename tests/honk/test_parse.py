import pytest

import pathlib
import subprocess


MOCK_PLUGIN_PATH = pathlib.Path.cwd() / "tests" / "honk" / "mock_plugin.py"


@pytest.fixture
def mock_path(tmp_path: pathlib.Path) -> pathlib.Path:
    MOCK_PLUGIN_PATH.copy_into(tmp_path)
    subprocess.run(["honk", "plugin", "load", "mock_plugin"], cwd=tmp_path)
    return tmp_path


def test_parse(mock_path: pathlib.Path, subtests: pytest.Subtests) -> None:
    with subtests.test("Test parsing data from stdin"):
        result = subprocess.run(
            ["honk", "parse", "-m", "mock", "echo"],
            capture_output=True,
            text=True,
            cwd=mock_path,
            input="mock",
        )

        result.check_returncode()
        assert result.stdout == "Parsed data: mock\n"

    with subtests.test("Test error parsing data from stdin without a method"):
        result = subprocess.run(
            ["honk", "parse", "echo"],
            capture_output=True,
            text=True,
            cwd=mock_path,
            input="mock",
        )

        assert result.returncode == 2
        assert (
            "Parsing method is required when reading from stdin"
            in result.stderr
        )

    sample_path = mock_path / "sample.txt"
    sample_path.write_text("sample")

    with subtests.test("Test parsing data from file with specified method"):
        result = subprocess.run(
            ["honk", "parse", "-p", "sample.txt", "-m", "mock", "echo"],
            capture_output=True,
            text=True,
            cwd=mock_path,
        )

        result.check_returncode()
        assert result.stdout == "Parsed data: sample\n"

    with subtests.test("Test parsing data from file with automatic method"):
        result = subprocess.run(
            ["honk", "parse", "-p", "sample.txt", "echo"],
            capture_output=True,
            text=True,
            cwd=mock_path,
        )

        result.check_returncode()
        assert result.stdout == "Read text: sample\n"

    with subtests.test("Test a custom template"):
        result = subprocess.run(
            ["honk", "parse", "-m", "mock", "mock"],
            capture_output=True,
            text=True,
            cwd=mock_path,
            input="mock",
        )

        result.check_returncode()
        assert result.stdout == "Processed data: Parsed data: mock\n"
