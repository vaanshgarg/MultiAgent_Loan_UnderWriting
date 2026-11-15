
import os
from dotenv import load_dotenv

load_dotenv()


def get_settings():
    """Load project configuration from environment variables."""

    return {
        "google_api_key": os.getenv("GOOGLE_API_KEY"),
        "google_model": os.getenv(
            "GOOGLE_MODEL",
            "gemini-2.5-flash"
        ),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "openai_model": os.getenv(
            "OPENAI_MODEL",
            "gpt-4o-mini"
        ),
    }


def create_gemini_client():
    """Create a Microsoft Agent Framework Gemini client."""

    from agent_framework.gemini import GeminiChatClient

    settings = get_settings()

    if not settings["google_api_key"]:
        raise ValueError(
            "GOOGLE_API_KEY is missing. Check your .env file."
        )

    return GeminiChatClient(
        api_key=settings["google_api_key"],
        model=settings["google_model"],
    )


def create_openai_client():
    """Create the existing OpenAI client if needed."""

    from agent_framework.openai import OpenAIChatClient

    settings = get_settings()

    if not settings["openai_api_key"]:
        raise ValueError(
            "OPENAI_API_KEY is missing. Check your .env file."
        )

    return OpenAIChatClient(
        api_key=settings["openai_api_key"],
        model=settings["openai_model"],
    )
	 