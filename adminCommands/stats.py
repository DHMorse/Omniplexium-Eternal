from discord.ext import commands
import discord
import json
import datetime

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
        cursor.execute("SELECT xp, money, lastLogin, daysLoggedInInARow FROM users WHERE userId = %s", (member.id,))
        result = cursor.fetchone()

        if result:
            xp, money, lastLogin, daysLoggedInInARow = result
            level = xpToLevel(xp)

            # Create a list of dictionaries for the items
            items_list = []

            cursor.execute("SELECT * FROM cards WHERE userId = %s", (member.id,))
            cards = cursor.fetchall()

            for card in cards:
                item = {
                    "itemId": card[0],
                    "itemName": card[1],
                    "userId": card[2]
                }
                items_list.append(item)

            # Send the stats with items as a JSON code block
            await ctx.send(f"{member.name}'s Stats:\n"
                           f"xp: {xp}\n"
                           f"Level: {level}\n"
                           f"Money: ${money}\n"
                           f"Last Login: {lastLogin}\n"
                           f"Last Login Human Readable: {datetime.fromtimestamp(lastLogin).strftime('%Y-%m-%d %H:%M:%S')}\n"
                           f"Days Logged In In A Row: {daysLoggedInInARow}\n"
                           f"Items: ```json\n{json.dumps(items_list, indent=4)}\n```")
        else:
            await ctx.send(f"{member.name} has no records in the database.")
    
    finally:
        cursor.close()
        conn.close()
