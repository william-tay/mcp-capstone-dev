# Phrase Registry MCP Server (Source Code)

This project provides an MCP server template built with FastMCP.

It serves as the base implementation for two extended branches:
- User Login Server  
- File Upload Server  

## Overview
The server implements a phrase registry system backed by a JSON file.

It demonstrates:
- MCP tool registration  
- Request handling  
- Data persistence  
- Authentication logic  

## Features
- `login(username, password)`  
  Authentication check using hardcoded credentials  

- `register_phrase(phrase)`  
  Stores a phrase in a local JSON database  

- `delete_phrase(phrase)`  
  Removes a phrase from the registry  

- `list_phrases()`  
  Returns all stored phrases  

## Data Storage
- Uses a local file: `phrases_db.json`  
- Stores phrases as a list  
- Automatically creates the file if it does not exist  

## Running the Server
Run from the `examples/snippets/clients` directory:

```bash
uv run server phrase_registry stdio
```

## Purpose
This branch serves as a foundation for:
- Adding authentication and session handling (User Login Server branch)  
- Extending functionality to handle file uploads and storage (File Upload Server branch)  

## Notes
- Authentication is not secure (for demonstration only)  
- No concurrency or validation safeguards are implemented  
- Intended as a starting point for the MCP server branches  
