# DoomScroller

**The cure for doomscrolling.** DoomScroller is a personal AI agent that reads through the day's news so you don't have to endlessly scroll for it. Every night, it fetches recent articles, remembers what happened in past days, and emails you a concise, context-aware briefing before bed.

## What it does

- Fetches news from RSS feeds (currently Nepali outlets like RONB Post and Onlinekhabar)
- Parses full article text when RSS summaries are truncated
- Embeds each article and stores it in a local vector database (Chroma)
- Retrieves related past stories automatically (e.g. if today's news is a follow-up to yesterday's — "10 people died in the Kathmandu bus accident" connects back to "bus accident in Kathmandu" from the day before)
- Summarizes everything into one concise nightly briefing using free LLMs (Groq, with Mistral as fallback)
- Emails the briefing to you
- Automatically forgets stories older than 7 days, keeping the memory relevant

## Why

Most news apps either overwhelm you with a raw feed or give you isolated headlines with no memory of yesterday. DoomScroller is designed to feel like a briefing from someone who's been paying attention the whole week — not just today.

## Architecture

```
RSS Feeds → Fetch → Parse → ┬→ Embed → Store in Chroma (7-day memory)
                              └→ Retrieve related past context
                                        ↓
                              Summarize (Groq → Mistral fallback)
                                        ↓
                                   Email briefing
```

## Tech stack

| Layer | Tool |
|---|---|
| Backend | FastAPI |
| Orchestration | LangChain (LangGraph planned for future iteration) |
| Embeddings | Mistral Embeddings API |
| Vector store | Chroma (local, free) — Pinecone planned for future scaling |
| Summarization | Groq (primary) / Mistral (fallback) |
| News ingestion | feedparser (RSS) + BeautifulSoup4 (full article parsing) |
| Email delivery | smtplib |
| Scheduling | Local cron / APScheduler (GitHub Actions planned for later) |

## Project structure

```
doomscroller/
├── requirements.txt
├── .env                    # API keys - never commit this
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── config.py            # env var loading
│   ├── ingestion/
│   │   ├── rss_fetcher.py   # pulls last 24h of articles from RSS feeds
│   │   └── parser.py        # extracts full article text via BeautifulSoup4
│   ├── memory/
│   │   ├── embeddings.py    # Mistral embeddings wrapper
│   │   ├── vector_store.py  # Chroma storage + similarity search
│   │   └── cleanup.py       # deletes articles older than 7 days
│   ├── llm/
│   │   ├── providers.py     # Groq + Mistral clients with fallback
│   │   └── prompts.py       # summarization prompt templates
│   ├── pipeline/
│   │   └── nightly_run.py   # orchestrates the full nightly flow
│   └── delivery/
│       └── emailer.py       # formats + sends the nightly email
└── scripts/
    └── run_once.py           # manual trigger for local testing
```

## Setup

1. Clone the repo and create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with:
   ```
   MISTRAL_API_KEY=your_key_here
   GROQ_API_KEY=your_key_here
   EMAIL_ADDRESS=your_email_here
   EMAIL_PASSWORD=your_app_password_here
   RECIPIENT_EMAIL=where_to_send_briefing@example.com
   ```

4. Run the pipeline manually to test:
   ```bash
   python3 scripts/run_once.py
   ```

## Status

Actively in development. Currently building and testing modules individually before wiring the full pipeline together. News sources are limited to Nepali outlets for v1; X/social media integration was considered but deprioritized due to API cost constraints — may be revisited later.

## Roadmap

- [ ] Finish wiring `nightly_run.py` end-to-end
- [ ] Add scheduling (cron / APScheduler)
- [ ] Tune similarity threshold for follow-up story detection
- [ ] Consider LangGraph for more complex branching logic
- [ ] Evaluate switching to Pinecone if scale requires it
- [ ] Revisit X/social media ingestion if budget allows