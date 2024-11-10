from discord.ext import commands
import discord

from const import pool

@commands.command()
async def reset(ctx, stat: str = "", member: discord.Member = None):
    if ctx.author.guild_permissions.administrator != True:
        await ctx.send("You do not have the required permissions to use this command.")
        return
    
    conn = pool.get_connection()
    cursor = conn.cursor()

    if member is None:
        member = ctx.author

    member = member.id

    try:
        if stat == "xp":
            cursor.execute("UPDATE users SET xp = %s WHERE user_id = %s", (0, member))
            conn.commit()
            await ctx.send(f"Reset {ctx.author.name}'s xp to 0.")
        elif stat == "money":
            cursor.execute("UPDATE users SET money = %s WHERE user_id = %s", (0, member))
            conn.commit()
            await ctx.send(f"Reset {ctx.author.name}'s money to $0.")
        else:
            await ctx.send("Please specify a valid field to reset.")
    finally:
        cursor.close()
        conn.close()
