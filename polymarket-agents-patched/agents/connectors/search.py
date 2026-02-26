import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

# NOTE: Keep this key name aligned with .env.example
openai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

# Instantiate Tavily client only if key is present
# (prevents hard crashes in environments where search is optional)
tavily_client = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None


def get_search_context(query: str) -> str:
    if not tavily_client:
        raise RuntimeError("TAVILY_API_KEY is not configured")
    return tavily_client.get_search_context(query=query)
