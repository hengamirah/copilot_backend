import logging

# Configure logging to a file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log', # The file to write logs to
    filemode='a' # Append to the file (use 'w' to overwrite)
)

# Create a logger instance for your module
logger = logging.getLogger(__name__)
