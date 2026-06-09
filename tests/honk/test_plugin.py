import pytest

import pathlib
import subprocess


def test_list_loaded(tmp_path: pathlib.Path) -> None:
    result = subprocess.run(
        ["honk", "plugin", "list"], capture_output=True, text=True, cwd=tmp_path
    )

    result.check_returncode()
    assert result.stdout == "Loaded plugins:\n- stdplugin\n"
    assert (tmp_path / "plugins.json").exists()


def test_load(tmp_path: pathlib.Path, subtests: pytest.Subtests) -> None:
    mock_plugin = tmp_path / "test_plugin.py"
    mock_plugin.touch()

    with subtests.test("Error on plugin loading"):
        load_result = subprocess.run(
            ["honk", "plugin", "load", "test_plugin"], cwd=tmp_path
        )

        load_result.check_returncode()

        listed = subprocess.check_output(
            ["honk", "plugin", "list"], text=True, cwd=tmp_path
        )

        assert listed == "Loaded plugins:\n- stdplugin\n- test_plugin\n"

    with subtests.test("No error on trying to load a plugin twice"):
        load_result = subprocess.run(
            ["honk", "plugin", "load", "test_plugin"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert load_result.returncode == 2
        assert "Plugin test_plugin is already loaded" in load_result.stderr


def test_unload(tmp_path: pathlib.Path, subtests: pytest.Subtests) -> None:
    with subtests.test("Error on unloading plugin"):
        unload_result = subprocess.run(
            ["honk", "plugin", "unload", "stdplugin"], cwd=tmp_path
        )

        unload_result.check_returncode()

        listed = subprocess.check_output(
            ["honk", "plugin", "list"], text=True, cwd=tmp_path
        )

        assert listed == "Loaded plugins:\n"

    with subtests.test("No error on unloading non-existent plugin"):
        unload_result = subprocess.run(
            ["honk", "plugin", "unload", "test_plugin"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert unload_result.returncode == 2
        assert "Plugin test_plugin is not loaded" in unload_result.stderr
