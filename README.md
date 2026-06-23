# Honk Parser

A tool that parses your data into whatever you desire.

## Installation

Honk Parser is available on PyPI and can be installed using `pip`:

```sh
pip install honk-parser
```

## Overview

Honk Parser is a CLI tool that reads structured data from files or standard input, parses it using a specified method, and applies a template to display or transform the result. The tool is built around a flexible plugin system that allows you to extend both parsing methods and output templates.

```sh
honk --help
```

Displays general help information about the tool.

## Core Concepts

- **Parsing Method**: A function that converts raw text (e.g., JSON, TOML) into a Python object.
- **Template**: A function that takes a parsed data object and outputs it in a desired format (e.g., plain text, JSON, Markdown table).
- **Plugin**: A Python module that registers new parsing methods and templates.

## Subcommands

Honk Parser provides two main subcommands: `parse` and `plugin`.

### Parse Command

The `parse` command reads data and processes it through a parser and a template.

```sh
honk parse [OPTIONS] <TEMPLATE> [OPTIONS]
```

#### Options

| Option | Description |
| ------ | ----------- |
| `-p, --path PATH` | Path to the file to read from. If omitted, reads from stdin. |
| `-m, --method METHOD` | Parsing method to use. Can be omitted when reading from a file — the file extension is used automatically. |
| `-t, --target TARGET` | Target object path within the parsed data. Defaults to `"."` (the root). |
| `-d, --delim DELIM` | Delimiter for the target path. Defaults to `"/"`. |

#### Examples

Parse a JSON file and echo the result:

```sh
honk parse -p data.json echo
```

Parse TOML from stdin and output as JSON:

```sh
echo 'name = "honk"' | honk parse -m toml json
```

Extract a nested value using a target path:

```sh
honk parse -p data.json -t "user/name" echo
```

Use a wildcard (`*`) in the target path:

```sh
honk parse -p data.json -t "user/*/name" echo
```

Use a custom delimiter for the target path:

```sh
honk parse -p data.json -t "user.name" -d "." echo
```

### Plugin Command

The `plugin` command manages which plugins are loaded.

```sh
honk plugin [SUBCOMMAND] [OPTIONS]
```

#### Subcommands

| Subcommand | Description |
| ---------- | ----------- |
| `load MODULE` | Load a plugin module by name. |
| `unload MODULE` | Unload a previously loaded plugin. |
| `list` | List all currently loaded plugins. |

#### Plugin Loading Mechanism

When Honk Parser starts, it looks for a `plugins.json` file in the current working directory. If the file exists, it loads all modules listed in it. If it doesn't exist, the `stdplugin` is loaded by default.

The `plugin` commands modify this `plugins.json` file, making plugin configuration persistent across invocations.

#### Examples

Load a custom plugin:

```sh
honk plugin load my_plugin
```

Unload a plugin:

```sh
honk plugin unload my_plugin
```

List loaded plugins:

```sh
honk plugin list
```

Output:

```text
Loaded plugins:
- stdplugin
- my_plugin
```

## Plugin System

Honk Parser's plugin system allows you to extend the tool with custom parsing methods and templates. Plugins are Python modules that use the `@parser` and `@template` decorators to register new functionality.

### How Plugins Work

1. A plugin is a Python module that imports `honk` and uses its decorators.
2. The plugin file should be placed in a directory that is in Python's module search path, or you can use a local module by running `honk` from the directory containing it.
3. To load a plugin, use `honk plugin load <module_name>`.
4. The plugin's `@parser` and `@template` decorators register functions that become available via the `-m` option and as template names.

### Creating a Plugin

Here's a minimal plugin that adds a custom parser and template:

```python
# my_plugin.py
import honk
import click

from typing import Mapping


@honk.parser("custom")
def parse_custom(text: str) -> dict[str, str]:
    """Parse custom-formatted text into a dictionary."""
    result: dict[str, str] = {}

    for line in text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            result[key] = value.strip()
    return result


@honk.template(help="Display data in custom format")
def custom_format(data: Mapping[str, str]) -> None:
    """Render data as key: value pairs."""
    for key, value in data.items():
        click.echo(f"{key}: {value}")

```

After loading this plugin:

```sh
honk plugin load my_plugin
```

You can use it:

```sh
echo "name: honk" | honk parse -m custom custom-format
```

## Standard Plugin (`stdplugin`)

The standard plugin is loaded by default and provides built-in parsers and templates for common use cases.

### Built-in Parsers

| Method | Description |
| ------ | ----------- |
| `json` | Parses JSON data using `json.loads` |
| `toml` | Parses TOML data using `tomllib.loads` |

### Built-in Templates

| Template | Description |
| -------- | ----------- |
| `echo` | Prints the parsed data as-is using `click.echo` |
| `json` | Prints the parsed data in JSON format |
| `map-map` | Renders a mapping of mappings as a Markdown table |
| `map-arr` | Renders a mapping of arrays as a Markdown table |
| `arr-map` | Renders an array of mappings as a Markdown table |

#### `map-map` Template

Parses nested mappings (e.g., `Mapping[str, Mapping[str, Any]]`) and outputs a Markdown table.

**Options:**

| Option | Description |
| ------ | ----------- |
| `--header TEXT` | Header text for the first column |
| `--excluded-col TEXT` | Columns to exclude (supports `*` wildcards), can be used multiple times |
| `--excluded-row TEXT` | Rows to exclude (supports `*` wildcards), can be used multiple times |
| `-s, --swap` | Swap columns and rows |

**Example:**

```sh
honk parse -p data.json map-map --header "Files" --excluded-col "*_display"
```

#### `map-arr` Template

Parses a mapping of arrays (e.g., `Mapping[str, Sequence[Any]]`) and outputs a Markdown table.

**Options:**

| Option | Description |
| ------ | ----------- |
| `-e, --excluded TEXT` | Keys to exclude (supports `*` wildcards) |

**Example:**

```sh
honk parse -p data.json map-arr -e "*_display"
```

#### `arr-map` Template

Parses an array of mappings (e.g., `Sequence[Mapping[str, Any]]`) and outputs a Markdown table.

**Options:**

| Option | Description |
| ------ | ----------- |
| `-e, --excluded TEXT` | Columns to exclude (supports `*` wildcards) |

**Example:**

```sh
honk parse -p data.json arr-map -e "internal_id"
```

## Plugin API

### `@parser` Decorator

The `@parser` decorator registers a function as a parsing method for a given file extension.

```python
@honk.parser(ext: str)
def parse_function(text: str) -> Any:
    ...
```

**Parameters:**

- `ext` (str): The file extension (e.g., `"json"`, `"toml"`) that this parser handles.

**Requirements:**

- The decorated function must accept a single `str` argument (the raw text content).
- The function should return a parsed Python object (e.g., `dict`, `list`).

**Example:**

```python
import honk


@honk.parser("csv")
def parse_csv(text: str) -> list[dict[str, str]]:
    """Parse CSV data into a list of dictionaries."""
    header, *rows = text.replace(" ", "").strip("\n").split("\n")

    cols = header.split(",")

    return [{k: v for k, v in zip(cols, row.split(","))} for row in rows]

```

### `@template` Decorator

The `@template` decorator registers a function as an output template.

```python
@honk.template(*args, **kwargs)
def template_function(data, ...) -> None:
    ...
```

You can apply `click`'s decorators to add options and arguments.

**Parameters:**

- `*args, **kwargs`: These are passed through to `click`'s `@command` decorator.

**Requirements:**

- The decorated function must accept the parsed data as its first argument (named `data` by convention).
- Additional parameters can be added and will be exposed as Click options.
- The function should output the result (e.g., using `click.echo`).

**Example:**

```python
import honk
import click

from typing import Sequence


@honk.template(help="Display data as a simple list")
@click.option("--prefix", default="- ", help="Prefix for each item")
def list_format(data: Sequence[str], prefix: str) -> None:
    """Render a list with a custom prefix."""
    for item in data:
        click.echo(f"{prefix}{item}")
```

### Wildcard Matching

The standard plugin uses wildcard matching for exclusion patterns. The `match_wildcard` function supports `*` as a wildcard character:

- `*_display` matches any string ending with `_display`
- `test*` matches any string starting with `test`
- `*log*` matches any string containing `log`

## Complete Example

Here's a complete example showing a custom plugin that parses a simple key-value format and displays it as a table:

```python
# kv_plugin.py
import click

from typing import Mapping

import honk


@honk.parser("kv")
def parse_kv(text: str) -> dict[str, str]:
    """Parse key=value pairs."""
    result: dict[str, str] = {}
    for line in text.split("\n"):
        if "=" in line:
            key, value = line.split("=", 1)
            result[key] = value
    return result


@honk.template(help="Display key-value pairs as a table")
@click.option("--sort", is_flag=True, help="Sort keys alphabetically")
def kv_table(data: Mapping[str, str], sort: bool) -> None:
    """Render key-value pairs in a Markdown table."""
    keys = sorted(data.keys()) if sort else list(data.keys())
    click.echo("| Key | Value |")
    click.echo("| --- | ----- |")
    for key in keys:
        click.echo(f"| {key} | {data[key]} |")

```

Load and use:

```sh
honk plugin load kv_plugin
echo "name=honk\nversion=0.2" | honk parse -m kv kv-table --sort
```

Output:

```markdown
| Key | Value |
| --- | ----- |
| name | honk |
| version | 0.2 |
```

## Target Path Syntax

The `-t, --target` option allows you to extract nested data from the parsed object.

- Use `/` as the default delimiter (or specify a custom delimiter with `-d`).
- Use numeric indices for array access.
- Use `*` as a wildcard to iterate over all keys in a mapping.

**Examples:**

| Target | Description |
| ------ | ----------- |
| `.` | The entire parsed object |
| `user/name` | The `name` field under `user` |
| `users/0/name` | The `name` of the first user |
| `users/*/name` | All `name` fields from all users (returns a dict) |
| `data.results` | With `-d "."`, accesses nested using dot notation |

**Example with wildcard:**

```sh
honk parse -p users.json -t "users/*/name" echo
```

This extracts all user names from a `users` array or mapping.

## Development

### Running Tests

The project uses `pytest` for testing. Tests are organized in the `tests/` directory.

```sh
pytest tests/
```

### Building from Source

```sh
uv build
```

## License

No licence =)
