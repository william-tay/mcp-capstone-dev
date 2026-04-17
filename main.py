"""
Phrase Registry MCP Server

Run from the `examples/snippets/clients` directory:
    uv run server phrase_registry stdio
"""

import json
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("PhraseRegistry")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phrases_db.json")


#  Database Helpers #

def load_db():
    """Load phrases from the JSON database, or return an empty list if not found."""
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r") as f:
            return json.load(f)
    return []


def save_db(data):
    """Save phrases to the JSON database."""
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)


# Login and Authentication #

@mcp.tool()
def login(username: str, password: str) -> str:
    """Log in to the Phrase Registry server with a username and password."""
    if username == "admin" and password == "pass":
        return "Hi welcome to the phrase registry server."
    return "Incorrect username or password."


# Phrase Registry #

@mcp.tool()
def register_phrase(phrase: str) -> str:
    """Store any phrase in the phrase registry."""
    phrase_clean = phrase.strip().lower()
    data = load_db()

    if phrase_clean not in data:
        data.append(phrase_clean)
        save_db(data)
        return f"Phrase '{phrase_clean}' stored in the registry."
    else:
        return f"Phrase '{phrase_clean}' is already in the registry."


@mcp.tool()
def delete_phrase(phrase: str) -> str:
    """Delete a phrase from the registry by name."""
    phrase_clean = phrase.strip().lower()
    data = load_db()

    if phrase_clean in data:
        data.remove(phrase_clean)
        save_db(data)
        return f"Phrase '{phrase_clean}' has been removed from the registry."
    else:
        return f"Phrase '{phrase_clean}' was not found in the registry."


@mcp.tool()
def list_phrases() -> list:
    """List all stored phrases in the registry."""
    return load_db()


if __name__ == "__main__":
    print("Starting Phrase Registry MCP server...")
    mcp.run()
