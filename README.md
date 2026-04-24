Phrase Registry MCP Server (Source code):

This project provides a  MCP server template built with FastMCP. 

It serves as the base implementation for two extended branches:

User Login Server
File Upload Server


The server implements a minimal phrase registry system backed by a JSON file. 

It demonstrates:

MCP tool registration
Basic request handling
Simple data persistence
Lightweight authentication logic
Features
login(username, password)
Basic authentication check (hardcoded credentials)
register_phrase(phrase)
Stores a phrase in a local JSON database
delete_phrase(phrase)
Removes a phrase from the registry
list_phrases()
Returns all stored phrases
Data Storage
Uses a local file: phrases_db.json
Stores phrases as a simple list
Automatically creates the file if it does not exist


Running the Server

Run from the examples/snippets/clients directory:

uv run server phrase_registry stdio





This branch serves as a foundation for:

Adding proper authentication and session handling (User Login Server branch)

Extending functionality to handle file uploads and storage (File Upload Server branch)



Notes:

Authentication is not secure (for demonstration only)

No concurrency or validation safeguards are implemented

Designed for a starting point to base each of the MCP sever branches
