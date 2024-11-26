from discord.ext import commands
import discord

from const import ADMIN_LOG_CHANNEL_ID
from const import pool 

@commands.command()
async def set(ctx, stat: str = '', value: str = '', member: discord.Member = None):
    if ctx.author.guild_permissions.administrator != True:
        await ctx.send("You do not have the required permissions to use this command.")
        return
    
    conn = pool.get_connection()
    cursor = conn.cursor()

    if member is None:
        member = ctx.author

    if value == '':
        await ctx.send("Please specify a value to set.")
        return
    
    try:
        if stat == "xp":
            value = int(value)
    except ValueError:
        await ctx.send("Value's for xp and money must be integers.")
        return

    try:
        if stat == "xp":
            cursor.execute("UPDATE users SET xp = %s WHERE userId = %s", (value, member.id))
            conn.commit()
            await ctx.send(f"Set {member.name}'s xp to {value}.")
        elif stat == "money":
            cursor.execute("UPDATE users SET money = %s WHERE userId = %s", (value, member.id))
            conn.commit()
            await ctx.send(f"Set {member.name}'s money to ${value}.")
        else:
            await ctx.send("Please specify a valid stat to set it's value.")
    
    except Exception as e:
        channel = ctx.bot.get_channel(ADMIN_LOG_CHANNEL_ID)
        await channel.send(f"Error: {e}")

    finally:
        cursor.close()
        conn.close()