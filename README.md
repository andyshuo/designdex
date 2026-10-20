# ui-ux-pro-max

A design knowledge base that answers questions on your machine, offline.

Ask it which chart fits time-series data, which font pairing suits a data dashboard, or how to memoize an expensive React render. It returns the specific rows — as Markdown for a human, or JSON for a program.

No API key, no network call, no service to keep alive, and no dependencies — 24 CSV files, one Python package, the standard library.

```
$ uiux-pro-max "glassmorphism" --max-results 1

## UI Pro Max Search Results
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

## Why this exists

Design guidance lives in blog posts that go stale and design tools that want a subscription. Ask a language model "what colours suit a fintech dashboard" and it invents an answer that reads just as confidently as a correct one.

This is the opposite arrangement: a fixed, reviewable table of decisions, plus a ranker that finds the right row. If a palette is wrong you can open `colors.csv` and change it. You cannot edit a hallucination.

It is also a cheap retrieval step in front of an LLM. Hand the model two rows instead of forty pages of prompt.

## Install

```bash
pip install .          # or: pipx install .
uiux-pro-max --help
```

Python 3.9 or newer. There are no dependencies — the standard library only.

## What it does

### Search a domain

```bash
uiux-pro-max "accessible focus states for a form"
```

The domain is guessed from the query when you do not pass one:

```
**Domain:** web | **Query:** accessible focus states for a form
**Source:** web-interface.csv | **Found:** 1 results

### Result 1
- **Category:** Focus
- **Issue:** Visible Focus States
- **Do:** Use :focus-visible with ring/outline
- **Don't:** No focus indication
- **Severity:** Critical
```

Pass `--domain` when the guess is wrong, `--json` when a program is reading, and `--max-results` to widen the net.

### Search a framework

```bash
uiux-pro-max "memoization" --stack react
```

```
**Stack:** react | **Query:** useMemo
**Source:** stacks/react.csv | **Found:** 1 results

### Result 1
- **Category:** Rendering
- **Guideline:** Memoize expensive calculations
- **Code Good:** useMemo(() => expensive(), [deps])
- **Code Bad:** const result = expensiveCalc()
- **Docs URL:** https://react.dev/reference/react/useMemo
```

### Assemble a whole design system

```bash
uiux-pro-max "SaaS analytics dashboard for a fintech" \
  --design-system --project-name "Fintech Console"
```

This composes several tables into one block — a landing-page pattern with its section order, a visual style with its effects, a palette with hex values, a font pairing with the Google Fonts import URL, the anti-patterns to avoid, and a pre-delivery checklist:

```
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

Add `--persist` to write the result to disk as a master document plus per-page overrides:

```bash
uiux-pro-max "SaaS analytics dashboard" --design-system --persist \
  --project-name "Fintech Console" --page "settings"
```

## What is in the box

Ten domains, 1429 curated rows.

| Domain | Rows | Answers questions about |
| --- | ---: | --- |
| `style` | 67 | visual styles — glassmorphism, brutalism, data-dense dashboards |
| `color` | 96 | palettes by product category, with hex notes |
| `typography` | 57 | font pairings, mood, and the CSS import |
| `chart` | 25 | which chart type fits which data |
| `landing` | 27 | landing-page patterns, section order, conversion notes |
| `product` | 96 | UI conventions by product category |
| `ux` | 99 | UX rules with severity |
| `web` | 30 | interface do/don't with code |
| `react` | 44 | React performance rules |
| `icons` | 100 | icon recommendations |

Plus 13 framework guides under `--stack`: `html-tailwind`, `react` (53), `nextjs` (52), `astro` (53), `vue` (49), `nuxtjs` (58), `nuxt-ui` (50), `svelte` (53), `swiftui` (50), `react-native` (51), `flutter` (52), `shadcn` (60), `jetpack-compose` (52).

## How the ranking works

BM25, implemented in `src/uiux_pro_max/core.py` — the same family of scoring that Elasticsearch and Lucene use, in about a hundred and twenty lines.

```python
idf[word] = log((N - freq + 0.5) / (freq + 0.5) + 1)
score += idf[t] * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / avgdl))
```

`k1 = 1.5` and `b = 0.75` are the textbook defaults. They were not tuned against a labelled set, because there isn't one.

Each table declares which columns are searchable and which are returned, so a row is scored on the text a person would actually search — `Keywords`, `Best For`, `Description` — and never on hex values or CSS snippets that would drown the ranking in noise.

## Use it as a library

```python
from uiux_pro_max import search, search_stack, detect_domain, generate_design_system

rows = search("dark dashboard", domain="style", max_results=3)
rows = search_stack("flatlist", stack="react-native", max_results=3)
detect_domain("which chart for time series")  # -> "chart"
design = generate_design_system("fintech dashboard", project_name="Console")
```

Every function returns plain dicts and lists. There is no state to manage and no client to configure.

## Where the data comes from

The rows are hand-curated, and every external reference in them points at first-party documentation: `react.dev`, `tailwindcss.com`, `ui.shadcn.com`, `fonts.google.com`, `developer.apple.com/documentation/swiftui`, `api.flutter.dev`. The code snippets are one-liners showing API usage, not excerpts from other people's programs.

## What this is not

Stated plainly, because the honest boundary is more useful than a feature list.

- **It is not a model.** There are no embeddings. It matches words, not meaning. A query using none of a table's vocabulary scores every row at zero and comes back empty — which is the correct answer, not a bug.
- **The tokenizer drops words of two characters or fewer**, so `UI`, `UX` and `px` never match. This is deliberate: those tokens appear in almost every row, so they rank nothing.
- **The data is one set of opinions.** It reflects a coherent convention, not a survey of designers. Treat a row as a strong default to argue with, not a citation.
- **`--design-system` composes rows; it does not evaluate a design.** It has never seen your page.
- **The ranking is only as good as the vocabulary you use.** "Make it feel expensive" retrieves nothing. "glassmorphism" retrieves the row.

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest --cov=uiux_pro_max --cov-report=term-missing
ruff check .
ruff format --check .
```

100 tests, 92% statement coverage. Each of the five bugs found during that work is pinned by a test that fails if the fix is reverted — the BM25 index not resetting between `fit` calls (which drove IDF negative and inverted the ranking), keyword matching on substrings so that "guide" matched "ui", a silent fallback for unknown domains, a negative `--max-results` returning all-but-the-last row, and a stray `from core import search` that broke `--page` outside the original directory.

## License

MIT. See [LICENSE](LICENSE).
