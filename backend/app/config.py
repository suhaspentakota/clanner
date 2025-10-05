from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    PPLX_API_KEY: Optional[str] = None
    BING_SUBSCRIPTION_KEY: Optional[str] = None

    # Extra providers
    GROQ_API_KEY: Optional[str] = None
    MISTRAL_API_KEY: Optional[str] = None
    TOGETHER_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None

    # Azure OpenAI
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = None
    AZURE_OPENAI_API_VERSION: Optional[str] = "2024-06-01"

    # Model defaults
    CLANNER_DEFAULT_OPENAI_MODEL: str = "gpt-5.0"
    CLANNER_DEFAULT_ANTHROPIC_MODEL: str = "claude-3-5-sonnet-latest"
    CLANNER_DEFAULT_GOOGLE_MODEL: str = "gemini-2.5-pro"
    CLANNER_DEFAULT_PPLX_MODEL: str = "llama-3.1-sonar-large-128k-online"
    CLANNER_DEFAULT_GROQ_MODEL: str = "llama-3.1-70b-versatile"
    CLANNER_DEFAULT_MISTRAL_MODEL: str = "mistral-large-latest"
    CLANNER_DEFAULT_TOGETHER_MODEL: str = "meta-llama/Llama-3.1-70B-Instruct-Turbo"
    CLANNER_DEFAULT_OPENROUTER_MODEL: str = "openai/gpt-4o-mini"
    CLANNER_EMBEDDING_MODEL: str = "text-embedding-3-small"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

settings = Settings()
