from discord.ext import commands
import discord

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
        cursor.execute("SELECT xp, money, items FROM users WHERE user_id = %s", (member.id,))
        result = cursor.fetchone()

        if result:
            xp, money, items_list = result
            level = xpToLevel(xp)
            await ctx.send(f"{member.name}'s Stats:\nxp: {xp}\nLevel: {level}\nMoney: ${money}\nItems: {items_list}")
        else:
            await ctx.send(f"{member.name} has no records in the database.")
    
    finally:
        cursor.close()
        conn.close()