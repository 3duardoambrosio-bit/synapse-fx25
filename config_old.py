from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    # Claves de API
    PERPLEXITY_API_KEY: str | None = os.getenv("PERPLEXITY_API_KEY")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

    # Modelos y timeouts
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TIMEOUT: float = float(os.getenv("OPENAI_TIMEOUT", "25"))
    PERPLEXITY_TIMEOUT: float = float(os.getenv("PERPLEXITY_TIMEOUT", "25"))

    # Rutas de salida
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "outputs")
    LINEAGE_DIR: str = os.getenv("LINEAGE_DIR", "decision_lineage")

settings = Settings()
