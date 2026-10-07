# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr helps you decide whether a thrifted item is worth buying. You describe what you're looking for in plain language, like "vintage graphic tee under $30, size M," and it searches secondhand listings from Depop, Poshmark and thredUp for the best match within your size and budget. It then suggests one or two outfits built around that item using clothes you already own (or general styling ideas if your wardrobe is empty), and writes a short caption you could post about the find. If nothing matches, it tells you what to change: your size, your price limit, or your wording.


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** 
This function takes a description from the user (and optionally a size and/or price ceiling), and gives back the listings that fit the description of the user, with the best match coming first.
- **Inputs:** <!-- name and type each: `max_price` (float), not "a price" -->
The inputs:
     - description (string)
     - size (string)
     - max_price (float)
- **Returns:** This function returns a list of items (in {} - so a dictionary!) that fit the criteria that was set on it (based on the user's description and filtered by size and price). Each listing contains id, title, description, category, style_tags (list), size, condition, price (float), colors (list), brand (str or None), platform.
- **When it has nothing:** When it has nothing, it simply returns an empty list

### `suggest_outfit`

- **What it does:** This function suggests one to two outfits based on the user's wardrobe and a thrifted item that the user selects. If the user's wardrobe is empty, it suggests based on general styling advice. 
- **Inputs:**
     - new_item (dict)
     - wardrobe (dict)
- **Returns:** This function returns a non-empty string with outfit suggestions based on your wardrobe and the item provided (and if wardrobe is empty, the suggestion is based on general styling).
- **When it has nothing:** When the wardrobe is empty, they are provided with general styling tips.

### `create_fit_card`

- **What it does:** This function writes a short postable caption about the outfit suggestion provided by suggest_outfit(). 
- **Inputs:**
     - outfit (string)
     - new_item (dict)
- **Returns:** This function returns a string that reads like a real post instead of a product description. This post should be slighty different everytime the function is ran.
- **When it has nothing:** When the 'output' is empty or whitespace, this function should catch it and return a descriptive message to the user.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` that says what the user could change (loosen the size, raise the price limit, or try different words) and return the session without calling `suggest_outfit`. Otherwise, take the first result as `session["selected_item"]` and continue to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Asking the model. `agent.py::parse_query` sends the query with a system prompt asking for JSON with `description`, `size` and `max_price`, at temperature 0 so the same query parses the same way. If the reply isn't valid JSON, it falls back to searching the whole query with no filters.

**What moves through the session:** `query` → `parsed` (description, size, max_price) → `search_results` → `selected_item` (the first result) → `outfit_suggestion` → `fit_card`. On an empty search, `error` is set and everything after `search_results` stays `None`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30, size M'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Pair the Y2K Baby Tee — Butterfly Print with baggy straight-leg jeans, dark wash to lean into authentic early 2000s street style. Add a brown leather belt to define the waist and finish the look with chunky white sneakers for a casual, nostalgic daytime vibe.

Layer the Y2K Baby Tee — Butterfly Print underneath the oversized grey crewneck sweatshirt paired with wide-leg khaki trousers for a comfortable yet stylish contrast of proportions. Complete the outfit with black combat boots to give the soft graphic top a slightly edgier finish.

  Fit card: Scored this little butterfly tee on depop for only $18.00 and it’s basically my entire middle school mood board come to life. I paired it with my favorite baggy dark wash jeans and a brown leather belt to lean into that classic early 2000s street style. Just added some chunky white sneakers to finish the whole nostalgic daytime vibe 🦋👟

0 model calls this session, 3 served from cache
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"


[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says mediumbut fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on thechest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_012', 'title': 'Oversized Crewneck Sweatshirt — Vintage Navy', 'description': 'Perfectly faded navy crewneck. Genuinely vintage — not manufactured distressed. Ribbed cuffs and hem. No graphics, clean.', 'category': 'tops', 'style_tags': ['vintage', 'basics', 'oversized', 'classic'], 'size': 'XL (fits oversized)', 'condition': 'good', 'price': 20.0, 'colors': ['navy'], 'brand': None, 'platform': 'thredUp'}]

```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"


For an effortless streetwear look, pair the Vintage Levi's 501 Jeans — Medium Wash with the white ribbed tank top and layer the oversized grey crewneck sweatshirt over top. Finish this relaxed outfit with your chunky white sneakers and the black crossbody bag for a casual day out. 

To lean into a tougher, vintage aesthetic, tuck the white ribbed tank top into the Vintage Levi's 501 Jeans — Medium Wash and secure it with the brown leather belt. Throw on the vintage black denim jacket and lace up your black combat boots to complete a cool, edgy ensemble.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"


Finally found the perfect pair of broken-in denim to wear with my crisp white sneakers and a beat-up graphic tee. I scored these exact jeans on depop for $38.00 and theyfit like an absolute dream. 👖✨
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I asked Claude to finish `search_listings` by scoring each listing on keyword overlap with the description.
- *What came back:* A scorer that counted every word the query and listing shared equally, whether it was in the title, the tags, or the description. When I ran `search_listings('graphic tee', max_price=30)`, Low-Rise Cargo Pants showed up in the results. Its description says "Great for layering with a long tee," so it matched "tee." The Mesh Long-Sleeve Top ("layering under a graphic tee") ranked above an actual band tee, and a sweatshirt matched "graphic" from "No graphics, clean."
- *What I changed:* I had the scoring weighted by where the word appears: a match in the title, style tags, category, colors, brand or platform counts 2, and a match only in the description counts 1. Descriptions often mention other items, so they shouldn't count as much as what the item actually is. After the change, all three real tees tied at the top and the pants and sweatshirt dropped to the bottom.

**Moment 2**

- *What I asked for:* How to parse the user's query into a description, a size, and a max price for `search_listings`.
- *What came back:* Claude recommended regex, because it's deterministic and costs no API calls.
- *What I changed:* I chose to have the model parse it instead (`agent.py::parse_query`, temperature 0, JSON output with a fallback if the reply isn't valid JSON). Testing showed it handled phrasings regex would struggle with, like "nothing over 50" and "black boots in a 9." But it read "a large tote bag" as size `large`, which would have filtered out every bag, since bags are "One Size." I added a rule to the system prompt that words describing the item rather than a clothing size, like "large tote" or "small bag," belong in the description. After that, "a large tote bag" parsed with no size, and "graphic tee in a large" still parsed `large` as the size.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The selected item reaches both tools intact | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card has exact price, platform, 2–4 sentences | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Size and price filters hold on every result | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Criterion 3 says "each with a different query", so its five tries are try 1 of
five separate scenarios: Levi's jeans, silk slip dress, leather bomber, cargo
pants and knit cardigan. Full output for every try is in
`results/run_2026-10-07_1942_before.md`.

**Real output for each criterion from one try**, pasted as text:

**Criterion 1 — matching query completes** — try 1, from `agent.py::run_agent`, run by `run_eval.py::main`; saved in `results/run_2026-10-07_1942_before.md`

```
Query: vintage graphic tee under $30
stopped early: no
selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
search_results: 10

[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[3] suggest_outfit
      in:  new_item=Y2K Baby Tee — Butterfly Print, wardrobe=10 items
      out: You should definitely buy the Y2K Baby Tee — Butterfly Print because it is a versatile piece that easily bridg…
[4] create_fit_card
      in:  outfit=<654 chars>, new_item=Y2K Baby Tee — Butterfly Print
      out: Scored this little butterfly tee on depop for $18.00 and it fits right into my rotation. I paired it with some…

Fit card:
Scored this little butterfly tee on depop for $18.00 and it fits right into my rotation. I paired it with some baggy dark wash straight-leg jeans and chunky white sneakers for an easy street-style look. Threw on my black crossbody bag to finish it off. 🦋
```

**Criterion 2 — impossible query stops early** — try 1, from `agent.py::run_agent`, run by `run_eval.py::main`; saved in `results/run_2026-10-07_1942_before.md`

```
Query: designer ballgown size XXS under $5
stopped early: yes — Nothing matched 'designer ballgown'. Try a different size than XXS (or no size), a price limit above $5.00 or different words.
selected_item: (none)
search_results: 0

[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
```

**Criterion 3 — the item reaches both tools** — try 1 (Levi's jeans scenario), from `agent.py::run_agent`, run by `run_eval.py::main`; saved in `results/run_2026-10-07_1942_before.md`

```
Query: levis jeans
stopped early: no
selected_item: Vintage Levi's 501 Jeans — Medium Wash ($38.0, depop)
search_results: 4

Outfit suggestion:
For a relaxed streetwear look, pair the Vintage Levi's 501 Jeans — Medium Wash with the white ribbed tank top and the oversized grey crewneck sweatshirt layered on top. Finish this effortless everyday vibe with the chunky white sneakers and the black crossbody bag.

For a slightly edgy, vintage-inspired outfit, combine the Vintage Levi's 501 Jeans — Medium Wash with the black cropped zip hoodie and the vintage black denim jacket. Ground the ensemble with the black combat boots, cinch the waist with the brown leather belt, and carry the black crossbody bag.

Fit card:
Found these exact vintage denim jeans on depop for $38.00 and they were totally worth the hunt. Threw them on with a black cropped zip hoodie and a vintage black denim jacket for that broken-in look. Grounded the whole fit with some heavy black combat boots and my trusty black crossbody bag. 🖤
```

**Criterion 4 — the fit card** — try 1, from `agent.py::run_agent`, run by `run_eval.py::main`; saved in `results/run_2026-10-07_1942_before.md`

```
Query: suede chelsea boots
stopped early: no
selected_item: Suede Chelsea Boots — Tan ($44.0, poshmark)
search_results: 1

Fit card:
Threw on these tan suede chelsea boots with some baggy dark wash denim and a white ribbed tank. Layered up a vintage black denim jacket and a brown leather belt to lean into that rugged western edge. Snagged them on Poshmark for $44.00 and they're going to be on heavy rotation all fall 🤠
```

**Criterion 5 — size and price filters** — try 1, from `agent.py::run_agent`, run by `run_eval.py::main`; saved in `results/run_2026-10-07_1942_before.md`. The run log only lists titles, so the sizes and prices below come from calling `tools.py::search_listings` directly with the same parsed inputs

```
Query: graphic tee size S under $25
stopped early: no
selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
search_results: 2

[1] parse_query
      in:  graphic tee size S under $25
      out: {'description': 'graphic tee', 'size': 'S', 'max_price': 25.0}
[2] search_listings
      in:  {'description': 'graphic tee', 'size': 'S', 'max_price': 25.0}
      out: 2 items: Y2K Baby Tee — Butterfly Print, Mesh Long-Sleeve Top — Black

search_listings('graphic tee', 'S', 25.0):
Y2K Baby Tee — Butterfly Print | size S/M | $18.00
Mesh Long-Sleeve Top — Black | size S/M | $15.00
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
(.venv) ai201-project2-fitfindr-starter-v2026 $ python app.py ask 'vintage graphic tee under $30, size M' --trace
[1] parse_query
      in:  vintage graphic tee under $30, size M
      out: {'description': 'vintage graphic tee', 'size': 'M', 'max_price': 30.0}
[2] search_listings
      in:  {'description': 'vintage graphic tee', 'size': 'M', 'max_price': 30.0}
      out: 9 items: Y2K Baby Tee — Butterfly Print, 90s Silk Slip Dress — Floral, Midi Length, Leather Belt — Brown, Braided … +6 more
[3] suggest_outfit
      in:  new_item=Y2K Baby Tee — Butterfly Print, wardrobe=10 items
      out: Pair the Y2K Baby Tee — Butterfly Print with baggy straight-leg jeans, dark wash to lean into authentic early …
[4] create_fit_card
      in:  outfit=<541 chars>, new_item=Y2K Baby Tee — Butterfly Print
      out: Scored this little butterfly tee on depop for only $18.00 and it’s basically my entire middle school mood boar…

  Found:
  Y2K Baby Tee — Butterfly Print — $18.00 on depop

  Outfit:
  Pair the Y2K Baby Tee — Butterfly Print with baggy straight-leg jeans, dark wash to lean into authentic early 2000s street style. Add a brown leather belt to define the waist and finish the look with chunky white sneakers for a casual, nostalgic daytime vibe.

  Layer the Y2K Baby Tee — Butterfly Print underneath the oversized grey crewneck sweatshirt paired with wide-leg khaki trousers for a comfortable yet stylish contrast of proportions. Complete the outfit with black combat boots to give the soft graphic top a slightly edgier finish.

  Fit card:
  Scored this little butterfly tee on depop for only $18.00 and it’s basically my entire middle school mood board come to life. I paired it with my favorite baggy dark wash jeans and a brown leather belt to lean into that classic early 2000s street style. Just added some chunky white sneakers to finish the whole nostalgic daytime vibe 🦋👟

0 model calls this session, 3 served from cache
```

**Empty search**

```
(.venv) ai201-project2-fitfindr-starter-v2026 $ python app.py ask 'designer ballgown size XXS under $5' --trace
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)

  Nothing matched 'designer ballgown'. Try a different size than XXS (or no size), a price limit above $5.00 or different words.

0 model calls this session, 1 served from cache
```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->
On the MCP move: I registered search_listings in mcp_server.py with @mcp.tool(), using the same typed inputs as my Tool Inventory (description: str, size: str | None, max_price: float | None). I also wrote a description for an agent that can't see my code: it gives price in US dollars (inclusive), example size formats, the fields each result has, and says an empty list means no match. In agent.py::run_agent, I replaced the direct search_listings(description, size, max_price) call with call_tool("search_listings", {...}). Nothing behaved differently afterwards. I compared the direct and MCP results on three queries (a match, a no-match and one with no filters), and they were identical, including the empty case returning [].


---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
