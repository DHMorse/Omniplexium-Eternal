import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='$', intents=discord.Intents.all()) #change the prefix to what ever i.e. "$" and some people call this var client instead of bot

@bot.event
async def on_ready():
    print(f'Bot is connected as {bot.user}')
# not really super needed but nice

bot.run("Your discord token which you get from discord dev portal or some shit")