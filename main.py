"""
Phrase Registry MCP Server Example

Run from the `examples/snippets/clients` directory:
    uv run server phrase_registry stdio
Or, for local testing:
    python main.py test
"""

import json
import os
import sys
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("PhraseRegistry")

# Path to the JSON database file
DB_PATH = "phrases_db.json"


# --- Database Helpers ---

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


# --- Core Tool ---

@mcp.tool()
def register_phrase(phrase: str) -> str:
    """
    Scan a phrase, and if it matches trigger words like 'hi' or 'hello',
    store it in the phrase registry (database).
    """
    trigger_words = {"hi", "hello", "hey", "greetings"}

    phrase_clean = phrase.strip().lower()
    data = load_db()

    if phrase_clean in trigger_words:
        if phrase_clean not in data:
            data.append(phrase_clean)
            save_db(data)
            return f"Phrase '{phrase_clean}' stored in the registry."
        else:
            return f"Phrase '{phrase_clean}' is already in the registry."
    else:
        return f"Phrase '{phrase_clean}' is not a recognized trigger word."


# --- Optional: View stored phrases ---

@mcp.tool()
def list_phrases() -> list:
    """List all stored phrases in the registry."""
    return load_db()


# --- Optional: Clear all phrases ---

@mcp.tool()
def clear_registry() -> str:
    """Clear all stored phrases."""
    save_db([])
    return "Phrase registry cleared."


# --- Example resource (still usable) ---

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Return a personalized greeting."""
    return f"Hello, {name}!"


# --- Example prompt (still usable) ---

@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt."""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }
    return f"{styles.get(style, styles['friendly'])} for someone named {name}."


# --- Run the server (standard entrypoint) OR local test mode ---

if __name__ == "__main__":
    # Check if "test" argument was provided
    if len(sys.argv) > 1 and sys.argv[1].lower() == "test":
        print("Running Phrase Registry in local test mode.\n")
        while True:
            phrase = input("Enter a phrase (or 'quit' to exit): ").strip()
            if phrase.lower() == "quit":
                print("Goodbye.")
                break
            print(register_phrase(phrase))
        print("\nAll stored phrases:", load_db())
    else:
        print("Starting Phrase Registry MCP server...")
        mcp.run()
