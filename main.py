import os
from dotenv import load_dotenv
from threading import Thread
from flask import Flask

# Load environment variables
load_dotenv()

# Create Flask app for keep-alive
app = Flask('')

@app.route('/')
def home():
    return "🐓 Rooster Horoscope Bot is alive! 🐓"

def run_flask():
    """Run Flask in a separate thread"""
    app.run(host='0.0.0.0', port=8080)

# Start Flask in background thread
flask_thread = Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

print("Flask keep-alive server started on port 8080")

# Now import and run the Discord bot (this will block)
import horoscope_bot
