import asyncio
from datetime import datetime, timedelta
import discord
from discord.ext import commands, tasks
import os
import sqlite3

# Add the parent directory to sys.path to import secret_const
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from const import DATABASE_PATH, COLORS, ADMIN_LOG_CHANNEL_ID, LOGIN_REMINDERS_CHANNEL_ID
from secret_const import TOKEN

bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())

# Define the task outside of the bot class
@tasks.loop(hours=1)
async def login_reminder_task():
    await check_login_reminders()

async def check_login_reminders():
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT userId, lastLogin FROM users WHERE loginReminders = TRUE")
            users = cursor.fetchall()
            
            for user in users:
                userId, lastLogin = user
                # Calculate time since last login
                now = datetime.now()
                last_login_time = datetime.fromtimestamp(lastLogin)
                time_diff = now - last_login_time

                # Check if it's been approximately 24 hours since last login
                if timedelta(hours=40) <= time_diff <= timedelta(hours=41):
                    try:
                        userObj = await bot.fetch_user(userId)
                        await userObj.send("Hey! It's been about 24 hours since your last login. Don't forget to check in!")
                    
                    except discord.errors.NotFound:
                        channel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
                        await channel.send(f"User `{userId}` not found while checking login reminders.")
                    
                    except discord.errors.Forbidden:
                        channel = bot.get_channel(LOGIN_REMINDERS_CHANNEL_ID)
                        await channel.send(f"<@{userId}> It's been about 24 hours since your last login. Don't forget to check in!")

    except sqlite3.Error as e:
        print(f"Database error while checking login reminders: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    if not login_reminder_task.is_running():
        login_reminder_task.start()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command. Please use $help to see available commands.")

bot.run(TOKEN)
