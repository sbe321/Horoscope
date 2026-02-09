import discord
from discord.ext import commands, tasks
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, time
import pytz
import random
import os

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Norway timezone
NORWAY_TZ = pytz.timezone('Europe/Oslo')

# Fun character introductions
CHARACTERS = [
    "The Shaolin Dragon Warrior",
    "Master Oogway the Wise Tortoise",
    "The Mystic Phoenix Oracle",
    "Shifu the Red Panda Master",
    "The Wandering Crane Sage",
    "Po the Kung Fu Panda",
    "The Golden Monkey Monk",
    "The Celestial Tiger Guardian",
    "Grand Master Mantis",
    "The Enlightened Snake Sensei"
]

# Your Discord channel ID (you'll need to replace this)
CHANNEL_ID = None  # Replace with your actual channel ID


async def fetch_rooster_horoscope():
    """Fetch the Rooster horoscope from horoscope.com"""
    url = "https://www.horoscope.com/us/horoscopes/chinese/horoscope-chinese-daily-today.aspx?sign=10"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for the horoscope content - it's usually in a specific paragraph
                    # Try to find the main content area first
                    content_area = soup.find('div', class_='main-horoscope')
                    
                    if content_area:
                        # Get all text and clean it
                        text = content_area.get_text(separator=' ', strip=True)
                        
                        # Remove common junk phrases
                        junk_phrases = [
                            'YesterdayTodayTomorrowWeekly',
                            'Weekly2026',
                            'Discover the key to your unique life path',
                            'premium Birth Chart',
                            'More Horoscopes for',
                            'Sun SignLoveCareerMoneyHealthChineseTarotNumerologyPlanetsFree',
                            'Love MatchFree Birth Chart',
                            '$1 Psychic Reading',
                            'Chinese HoroscopeUnpack what Year of the Dragon',
                            'From your love life to career and finances',
                            'no topic is off-limits in this report'
                        ]
                        
                        # Clean the text
                        for junk in junk_phrases:
                            text = text.replace(junk, '')
                        
                        # Find the date pattern and extract text after it
                        # Pattern: "Feb 9, 2026- " or similar
                        import re
                        match = re.search(r'[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}\s*-\s*(.+?)(?:Discover|More|Sun Sign|$)', text, re.DOTALL)
                        
                        if match:
                            horoscope_text = match.group(1).strip()
                            # Remove any remaining junk at the end
                            horoscope_text = re.sub(r'(Discover|More Horoscopes|Sun Sign|Love|Career).*$', '', horoscope_text, flags=re.DOTALL)
                            return horoscope_text.strip()
                    
                    # Fallback: look for paragraphs
                    paragraphs = soup.find_all('p')
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        # Look for horoscope-like text (complete sentences, reasonable length)
                        if 100 < len(text) < 500 and '.' in text and not any(junk in text for junk in ['Sign up', 'Click here', 'Read more', '$']):
                            return text
                    
                    return None
                else:
                    print(f"Failed to fetch horoscope. Status code: {response.status}")
                    return None
    except Exception as e:
        print(f"Error fetching horoscope: {e}")
        return None


@bot.event
async def on_ready():
    """Called when the bot is ready"""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} server(s)')
    
    # Start the daily horoscope task
    if not daily_horoscope.is_running():
        daily_horoscope.start()
    
    print("Daily horoscope task started!")


@tasks.loop(time=time(hour=0, minute=0))  # Runs at midnight
async def daily_horoscope():
    """Send daily horoscope at midnight Norway time"""
    if CHANNEL_ID is None:
        print("ERROR: CHANNEL_ID is not set! Please set your channel ID in the code.")
        return
    
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"ERROR: Could not find channel with ID {CHANNEL_ID}")
        return
    
    # Get current date in Norway timezone
    norway_now = datetime.now(NORWAY_TZ)
    date_str = norway_now.strftime("%B %d, %Y")
    
    # Fetch the horoscope
    horoscope = await fetch_rooster_horoscope()
    
    if horoscope:
        # Pick a random character
        character = random.choice(CHARACTERS)
        
        # Create the message
        message = f"🐓 **Rooster Horoscope for {date_str}** 🐓\n\n"
        message += f"_{character} says:_\n\n"
        message += f"{horoscope}"
        
        await channel.send(message)
        print(f"Horoscope sent for {date_str}")
    else:
        await channel.send("🐓 Sorry friends, the spirits are unclear today. The horoscope could not be retrieved. 🐓")
        print("Failed to fetch horoscope")


@daily_horoscope.before_loop
async def before_daily_horoscope():
    """Wait until the bot is ready before starting the loop"""
    await bot.wait_until_ready()
    
    # Sync to Norway timezone
    norway_now = datetime.now(NORWAY_TZ)
    print(f"Daily horoscope task will run at midnight Norway time (currently {norway_now.strftime('%H:%M')} in Norway)")


@bot.command(name='horoscope')
async def manual_horoscope(ctx):
    """Manually trigger horoscope (for testing)"""
    norway_now = datetime.now(NORWAY_TZ)
    date_str = norway_now.strftime("%B %d, %Y")
    
    horoscope = await fetch_rooster_horoscope()
    
    if horoscope:
        character = random.choice(CHARACTERS)
        message = f"🐓 **Rooster Horoscope for {date_str}** 🐓\n\n"
        message += f"_{character} says:_\n\n"
        message += f"{horoscope}"
        await ctx.send(message)
    else:
        await ctx.send("Sorry, couldn't fetch the horoscope right now!")


@bot.command(name='setchannel')
@commands.has_permissions(administrator=True)
async def set_channel(ctx):
    """Set the current channel as the horoscope channel"""
    global CHANNEL_ID
    CHANNEL_ID = ctx.channel.id
    
    # Update the environment variable
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    with open('.env', 'w') as f:
        found = False
        for line in lines:
            if line.startswith('CHANNEL_ID='):
                f.write(f'CHANNEL_ID={CHANNEL_ID}\n')
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f'CHANNEL_ID={CHANNEL_ID}\n')
    
    await ctx.send(f"✅ This channel has been set for daily horoscopes! Channel ID: {CHANNEL_ID}")


# Get token and channel ID from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
if os.getenv('CHANNEL_ID'):
    CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

# Check token and run bot
if TOKEN is None:
    print("ERROR: DISCORD_TOKEN not found in environment variables!")
    print("Please set your Discord bot token in the .env file")
else:
    print(f"Starting Discord bot...")
    bot.run(TOKEN)
