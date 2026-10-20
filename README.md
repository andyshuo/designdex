# designdex

**Design decisions you can grep.**

An offline index of UI/UX design decisions — 24 tables, 1,429 rows, ranked with BM25. Ask which chart fits time-series data, which font pairs with a data dashboard, or how to memoize an expensive React render, and it returns the row that answers it, as Markdown or JSON.

The tables are redistributed from the MIT-licensed [`ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill). The ranker, the package, the test suite and the fixes are what this repository adds — [details below](#where-the-data-comes-from).

[![ci](https://github.com/andyshuo/designdex/actions/workflows/ci.yml/badge.svg)](https://github.com/andyshuo/designdex/actions/workflows/ci.yml)

## Install

No runtime dependencies, so there is nothing to compile and nothing to download. Pick how much you want it to stick:

Run it once and leave no trace behind:

```console
$ uvx --from git+https://github.com/andyshuo/designdex designdex "glassmorphism"
```

Install the command onto your `PATH`:

```console
$ uv tool install git+https://github.com/andyshuo/designdex
$ designdex "glassmorphism"
```

Or work against a checkout, which is what you want if you intend to edit the tables:

```console
$ git clone https://github.com/andyshuo/designdex
$ cd designdex
$ uv sync
$ uv run designdex "glassmorphism"
```

Each of these prints:

```console
## designdex / result
**Domain:** style | **Query:** glassmorphism
**Source:** styles.csv | **Found:** 1 results

### Result 1
- **Style Category:** Glassmorphism
- **Keywords:** Frosted glass, transparent, blurred background, layered, vibrant background
- **Primary Colors:** Translucent white: rgba(255,255,255,0.1-0.3)
- **Effects & Animation:** Backdrop blur (10-20px), subtle border (1px solid rgba white 0.2)
- **Best For:** Modern SaaS, financial dashboards, high-end corporate, lifestyle apps
- **Accessibility:** ⚠ Ensure 4.5:1
- **CSS/Technical Keywords:** backdrop-filter: blur(15px), background: rgba(255, 255, 255, 0.15)
```

Python 3.9 or newer. `uv sync` installs from the committed `uv.lock`, so a checkout gets exactly the toolchain CI runs. At query time there is no network, no API key, and no service to keep alive. (It is still an ordinary wheel, so `pip install .` works if you would rather.)

## The problem

Design guidance lives in blog posts that go stale and design tools that want a subscription. Ask a language model what colours suit a fintech dashboard and it invents an answer that reads exactly as confidently as a correct one.

This is the other arrangement: a fixed, reviewable table of decisions, plus a ranker that finds the right row. If a palette is wrong you open `colors.csv` and change it. You cannot edit a hallucination.

It also works as a cheap retrieval step in front of an LLM — hand the model two rows instead of forty pages of prompt.

## Usage

### Search a domain

```console
$ designdex "accessible focus states for a form" --max-results 1

## designdex / result
**Domain:** web | **Query:** accessible focus states for a form
**Source:** web-interface.csv | **Found:** 1 results

### Result 1
- **Category:** Focus
- **Issue:** Visible Focus States
- **Platform:** Web
- **Description:** All interactive elements need visible focus states
- **Do:** Use :focus-visible with ring/outline
- **Don't:** No focus indication
- **Code Example Good:** focus-visible:ring-2 focus-visible:ring-blue-500
- **Code Example Bad:** outline-none // no replacement
- **Severity:** Critical
```

The domain is inferred from the query when you do not pass `--domain`. Pass `--json` when a program is reading, `--max-results` to widen the net, `-d` to override a bad guess.

### Search a framework

```console
$ designdex "useMemo" --stack react

## designdex / stack guideline
**Stack:** react | **Query:** useMemo
**Source:** stacks/react.csv | **Found:** 1 results

### Result 1
- **Category:** Rendering
- **Guideline:** Memoize expensive calculations
- **Description:** Use useMemo for costly computations
- **Code Good:** useMemo(() => expensive(), [deps])
- **Code Bad:** const result = expensiveCalc()
- **Severity:** Medium
- **Docs URL:** https://react.dev/reference/react/useMemo
```

### Assemble a whole design system

```console
$ designdex "SaaS analytics dashboard for a fintech" \
    --design-system --project-name "Fintech Console"
```

This composes several tables into one block — a landing-page pattern with its section order, a visual style with its effects, a palette, a font pairing with the Google Fonts import URL, the anti-patterns to avoid, and a pre-delivery checklist:

```text
|  TARGET: Fintech Console - RECOMMENDED DESIGN SYSTEM
|  PATTERN: AI Personalization Landing
|     CTA: Context-aware placement based on user segment
|  STYLE: Data-Dense Dashboard
|     Performance: ⚡ Excellent | Accessibility: ✓ WCAG AA
|  COLORS:
|     Primary:    #1E40AF
|     Secondary:  #3B82F6
|     CTA:        #F59E0B
|     Background: #F8FAFC
|  TYPOGRAPHY: Fira Code / Fira Sans
|     Google Fonts: https://fonts.google.com/share?selection.family=Fira+Code:wght@400...
```

Add `--persist` to write it out as a master document plus per-page overrides:

```console
$ designdex "fintech dashboard" --design-system --persist \
    -p "Fintech Console" --page settings

Design system persisted to /path/to/project/design-system/fintech-console/
  /path/to/project/design-system/fintech-console/MASTER.md
  /path/to/project/design-system/fintech-console/pages/settings.md
```

## What is in the box

Ten domains, 641 rows — 1,429 in total once the thirteen stack guides and the design-system reasoning table are counted.

| Domain | Rows | Answers questions about |
| --- | ---: | --- |
| `style` | 67 | visual styles — glassmorphism, brutalism, data-dense dashboards |
| `color` | 96 | palettes by product category, with hex values |
| `typography` | 57 | font pairings, mood, and the CSS import |
| `chart` | 25 | which chart type fits which data |
| `landing` | 27 | landing-page patterns, section order, conversion notes |
| `product` | 96 | UI conventions by product category |
| `web` | 30 | interface do/don't, with code |
| `ux` | 99 | UX rules with severity |
| `react` | 44 | React performance rules |
| `icons` | 100 | icon recommendations |

Plus 13 framework guides under `--stack`: `html-tailwind` (55), `react` (53), `nextjs` (52), `astro` (53), `vue` (49), `nuxtjs` (58), `nuxt-ui` (50), `svelte` (53), `swiftui` (50), `react-native` (51), `flutter` (52), `shadcn` (60), `jetpack-compose` (52).

## Why BM25 and not embeddings

The corpus is 1,429 rows written in a controlled vocabulary. That is small enough that a lexical ranker does the job, and lexical ranking has three properties a vector index does not:

- **No model, no download, no GPU.** The whole thing is the standard library, so it installs in a second and works on a plane.
- **Deterministic.** The same query returns the same ranking forever. You can put it in a test.
- **Explainable.** When a row wins, it won because specific query terms appear in specific columns. That reasoning is inspectable; a cosine similarity is not.

BM25, in about 120 lines:

```python
idf[word] = log((N - freq + 0.5) / (freq + 0.5) + 1)
score += idf[t] * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / avgdl))
```

`k1 = 1.5` and `b = 0.75` are the textbook defaults. They were not tuned against a labelled set, because there isn't one.

Each table declares which columns are searchable and which are returned, so a row is scored on the text a person would actually type — `Keywords`, `Best For`, `Description` — and never on hex values or CSS snippets that would drown the ranking in noise.

## As a library

```python
from designdex import search, search_stack, detect_domain, generate_design_system

search("dark dashboard", domain="style", max_results=3)
search_stack("flatlist", stack="react-native", max_results=3)
detect_domain("which chart for time series")  # -> "chart"
generate_design_system("fintech dashboard", project_name="Console")
```

Everything returns plain dicts and lists. No client to configure, no state to manage.

## Where the data comes from

The tables are not mine.

The 24 CSV files come from [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), a design skill released under the MIT licence. They are redistributed here under that licence, and its copyright notice travels with them in [LICENSE-DATA](LICENSE-DATA). Every external reference in the tables points at first-party documentation: `react.dev`, `tailwindcss.com`, `ui.shadcn.com`, `fonts.google.com`, `developer.apple.com/documentation/swiftui`, `api.flutter.dev`. The code snippets are one-liners showing API usage, not excerpts from other people's programs.

What is mine is the layer around them: turning a directory of scripts into an installable package, rewriting the CLI, writing the 100-test suite, setting up CI, and fixing the five bugs listed under Development. The tables were the raw material. The ranking that was silently wrong is what I found.

## What this is not

The boundary is more useful than a feature list, so here it is plainly.

- **It is not a model.** There are no embeddings. It matches words, not meaning. A query using none of a table's vocabulary scores every row at zero and comes back empty — that is the correct answer, not a bug.
- **The tokenizer drops words of two characters or fewer**, so `UI`, `UX` and `px` never match. Deliberate: those appear in nearly every row, so they rank nothing.
- **The data is one set of opinions.** It reflects a coherent convention, not a survey of designers. Treat a row as a strong default to argue with, not a citation.
- **`--design-system` composes rows; it does not evaluate a design.** It has never seen your page.
- **The ranking is only as good as your vocabulary.** "Make it feel expensive" retrieves nothing. "glassmorphism" retrieves the row.

## Development

```console
$ git clone https://github.com/andyshuo/designdex && cd designdex
$ uv sync
$ uv run pytest --cov=designdex --cov-report=term-missing
$ uv run ruff check .
$ uv run ruff format --check .
```

Dev dependencies live in `[dependency-groups]` (PEP 735), which `uv sync` installs without being asked. There is no other setup step: no virtualenv to activate, no `pip install -e`, and no build backend to configure by hand. `uv run designdex ...` runs your edited copy, so the loop between changing a row in `src/designdex/data/` and seeing what it retrieves is one command.

102 tests, 92% statement coverage, CI across Python 3.9–3.14.

Each of the five bugs fixed before the first release is pinned by a test that fails if the fix is reverted:

| Bug | Consequence |
| --- | --- |
| `BM25.fit` counted into its existing document frequencies | A second `fit` on one instance doubled every count and drove IDF negative, inverting the ranking |
| `detect_domain` matched keywords as bare substrings | "guide" matched "ui" and "sidebar" matched "bar", so queries were answered from the wrong table |
| An unknown domain silently fell back to `style` | Answered a question nobody asked, with a 200 OK |
| A negative `--max-results` sliced from the end | Returned every row except the last one |
| A function-local `from core import search` | `--page` was broken in every directory except `scripts/`, where the name happened to resolve |

## License

MIT covers the code — see [LICENSE](LICENSE). The design tables carry the licence they arrived with, reproduced in [LICENSE-DATA](LICENSE-DATA); both files ship inside the wheel.
