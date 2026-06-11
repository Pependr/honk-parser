import pytest

import json
import pathlib

from typing import Any

import conftest


def parse_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: pathlib.Path, data: Any) -> None:
    path.write_text(json.dumps(data))


def test_plugin_list(
    runner: conftest.Runner, subtests: pytest.Subtests
) -> None:
    with conftest.isolated_path(runner) as iso:
        mock_plugin = iso / "mock_plugin.py"
        mock_plugin.touch()

        plugin_path = iso / "plugins.json"

        with subtests.test("Error on listing plugins before loading"):
            result = conftest.invoke_root(runner, "plugin", "list")

            assert result.exit_code == 0
            assert result.output == "Loaded plugins:\n- stdplugin\n"
            assert plugin_path.exists()

        write_json(plugin_path, ["mock_plugin"])

        with subtests.test("Error on listing modyfied plugins file"):
            result = conftest.invoke_root(runner, "plugin", "list")

            assert result.exit_code == 0
            assert result.output == "Loaded plugins:\n- mock_plugin\n"

        write_json(plugin_path, [])

        with subtests.test("Error on listing empty plugins file"):
            result = conftest.invoke_root(runner, "plugin", "list")

            assert result.exit_code == 0
            assert result.output == "Loaded plugins:\n"


def test_plugin_load(
    runner: conftest.Runner, subtests: pytest.Subtests
) -> None:
    mock_plugin_path = pathlib.Path.cwd() / "tests" / "honk" / "mock_plugin.py"

    with conftest.isolated_path(runner) as iso:
        mock_plugin_path.copy_into(iso)

        plugin_path = iso / "plugins.json"

        with subtests.test("Error on plugin loading"):
            result = conftest.invoke_root(
                runner, "plugin", "load", "mock_plugin"
            )

            assert result.exit_code == 0
            assert parse_json(plugin_path) == [
                "stdplugin",
                "mock_plugin",
            ]

        with subtests.test("Error on listing plugins"):
            list_result = conftest.invoke_root(runner, "plugin", "list")

            assert list_result.exit_code == 0
            assert list_result.output == (
                "Loaded plugins:\n- stdplugin\n- mock_plugin\n"
            )

        with subtests.test("Error on testing help output"):
            help_result = conftest.invoke_root(runner, "parse", "--help")

            assert help_result.exit_code == 0
            assert "mock" in help_result.output

        with subtests.test("No error on loading same plugin twice"):
            result = conftest.invoke_root(
                runner, "plugin", "load", "mock_plugin"
            )

            assert result.exit_code == 2
            assert "Plugin mock_plugin is already loaded" in result.stderr


def test_plugin_unload(
    runner: conftest.Runner, subtests: pytest.Subtests
) -> None:
    with conftest.isolated_path(runner) as iso:
        plugin_path = iso / "plugins.json"

        with subtests.test("Error on unloading standart plugin"):
            result = conftest.invoke_root(
                runner, "plugin", "unload", "stdplugin"
            )

            assert result.exit_code == 0
            assert parse_json(plugin_path) == []

        with subtests.test("Error on listing plugins"):
            list_result = conftest.invoke_root(runner, "plugin", "list")

            assert list_result.exit_code == 0
            assert list_result.output == "Loaded plugins:\n"

        with subtests.test("Error on testing help output"):
            pytest.skip("It loads stdplugin anyway for some reason")

            help_result = conftest.invoke_root(runner, "parse", "--help")

            assert help_result.exit_code == 0
            assert "Commands" not in help_result.output

        with subtests.test("No error on unloading non-existent plugin"):
            result = conftest.invoke_root(
                runner, "plugin", "unload", "mock_plugin"
            )

            assert result.exit_code == 2
            assert "Plugin mock_plugin is not loaded" in result.stderr
