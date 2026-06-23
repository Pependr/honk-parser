import pytest

import pathlib
import subprocess

from dataclasses import dataclass

from typing import Protocol, Sequence


class RunnerFn(Protocol):
    def __call__(
        self, cmd: Sequence[str], *, input: str | None = None
    ) -> subprocess.CompletedProcess[str]: ...


SAMPLES = pathlib.Path.cwd() / "tests" / "stdplugin" / "samples"


@pytest.fixture
def runner(tmp_path: pathlib.Path) -> RunnerFn:
    def run(
        cmd: Sequence[str], *, input: str | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=tmp_path,
            input=input,
        )

    return run


def test_echo(runner: RunnerFn) -> None:
    process = runner(["honk", "parse", "-m", "toml", "echo"], input="bruh = 15")

    process.check_returncode()
    assert process.stdout == f"{ {"bruh": 15} }\n"


def test_json(runner: RunnerFn) -> None:
    process = runner(["honk", "parse", "-m", "toml", "json"], input="bruh = 15")

    process.check_returncode()
    assert process.stdout == '{"bruh": 15}\n'


def test_map_map(runner: RunnerFn, subtests: pytest.Subtests) -> None:
    SAMPLE_PATH = SAMPLES / "map_map.json"

    @dataclass(frozen=True, slots=True)
    class Sample:
        flags: tuple[str, ...]
        output: pathlib.Path

        def run(self) -> None:
            cmd: list[str] = [
                "honk",
                "parse",
                "-p",
                f"{SAMPLE_PATH}",
                "map-map",
            ]
            cmd.extend(self.flags)

            process = runner(cmd)

            process.check_returncode()
            assert process.stdout == self.output.read_text()

    FLAGS: tuple[tuple[str, ...], ...] = (
        (),
        ("--header", "files"),
        ("--excluded-col", "*_display"),
        ("--excluded-col", "*_display", "--excluded-col", "num_statements"),
        ("--excluded-row", "test*"),
        ("--excluded-row", "test*", "--excluded-col", "*_display"),
        ("--swap",),
    )

    for i, cmd in enumerate(FLAGS):
        sample = Sample(cmd, SAMPLES / f"map_map{i}.md")
        with subtests.test(
            "Test map-map", flags=sample.flags, output_path=f"{sample.output}"
        ):
            sample.run()


def test_map_arr(runner: RunnerFn, subtests: pytest.Subtests) -> None:
    SAMPLE_PATH = SAMPLES / "map_arr.json"

    @dataclass(frozen=True, slots=True)
    class Sample:
        flags: tuple[str, ...]
        output: pathlib.Path

        def run(self) -> None:
            cmd: list[str] = [
                "honk",
                "parse",
                "-p",
                f"{SAMPLE_PATH}",
                "map-arr",
            ]
            cmd.extend(self.flags)

            process = runner(cmd)

            process.check_returncode()
            assert process.stdout == self.output.read_text()

    FLAGS: tuple[tuple[str, ...], ...] = (
        (),
        ("-e", "*_display"),
        ("-e", "*_display", "-e", "num_statements"),
    )

    for i, cmd in enumerate(FLAGS):
        sample = Sample(cmd, SAMPLES / f"map_arr{i}.md")
        with subtests.test(
            "Test map-arr", flags=sample.flags, output_path=f"{sample.output}"
        ):
            sample.run()


def test_arr_map(runner: RunnerFn, subtests: pytest.Subtests) -> None:
    SAMPLE_PATH = SAMPLES / "arr_map.json"

    @dataclass(frozen=True, slots=True)
    class Sample:
        flags: tuple[str, ...]
        output: pathlib.Path

        def run(self) -> None:
            cmd: list[str] = [
                "honk",
                "parse",
                "-p",
                f"{SAMPLE_PATH}",
                "arr-map",
            ]
            cmd.extend(self.flags)

            process = runner(cmd)

            process.check_returncode()
            assert process.stdout == self.output.read_text()

    FLAGS: tuple[tuple[str, ...], ...] = (
        (),
        ("-e", "*_display"),
        ("-e", "*_display", "-e", "num_statements"),
    )

    for i, cmd in enumerate(FLAGS):
        sample = Sample(cmd, SAMPLES / f"arr_map{i}.md")
        with subtests.test(
            "Test arr-map", flags=sample.flags, output_path=f"{sample.output}"
        ):
            sample.run()
