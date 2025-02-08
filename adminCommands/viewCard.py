import discord
import sqlite3

from discord.ext import commands
from pathlib import Path

from const import COLORS, DATABASE_PATH

# Ensure CARD_DATA_IMAGES_PATH is a Path object
CARD_DATA_IMAGES_PATH = '' #Path(CARD_DATA_IMAGES_PATH)

@commands.command()
async def viewcard(ctx, *, query: str = "") -> None:
    if not ctx.author.guild_permissions.administrator:
        await ctx.send(f'''```ansi
{COLORS['yellow']}You do not have the required permissions to use this command.{COLORS['reset']}
```''')
        return
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor(dictionary=True)

        try:
            if not query:
                await ctx.send(f'''```ansi
{COLORS['red']}Please specify a valid card name or ID to view.{COLORS['reset']}
```''')
                return

            cardData = None

            # Try to find by itemId if the query is numeric
            if query.isdigit():
                cursor.execute("SELECT * FROM cards WHERE itemId = ?", (int(query),))
                cardData = cursor.fetchone()
            else:
                # Otherwise, find by itemName (case-insensitive)
                cursor.execute("SELECT * FROM cards WHERE LOWER(itemName) = LOWER(?)", (query,))
                cardData = cursor.fetchone()
            
            if cardData is None:
                await ctx.send(f'''```ansi
{COLORS['red']}No card found for '{query}'.{COLORS['reset']}
```''')
                return

            # Extract the itemId and construct the image path
            item_id = cardData['itemId']
            image_path = CARD_DATA_IMAGES_PATH / f"{item_id}.png"

            # Check if the image file exists
            if not image_path.exists():
                await ctx.send(f'''```ansi
{COLORS['red']}Image for card with ID {item_id} not found.{COLORS['reset']}
```''')
                return

            # Send the image
            await ctx.send(file=discord.File(image_path))
        except Exception as e:
            await ctx.send(f'''```ansi
{COLORS['red']}An error occurred: {e}\u001b[0m{COLORS['reset']}
```''')
            return