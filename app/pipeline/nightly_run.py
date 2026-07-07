import time 
from ingestion.rss_fetcher import fetch_recent_articles
from ingestion.parser import fetch_full_article
from memory.vector_store import store_articles, find_related_past_article
from memory.cleanup import delete_old_articles
from llm.prompts import (
    nightly_briefing_prompt,
    format_articles_for_prompt,
    format_related_context
)

from llm.providers import get_llm
from delivery.emailer import send_briefing_email


MIN_SUMMARY_LENGTH = 100 

def enrich_articles(articles: list[dict]) -> list[dict]:
    
    for article in articles:
        if len(article.get("summary","")) < MIN_SUMMARY_LENGTH and article.get("link"):
            full_text = fetch_full_article(article['link'])
            if full_text:
                article['summary'] = full_text
    
    return articles

def gather_related_context(articles: list[dict]) -> list[dict]:
    
    all_related = []
    seen_titles = set()

    for article in articles:
        
        text = f"{article['title']}\n{article.get('summary','')}"
        matches = find_related_past_article(text)

        for match in matches:
            if match['title'] not in seen_titles:
                seen_titles.add(match['title'])
                all_related.append(match)
        
    return all_related

def generate_briefing(articles: list[dict], related_context: list[dict]) -> str:
    chain = nightly_briefing_prompt | get_llm()

    return chain.invoke({
        "today_articles": format_articles_for_prompt(articles),
        "past_context" : format_related_context(related_context)
    })

def run_pipeline() -> str:
    """
    Runs the full nightly pipeline end-to-end and returns the final
    briefing text (does not send email - that's handled separately
    by delivery/emailer.py).
    """
    print("[1/6] Fetching today's articles...")
    articles = fetch_recent_articles()
    print(f"    -> {len(articles)} articles found")
 
    if not articles:
        return "No articles were found in the last 24 hours."
 
    print("[2/6] Enriching truncated summaries...")
    articles = enrich_articles(articles)
 
    print("[3/6] Retrieving related past context...")
    related_context = gather_related_context(articles)
    print(f"    -> {len(related_context)} related past stories found")
 
    print("[4/6] Storing today's articles in memory...")
    stored_count = store_articles(articles)
    print(f"    -> {stored_count} articles stored")
 
    print("[5/6] Generating briefing...")
    briefing = generate_briefing(articles, related_context)
 
    print("[6/6] Cleaning up old memory...")
    deleted_count = delete_old_articles()
    print(f"    -> {deleted_count} old articles removed")
 
    return briefing
 
 
if __name__ == "__main__":
    result = run_pipeline()
    print("\n--- TONIGHT'S BRIEFING ---\n")
    print(result)

    try:
        send_briefing_email(result)
    except Exception as e:
        print(f"Email failed, but briefing was generated:\n{e}")