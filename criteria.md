# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->

`search_listings` is plain code, so the same query finds the same listings
every time. The risk is the two model calls after it: `suggest_outfit` and
`create_fit_card` go over the network, and one timeout or empty response ends
the run without a fit card even when search worked. 4 of 5 leaves room for one
bad model response.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->

The only model call on this path is parsing, which runs at temperature 0, so the same query parses the same way almost every time. Search and the stop (an if on an empty list in run_agent) are plain code. Even if parsing got the size or price wrong, the query's keywords match no listing on their own, so the branch fires either way. One miss in five means the branch is broken, not unlucky.

---

## 3. Something about state

Given a query that returns at least one listing, the outfit suggestion names the selected item, and the fit card
names that item recognizably (e.g. "butterfly tee" for the Y2K Baby Tee) with its exact price and platform, with no
other listing mentioned — 4 of 5 tries, each with a different query.
<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->



**Why this target:**

The item reaches both tools through the session, which is plain code, so the handoff itself should never be wrong. 
The slack is for the model's writing: it may leave the item unnamed or describe it too loosely to recognize, so one
miss in five is allowed. The exact price and platform are the real state check, since the wrong item would show the
wrong ones. 
Details from a different listing are never allowed, because that's a state bug, not the model's wording.

---

## 4. Something about the fit card

The caption contains the exact price (e.g. $18 or $18.00) and the platform name,
and is 2–4 sentences long - 4 of 5 times.
<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->



**Why this target:**

Price and platform are passed straight into the prompt, so the model has everything it needs, and missing 
them more than once in five would mean my prompt is wrong. I don't require 5/5 because the caption is meant 
to read like a real post, not a listing, and at a nonzero temperature the model will sometimes drop the price for style or run to a fifth sentence.

---

## 5. Your choice

For named queries that include a size and/or a price ceiling (e.g. "graphic tee size S under $25", "jacket size M"), 
every returned listing has a matching size (S matches S and S/M, never US 9 or XL) and a price at or under 
the ceiling - 5 out of 5 times.

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->



**Why this target:**

Once the query is parsed, size and price are hard filters in plain code. Parsing is the only model call, and it
runs at temperature 0, so the same query parses the same way and returns the same listings every time. One wrong
listing is a bug, not bad luck.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
