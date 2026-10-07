"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import json

import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import generate, ModelUnavailable
from mcp_client import call_tool


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── query parsing ─────────────────────────────────────────────────────────────

PARSE_SYSTEM = (
    "You pull shopping filters out of a thrift-store search. "
    "Reply with only a JSON object with exactly these keys:\n"
    '  "description": the words describing the item itself (type, style, '
    "color, brand), without the size or price;\n"
    '  "size": the size exactly as the user wrote it (e.g. "M", "W30 L30", '
    '"9", "petite"), or null if they gave none;\n'
    '  "max_price": the most they will pay, as a number, or null if they '
    "gave none.\n"
    "Words that describe the item rather than a clothing size, like "
    "'large tote' or 'small bag', belong in the description. "
    "Never guess a size or price the user didn't state. "
    "No explanation and no code fences, just the JSON."
)


def parse_query(query: str) -> dict:
    """
    Ask the model to split a query into description, size, and max_price.

    "vintage graphic tee under $30, size M"
        → {"description": "vintage graphic tee", "size": "M", "max_price": 30.0}

    The size comes back as the user wrote it — tools.parse_size does the
    normalizing, so "petite" still reaches search and fails there, on purpose.

    Temperature 0, so the same query parses the same way every time. If the
    reply isn't usable JSON, fall back to searching the whole query with no
    filters rather than crashing.
    """
    fallback = {"description": query, "size": None, "max_price": None}

    reply = generate(query, system=PARSE_SYSTEM, temperature=0.0).strip()
    # Models sometimes wrap JSON in ```json fences even when told not to.
    reply = reply.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        data = json.loads(reply)
    except json.JSONDecodeError:
        return fallback
    if not isinstance(data, dict):
        return fallback

    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        description = query

    size = data.get("size")
    size = size.strip() if isinstance(size, str) and size.strip() else None

    try:
        max_price = float(data.get("max_price"))
    except (TypeError, ValueError):   # null, missing, or not a number
        max_price = None
    if max_price is not None and max_price <= 0:
        max_price = None

    return {"description": description.strip(), "size": size, "max_price": max_price}


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)
    count = 0

    # Step 3: parse the query — done by the model, see parse_query().
    count += 1
    trace.check_iterations(count)

    session["parsed"] = parse_query(query)

    # Step 4: search with what was parsed, then branch on the result.
    count += 1
    trace.check_iterations(count)

    description = session["parsed"]["description"]
    size = session["parsed"]["size"]
    max_price = session["parsed"]["max_price"]
    session["search_results"] = call_tool("search_listings", { 
        "description": description,
        "size": size,
        "max_price": max_price
    })

    if not session["search_results"]:
        # The branch: stop before suggest_outfit, and say what to change.
        changes = []
        if size:
            changes.append(f"a different size than {size} (or no size)")
        if max_price is not None:
            changes.append(f"a price limit above ${max_price:.2f}")
        changes.append("different words")
        # ["a", "b", "c"] → "a, b or c"
        if len(changes) == 1:
            suggestion = changes[0]
        else:
            suggestion = ", ".join(changes[:-1]) + " or " + changes[-1]
        session["error"] = f"Nothing matched '{description}'. Try {suggestion}."
        return session

    # Step 5: choose the best match — search already sorted it first.
    session["selected_item"] = session["search_results"][0]

    # Step 6: suggest outfits for that item from the user's wardrobe.
    count += 1
    trace.check_iterations(count)

    session["outfit_suggestion"] = suggest_outfit(session["selected_item"], session["wardrobe"])

    # Step 7: write the fit card from the outfit and the item.
    count += 1
    trace.check_iterations(count)

    session["fit_card"] = create_fit_card(session["outfit_suggestion"], session["selected_item"])

    # Step 8: done — error is still None, so the caller knows the run finished.
    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
