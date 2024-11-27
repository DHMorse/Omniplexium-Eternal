import os
import numpy as np
import discord
from discord.ext import commands
from mysql.connector import pooling
from datetime import datetime, timezone

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
        cursor.execute("SELECT xp FROM users WHERE userId = %s", (discordAuthor.id,))
        database = cursor.fetchone()

        current_xp = database[0]
        current_level = xpToLevel(current_xp)

        # Update XP based on add flag
        new_xp = current_xp + xp if add else current_xp - xp

        cursor.execute("UPDATE users SET xp = %s WHERE userId = %s", (new_xp, discordAuthor.id))
        conn.commit()

        # Calculate new level after XP update
        newLevel = xpToLevel(new_xp)

    finally:
        cursor.close()
        conn.close()

    levelUp = current_level < newLevel
    levelDown = current_level > newLevel

    if levelUp or levelDown:
        # Send the level-up message with the correct level
        try:
            channel = bot.get_channel(LOG_CHANNEL_ID)
        except:
            channel = bot.client.get_channel(LOG_CHANNEL_ID)

        if newLevel == 1 or newLevel > 9 and levelUp:
            doMention = True
        elif levelUp:
            doMention = False
        elif levelDown:
            doMention = True
        
        for i in range(current_level, newLevel + 1):
            if levelUp:
                now = datetime.now(timezone.utc)
                embed = discord.Embed(
                    title="Member Leveled Up",
                    description=f"**Member:** \n{discordAuthor}\n\n"
                                f"**Account Level:** \n{i}\n",
                    color=discord.Color.green(),
                    timestamp=now  # Automatically add the timestamp to the footer
                )

                embed.set_thumbnail(url=discordAuthor.display_avatar.url)

                await channel.send(discordAuthor.mention if doMention == True else '', embed=embed)
            
            if levelDown:
                now = datetime.now(timezone.utc)
                embed = discord.Embed(
                    title="Member Leveled Down",
                    description=f"**Member:** \n{discordAuthor}\n\n"
                                f"**Account Level:** \n{i}\n",
                    color=discord.Color.dark_magenta(),
                    timestamp=now  # Automatically add the timestamp to the footer
                )

                embed.set_thumbnail(url=discordAuthor.display_avatar.url)

                await channel.send(embed=embed)

            role = discord.utils.get(ctx.guild.roles, name=f"Level {i}")
            
            if role is None:
                channel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
                await channel.send(f"Role 'Level {i}' does not exist.")
                return
            if role in discordAuthor.roles:
                try:
                    channel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
                except:
                    channel = bot.client.get_channel(ADMIN_LOG_CHANNEL_ID)
                await channel.send(f"{discordAuthor.name} already has the 'Level {i}' role, but we tried to give it to them again.")
                return
            elif levelUp:
                await discordAuthor.add_roles(role)
            elif levelDown:
                await discordAuthor.remove_roles(role)

    return None