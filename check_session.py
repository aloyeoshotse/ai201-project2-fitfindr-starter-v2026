"""
Two session checks for run_agent.

    python check_session.py

1. Happy path: print the session, and check that the item in
   session["selected_item"] is the same one that reached suggest_outfit.
2. A query that matches nothing: check that session["fit_card"] is still None
   and that the error message names what the user could change.
"""

import json

import agent
from utils.data_loader import get_example_wardrobe

# Wrap suggest_outfit so we can see exactly which item reached it.
received = {}
real_suggest_outfit = agent.suggest_outfit


def recording_suggest_outfit(new_item, wardrobe):
    received["item"] = new_item
    return real_suggest_outfit(new_item, wardrobe)


agent.suggest_outfit = recording_suggest_outfit


def print_session(session):
    """The whole session, with the wardrobe and search results shortened."""
    shown = dict(session)
    shown["wardrobe"] = f"<{len(session['wardrobe']['items'])} items>"
    shown["search_results"] = [r["title"] for r in session["search_results"]]
    print(json.dumps(shown, indent=2, ensure_ascii=False))


print("=== 1. Happy path ===")
session = agent.run_agent("vintage graphic tee under $30, size M", get_example_wardrobe())
print_session(session)

selected = session["selected_item"]
reached = received.get("item")
print()
print("selected_item:         ", selected["id"], selected["title"])
print("reached suggest_outfit:", reached["id"] if reached else None, reached["title"] if reached else "")
print("PASS" if reached is selected else "FAIL", "— same item")

print("\n=== 2. A query that matches nothing ===")
received.clear()
session = agent.run_agent("designer ballgown size XXS under $5", get_example_wardrobe())
print("error:   ", session["error"])
print("fit_card:", session["fit_card"])
print("PASS" if session["fit_card"] is None else "FAIL", "— fit_card is None")
print("PASS" if not received else "FAIL", "— suggest_outfit was never called")
print("PASS" if session["error"] and "Try" in session["error"] else "FAIL",
      "— message names what to change")
