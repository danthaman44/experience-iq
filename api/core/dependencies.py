"""
Dependency injection providers for the application.
"""

from typing import Annotated

from fastapi import Depends
from google import genai
from supabase import Client, create_client

from .config import settings


def get_supabase_client() -> Client:
    """
    Dependency provider for Supabase client.

    Returns:
        Client: Configured Supabase client instance
    """
    return create_client(
        settings.SUPABASE_URL, settings.SUPABASE_PUBLISHABLE_DEFAULT_KEY
    )


def get_gemini_client() -> genai.Client:
    """
    Dependency provider for Google Gemini client.

    Returns:
        genai.Client: Configured Gemini client instance
    """
    return genai.Client(api_key=settings.GOOGLE_GENERATIVE_AI_API_KEY)


# Type aliases for dependency injection
SupabaseClient = Annotated[Client, Depends(get_supabase_client)]
GeminiClient = Annotated[genai.Client, Depends(get_gemini_client)]
