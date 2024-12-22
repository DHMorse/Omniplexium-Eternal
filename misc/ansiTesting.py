from discord.ext import commands
import discord
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from secret_const import TOKEN
from const import COLORS

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    # ANSI GREEN COLOR CODE: \u001b[0;36m
    await ctx.send('''```ansi
\u001b[0;36mPong!```
                    ''')

@bot.command()
async def pong(ctx):
    # ANSI RED COLOR CODE: \u001b[0;31m
    await ctx.send("```ansi\n\u001b[0;31mPing!```")

@bot.command()
async def ansi(ctx):
    await ctx.send('''```ansi
\u001b[1;31mError! Something went wrong.
\u001b[1;34mSuccess! Operation completed successfully. 
\u001b[1;33mWarning! Please proceed with caution.
                    ```''')

@bot.command()
async def color(ctx):
    await ctx.send(f"""```ansi
{COLORS['red']}This is red text.{COLORS['reset']}
{COLORS['blue']}This is green text.{COLORS['reset']}
{COLORS['yellow']}This is yellow text.{COLORS['reset']}
```""")

@bot.command()
async def ini(ctx):
    await ctx.send('''```ini
[ERROR] ❌ Something went wrong.
[WARNING] ⚠️ Please proceed with caution.
[SUCCESS] ✅ Operation completed successfully.
```''')

bot.run(TOKEN)