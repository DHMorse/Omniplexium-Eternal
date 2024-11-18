from discord.ext import commands
import discord
import json

from const import pool
from const import xpToLevel

@commands.command()
async def stats(ctx, member: discord.Member = None):
    if ctx.author.guild_permissions.administrator != True:
        await ctx.send("You do not have the required permissions to use this command.")
        return

    conn = pool.get_connection()
    cursor = conn.cursor()
    
    member = member or ctx.author
    
    try:
        cursor.execute("SELECT xp, money FROM stats WHERE userId = %s", (member.id,))
        result = cursor.fetchone()

        if result:
            xp, money = result
            level = xpToLevel(xp)


            cursor.execute("SELECT * FROM cards WHERE userId = %s", (member.id,))
            cards = cursor.fetchall()

            # Create a dictionary where key is itemID and value is the item details
            cards_dict = {card[0]: card[1:] for card in cards}  # card[0] is itemID, card[1:] is the rest of the data

            # Send the stats with items as a JSON code block
            await ctx.send(f"{member.name}'s Stats:\n"
                           f"xp: {xp}\n"
                           f"Level: {level}\n"
                           f"Money: ${money}\n"
                           f"Items: ```json\n{json.dumps(cards_dict, indent=4)}\n```")
        else:
            await ctx.send(f"{member.name} has no records in the database.")
    
    finally:
        cursor.close()
        conn.close()
