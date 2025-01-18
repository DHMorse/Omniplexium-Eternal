import asyncio
from datetime import datetime
import discord
from discord.ext import commands
import os
import sys

# Add the parent directory to sys.path to import secret_const
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from secret_const import TOKEN

# Create the bot instance
bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    print(f"Message from {message.author}: {message.content}")

async def hourly_task():
    while True:
        # Get current time
        now = datetime.now()

        # Calculate time until the next hour
        current_hour = now.hour
        next_hour = (current_hour + 1) % 24
        next_hour_time = now.replace(hour=next_hour, minute=0, second=0, microsecond=0)

        # Calculate the delay until the next hour
        delta_t = (next_hour_time - now).total_seconds()

        # Wait until the next hour
        await asyncio.sleep(delta_t)

        # Print statement at the top of every hour
        print(f'It is now {next_hour_time.strftime("%H:%M:%S")} UTC. Time to print something!')

@bot.event
async def setup_hook():
    # Schedule the hourly task to start when the bot is ready
    print('I"m doing stuff')
    bot.loop.create_task(hourly_task())

# Run the bot
bot.run(TOKEN)
