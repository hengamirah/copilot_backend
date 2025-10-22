from dotenv import load_dotenv
import os
from src.core.logger import logger

# Load environment variables from the .env file
load_dotenv(r'C:\Users\Lim Fang Wei\Downloads\personal\data_agent\src\core\.env')

# Access the variables
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

os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY 
os.environ["OPENAI_API_KEY"]=OPENAI_API_KEY