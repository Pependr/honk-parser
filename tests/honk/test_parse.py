import pytest

import json
import pathlib
import subprocess

from dataclasses import dataclass

from typing import Any


MOCK_PLUGIN_PATH = pathlib.Path.cwd() / "tests" / "honk" / "mock_plugin.py"


@pytest.fixture
def mock_path(tmp_path: pathlib.Path) -> pathlib.Path:
    MOCK_PLUGIN_PATH.copy_into(tmp_path)
    subprocess.run(["honk", "plugin", "load", "mock_plugin"], cwd=tmp_path)
    return tmp_path


def test_parse_strats(
    mock_path: pathlib.Path, subtests: pytest.Subtests
) -> None:
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


def test_parse_dig(tmp_path: pathlib.Path, subtests: pytest.Subtests) -> None:
    @dataclass(frozen=True, slots=True)
    class Sample:
        target: str
        data: Any
        result: Any
        delim: str | None = None

        def run(self) -> None:
            args: list[str] = [
                "honk",
                "parse",
                "-m",
                "json",
                "-t",
                self.target,
                "json",
            ]

            if self.delim is not None:
                args.insert(-1, "-d")
                args.insert(-1, self.delim)

            process = subprocess.run(
                args,
                capture_output=True,
                text=True,
                cwd=tmp_path,
                input=json.dumps(self.data),
            )

            process.check_returncode()
            assert process.stdout == f"{json.dumps(self.result)}\n"

    SAMPLES: tuple[Sample, ...] = (
        Sample("bruh", {"bruh": 10, "dude": 6.7}, 10),
        Sample("bruh/dude/man", {"bruh": {"dude": {"man": 6.7}}}, 6.7),
        Sample(
            "files.src/honk.missing_lines",
            {"files": {"src/honk": {"missing_lines": 10}}},
            10,
            ".",
        ),
        Sample("1", [1, 2, 3], 2),
        Sample("array/1", {"array": [1, 2, 3]}, 2),
        Sample("0,0,0,0", [[[[4]]]], 4, ","),
        Sample(
            "people/*/name",
            {
                "people": {
                    "user1": {"name": "Bob", "age": 33},
                    "user2": {"name": "Alice", "age": 22},
                    "user3": {"name": "Anthony", "age": 16},
                }
            },
            {"user1": "Bob", "user2": "Alice", "user3": "Anthony"},
        ),
        Sample(
            "people/*/*/0",
            {
                "people": {
                    "user1": {"name": "Bob", "surname": "Robinson"},
                    "user2": {"name": "Alice", "surname": "Smith"},
                    "user3": {"name": "Anthony", "surname": "Gooseling"},
                }
            },
            {
                "user1": {"name": "B", "surname": "R"},
                "user2": {"name": "A", "surname": "S"},
                "user3": {"name": "A", "surname": "G"},
            },
        ),
    )

    for sample in SAMPLES:
        with subtests.test("Test data picking", sample=repr(sample)):
            sample.run()
