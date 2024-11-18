import os
import numpy as np
import discord
from discord.ext import commands
from mysql.connector import pooling

from secret_const import DATABASE_CONFIG

LOG_CHANNEL_ID = 1304829859549155328

ADMIN_LOG_CHANNEL_ID = 1304245019300986941

ROOT_DIR = os.path.expanduser('~/Omniplexium-Eternal')

CURRENT_ITEM_ID_PATH = os.path.join(ROOT_DIR, 'currentItemID.txt')

CACHE_DIR_PFP = os.path.join(ROOT_DIR, 'cacheDir', 'pfps')

LEADERBOARD_PIC = os.path.join(ROOT_DIR, 'leaderboard.png')

DEFUALT_PROFILE_PIC = os.path.join(CACHE_DIR_PFP, 'defualt.png')

CARD_DATA_PATH = os.path.join(ROOT_DIR, 'cardData')

CARD_DATA_IMAGES_PATH = os.path.join(CARD_DATA_PATH, 'images')

CARD_DATA_JSON_PATH = os.path.join(CARD_DATA_PATH, 'json')

pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,
    **DATABASE_CONFIG
)

def xpToLevel(xp: any) -> int:
    # Constants
    TOTAL_LEVELS = 100
    XP_LEVEL_10 = 100
    XP_LEVEL_100 = 10e12  # 1 trillion

    # Calculate the exponential growth factor
    base = (XP_LEVEL_100 / XP_LEVEL_10) ** (1 / (TOTAL_LEVELS - 10))
    
    # Ensure xp is treated as a int
    xp = int(xp)

    # Calculate the level using logarithmic transformation
    if xp <= XP_LEVEL_10:
        # every muiltply of 10 xp is a level
        return int(xp // 10)
    elif xp >= XP_LEVEL_100:
        return TOTAL_LEVELS

    # Reverse-engineer the level based on the xp input
    level = 10 + np.log(xp / XP_LEVEL_10) / np.log(base)
    return int(level)

async def updateXpAndCheckLevelUp(ctx, bot, xp: int, add: bool = True) -> None:
    if isinstance(xp, float): 
        xp = int(xp)
    elif isinstance(xp, str):
        try:
            xp = int(xp)
        except:
            raise ValueError("argument 'xp' must be an int, float, or a string that can be converted to an integer.")

    if not isinstance(add, bool):
        raise ValueError("argument 'add' must be a boolean.")

    # checks which version of the discord API is being used 
    # and this is a bit of hack to use the same function for both
    try:
        ctx.author.id
        discordAuthor = ctx.author
    except:
        discordAuthor = ctx.user

    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT xp FROM stats WHERE userId = %s", (discordAuthor.id,))
        database = cursor.fetchone()

        current_xp = database[0]
        current_level = xpToLevel(current_xp)

        # Update XP based on add flag
        new_xp = current_xp + xp if add else current_xp - xp

        cursor.execute("UPDATE stats SET xp = %s WHERE userId = %s", (new_xp, discordAuthor.id))
        conn.commit()

        # Calculate new level after XP update
        new_level = xpToLevel(new_xp)

    finally:
        cursor.close()
        conn.close()

    level_up = current_level < new_level 
    new_level 
    if level_up:
        # Send the level-up message with the correct level
        channel = bot.get_channel(LOG_CHANNEL_ID)

        if new_level == 1 or new_level > 9:
            await channel.send(f"Congratulations, {discordAuthor.mention}! You have leveled up to level {new_level}!")
        else:
            await channel.send(f"Congratulations, {discordAuthor}! You have leveled up to level {new_level}!")
        
        role = discord.utils.get(ctx.guild.roles, name=f"Level {new_level}")
        
        if role is None:
            channel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
            await channel.send(f"Role 'Level {new_level}' does not exist.")
            return
        if role in discordAuthor.roles:
            channel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
            await channel.send(f"{discordAuthor.name} already has the 'Level {new_level}' role, but we tried to give it to them again.")
            return
        else:
            await discordAuthor.add_roles(role)

    return None