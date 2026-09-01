import os

from pydantic_settings import BaseSettings


class AISettings(BaseSettings):
    """Provider/model configuration for optional AI capabilities."""

    OPENROUTER_API_KEY: str = os.getenv(
        "OPENROUTER_API_KEY", ""
    )
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")

    OPENROUTER_URL: str = os.getenv(
        "OPENROUTER_URL",
        "https://openrouter.ai/api/v1",
    )

    LEGAL_DRAFTING_MODEL: str = os.getenv(
        "LEGAL_DRAFTING_MODEL",
        "meta-llama/llama-3.1-70b-instruct",
    )
    IIT_MADRAS_TRANSLATION_MODEL: str = os.getenv(
        "IIT_MADRAS_TRANSLATION_MODEL",
        "ai4bharat/indictrans2-en-indic-1b",
    )


ai_settings = AISettings()
