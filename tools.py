"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Size matching (used by search_listings) ───────────────────────────────────

# Every way of writing a letter size we accept, grouped by its canonical form.
# Includes sizes the data doesn't have yet (xxs, xs, xxl) so they can still
# match if those listings are ever added.
LETTER_SIZE_SPELLINGS = {
    "xxs": ["xxs", "2xs", "xx-small"],
    "xs":  ["xs", "x-small", "xsmall", "extra small"],
    "s":   ["s", "sm", "small"],
    "m":   ["m", "med", "medium"],
    "l":   ["l", "lg", "large"],
    "xl":  ["xl", "x-large", "xlarge", "extra large"],
    "xxl": ["xxl", "2xl", "xx-large"],
}

# Flipped into spelling → size, so parse_size can look a spelling up directly.
LETTER_SIZES = {
    spelling: size
    for size, spellings in LETTER_SIZE_SPELLINGS.items()
    for spelling in spellings
}

# Realistic ranges, used to decide what a bare number like "9" or "30" means.
SHOE_RANGE = (4, 16)     # US shoe sizes
WAIST_RANGE = (22, 48)   # waist in inches


def parse_size(text: str | None) -> dict | None:
    """
    Read a size string — from a listing or from a user — into a kind plus values.

    Returns one of:
        {"kind": "letter",   "sizes": {"s", "m"}}
        {"kind": "waist",    "waist": 30, "length": 30 or None}
        {"kind": "shoe",     "size": 8.5}
        {"kind": "one_size", "adjustable": True or False}
    or None when the size can't be read (e.g. "petite").

    Order matters: one size, then waist, then shoe, then letters. "30/30" has
    to be read as a waist before the letter rule splits it on "/".
    """
    if not isinstance(text, str):
        return None

    text = text.strip()
    adjustable = "adjustable" in text                # check before parentheses go
    text = re.sub(r"\(.*?\)", " ", text)             # "xl (oversized)" → "xl"
    text = re.sub(r"^size\s*:?\s*", "", text.strip())  # "size 9" → "9"
    text = " ".join(text.split())
    if not text:
        return None

    # One size — checked before "/" so "one size / oversized" isn't a range.
    if "one size" in text or text in ("os", "onesize"):
        return {"kind": "one_size", "adjustable": adjustable}

    # Waist: "w30", "w30 l30", "w30l30"
    match = re.fullmatch(r"w\s*(\d{2})(?:\s*l\s*(\d{2}))?", text)
    # Waist: "30x30", "30 x 30", "30/30"
    match = match or re.fullmatch(r"(\d{2})\s*[x/]\s*(\d{2})", text)
    # Waist: "waist 30", "30 waist", "30w"
    match = match or re.fullmatch(r"(?:waist\s*(\d{2})|(\d{2})\s*(?:waist|w))", text)
    if match:
        numbers = [int(n) for n in match.groups() if n]
        if text.startswith("waist") or text.endswith(("waist", "w")):
            waist, length = numbers[0], None
        else:
            waist = numbers[0]
            length = numbers[1] if len(numbers) > 1 else None
        if WAIST_RANGE[0] <= waist <= WAIST_RANGE[1]:
            return {"kind": "waist", "waist": waist, "length": length}
        return None

    # Length only: "l30" — waist unknown.
    match = re.fullmatch(r"l\s*(\d{2})", text)
    if match:
        return {"kind": "waist", "waist": None, "length": int(match.group(1))}

    # Shoe: "us 9", "us 8.5"
    match = re.fullmatch(r"us\s*(\d+(?:\.\d+)?)", text)
    if match:
        number = float(match.group(1))
        if SHOE_RANGE[0] <= number <= SHOE_RANGE[1]:
            return {"kind": "shoe", "size": number}
        return None

    # Bare number: decide shoe or waist by range.
    match = re.fullmatch(r"\d+(?:\.\d+)?", text)
    if match:
        number = float(text)
        if SHOE_RANGE[0] <= number <= SHOE_RANGE[1]:
            return {"kind": "shoe", "size": number}
        if WAIST_RANGE[0] <= number <= WAIST_RANGE[1] and number.is_integer():
            return {"kind": "waist", "waist": int(number), "length": None}
        return None

    # Letters, including ranges: "s/m", "small/medium"
    pieces = [piece.strip() for piece in text.split("/")]
    if all(piece in LETTER_SIZES for piece in pieces):
        return {"kind": "letter", "sizes": {LETTER_SIZES[piece] for piece in pieces}}

    return None


def compare_size(user_size: str, listing_size: str) -> bool:
    """
    True if a listing's size fits the size the user asked for.

    Only call this when the user actually gave a size. "No size given" means
    skip the size filter entirely — that's search_listings' job, not this one.

    Rules:
        - Unreadable on either side → False.
        - Adjustable one-size listings match any letter size.
        - Different kinds never match (a shoe 9 never matches a W30).
        - letter: the two sets share a size ("m" matches "s/m").
        - waist:  waists equal; lengths must also be equal, but only when
                  both sides give one ("w30 l30" still matches "W30").
        - shoe:   numbers equal ("8.5" matches "US 8.5").
    """
    user = parse_size(user_size)
    listing = parse_size(listing_size)
    if user is None or listing is None:
        return False

    if listing["kind"] == "one_size" and listing["adjustable"] and user["kind"] == "letter":
        return True

    if user["kind"] != listing["kind"]:
        return False

    kind = user["kind"]
    if kind == "one_size":
        return True
    if kind == "letter":
        return bool(user["sizes"] & listing["sizes"])
    if kind == "shoe":
        return user["size"] == listing["size"]
    if kind == "waist":
        if user["waist"] is not None and user["waist"] != listing["waist"]:
            return False
        if user["length"] is not None and listing["length"] is not None:
            return user["length"] == listing["length"]
        return True
    return False


# ── Keyword matching (used by search_listings) ────────────────────────────────

# Words that show up in almost every query or listing and say nothing about
# the item. Without this, "looking for a vintage tee" scores every listing.
STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "with", "in", "on", "of", "to", "at",
    "i", "im", "me", "my", "want", "need", "looking", "find", "some",
    "something", "any", "anything", "that", "this", "is", "it", "but",
    "like", "under", "over", "size", "price",
}


def text_to_words(text: str | None) -> set[str]:
    """
    Turn text into a set of lowercase keywords, the same way for queries and
    listings, so the two can be compared whole word to whole word.

    "Levi's 501 Jeans — Medium Wash" → {"levi", "501", "jean", "medium", "wash"}

    Comparing whole words, never substrings, is the point: "hat" in "that" is
    True, but "hat" is not in {"that"}.
    """
    if not text:
        return set()

    text = text.lower().replace("'", "").replace("’", "")   # "levi's" → "levis"
    text = re.sub(r"[^a-z0-9]+", " ", text)                  # punctuation → spaces

    words = set()
    for word in text.split():
        if word in STOPWORDS:
            continue
        # Plurals: "tees" → "tee", "jeans" → "jean". Skip "-ss" so "dress"
        # stays "dress". Done on both sides, so the two always agree.
        if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
            word = word[:-1]
        words.add(word)
    return words


def score_listing(query_words: set[str], item: dict) -> int:
    """
    How well one listing matches the query's words.

    A word found in what the item IS (title, tags, category, colors, brand,
    platform) is worth 2. A word found only in the description is worth 1,
    because descriptions often mention other items — "layering with a long
    tee" on a pair of cargo pants shouldn't rank with an actual tee.
    """
    strong = text_to_words(" ".join([
        item["title"],
        item["category"],
        " ".join(item["style_tags"]),
        " ".join(item["colors"]),
        item["platform"],
        item["brand"] or "",          # brand is None for most listings
    ]))
    weak = text_to_words(item["description"]) - strong

    return 2 * len(query_words & strong) + len(query_words & weak)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """

    listings = load_listings()

    # Filters run only when a value was given. No size means "any size".
    if max_price is not None:
        listings = [item for item in listings if item["price"] <= max_price]
    if size:
        listings = [item for item in listings if compare_size(size, item["size"])]

    # Score by how many of the query's words each listing contains.
    query_words = text_to_words(description)
    scored = []
    for item in listings:
        score = score_listing(query_words, item)
        if score > 0:
            scored.append((score, item))

    # Highest score first. Ties keep the order they had in the data.
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for score, item in scored[:config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

OUTFIT_SYSTEM = (
    "You are a stylist helping someone decide whether to buy a thrifted item. "
    "Suggest one or two complete outfits built around that item. "
    "Mention the item by its title at least once. "
    "Write each outfit as a short paragraph of two or three sentences, "
    "specific about pieces, colors, and the overall vibe. "
    "Only say the user owns a piece if it appears in the wardrobe list you're given. "
    "If there is no wardrobe list, suggest general pieces and never say the user owns anything. "
    "Plain text only: no headings, no markdown, no questions back to the user."
)


def describe_item(item: dict) -> str:
    """One listing as a multi-line block for a prompt."""
    return (
        f"{item['title']}\n"
        f"Category: {item['category']}\n"
        f"Colors: {', '.join(item['colors'])}\n"
        f"Style: {', '.join(item['style_tags'])}\n"
        f"Description: {item['description']}"
    )


def describe_wardrobe(wardrobe: dict) -> str:
    """The user's wardrobe as a bulleted list for a prompt, one piece per line."""
    lines = []
    for piece in wardrobe["items"]:
        line = f"- {piece['name']} ({piece['category']}; {', '.join(piece['colors'])})"
        if piece.get("notes"):                 # notes is optional and often None
            line += f" — {piece['notes']}"
        lines.append(line)
    return "\n".join(lines)


def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    if not wardrobe.get("items"):
        prompt = (
            f"The item:\n{describe_item(new_item)}\n\n"
            "The user hasn't saved any clothes yet. "
            "Suggest general pieces that would pair well with it."
        )
    else:
        prompt = (
            f"The item:\n{describe_item(new_item)}\n\n"
            f"The user's wardrobe:\n{describe_wardrobe(wardrobe)}\n\n"
            "Build each outfit around the item using pieces from this wardrobe, "
            "naming each piece exactly as it's written in the list. "
            "If the wardrobe is missing something an outfit needs, like shoes, "
            "you may suggest a general piece, but make clear the user doesn't own it."
        )

    outfit = generate(prompt, system=OUTFIT_SYSTEM)
    return outfit.strip() or "Couldn't come up with an outfit for this item. Try again."
    


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

FIT_CARD_SYSTEM = (
    "You write captions for thrift finds, the kind someone posts with a photo "
    "of their outfit. Write 2 to 4 sentences in a casual first-person voice. "
    "Mention the item, its price, and the platform it came from once each, "
    "writing the price and platform exactly as given. "
    "Refer to the item naturally, not by its full listing title. "
    "Be specific about the vibe: name real pieces from the outfit instead of "
    "generic praise like 'so cute' or 'obsessed'. "
    "It should not read like a listing: no sizes, condition, or bullet points. "
    "Plain text, no hashtags, at most two emojis."
)


def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """

    if not outfit or not outfit.strip():
        return "No outfit suggestion to build a caption from."
  
    prompt = (
        f"The find:\n{describe_item(new_item)}\n"
        f"Price: ${new_item['price']:.2f}\n"
        f"Platform: {new_item['platform']}\n\n"
        f"How I'm styling it:\n{outfit}\n\n"
        "Pick the outfit you like best from above and write the caption about it."
    )
    caption = generate(prompt, system=FIT_CARD_SYSTEM)
    return caption.strip() or "Couldn't write a caption for this find. Try again."
