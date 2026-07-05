"""
prompts.py

Prompt templates used to turn a batch of raw articles (plus any related
past stories pulled from memory) into one concise nightly briefing.
"""

from langchain_core.prompts import ChatPromptTemplate

NIGHTLY_BRIEFING_SYSTEM_PROMPT = """\
You are a calm, sharp news editor writing a short nightly briefing for one
reader before they go to bed. You will be given today's articles, and for
some of them, related stories from earlier in the week.

Your job:
- Output ONLY a bullet-point list, one point per story - no intro, no paragraphs
- Each bullet should be 1-2 short sentences, plain language, no fluff
- Group related articles into a single bullet (don't repeat the same event twice)
- Cover the main developments of the day across all topics given, not just one
- When a story is a follow-up to an earlier one, say so directly within the bullet
  (e.g. "Kathmandu bus accident (reported yesterday) has now claimed 10 lives")
- Do not invent details, numbers, or outcomes that are not explicitly present
  in the source articles - if unsure whether something is a genuine follow-up,
  treat it as a separate, standalone story instead of guessing a connection
- Do not add a title, summary line, sign-off, or closing remark - bullets only

Format each bullet exactly like this:
- [Topic] One to two sentence summary of what happened.
"""

NIGHTLY_BRIEFING_USER_TEMPLATE = """\
Today's articles:
{today_articles}

Related past context (may be empty if nothing relevant was found):
{past_context}

Write tonight's briefing.
"""

nightly_briefing_prompt = ChatPromptTemplate.from_messages([
    ("system", NIGHTLY_BRIEFING_SYSTEM_PROMPT),
    ("user", NIGHTLY_BRIEFING_USER_TEMPLATE),
])


def format_articles_for_prompt(articles: list[dict]) -> str:
    """Turn a list of article dicts into a readable block of text for the prompt."""
    if not articles:
        return "No articles available."

    blocks = []
    for a in articles:
        blocks.append(
            f"- [{a.get('source', 'Unknown')}] {a['title']}\n  {a.get('summary', '')}"
        )
    return "\n".join(blocks)


def format_related_context(related_matches: list[dict]) -> str:
    """Turn retrieved past-article matches into a readable block of text."""
    if not related_matches:
        return "None found."

    blocks = []
    for m in related_matches:
        blocks.append(f"- (similarity {m['score']:.2f}) {m['title']}: {m.get('summary', '')}")
    return "\n".join(blocks)


# if __name__ == "__main__":
#     # Quick manual test: python prompts.py
#     sample_articles = [
#         {"source": "RONB Post", "title": "10 die in Kathmandu bus accident",
#          "summary": "The bus accident reported yesterday has claimed 10 lives."},
#     ]
#     sample_related = [
#         {"score": 0.87, "title": "Bus accident in Kathmandu injures several",
#          "summary": "A bus veered off the road yesterday, injuring passengers."},
#     ]

#     messages = nightly_briefing_prompt.format_messages(
#         today_articles=format_articles_for_prompt(sample_articles),
#         past_context=format_related_context(sample_related),
#     )
#     for m in messages:
#         print(f"--- {m.type} ---")
#         print(m.content)