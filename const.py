import os
import numpy as np
import discord
from datetime import datetime, timezone
import sqlite3

COLORS = {
    'red': '\u001b[1;31m',
    'yellow': '\u001b[1;33m',
    'blue': '\u001b[1;34m',
    'reset': '\u001b[0m'
}

LOG_CHANNEL_ID = 1304829859549155328

ADMIN_LOG_CHANNEL_ID = 1304245019300986941

ROOT_DIR = os.path.expanduser('~/Omniplexium-Eternal')

DATABASE_PATH = os.path.join(ROOT_DIR, 'discorddb.db')

CURRENT_ITEM_ID_PATH = os.path.join(ROOT_DIR, 'currentItemID.txt')

CACHE_DIR_PFP = os.path.join(ROOT_DIR, 'cacheDir', 'pfps')

LEADERBOARD_PIC = os.path.join(ROOT_DIR, 'leaderboard.png')

DEFUALT_PROFILE_PIC = os.path.join(CACHE_DIR_PFP, 'defualt.png')

CARD_DATA_PATH = os.path.join(ROOT_DIR, 'cardData')

CARD_DATA_IMAGES_PATH = os.path.join(CARD_DATA_PATH, 'images')

CARD_DATA_JSON_PATH = os.path.join(CARD_DATA_PATH, 'json')

def checkDatabase() -> None:
    try:
        if not os.path.exists(DATABASE_PATH):
            # yellow
            print("\033[93mDatabase does not exist. Creating a new one...\033[0m")
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()

                # Create the 'users' table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    userId BIGINT NOT NULL PRIMARY KEY, -- SQLite uses TEXT instead of varchar
                    username TEXT, -- varchar(100) translates to TEXT in SQLite
                    money DECIMAL(10, 2),
                    xp BIGINT,
                    lastLogin BIGINT,
                    daysLoggedInInARow INTEGER DEFAULT 0 -- int(11) is INTEGER in SQLite
                )
                ''')

                # Create the 'loginRewards' table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS loginRewards (
                    level INTEGER NOT NULL PRIMARY KEY, -- int(11) is INTEGER in SQLite
                    rewardType TEXT NOT NULL, -- varchar(10) translates to TEXT
                    amountOrCardId INTEGER NOT NULL -- int(11) is INTEGER in SQLite
                )
                ''')

                # Create the 'items' table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS cards (
                    itemId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, -- auto_increment is AUTOINCREMENT in SQLite
                    itemName TEXT,
                    userId BIGINT,
                    cardId INTEGER
                )
                ''')

                # green 
                print("\033[92mDatabase created successfully.\033[0m")

    except Exception as e:
        # red
        print("\033[91mAn error occurred while creating the database.\033[0m")
        return None

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



def levelToXp(level: int) -> int:
    # Constants
    TOTAL_LEVELS = 100
    XP_LEVEL_10 = 100
    XP_LEVEL_100 = 10e12  # 1 trillion

    # Calculate the exponential growth factor
    base = (XP_LEVEL_100 / XP_LEVEL_10) ** (1 / (TOTAL_LEVELS - 10))
    
    if level <= 10:
        # XP grows linearly for levels <= 10
        return level * 10
    elif level >= TOTAL_LEVELS:
        # XP caps at XP_LEVEL_100 for level 100
        return int(XP_LEVEL_100)

    # Calculate XP required for the level
    xp = XP_LEVEL_10 * (base ** (level - 10))
    return int(xp)



async def updateXpAndCheckLevelUp(ctx, bot, xp: int, add: bool = True) -> None:
    # Input validation
    if isinstance(xp, float):
        xp = int(xp)
    elif isinstance(xp, str):
        try:
            xp = int(xp)
        except ValueError:
            raise ValueError("argument 'xp' must be an int, float, or a string that can be converted to an integer.")
    
    if not isinstance(add, bool):
        raise ValueError("argument 'add' must be a boolean.")

    # Get discord author
    try:
        discordAuthor = ctx.author
    except AttributeError:
        discordAuthor = ctx.user

    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Get current XP
            cursor.execute("SELECT xp FROM users WHERE userId = ?", (discordAuthor.id,))
            database = cursor.fetchone()
            
            if not database:
                raise ValueError(f"User {discordAuthor.id} not found in database")
                
            current_xp = database[0]
            current_level = xpToLevel(current_xp)
            
            # Update XP based on add flag
            new_xp = current_xp + xp if add else current_xp - xp
            cursor.execute("UPDATE users SET xp = ? WHERE userId = ?", (new_xp, discordAuthor.id))
            conn.commit()
            
            # Calculate new level after XP update
            newLevel = xpToLevel(new_xp)
            
            levelUp = current_level < newLevel
            levelDown = current_level > newLevel
            
            if levelUp or levelDown:
                # Get the appropriate channel
                try:
                    channel = bot.get_channel(LOG_CHANNEL_ID)
                except AttributeError:
                    channel = bot.client.get_channel(LOG_CHANNEL_ID)
                
                # Determine if we should mention the user
                doMention = (newLevel == 1 or newLevel > 9) if levelUp else True
                
                # Handle level up messages and role assignments
                if levelUp:
                    for i in range(current_level, newLevel):
                        now = datetime.now(timezone.utc)
                        embed = discord.Embed(
                            title="Member Leveled Up",
                            description=f"**Member:** \n{discordAuthor}\n\n"
                                        f"**Account Level:** \n{i + 1}\n",
                            color=discord.Color.green(),
                            timestamp=now
                        )
                        embed.set_thumbnail(url=discordAuthor.display_avatar.url)
                        
                        await channel.send(
                            discordAuthor.mention if doMention else '', 
                            embed=embed
                        )
                        
                        # Handle role assignment
                        role = discord.utils.get(ctx.guild.roles, name=f"Level {i + 1}")
                        if role is None:
                            try:
                                adminChannel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
                            except AttributeError:
                                adminChannel = bot.client.get_channel(ADMIN_LOG_CHANNEL_ID)
                            await adminChannel.send(f"Role 'Level {i + 1}' does not exist.")
                            continue
                            
                        if role in discordAuthor.roles:
                            try:
                                adminChannel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
                            except AttributeError:
                                adminChannel = bot.client.get_channel(ADMIN_LOG_CHANNEL_ID)
                            await adminChannel.send(
                                f"{discordAuthor.name} already has the 'Level {i+ 1}' role, "
                                "but we tried to give it to them again."
                            )
                            continue
                            
                        await discordAuthor.add_roles(role)
                        
    except sqlite3.Error as e:
        print(f"Database error in updateXpAndCheckLevelUp: {e}")
    except Exception as e:
        print(f"Error in updateXpAndCheckLevelUp: {e}")


def copyCard(cardId: int, userId: int) -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT itemName FROM cards WHERE itemId = ?", (cardId,))
        cardName = cursor.fetchone()[0]

        if cardName is None:
            raise ValueError(f"Card with ID {cardId} does not exist.")

        cursor.execute("INSERT INTO cards (itemName, userId, cardId) VALUES (?, ?, ?)", (cardName, userId, cardId)) # card name is a tuple
        conn.commit()

        # get the current max itemId
        cursor.execute("SELECT MAX(itemId) FROM cards")
        maxItemId = cursor.fetchone()[0]

    return None