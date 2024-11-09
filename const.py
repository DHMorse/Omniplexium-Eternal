import os
import numpy as np
from discord.ext import commands
from mysql.connector import pooling

from secret_const import DATABASE_CONFIG

LOG_CHANNEL_ID = 1304829859549155328

ROOT_DIR = os.path.expanduser('~/Documents/Omniplexium-Eternal/')

CACHE_DIR_PFP = os.path.join(ROOT_DIR, 'cache_dir', 'pfps')

LEADERBOARD_PIC = os.path.join(ROOT_DIR, 'leaderboard.png')

DEFUALT_PROFILE_PIC = os.path.join(CACHE_DIR_PFP, 'defualt.png')


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

async def update_xp_and_check_level_up(ctx, xp: int, add: bool = True) -> bool:

    # kind of unnecessary but reducdancy is always nice
    if type(xp) == float: 
        xp = int(xp)
    elif type(xp) == str:
        try:
            xp = int(xp)
        except:
            raise ValueError("argument \"xp\" must be an int, float, or a string that can be converted to an integer. \"xp\" *SHOULD* always be an int tho.")

    if type(add) != bool:
        raise ValueError("argument \"add\" must be a boolean.")

    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        try:
            cursor.execute("SELECT xp, money FROM users WHERE user_id = %s", (ctx.author.id,))
            database = cursor.fetchone()
        except:
            cursor.execute("SELECT xp, money FROM users WHERE user_id = %s", (ctx.user.id,))
            database = cursor.fetchone()

        current_xp_level = xpToLevel(database[0])
        
        if add == True:
            new_xp = database[0] + xp
        else:
            new_xp = database[0] - xp

        try:
            cursor.execute("UPDATE users SET xp = %s WHERE user_id = %s", (new_xp, ctx.author.id))
        except:
            cursor.execute("UPDATE users SET xp = %s WHERE user_id = %s", (new_xp, ctx.user.id))
        
        conn.commit()

    finally:
        cursor.close()
        conn.close()

    if current_xp_level < xpToLevel(new_xp):
        return True
    else:
        return False