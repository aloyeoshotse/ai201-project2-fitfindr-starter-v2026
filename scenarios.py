"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
    # Criterion 3 — state. "Each with a different query", so five scenarios,
    # one per item. Each one's top result is a different listing, so a wrong
    # handoff would show up as the wrong title, price or platform. Judge try 1
    # of each row; the five rows together are the five tries.
    {
        "name": "state: levi's jeans",
        "query": "levis jeans",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "state: silk slip dress",
        "query": "silk slip dress",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "state: leather bomber",
        "query": "leather bomber jacket under $80",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "state: cargo pants",
        "query": "cargo pants",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "state: knit cardigan",
        "query": "chunky knit cardigan",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Criterion 4 — the fit card. The same item five times, so the five
        # captions can be checked for price, platform and length side by side.
        "name": "fit card: chelsea boots",
        "query": "suede chelsea boots",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Criterion 5 — size and price filters together. Every result must be
        # a size that fits S (S or S/M, never US 9 or XL) and cost $25 or less.
        "name": "filters: size S under $25",
        "query": "graphic tee size S under $25",
        "wardrobe": "example",
        "criterion": 5,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
