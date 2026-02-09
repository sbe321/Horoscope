from keep_alive import keep_alive
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Keep the repl alive
keep_alive()

# Import and run the bot
import horoscope_bot
