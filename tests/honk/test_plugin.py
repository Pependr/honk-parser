import pytest

import json
import pathlib
import subprocess

from typing import Any


MOCK_PLUGIN_PATH = pathlib.Path.cwd() / "tests" / "honk" / "mock_plugin.py"
PLUGINS = "plugins.json"


def parse_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: pathlib.Path, data: Any) -> None:
    path.write_text(json.dumps(data))


def test_plugin_list(tmp_path: pathlib.Path, subtests: pytest.Subtests) -> None:
    mock_plugin = tmp_path / "mock_plugin.py"
    mock_plugin.touch()

    plugins_path = tmp_path / PLUGINS

    with subtests.test("Testing list without loaded plugins"):
        result = subprocess.run(
            ["honk", "plugin", "list"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        result.check_returncode()
        assert result.stdout == "Loaded plugins:\n- stdplugin\n"
        assert plugins_path.exists()
        assert parse_json(plugins_path) == ["stdplugin"]

    write_json(plugins_path, ["mock_plugin"])

    with subtests.test("Testing list on a modyfied plugins file"):
        result = subprocess.run(
            ["honk", "plugin", "list"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        result.check_returncode()
        assert result.stdout == "Loaded plugins:\n- mock_plugin\n"

    write_json(plugins_path, [])

    with subtests.test("Testing list on empty plugins file"):
        result = subprocess.run(
            ["honk", "plugin", "list"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        result.check_returncode()
        assert result.stdout == "Loaded plugins:\n"


def test_plugin_load(tmp_path: pathlib.Path, subtests: pytest.Subtests) -> None:
    MOCK_PLUGIN_PATH.copy_into(tmp_path)

    plugins_path = tmp_path / PLUGINS

    with subtests.test("Testing loading the mock plugin"):
        result = subprocess.run(
            ["honk", "plugin", "load", "mock_plugin"], cwd=tmp_path
        )

        result.check_returncode()
        assert parse_json(plugins_path) == ["stdplugin", "mock_plugin"]

    with subtests.test("Testing help output"):
        result = subprocess.check_output(
            ["honk", "parse", "--help"], text=True, cwd=tmp_path
        )

        assert "mock" in result

    with subtests.test("Testing error on loading a plugin twice"):
        result = subprocess.run(
            ["honk", "plugin", "load", "mock_plugin"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 2
        assert "Plugin mock_plugin is already loaded" in result.stderr

    with subtests.test("Test error on loading non-existent plugin"):
        result = subprocess.run(
            ["honk", "plugin", "load", "my_plugin"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 2
        assert "No module named my_plugin" in result.stderr


def test_plugin_unload(
    tmp_path: pathlib.Path, subtests: pytest.Subtests
) -> None:
    MOCK_PLUGIN_PATH.copy_into(tmp_path)

    plugins_path = tmp_path / PLUGINS

    with subtests.test("Testing unloading the stdplugin"):
        result = subprocess.run(
            ["honk", "plugin", "unload", "stdplugin"], cwd=tmp_path
        )

        result.check_returncode()
        assert parse_json(plugins_path) == []

    with subtests.test("Testing help output"):
        result = subprocess.check_output(
            ["honk", "parse", "--help"], text=True, cwd=tmp_path
        )

        assert "Commands" not in result

    with subtests.test("Testing error on unloading an unloaded plugin"):
        result = subprocess.run(
            ["honk", "plugin", "unload", "mock_plugin"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 2
        assert "Plugin mock_plugin is not loaded" in result.stderr
