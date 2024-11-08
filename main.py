'''
Two (three?) forms of currency:
- Points: for sending messages and playing easy games (karma, aura, social status)
- MONEY money: for leveling up, doing useful crap, etc. (money, stocks, economic crap)
(- REAL MONEY MONEY money: buy with USD lol)

EXTREME rewards for inviting people (automatic? manual?)
'''




import discord
from discord.ext import commands
from secret_const import TOKEN

bot = commands.Bot(command_prefix='', intents=discord.Intents.all()) #change the prefix to what ever i.e. "$" and some people call this var client instead of bot

@bot.event
async def on_ready():
    print(f'Bot is connected as {bot.user}')
# not really super needed but nice

bot.run(TOKEN)