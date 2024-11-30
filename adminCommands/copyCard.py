from discord.ext import commands
import discord

from const import copyCard
from const import pool

@commands.command()
async def copycard(ctx, *cardIdOrName: str, member: discord.Member = None) -> None:
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have the required permissions to use this command.")
        return
    
    if member is None:
        member = ctx.author
    
    try:
        # Join multiple word arguments into a single string for card name
        card_name = " ".join(cardIdOrName)
        
        # Check if the input is a digit (card ID)
        if card_name.isdigit():
            card_id = int(card_name)
        else:
            # If not a digit, look up the card ID by name
            conn = pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT itemId FROM cards WHERE itemName = %s", (card_name,))
            result = cursor.fetchone()
            
            if result is None:
                await ctx.send(f"No card found with the name '{card_name}'.")
                return
            
            card_id = result[0]
            cursor.close()
            conn.close()
        
        # Copy the card
        copyCard(card_id, int(member.id))
        await ctx.send(f"Card with ID {card_id} has been successfully copied to {member.name}.")
    
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")