"""
Filesystem MCP Server

Claude Desktop / stdio-safe version.

Use with Claude Desktop by pointing the client at this script with an absolute
path to python.exe and an absolute path to this file.

For local manual testing only:
    python main.py test

For MCP / Claude Desktop:
    python main.py
"""

from __future__ import annotations

import base64
import fnmatch
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# IMPORTANT:
# Change this to the real folder you want Claude to be allowed to access.
ROOT_DIR = Path(r"C:\Users\YourName\Documents\my_workspace").resolve()

# Create the workspace folder if it does not exist.
ROOT_DIR.mkdir(parents=True, exist_ok=True)

# Create a starter file so the workspace is not empty.
README_PATH = ROOT_DIR / "README.txt"
if not README_PATH.exists():
    README_PATH.write_text(
        "This is the root workspace for the Filesystem MCP server.\n"
        "All file operations are restricted to this directory.\n",
        encoding="utf-8",
    )

# FastMCP server.
mcp = FastMCP("filesystem")


# --- Path / Safety Helpers ---

def _resolve_path(user_path: str) -> Path:
    """Resolve a user-supplied path safely inside ROOT_DIR."""
    if user_path is None:
        raise ValueError("Path cannot be None.")

    raw = user_path.strip()
    if not raw:
        raise ValueError("Path cannot be empty.")

    candidate = Path(raw)

    # Force all work to stay under ROOT_DIR.
    if candidate.is_absolute():
        candidate = Path(*candidate.parts[1:])

    resolved = (ROOT_DIR / candidate).resolve()

    try:
        resolved.relative_to(ROOT_DIR)
    except ValueError as exc:
        raise ValueError(f"Path '{user_path}' escapes the allowed root directory.") from exc

    return resolved


def _to_relative(path: Path) -> str:
    return str(path.relative_to(ROOT_DIR)) if path != ROOT_DIR else "."


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _file_info(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": _to_relative(path),
        "name": path.name,
        "type": "directory" if path.is_dir() else "file",
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "created": stat.st_ctime,
    }


# --- Core Filesystem Tools ---

@mcp.tool()
def get_root_directory() -> str:
    """Return the root directory this MCP server is allowed to access."""
    return str(ROOT_DIR)


@mcp.tool()
def path_exists(path: str) -> dict[str, Any]:
    """Check whether a file or directory exists."""
    target = _resolve_path(path)
    exists = target.exists()
    result = {
        "path": _to_relative(target),
        "exists": exists,
        "is_file": target.is_file() if exists else False,
        "is_directory": target.is_dir() if exists else False,
    }
    if exists:
        result.update(_file_info(target))
    return result


@mcp.tool()
def list_directory(
    path: str = ".",
    recursive: bool = False,
    include_hidden: bool = False,
) -> list[dict[str, Any]]:
    """List files and directories inside a directory."""
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"Directory '{path}' does not exist.")
    if not target.is_dir():
        raise NotADirectoryError(f"'{path}' is not a directory.")

    entries: list[dict[str, Any]] = []
    iterator = target.rglob("*") if recursive else target.iterdir()

    for item in sorted(iterator, key=lambda p: str(p).lower()):
        rel = _to_relative(item)
        if not include_hidden and any(part.startswith(".") for part in Path(rel).parts if part != "."):
            continue
        entries.append(_file_info(item))

    return entries


@mcp.tool()
def make_directory(path: str, parents: bool = True, exist_ok: bool = True) -> str:
    """Create a directory."""
    target = _resolve_path(path)
    target.mkdir(parents=parents, exist_ok=exist_ok)
    return f"Directory created: {_to_relative(target)}"


@mcp.tool()
def remove_directory(path: str, recursive: bool = False, missing_ok: bool = False) -> str:
    """Remove a directory. Set recursive=True to remove non-empty directories."""
    target = _resolve_path(path)

    if not target.exists():
        if missing_ok:
            return f"Directory not found, nothing removed: {path}"
        raise FileNotFoundError(f"Directory '{path}' does not exist.")

    if not target.is_dir():
        raise NotADirectoryError(f"'{path}' is not a directory.")

    if recursive:
        shutil.rmtree(target)
    else:
        target.rmdir()

    return f"Directory removed: {_to_relative(target)}"


@mcp.tool()
def read_file(path: str, encoding: str = "utf-8") -> str:
    """Read a text file and return its contents."""
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File '{path}' does not exist.")
    if not target.is_file():
        raise IsADirectoryError(f"'{path}' is a directory, not a file.")
    return target.read_text(encoding=encoding)


@mcp.tool()
def write_file(
    path: str,
    content: str,
    overwrite: bool = True,
    encoding: str = "utf-8",
    create_parents: bool = True,
) -> str:
    """Write text to a file, optionally preventing overwrite."""
    target = _resolve_path(path)

    if target.exists() and target.is_dir():
        raise IsADirectoryError(f"'{path}' is a directory, not a file.")

    if target.exists() and not overwrite:
        raise FileExistsError(f"File '{path}' already exists and overwrite=False.")

    if create_parents:
        _ensure_parent(target)

    target.write_text(content, encoding=encoding)
    return f"Wrote {len(content)} characters to {_to_relative(target)}"


@mcp.tool()
def append_file(
    path: str,
    content: str,
    encoding: str = "utf-8",
    create_if_missing: bool = True,
    create_parents: bool = True,
) -> str:
    """Append text to a file."""
    target = _resolve_path(path)

    if target.exists() and target.is_dir():
        raise IsADirectoryError(f"'{path}' is a directory, not a file.")

    if not target.exists() and not create_if_missing:
        raise FileNotFoundError(f"File '{path}' does not exist and create_if_missing=False.")

    if create_parents:
        _ensure_parent(target)

    with open(target, "a", encoding=encoding) as f:
        f.write(content)

    return f"Appended {len(content)} characters to {_to_relative(target)}"


@mcp.tool()
def replace_in_file(
    path: str,
    old_text: str,
    new_text: str,
    count: int = -1,
    encoding: str = "utf-8",
) -> dict[str, Any]:
    """Replace text in a file. Set count=-1 to replace all occurrences."""
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File '{path}' does not exist.")
    if not target.is_file():
        raise IsADirectoryError(f"'{path}' is a directory, not a file.")

    content = target.read_text(encoding=encoding)
    occurrences = content.count(old_text)

    if occurrences == 0:
        return {
            "path": _to_relative(target),
            "replacements_made": 0,
            "message": "Target text was not found.",
        }

    if count is None or count < 0:
        new_content = content.replace(old_text, new_text)
        replacements_made = occurrences
    else:
        new_content = content.replace(old_text, new_text, count)
        replacements_made = min(occurrences, count)

    target.write_text(new_content, encoding=encoding)

    return {
        "path": _to_relative(target),
        "replacements_made": replacements_made,
        "message": "File updated successfully.",
    }


@mcp.tool()
def insert_in_file(
    path: str,
    content_to_insert: str,
    line_number: int,
    encoding: str = "utf-8",
) -> str:
    """
    Insert text before a 1-based line number.
    Use line_number = number_of_lines + 1 to append as a new final line block.
    """
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File '{path}' does not exist.")
    if not target.is_file():
        raise IsADirectoryError(f"'{path}' is a directory, not a file.")
    if line_number < 1:
        raise ValueError("line_number must be 1 or greater.")

    original = target.read_text(encoding=encoding)
    lines = original.splitlines(keepends=True)

    if line_number > len(lines) + 1:
        raise ValueError(
            f"line_number {line_number} is out of range for a file with {len(lines)} lines."
        )

    insertion = content_to_insert
    if insertion and not insertion.endswith(("\n", "\r")):
        insertion += "\n"

    index = line_number - 1
    lines.insert(index, insertion)
    target.write_text("".join(lines), encoding=encoding)

    return f"Inserted content into {_to_relative(target)} before line {line_number}"


@mcp.tool()
def remove_file(path: str, missing_ok: bool = False) -> str:
    """Delete a file."""
    target = _resolve_path(path)

    if not target.exists():
        if missing_ok:
            return f"File not found, nothing removed: {path}"
        raise FileNotFoundError(f"File '{path}' does not exist.")

    if not target.is_file():
        raise IsADirectoryError(f"'{path}' is a directory, not a file.")

    target.unlink()
    return f"File removed: {_to_relative(target)}"


@mcp.tool()
def move_path(source_path: str, destination_path: str, overwrite: bool = False) -> str:
    """Move or rename a file or directory."""
    source = _resolve_path(source_path)
    destination = _resolve_path(destination_path)

    if not source.exists():
        raise FileNotFoundError(f"Source path '{source_path}' does not exist.")

    if destination.exists():
        if not overwrite:
            raise FileExistsError(
                f"Destination '{destination_path}' already exists and overwrite=False."
            )
        if destination.is_dir() and not source.is_dir():
            raise IsADirectoryError("Cannot overwrite a directory with a file.")
        if destination.is_file() and source.is_dir():
            raise NotADirectoryError("Cannot overwrite a file with a directory.")
        if destination.is_dir():
            shutil.rmtree(destination)
        else:
            destination.unlink()

    _ensure_parent(destination)
    shutil.move(str(source), str(destination))
    return f"Moved '{_to_relative(source)}' to '{_to_relative(destination)}'"


@mcp.tool()
def copy_path(source_path: str, destination_path: str, overwrite: bool = False) -> str:
    """Copy a file or directory."""
    source = _resolve_path(source_path)
    destination = _resolve_path(destination_path)

    if not source.exists():
        raise FileNotFoundError(f"Source path '{source_path}' does not exist.")

    if destination.exists():
        if not overwrite:
            raise FileExistsError(
                f"Destination '{destination_path}' already exists and overwrite=False."
            )
        if destination.is_dir():
            shutil.rmtree(destination)
        else:
            destination.unlink()

    _ensure_parent(destination)

    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        shutil.copy2(source, destination)

    return f"Copied '{_to_relative(source)}' to '{_to_relative(destination)}'"


@mcp.tool()
def get_file_info(path: str) -> dict[str, Any]:
    """Return metadata about a file or directory."""
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"Path '{path}' does not exist.")
    return _file_info(target)


@mcp.tool()
def touch_file(path: str, create_parents: bool = True) -> str:
    """Create an empty file if it does not exist, or update its modified time if it does."""
    target = _resolve_path(path)
    if create_parents:
        _ensure_parent(target)
    target.touch(exist_ok=True)
    return f"Touched file: {_to_relative(target)}"


@mcp.tool()
def search_paths(
    path: str = ".",
    name_pattern: str = "*",
    recursive: bool = True,
    include_hidden: bool = False,
    files_only: bool = False,
    directories_only: bool = False,
) -> list[dict[str, Any]]:
    """Search for files and directories by glob-style name pattern."""
    if files_only and directories_only:
        raise ValueError("files_only and directories_only cannot both be True.")

    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"Directory '{path}' does not exist.")
    if not target.is_dir():
        raise NotADirectoryError(f"'{path}' is not a directory.")

    iterator = target.rglob("*") if recursive else target.iterdir()
    results: list[dict[str, Any]] = []

    for item in sorted(iterator, key=lambda p: str(p).lower()):
        rel = _to_relative(item)
        if not include_hidden and any(part.startswith(".") for part in Path(rel).parts if part != "."):
            continue
        if not fnmatch.fnmatch(item.name, name_pattern):
            continue
        if files_only and not item.is_file():
            continue
        if directories_only and not item.is_dir():
            continue
        results.append(_file_info(item))

    return results


@mcp.tool()
def search_file_contents(
    text: str,
    path: str = ".",
    recursive: bool = True,
    case_sensitive: bool = False,
    file_extensions: list[str] | None = None,
    encoding: str = "utf-8",
) -> list[dict[str, Any]]:
    """Search text inside files under a directory and return matching lines."""
    if not text:
        raise ValueError("Search text cannot be empty.")

    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"Directory '{path}' does not exist.")
    if not target.is_dir():
        raise NotADirectoryError(f"'{path}' is not a directory.")

    iterator = target.rglob("*") if recursive else target.iterdir()
    needle = text if case_sensitive else text.lower()
    results: list[dict[str, Any]] = []

    normalized_exts = None
    if file_extensions:
        normalized_exts = {ext if ext.startswith(".") else f".{ext}" for ext in file_extensions}

    for item in sorted(iterator, key=lambda p: str(p).lower()):
        if not item.is_file():
            continue
        if normalized_exts and item.suffix not in normalized_exts:
            continue

        try:
            content = item.read_text(encoding=encoding)
        except (UnicodeDecodeError, OSError):
            continue

        for idx, line in enumerate(content.splitlines(), start=1):
            haystack = line if case_sensitive else line.lower()
            if needle in haystack:
                results.append(
                    {
                        "path": _to_relative(item),
                        "line_number": idx,
                        "line": line,
                    }
                )

    return results


@mcp.tool()
def read_file_base64(path: str) -> dict[str, Any]:
    """Read any file as base64, useful for binary files."""
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File '{path}' does not exist.")
    if not target.is_file():
        raise IsADirectoryError(f"'{path}' is a directory, not a file.")

    data = target.read_bytes()
    return {
        "path": _to_relative(target),
        "base64": base64.b64encode(data).decode("ascii"),
        "size": len(data),
    }


@mcp.tool()
def write_file_base64(
    path: str,
    base64_content: str,
    overwrite: bool = True,
    create_parents: bool = True,
) -> str:
    """Write any file from a base64 string, useful for binary files."""
    target = _resolve_path(path)

    if target.exists() and target.is_dir():
        raise IsADirectoryError(f"'{path}' is a directory, not a file.")

    if target.exists() and not overwrite:
        raise FileExistsError(f"File '{path}' already exists and overwrite=False.")

    if create_parents:
        _ensure_parent(target)

    data = base64.b64decode(base64_content)
    target.write_bytes(data)
    return f"Wrote {len(data)} bytes to {_to_relative(target)}"


@mcp.tool()
def directory_tree(path: str = ".", max_depth: int = 3, include_hidden: bool = False) -> str:
    """Return a simple text tree for a directory."""
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"Directory '{path}' does not exist.")
    if not target.is_dir():
        raise NotADirectoryError(f"'{path}' is not a directory.")
    if max_depth < 0:
        raise ValueError("max_depth must be 0 or greater.")

    lines: list[str] = [f"{_to_relative(target)}/"]

    def walk(current: Path, prefix: str, depth: int) -> None:
        if depth > max_depth:
            return

        children = sorted(current.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        visible_children = []
        for child in children:
            rel = _to_relative(child)
            if not include_hidden and any(part.startswith(".") for part in Path(rel).parts if part != "."):
                continue
            visible_children.append(child)

        for i, child in enumerate(visible_children):
            is_last = i == len(visible_children) - 1
            connector = "└── " if is_last else "├── "
            suffix = "/" if child.is_dir() else ""
            lines.append(f"{prefix}{connector}{child.name}{suffix}")
            if child.is_dir() and depth < max_depth:
                extension = "    " if is_last else "│   "
                walk(child, prefix + extension, depth + 1)

    walk(target, "", 0)
    return "\n".join(lines)


# --- Optional Prompt ---

@mcp.prompt()
def filesystem_assistant_prompt(task: str) -> str:
    """Generate a prompt telling an AI assistant to complete a filesystem task carefully."""
    return (
        "You are helping with a filesystem task inside a restricted project root. "
        "Read the relevant files first, make the smallest safe changes needed, "
        "and describe exactly what you changed. Task: "
        f"{task}"
    )


# --- Local Test Mode ---

def _run_local_test() -> None:
    print("Running Filesystem MCP in local test mode.")
    print(f"Root directory: {ROOT_DIR}\n")
    print("Type one of these commands:")
    print("  list <path>")
    print("  read <path>")
    print("  write <path> <text>")
    print("  append <path> <text>")
    print("  mkdir <path>")
    print("  rmfile <path>")
    print("  rmdir <path>")
    print("  tree <path>")
    print("  quit\n")

    while True:
        raw = input("> ").strip()
        if not raw:
            continue
        if raw.lower() == "quit":
            print("Goodbye.")
            break

        parts = raw.split(" ", 2)
        command = parts[0].lower()

        try:
            if command == "list" and len(parts) >= 2:
                print(json.dumps(list_directory(parts[1]), indent=2))
            elif command == "read" and len(parts) >= 2:
                print(read_file(parts[1]))
            elif command == "write" and len(parts) >= 3:
                print(write_file(parts[1], parts[2]))
            elif command == "append" and len(parts) >= 3:
                print(append_file(parts[1], parts[2]))
            elif command == "mkdir" and len(parts) >= 2:
                print(make_directory(parts[1]))
            elif command == "rmfile" and len(parts) >= 2:
                print(remove_file(parts[1]))
            elif command == "rmdir" and len(parts) >= 2:
                print(remove_directory(parts[1]))
            elif command == "tree":
                path = parts[1] if len(parts) >= 2 else "."
                print(directory_tree(path))
            else:
                print("Unknown command or missing arguments.")
        except Exception as exc:  # pragma: no cover - local test helper
            print(f"Error: {exc}")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1].lower() == "test":
        _run_local_test()
        return

    # IMPORTANT for stdio MCP servers:
    # do not print anything to stdout before or during mcp.run().
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
