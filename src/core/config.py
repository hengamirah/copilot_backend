from dotenv import load_dotenv
import os
from src.core.logger import logger

# Load environment variables from the .env file
load_dotenv()

# Access the variables
API_KEY = os.getenv("API_KEY")
COMPLEX_GEMINI_MODEL = os.getenv("COMPLEX_GEMINI_MODEL")
SIMPLE_GEMINI_MODEL = os.getenv("SIMPLE_GEMINI_MODEL")
APP_NAME = os.getenv("APP_NAME")
MSSQL=os.getenv("MSSQL")

os.environ["GOOGLE_API_KEY"] = API_KEY 

logger.debug(f"API_KEY: {API_KEY}")
logger.debug(f"COMPLEX_GEMINI_MODEL: {COMPLEX_GEMINI_MODEL}")
logger.debug(f"SIMPLE_GEMINI_MODEL: {SIMPLE_GEMINI_MODEL}")
logger.debug(f"APP_NAME: {APP_NAME}")
logger.debug(f"MSSQL: {MSSQL}")