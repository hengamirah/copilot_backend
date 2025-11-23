from dotenv import load_dotenv
import os
from src.core.logger import logger
from pathlib import Path

# ensure we load the project .env (repo root runs code)
ROOT = Path(__file__).resolve().parents[2]  # repo/src/core -> parents[2] => repo root
ENV_PATH = ROOT / "src" / "core" / ".env.development"
load_dotenv(ENV_PATH.as_posix())

# Access the variables
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
COMPLEX_GEMINI_MODEL = os.getenv("COMPLEX_GEMINI_MODEL")
SIMPLE_GEMINI_MODEL = os.getenv("SIMPLE_GEMINI_MODEL")
APP_NAME = os.getenv("APP_NAME")
MSSQL=os.getenv("MSSQL")
CHROMA_PATH=os.getenv("CHROMA_PATH")
HOST=os.getenv("HOST")
PORT=os.getenv("PORT")
DBNAME=os.getenv("DBNAME")
USER=os.getenv("USER")
PASSWORD=os.getenv("PASSWORD")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

logger.info(f"Environment variables have been set.")
logger.debug(f"COMPLEX_GEMINI_MODEL: {COMPLEX_GEMINI_MODEL}")
logger.debug(f"SIMPLE_GEMINI_MODEL: {SIMPLE_GEMINI_MODEL}")
logger.debug(f"APP_NAME: {APP_NAME}")
logger.debug(f"MSSQL: {MSSQL}")
logger.debug(f"CHROMA_PATH: {CHROMA_PATH}")
logger.debug(f"HOST: {HOST}")
logger.debug(f"PORT: {PORT}")
logger.debug(f"DBNAME: {DBNAME}")
logger.debug(f"USER: {USER}")

def get_llm_config(prefer_complex_model: bool = True) -> dict:
    """
    Return a normalized LLM configuration dict:
      { provider: 'gemini'|'openai', api_key: str, model_name: str }
    prefer_complex_model controls whether to return COMPLEX_GEMINI_MODEL or SIMPLE_GEMINI_MODEL for Gemini.
    """
    provider = (os.getenv("LLM_PROVIDER") or "gemini").lower()
    if provider == "openai":
        api_key = OPENAI_API_KEY
        model_name = OPENAI_MODEL or "gpt-4o-mini"
    else:
        # default Gemini
        api_key = GEMINI_API_KEY
        model_name = COMPLEX_GEMINI_MODEL if prefer_complex_model else SIMPLE_GEMINI_MODEL
        if not model_name:
            model_name = "gemini-2.5-flash"
    return {"provider": provider, "api_key": api_key, "model_name": model_name}

