# ✈️ FlightFinder AI

A ChatGPT‑powered agent that finds **real‑time, wallet‑friendly flight itineraries** and presents them in a conversational UI (Gradio) or via the command line.

*Powered by OpenAI’s function‑calling API and live data from Kiwi’s RapidAPI “Cheap Flights” service.*

---

## Table of Contents

1. [Features](#features)
2. [Architecture Overview](#architecture-overview)
3. [Quick Start](#quick-start)
4. [Configuration (`.env`)](#configuration-env)
5. [CLI Usage](#cli-usage)
6. [Gradio Chat UI](#gradio-chat-ui)
7. [Running Tests](#running-tests)
8. [Providers & Extensibility](#providers--extensibility)
9. [Project Structure](#project-structure)
10. [Troubleshooting](#troubleshooting)
11. [Roadmap](#roadmap)
12. [License](#license)

---

## Features

| 💡  | Capability                                                                                              |
| --- | ------------------------------------------------------------------------------------------------------- |
| 🔍  | Live flight search (Kiwi / RapidAPI) with deep‑links that open the exact itinerary on kiwi.com          |
| 🤖  | Cost‑savvy LLM agent that reasons over constraints (date windows, stopovers, budget caps)               |
| 🛠️ | OpenAI *function calling* — every search is transparent & reproducible                                  |
| 💬  | Two front‑ends: **CLI** (`python -m flighthelper -q ...`) and **chat web UI** (Gradio)                  |
| 🔄  | Editable provider plug‑in system (`src/providers/…`) so you can swap Kiwi for Amadeus, Skyscanner, etc. |
| 🧪  | Pytest smoke tests to verify the provider stays alive 🚦                                                |
| 📦  | Zero requirements.txt – uses **[uv](https://github.com/astral-sh/uv)** + **PEP 621** `pyproject.toml`   |

---

## Architecture Overview

```text
┌──────────────┐           Function call              ┌────────────────────────┐
│  Gradio UI   │  ─────┐   (flight_search)   ┌──────▶ │ Kiwi RapidAPI Provider │
└──────────────┘       │                     │        └────────────────────────┘
                       │                     |
┌──────────────┐   User Prompt          Tool Result   ┌───────────┐
│     CLI      │  ─────┘  ┌───────────────┐  └──────▶ │   Agent   │
└──────────────┘          │   OpenAI GPT  │           └───────────┘
                          └───────────────┘
```

* Two entry points (CLI / UI) send user text → `agent.ask()`
* `agent.py` uses Chat Completions with a single *function tool* (`flight_search`).
* When GPT decides it needs data, it calls the tool → `providers.rapid_kiwi.search()`
* Provider hits RapidAPI → parses JSON → returns `[ {price, deeplink}, … ]`.
* GPT incorporates that data, returns a final answer.

---

## Quick Start

### 1·Clone & enter repo

```bash
git clone https://github.com/your-org/flighthelper.git
cd flighthelper
```

### 2·Create & activate a virtual‑env

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3·Install **uv** & project deps (editable)

```bash
pip install uv
uv sync  # pulls deps from pyproject.toml
```

### 4·Configure secrets

```bash
cp .env.example .env
# edit .env with your keys
```

* **OPENAI\_API\_KEY** – must have *paid* API credit, ChatGPT Plus alone isn’t enough.
* **RAPID\_KEY** – RapidAPI key for *Kiwi‑com Cheap Flights*.

### 5·Smoke‑test

```bash
pytest -q tests/test_kiwi_roundtrip.py
```

If it prints a ✓ and passes, your RapidAPI key works.

---

## Configuration (`.env`)

| Variable          | Purpose                            | Example            |
| ----------------- | ---------------------------------- | ------------------ |
| `OPENAI_API_KEY`  | Auth for OpenAI Platform           | `sk-…`             |
| `RAPID_KEY`       | Auth for RapidAPI Kiwi endpoint    | `xxxxxxxxxxxxxxxx` |
| `FLIGHT_PROVIDER` | Dotted path under `src/providers/` | `rapid_kiwi`       |
| `GPT_MODEL`       | Which OpenAI model to use          | `gpt-4o-mini`      |

You can also export these directly in your shell; `python‑dotenv` will not override existing env vars.

---

## CLI Usage

```bash
python -m flighthelper -q "Cheapest LIM to CUR 10‑13 Sep 2025"
```

Example output:

```markdown
**Best deal:** 178 USD (Avianca LIM → BOG → CUR).  
[Book on Kiwi](https://www.kiwi.com/…)
```

---

## Gradio Chat UI

```bash
python -m flighthelper                # same module, no -q flag
```

* Opens [http://0.0.0.0:7860](http://0.0.0.0:7860) locally.
* Type your query → press **Enter**.
* Replies include markdown, links, copy buttons.
* To expose publicly, set `share=True` in `src/ui.py` or run `python -m flighthelper --share` if you add an argparse flag.

---

## Running Tests

| Command                                  | What it does                                          |
| ---------------------------------------- | ----------------------------------------------------- |
| `pytest -q`                              | Run the whole suite (currently 1 provider smoke test) |
| `pytest -q tests/test_kiwi_roundtrip.py` | Quick provider sanity check                           |

Tests auto‑skip if `RAPID_KEY` is missing.

---

## Providers & Extensibility

1. **Add a new file** under `src/providers/`, e.g. `skyscanner.py`.
2. Implement:

```python
def search(origin, dest, depart_after, arrive_before, limit=12) -> list[dict]:
    pass
```

   Return `[{"price": float, "deeplink": str}, …]`.
3. Export `FLIGHT_PROVIDER=skyscanner` in `.env`.
4. Write a corresponding test in `tests/`.

The agent logic stays unchanged thanks to late binding in `config.py`.

---

## Project Structure

```text
flighthelper/
├── src/
│   ├── providers/         # pluggable data sources
│   ├── agent.py           # OpenAI function‑calling brain
│   ├── ui.py              # Gradio ChatInterface wrapper
│   ├── config.py          # env loader & dynamic provider import
│   └── __main__.py        # CLI + UI launcher
├── tests/                 # pytest smoke tests
└── pyproject.toml         # deps + metadata (PEP 621)
```

---

## Troubleshooting

| Error / Symptom                             | Likely cause                      | Fix                                                                                                                                 |
| ------------------------------------------- | --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `openai.error.InsufficientQuota`            | ChatGPT Plus ≠ API credit         | Add a card → top up at [https://platform.openai.com/account/billing/overview](https://platform.openai.com/account/billing/overview) |
| `HTTP 404 /v2/search`                       | Kiwi Rapid host changed endpoints | We use `/round‑trip`; ensure `rapid_kiwi.py` is up to date                                                                          |
| Gradio stack‑trace with *bool not iterable* | OpenAPI schema bug                | UI sets `show_api=False` – verify you’re running latest `src/ui.py`                                                                 |
| Enter key doesn’t send message              | Using outdated Blocks wiring      | Switch to `gr.ChatInterface`, as in `ui.py`                                                                                         |

---

## License

[MIT](LICENSE) –free as in ✈️air.
