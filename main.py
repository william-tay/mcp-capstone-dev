import hashlib
import json
import os
import secrets
import sys
import time
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("PhraseRegistry")


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phrases_db.json")

USERS = {
    os.environ.get("REGISTRY_USER", "admin"): hashlib.sha256(
        os.environ.get("REGISTRY_PASS", "password123").encode()
    ).hexdigest()
}

active_tokens: dict = {}
TOKEN_TTL = 3600


def _issue_token(username: str) -> str:
    token = secrets.token_hex(16)
    active_tokens[token] = {
        "username": username,
        "expires": time.time() + TOKEN_TTL,
    }
    return token


def _verify_token(token: str) -> bool:
    entry = active_tokens.get(token)
    if not entry:
        return False
    if time.time() > entry["expires"]:
        del active_tokens[token]
        return False
    return True


def load_db():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r") as f:
            return json.load(f)
    return []


def save_db(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)


@mcp.tool()
def login(username: str, password: str):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    if USERS.get(username) == hashed:
        token = _issue_token(username)
        return {"status": "success", "token": token}
    return {"status": "error", "message": "Invalid username or password"}


@mcp.tool()
def register_phrase(phrase: str, token: str):
    if not _verify_token(token):
        return {"status": "error", "message": "Unauthorized"}

    trigger_words = {"hi", "hello", "hey", "greetings"}
    phrase_clean = phrase.strip().lower()
    data = load_db()

    if phrase_clean in trigger_words:
        if phrase_clean not in data:
            data.append(phrase_clean)
            save_db(data)
            return {"status": "success", "message": f"Stored '{phrase_clean}'"}
        else:
            return {"status": "info", "message": f"'{phrase_clean}' already exists"}
    else:
        return {"status": "error", "message": "Not a trigger word"}


@mcp.tool()
def list_phrases(token: str):
    if not _verify_token(token):
        return {"status": "error", "message": "Unauthorized"}
    return {"status": "success", "data": load_db()}


@mcp.tool()
def clear_registry(token: str):
    if not _verify_token(token):
        return {"status": "error", "message": "Unauthorized"}
    save_db([])
    return {"status": "success", "message": "Registry cleared"}


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    return f"Hello, {name}!"


@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }
    return f"{styles.get(style, styles['friendly'])} for someone named {name}."


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "test":
        print("Running Phrase Registry in local test mode.\n")

        username = input("Username: ").strip()
        password = input("Password: ").strip()
        result = login(username, password)
        print(result)

        if result.get("status") != "success":
            sys.exit(1)

        token = result["token"]

        while True:
            phrase = input("\nEnter a phrase (or 'quit' to exit): ").strip()
            if phrase.lower() == "quit":
                print("Goodbye.")
                break
            print(register_phrase(phrase, token))

        print("\nAll stored phrases:", list_phrases(token))
    else:
        print("Starting Phrase Registry MCP server...")
        mcp.run()
