import os
from pydantic_settings import BaseSettings

class AISettings(BaseSettings):
    # These parameters are securely loaded via system env variables or .env file
    # Never committed to public git history
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # Model Mappings
    LEGAL_DRAFTING_MODEL: str = "meta-llama/llama-3.1-70b-instruct"
    IIT_MADRAS_TRANSLATION_MODEL: str = "ai4bharat/indictrans2-en-indic-1b"

ai_settings = AISettings()

