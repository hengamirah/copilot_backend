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
CHROMA_PATH=os.getenv("CHROMA_PATH")
HOST=os.getenv("HOST")
PORT=os.getenv("PORT")
DBNAME=os.getenv("DBNAME")
USER=os.getenv("USER")
PASSWORD=os.getenv("PASSWORD")

os.environ["GOOGLE_API_KEY"] = API_KEY 

logger.info(f"Environment variables have been set.")
logger.debug(f"API_KEY: {API_KEY}")
logger.debug(f"COMPLEX_GEMINI_MODEL: {COMPLEX_GEMINI_MODEL}")
logger.debug(f"SIMPLE_GEMINI_MODEL: {SIMPLE_GEMINI_MODEL}")
logger.debug(f"APP_NAME: {APP_NAME}")
logger.debug(f"MSSQL: {MSSQL}")
logger.debug(f"CHROMA_PATH: {CHROMA_PATH}")
logger.debug(f"HOST: {HOST}")
logger.debug(f"PORT: {PORT}")
logger.debug(f"DBNAME: {DBNAME}")
logger.debug(f"USER: {USER}")
logger.debug(f"PASSWORD: {PASSWORD}")