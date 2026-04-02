# Filesystem MCP Server for Claude Desktop

A local MCP server that lets Claude Desktop work with files and folders inside one safe workspace directory.

It can:
- create files
- read files
- write files
- append to files
- replace text in files
- insert text at a line number
- delete files
- create directories
- remove directories
- move and copy files/folders
- search for files by name
- search file contents
- show file info
- print a directory tree
- read/write binary files with base64

## Important Safety Note

This server is restricted to **one workspace folder** only.

The code now uses the current user's home folder automatically:

```python
ROOT_DIR = (Path.home() / "Documents" / "my_workspace").resolve()
```

That means the workspace will normally be created here for whoever runs it:

```text
C:\Users\<their-username>\Documents\my_workspace
```

So you do **not** need to hardcode a Windows username into the script anymore.

---

## 1. Requirements

You need:
- Python 3.10 or newer
- the MCP Python package that provides `FastMCP`

Your script imports:

```python
from mcp.server.fastmcp import FastMCP
```

So you must have that installed in the Python environment you use to run the server.

---

## 2. Project Files

Your project can look like this:

```text
your-project-folder/
│
├── main.py
├── README.md
└── claude_desktop_config.json
```

- `main.py` = your filesystem MCP server code
- `README.md` = this file
- `claude_desktop_config.json` = your Claude Desktop config example

---

## 3. Save the Server Code

1. Open a code editor like VS Code.
2. Create a folder for your project.
3. Create a file named `main.py`.
4. Paste the full filesystem MCP server code into `main.py`.
5. Save the file.

Example folder:

```text
C:\Users\kaido\Documents\filesystem-mcp\main.py
```

---

## 4. Workspace Folder Behavior

Inside `main.py`, the server now uses:

```python
ROOT_DIR = (Path.home() / "Documents" / "my_workspace").resolve()
```

This means:
- it automatically uses the current Windows user
- it creates the workspace folder if it does not exist
- it creates a `README.txt` starter file inside the workspace the first time it runs

So if Claude Desktop is running under your Windows account, the workspace will usually be:

```text
C:\Users\kaido\Documents\my_workspace
```

If another user runs the same server on their computer, it will use **their** Documents folder automatically.

---

## 5. Install Python

If Python is not already installed:

1. Download Python from the official Python website.
2. Install it.
3. Make sure Python is added to PATH during installation.

To check that Python works, open Command Prompt or PowerShell and run:

```bash
python --version
```

If that does not work, try:

```bash
py --version
```

---

## 6. Install the MCP Package

Open Command Prompt or PowerShell and install the package:

```bash
python -m pip install mcp
```

If your system uses `py`, you can also do:

```bash
py -m pip install mcp
```

To test whether the import works, run:

```bash
python main.py test
```

If you get an import error, the package is not installed in the Python environment you are using.

---

## 7. Test the Server Locally First

Before connecting it to Claude Desktop, test it locally.

From the folder containing `main.py`, run:

```bash
python main.py test
```

This starts a simple local test mode.

Example commands:

```text
list .
read README.txt
write sample.txt hello
append sample.txt more text
mkdir docs
tree .
quit
```

This test mode is only for manual testing.

---

## 8. Important Claude Desktop Compatibility Note

In normal MCP mode, the server uses:

```python
mcp.run(transport="stdio")
```

The script should **not print to stdout** in normal MCP mode, because Claude Desktop communicates with the server over stdio.

That is why the normal startup section should look like this:

```python
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "test":
        _run_local_test()
    else:
        mcp.run(transport="stdio")
```

The `print(...)` calls are fine in test mode, but do not add normal startup prints in MCP mode.

---

## 9. Add It to Claude Desktop

Open your Claude Desktop config and add the filesystem server under `mcpServers`.

Example:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "python",
      "args": [
        "C:\\Users\\USER\\Documents\\filesystem-mcp\\main.py"
      ]
    }
  }
}
```

If you already have other MCP servers, just add `filesystem` beside them.

Example merged config:

```json
{
  "mcpServers": {
    "ghidra": {
      "command": "python",
      "args": [
        "C:/Users/kaido/Documents/GhidraMCP-release-1-2/bridge_mcp_ghidra.py",
        "--ghidra-server",
        "http://127.0.0.1:8080/"
      ]
    },
    "mcp-forensic-toolkit": {
      "command": "C:\\Users\\kaido\\AppData\\Local\\pypoetry\\Cache\\virtualenvs\\mcp-forensic-toolkit-oRbbFZcU-py3.11\\Scripts\\mcp.exe",
      "args": [
        "run",
        "C:\\Users\\kaido\\Desktop\\ForesnsicTools\\mcp-forensic-toolkit\\mcp_forensic_toolkit\\server.py"
      ]
    },
    "filesystem": {
      "command": "python",
      "args": [
        "C:\\Users\\kaido\\Documents\\filesystem-mcp\\main.py"
      ]
    }
  },
  "preferences": {
    "coworkScheduledTasksEnabled": false,
    "sidebarMode": "chat",
    "coworkWebSearchEnabled": true,
    "ccdScheduledTasksEnabled": false
  }
}
```

---

## 10. Where to Put the Claude Config File

On Windows, Claude Desktop commonly uses:

```text
%APPDATA%\Claude\claude_desktop_config.json
```

A typical full path looks like:

```text
C:\Users\kaido\AppData\Roaming\Claude\claude_desktop_config.json
```

If you already edited this file for other MCP servers, just add the `filesystem` entry into that same file.

---

## 11. Restart Claude Desktop

After saving:
- `main.py`
- your Claude Desktop config file

fully close Claude Desktop and open it again.

If the server starts correctly, Claude Desktop should detect the MCP server and make its tools available.

---

## 12. If `python` Does Not Work in Claude Desktop

Sometimes Claude Desktop cannot find `python` from PATH.

If that happens, replace this:

```json
"command": "python"
```

with the full path to Python, for example:

```json
"command": "C:\\Users\\kaido\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"
```

Then keep the script path in `args`.

Example:

```json
"filesystem": {
  "command": "C:\\Users\\kaido\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
  "args": [
    "C:\\Users\\kaido\\Documents\\filesystem-mcp\\main.py"
  ]
}
```

---

## 13. Common Problems

### Problem: `No module named mcp`
Install the package in the same Python environment Claude Desktop is using:

```bash
python -m pip install mcp
```

### Problem: Claude Desktop does not show the server
Check:
- the JSON is valid
- the path to `main.py` is correct
- `python` is actually available to Claude Desktop
- the server runs locally with `python main.py test`

### Problem: The workspace folder is not where expected
Remember, the server now uses:

```python
Path.home() / "Documents" / "my_workspace"
```

So the folder is based on the user account running the process.

### Problem: Folder will not delete
If the folder is not empty, use recursive deletion through the tool:

```python
remove_directory("myfolder", recursive=True)
```

Be careful with that.

---

## 14. Recommended First Test in Claude Desktop

1. Make sure `main.py` is saved.
2. Add the `filesystem` server to Claude config.
3. Restart Claude Desktop.
4. Ask Claude to do something simple in the workspace, like:
   - list files in the workspace
   - read `README.txt`
   - create a file named `test.txt`

If that works, the server is connected properly.

---

## 15. Final Notes

This version is better than the earlier hardcoded one because:
- it does not depend on a specific username
- it auto-creates the workspace for the current user
- it is safer for Claude Desktop stdio MCP mode

You can still customize it later with:
- file extension blocking
- read-only folders
- maximum file size limits
- logging
- confirmation rules before delete operations
