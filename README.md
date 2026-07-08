# DoomScroller

**The cure for doomscrolling.** DoomScroller is a personal AI agent that reads through the day's Nepali news so you don't have to endlessly scroll for it. Every night, it fetches recent articles, remembers what happened in past days, and emails you a concise, English-language briefing before bed.

## What it does

- Fetches news from RSS feeds (currently RONB Post; Onlinekhabar planned)
- Parses full article text when RSS summaries are truncated
- Embeds each article and stores it in Pinecone (7-day rolling memory)
- Retrieves related past stories automatically, so follow-up news is connected (e.g. "bus accident reported yesterday has now claimed 10 lives")
- Summarizes everything into one concise nightly briefing in English, translated from Nepali sources, using free LLMs (Groq primary, Mistral fallback)
- Emails the briefing as a formatted HTML email
- Automatically forgets stories older than 7 days, keeping memory relevant

## Why

Most news apps either overwhelm you with a raw feed or give isolated headlines with no memory of yesterday. DoomScroller is designed to feel like a briefing from someone who's been paying attention all week — not just today.

## Architecture

```
RSS Feeds → Fetch → Parse → ┬→ Embed → Store in Pinecone (7-day memory)
                              └→ Retrieve related past context
                                        ↓
                              Summarize (Groq → Mistral fallback)
                                        ↓
                                   Email briefing (HTML)
```

## Tech stack

| Layer          | Tool                                                      |
| -------------- | ---------------------------------------------------------- |
| Orchestration  | LangChain (plain functions; LangGraph considered for later) |
| Embeddings     | Mistral Embeddings API (direct HTTP calls)                 |
| Vector store   | Pinecone (serverless, hosted)                               |
| Summarization  | Groq (primary) / Mistral (fallback)                        |
| News ingestion | feedparser (RSS) + BeautifulSoup4 (full article parsing)   |
| Email delivery | smtplib (HTML + plain-text fallback)                       |
| Scheduling     | GitHub Actions (planned)                                    |

## Project structure

```
DoomScroller/
├── requirements.txt
├── .env                    # API keys - never commit this
├── app/
│   ├── config.py            # centralized env vars and constants
│   ├── ingestion/
│   │   ├── rss_fetcher.py   # pulls last 24h of articles from RSS feeds
│   │   └── parser.py        # extracts full article text via BeautifulSoup4
│   ├── memory/
│   │   ├── embeddings.py    # Mistral embeddings wrapper
│   │   ├── vector_store.py  # Pinecone storage + similarity search
│   │   └── cleanup.py       # deletes articles older than 7 days
│   ├── llm/
│   │   ├── providers.py     # Groq + Mistral clients with fallback
│   │   └── prompts.py       # summarization prompt templates (English output)
│   ├── pipeline/
│   │   └── nightly_run.py   # orchestrates the full nightly flow + email
│   └── delivery/
│       └── emailer.py       # formats (HTML) + sends the nightly email
└── scripts/
    ├── run_once.py           # manual trigger, run from repo root
    └── setup_pinecone.py     # one-time Pinecone index creation
```

## Setup

1. Clone the repo and create a virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:

```
MISTRAL_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
PINECONE_INDEX_NAME=doomscroller
EMAIL_ADDRESS=your_sender_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
RECIPIENT_EMAIL=where_to_send_briefing@example.com
```

> Use a [Gmail App Password](https://myaccount.google.com/apppasswords), not your regular password. Requires 2-Step Verification enabled.

4. Create the Pinecone index (one-time):

```
python3 scripts/setup_pinecone.py
```

5. Run the pipeline manually:

```
python3 scripts/run_once.py
```