from discord.ext import commands
import discord
import os

from const import CARD_DATA_IMAGES_PATH
from const import pool

@commands.command()
async def viewCard(ctx, card: str = "") -> None:
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have the required permissions to use this command.")
        return
    
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)  # Use dictionary cursor for easier field access

    try:
        if not card:
            await ctx.send("Please specify a valid card to reset.")
            return

        # Query the cards table based on cardName
        cursor.execute("SELECT * FROM cards WHERE itemName = %s", (card,))
        card_data = cursor.fetchone()
        
        if card_data is None:
            await ctx.send("Card not found.")
            return

        # Extract the itemId and construct the image path
        item_id = card_data['itemId']
        image_path = CARD_DATA_IMAGES_PATH / f"{item_id}.png"

        # Check if the image file exists
        if not os.path.exists(image_path):
            await ctx.send(f"Image for itemId {item_id} not found.")
            return

        # Send the image
        await ctx.send(file=discord.File(image_path))
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
