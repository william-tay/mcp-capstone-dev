# Filesystem MCP Server for Claude Desktop

This project is a local **Python MCP server** that gives Claude Desktop file-system tools inside **one allowed workspace folder**.

It can:
- create files and folders
- read files
- write and append to files
- replace text in files
- insert text at a line number
- move and copy files/folders
- search by filename
- search inside files
- show metadata
- show a directory tree
- read and write binary files using base64

## What changed to make it Claude Desktop friendly

This version is written for **stdio** use with Claude Desktop.

That matters because MCP’s docs warn that stdio servers must **not write to stdout**, or the JSON-RPC protocol can break. This version only uses normal `print()` calls in the separate `test` mode, and runs Claude Desktop mode with `mcp.run(transport="stdio")` and no startup stdout output.

## Files in this folder

- `main.py` — the MCP server Claude Desktop launches
- `README.md` — this setup guide
- `claude_desktop_config.example.json` — a starter config you can copy into Claude Desktop’s config file
- `requirements.txt` — Python dependency list

---

## 1. Requirements

You need:
- **Windows or macOS** with Claude Desktop installed
- **Python 3.10 or newer**
- the **Python MCP SDK 1.2.0 or newer**

The current MCP docs say Python MCP servers need **Python 3.10+** and the **Python MCP SDK 1.2.0+**.

---

## 2. Put the files in a folder

Create a folder for the project, for example:

```text
C:\Users\YourName\Documents\filesystem-mcp
```

Put these files in it:

```text
filesystem-mcp/
├── main.py
├── README.md
├── claude_desktop_config.example.json
└── requirements.txt
```

---

## 3. Edit the workspace folder in `main.py`

Open `main.py` and find this line:

```python
ROOT_DIR = Path(r"C:\Users\YourName\Documents\my_workspace").resolve()
```

Change it to the real folder you want Claude to manage.

Example:

```python
ROOT_DIR = Path(r"C:\Users\Gwen\Documents\my_workspace").resolve()
```

When the server starts, it automatically creates that folder if it does not already exist.
It also creates a small `README.txt` starter file in that workspace.

---

## 4. Install Python packages

Open **Command Prompt** in your project folder and run:

```bat
python -m pip install -r requirements.txt
```

If `python` does not work, try:

```bat
py -m pip install -r requirements.txt
```

---

## 5. Test the server by itself first

Before involving Claude Desktop, make sure the script works on its own.

Run:

```bat
python main.py test
```

You should get a simple local test prompt.

Try these commands:

```text
list .
read README.txt
tree .
write sample.txt hello from test mode
list .
quit
```

If that works, the basic file logic is working.

---

## 6. Find your Python executable path

Claude Desktop is most reliable when you give it an **absolute path** to Python instead of just `python`.

In Command Prompt, run:

```bat
where python
```

You will get a path like one of these:

```text
C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe
```

or:

```text
C:\Python311\python.exe
```

Copy the full path.

---

## 7. Find your project file path

You also need the full path to `main.py`.

Example:

```text
C:\Users\YourName\Documents\filesystem-mcp\main.py
```

---

## 8. Open Claude Desktop config

The current MCP docs show that Claude Desktop can be configured through its developer config file, and the docs list the file location as:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

### Easiest way

In Claude Desktop:
1. Open **Settings**
2. Open **Developer**
3. Click **Edit Config**

That opens the right file automatically.

---

## 9. Paste in the MCP config

Replace the contents with a config like this.

### Windows example

```json
{
  "mcpServers": {
    "filesystem-python": {
      "command": "C:\\Users\\YourName\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
      "args": [
        "C:\\Users\\YourName\\Documents\\filesystem-mcp\\main.py"
      ]
    }
  }
}
```

### Important

- Use the **absolute path** to `python.exe`
- Use the **absolute path** to `main.py`
- Do **not** use relative paths

The MCP debugging docs recommend absolute paths because the working directory for stdio servers launched by the client may be undefined.

---

## 10. Restart Claude Desktop

After saving the config:

1. Completely quit Claude Desktop
2. Open it again

If the server connects properly, you should be able to see MCP tools from the chat UI / connectors area.
Claude’s help docs say you can also check **Developer settings** for connection status and logs.

---

## 11. First test prompts to try in Claude Desktop

Once Claude Desktop is restarted, try prompts like:

- `What is my allowed root directory?`
- `List the files in the workspace.`
- `Create a file named notes.txt that says hello.`
- `Make a folder named drafts.`
- `Search for txt files in the workspace.`
- `Show me a tree of the workspace.`

Claude should ask for approval before using the tools.

---

## 12. Troubleshooting

### Problem: nothing shows up in Claude Desktop

Try these in order:
1. Quit Claude Desktop fully and reopen it
2. Re-check your JSON syntax
3. Make sure your paths are absolute, not relative
4. Manually run the same command in Command Prompt to see if Python errors appear

Example manual run:

```bat
"C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe" "C:\Users\YourName\Documents\filesystem-mcp\main.py"
```

If it just sits there silently, that is normal for an MCP stdio server.
If it throws an import or syntax error, fix that first.

### Problem: `No module named mcp`

Install the dependency again:

```bat
python -m pip install -r requirements.txt
```

### Problem: server disconnects immediately

The most common causes are:
- wrong Python path
- wrong `main.py` path
- bad JSON in Claude config
- a `print()` or other stdout output in normal MCP mode

This rewritten server avoids stdout output during `mcp.run(transport="stdio")`, which is required for stdio servers.

### Problem: where are Claude Desktop logs?

The MCP local-server docs say Claude Desktop writes logs here:

- **macOS:** `~/Library/Logs/Claude`
- **Windows:** `%APPDATA%\Claude\logs`

Look for:
- `mcp.log`
- `mcp-server-SERVERNAME.log`

---

## 13. Optional: desktop extensions (`.mcpb`)

Claude Desktop now also supports local MCP servers through **desktop extensions** installed from a `.mcpb` file.
The support docs say:

1. Go to **Settings > Extensions**
2. Open **Advanced settings**
3. Click **Install Extension…**
4. Select the `.mcpb` file

Claude Desktop also supports **Node.js, Python, and binary** desktop extensions.

For this project, the **simplest setup** is still the config-file method above.
If you later want a one-click install bundle, you can package the server as an `.mcpb` extension.

---

## 14. Why this version is safer than the old one

This version is better for Claude Desktop because it:
- uses `mcp.run(transport="stdio")`
- avoids startup stdout output in normal mode
- keeps all file access restricted to one hardcoded workspace folder
- uses absolute-path-friendly setup in the README

---

## 15. requirements.txt

This project uses:

```text
mcp[cli]>=1.2.0
```

---

## 16. Quick setup checklist

1. Put the files in one folder
2. Edit `ROOT_DIR` in `main.py`
3. Run `python -m pip install -r requirements.txt`
4. Run `python main.py test`
5. Find your full Python path with `where python`
6. Open Claude Desktop → Settings → Developer → Edit Config
7. Paste the JSON config with absolute paths
8. Restart Claude Desktop
9. Test a simple file command in chat

If you do those steps in order, this should be the cleanest way to get your Python filesystem MCP server working with Claude Desktop.
