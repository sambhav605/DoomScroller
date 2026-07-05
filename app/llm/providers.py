import os 
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not GROQ_API_KEY:
    raise EnvironmentError("GROQ_API_KEY not found, add it in your .env file")

if not MISTRAL_API_KEY:
    raise EnvironmentError("MISTRAL_API_KEY not found, add it in your .env file")

GROQ_MODEL = "llama-3.1-8b-instant"
MISTRAL_MODEL = "mistral-small-latest"

_llm_with_fallback = None

def get_llm():
    global _llm_with_fallback

    if _llm_with_fallback is None:
        primary = ChatGroq(
            model= GROQ_MODEL,
            api_key= GROQ_API_KEY,
            temperature = 0.3,
        )
        fallback = ChatMistralAI(
            model = MISTRAL_MODEL,
            api_key= MISTRAL_API_KEY,
            temperature=0.3
        )

        _llm_with_fallback = primary.with_fallbacks([fallback])
        _llm_with_fallback = _llm_with_fallback | StrOutputParser()
    return _llm_with_fallback

def summarize(text:str)-> str:
    chain  = get_llm()
    return chain.invoke(text)