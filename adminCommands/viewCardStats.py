import discord
import sqlite3
import traceback 
import json
import io
from discord.ext import commands
from pathlib import Path

from const import  COLORS, DATABASE_PATH

# Ensure CARD_DATA_IMAGES_PATH is a Path object
CARD_DATA_IMAGES_PATH = ''#Path(CARD_DATA_IMAGES_PATH)

@commands.command()
async def viewcardstats(ctx, *, query: str = '') -> None:
    if not ctx.author.guild_permissions.administrator:
        await ctx.send(f'''```ansi\n{COLORS['yellow']}You do not have the required permissions to use this command.{COLORS['reset']}```''')
        return
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        try:
            if not query or query == '':
                await ctx.send(f'''```ansi\n{COLORS['yellow']}Please specify a valid card name or ID to view.{COLORS['reset']}```''')
                return

            cardId = None

            # Try to find by itemId if the query is numeric
            if query.isdigit():
                cursor.execute("SELECT cardId FROM cards WHERE cardId = ?", (int(query),))
                cardId = cursor.fetchone()
            else:
                # Otherwise, find by itemName (case-insensitive)
                cursor.execute("SELECT cardId FROM cards WHERE LOWER(itemName) = LOWER(?)", (query.lower(),))
                cardId = cursor.fetchone()
            
            if cardId is None:
                await ctx.send(f'''```ansi\n{COLORS['yellow']}No card found for '{query}'.{COLORS['reset']}```''')
                return

            # Extract the itemId and construct the image path
            itemId = cardId[0]
            image_path = CARD_DATA_IMAGES_PATH / f"{itemId}.png"

            # Check if the image file exists
            if not image_path.exists():
                await ctx.send(f'''```ansi\n{COLORS['red']}Image for card with ID {itemId} not found.{COLORS['reset']}```''')
                return

            cursor.execute("SELECT * FROM attacks WHERE cardId = ?", (itemId,))
            attack_columns = [desc[0] for desc in cursor.description]
            attack_rows = cursor.fetchall()
            attacks = [dict(zip(attack_columns, row)) for row in attack_rows]

            cursor.execute("SELECT * FROM cards WHERE cardId = ?", (itemId,))
            card_columns = [desc[0] for desc in cursor.description]
            card_info = cursor.fetchone()
            card_data = dict(zip(card_columns, card_info)) if card_info else {}

            data = {
                "cardData": card_data,
                "attacks": attacks
            }

            json_str = json.dumps(data, indent=4)
            file_obj = io.StringIO(json_str)
            await ctx.send(file=discord.File(file_obj, "card_data.json"))

            # Send the image
            await ctx.send(file=discord.File(image_path))

        except Exception as e:
            traceback_str = ''.join(traceback.format_exc())
            await ctx.send(f'''```ansi\n{COLORS['red']}An error occurred: {e}
Traceback: {traceback_str}{COLORS['reset']}```''')