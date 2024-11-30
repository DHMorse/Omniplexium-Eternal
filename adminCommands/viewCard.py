from discord.ext import commands
import discord
from pathlib import Path
from const import CARD_DATA_IMAGES_PATH, pool

# Ensure CARD_DATA_IMAGES_PATH is a Path object
CARD_DATA_IMAGES_PATH = Path(CARD_DATA_IMAGES_PATH)

@commands.command()
async def viewcard(ctx, *, query: str = "") -> None:
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have the required permissions to use this command.")
        return
    
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if not query:
            await ctx.send("Please specify a valid card name or ID to view.")
            return

        card_data = None

        # Try to find by itemId if the query is numeric
        if query.isdigit():
            cursor.execute("SELECT * FROM cards WHERE itemId = %s", (int(query),))
            card_data = cursor.fetchone()
        else:
            # Otherwise, find by itemName (case-insensitive)
            cursor.execute("SELECT * FROM cards WHERE LOWER(itemName) = LOWER(%s)", (query,))
            card_data = cursor.fetchone()
        
        if card_data is None:
            await ctx.send(f"No card found for '{query}'.")
            return

        # Extract the itemId and construct the image path
        item_id = card_data['itemId']
        image_path = CARD_DATA_IMAGES_PATH / f"{item_id}.png"

        # Check if the image file exists
        if not image_path.exists():
            await ctx.send(f"Image for itemId {item_id} not found.")
            return

        # Send the image
        await ctx.send(file=discord.File(image_path))
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
