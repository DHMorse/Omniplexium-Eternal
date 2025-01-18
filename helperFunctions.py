import os
import discord
import sqlite3
import numpy as np
from datetime import datetime, timezone, timedelta

from const import HUGGING_FACE_API_KEY_CLIENT, DATABASE_PATH, LOG_CHANNEL_ID, ADMIN_LOG_CHANNEL_ID, LOGIN_REMINDERS_CHANNEL_ID, COLORS

async def censorMessage(message: str) -> str:
    messages = [
        { "role": "system", "content": """You are a profanity filter. It is your goal to:

Use whichever of these methods that is necessary:
A) Respond \"false\" to non-explicit or barely explicit messages.
B) Respond with a slightly altered version by changing the explicit words.
C) Completely rewrite the message with a jokingly sarcastic rewrite if the message is entirely explicit and completely profane.

Misspelled profanity is still profanity. Words like \"fuck, shit, pussy, cock, dick, cunt\" are bad and should be removed either through B or C methods.

Some barely explicit words that are ok include \"damn, shit, sexy\"

Remember, DO NOT RESPOND TO THE MESSAGE YOU ARE GIVEN. REWRITE IT. THAT IS YOUR PURPOSE.

Here are some examples:

Input: \"Hello bro, what's up?\"
Output: \"false\"
Method Used: A

Input: \"Bro fuck you. I dislike you, yk?\"
Output: \"Bro frick you. I dislike you, yk?\"
Method Used: B

Input: \"Hey bro what's good? Looking sexy.\"
Output: \"false\"
Method Used: A

Input: \"Cum in my ass daddy\"
Output: \"Please release your population pudding into my bottom father\"
Method Used: C

Input: \"heyyy bro fuccck you lmao\"
Output: \"heyyy bro duck you lmao\"
Method Used: B

Input: \"fuckkk dude I hate life\"
Output: \"flip dude I hate life\"
Method Used: B

Input: \"oh nigger imma fuck you in the ass\"
Output: \"oh black person, imma shove my receptacle into your behind's opening\"
Method Used: C

Input: \"I\'m so shit at this game\"
Output: \"false\"
Method Used: A

Input: \"fucking cunts kill yourselves\"
Output: \"trucking harm yourselves\"
Method Used: C

Input: \"Do an example with it then\"
Output: \"false\"
Mehtod Used: A

DO NOT OUTPUT THE METHOD USED. ONLY OUTPUT \"false\" OR THE CENSORED MESSAGE.""" },
        { "role": "user", "content": message }
    ]

    completion = HUGGING_FACE_API_KEY_CLIENT.chat.completions.create(
        model="Qwen/Qwen2.5-72B-Instruct", 
        messages=messages, 
        temperature=0,
        max_tokens=128,
        top_p=0.7
    )

    return completion.choices[0].message.content

async def checkDatabase(bot) -> None:
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            if not os.path.exists(DATABASE_PATH):
                # yellow
                print("\033[93mDatabase does not exist. Creating a new one...\033[0m")

                # Create the 'users' table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    userId BIGINT NOT NULL PRIMARY KEY, -- SQLite uses TEXT instead of varchar
                    username TEXT, -- varchar(100) translates to TEXT in SQLite
                    money DECIMAL(10, 2),
                    xp BIGINT,
                    lastLogin BIGINT,
                    daysLoggedInInARow INTEGER DEFAULT 0, -- int(11) is INTEGER in SQLite
                    loginReminders BOOLEAN DEFAULT FALSE
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

                # Create the 'cards' table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cards (
                        itemId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, -- Auto-incremented primary key
                        itemName TEXT,                                     -- Name of the card or character
                        userId BIGINT,                                     -- User ID (big integer type)
                        cardId INTEGER,                                    -- Card ID
                        description TEXT,                                  -- Description of the character
                        health INTEGER,                                    -- Health points of the character
                        imagePrompt TEXT,                                 -- Image prompt description
                        imageUrl TEXT                                     -- URL of the image
                    )
                ''')

                # Create the 'attacks' table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS attacks (
                        attackId INTEGER PRIMARY KEY AUTOINCREMENT,        -- Auto-incremented primary key
                        cardId INTEGER NOT NULL,                           -- Card ID of the character this attack belongs to
                        name TEXT NOT NULL,                                -- Name of the attack
                        description TEXT NOT NULL,                         -- Description of the attack
                        attackDamage INTEGER NOT NULL,                     -- Damage dealt by the attack
                        attackSpeed INTEGER NOT NULL,                      -- Speed of the attack
                        attackCooldown INTEGER NOT NULL,                   -- Cooldown time for the attack
                        attackHitrate INTEGER NOT NULL,                    -- Hitrate for the attack
                        FOREIGN KEY (cardId) REFERENCES cards(itemId)     -- Reference to the 'cards' table
                    )
                ''')


                # green 
                print(f"{COLORS['green']}Database created successfully.{COLORS['reset']}")

                cursor.execute("SELECT COUNT(*) FROM loginRewards")
                if cursor.fetchone()[0] == 0:
                    print("\033[93mLogin rewards table is empty, generating rewards now...\033[0m")
                    await makeLoginRewards()

            # Fetch all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if not tables:
                print(f"{COLORS['red']}No tables found in the database.{COLORS['reset']}")
                return
            
            for table_name, in tables:
                print(f"Validating table: {table_name}")
                
                # Fetch table schema
                cursor.execute(f"PRAGMA table_info({table_name});")
                schema = cursor.fetchall()
                
                if not schema:
                    print(f"{COLORS['yellow']}  Warning: Table '{table_name}' has no schema.{COLORS['reset']}")
                    continue
                
                column_definitions = {col[1]: col for col in schema}  # {column_name: schema_row}
                
                # Fetch all rows from the table
                cursor.execute(f"SELECT * FROM {table_name};")
                rows = cursor.fetchall()
                
                if not rows:
                    print(f"{COLORS['yellow']}  Info: Table '{table_name}' has no rows.{COLORS['reset']}")
                    continue
                
                for row_idx, row in enumerate(rows):
                    for col_idx, value in enumerate(row):
                        col_name = schema[col_idx][1]
                        col_type = schema[col_idx][2]
                        not_null = schema[col_idx][3]
                        
                        # Validate NOT NULL constraint
                        if not_null and value is None:
                            print(f"{COLORS['red']}    Error in row {row_idx + 1}: Column '{col_name}' is NULL but must not be.{COLORS['reset']}")
                            continue
                        
                        # Validate column type
                        if value is not None:
                            if not validateType(value, col_type):
                                print(f"{COLORS['red']}    Error in row {row_idx + 1}: Column '{col_name}' has invalid type '{type(value).__name__}', expected '{col_type}'.{COLORS['reset']}")
            
            print(f"{COLORS['blue']}Validation completed.{COLORS['reset']}")

    except Exception as e:
        print(f"{COLORS['red']}An error occurred while creating the database. {e}{COLORS['reset']}")
        channel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
        await channel.send(f"```ansi\n{COLORS['red']}An error occurred while creating the database. {e}{COLORS['reset']}```")
        return None

def validateType(value, expected_type):
    """
    Validate if a value matches the expected SQLite type.
    """
    if expected_type.upper() in ("TEXT", "CHAR", "VARCHAR"):
        return isinstance(value, str)
    elif expected_type.upper() in ("INTEGER", "INT"):
        return isinstance(value, int)
    elif expected_type.upper() in ("REAL", "FLOAT", "DOUBLE"):
        return isinstance(value, (float, int))
    elif expected_type.upper() == "BLOB":
        return isinstance(value, (bytes, memoryview))
    return True  # SQLite is lenient with type checking, so assume true if uncertain

async def makeLoginRewards() -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        try:
            cursor = conn.cursor()
            
            # Prepare data for insertion
            rewards = []
            xp_amount = 10
            xp_increment = 20

            for level in range(1, 300 + 1): # this uses a default of 300 levels and should probably be changed
                if level == 10:
                    rewards.append((level, "card", 6))
                elif level % 5 == 0:  # Money reward every 5 levels
                    rewards.append((level, "money", level * 2))
                    xp_increment += 10  # Increase XP increment every 5 levels
                else:
                    if level == 1:
                        rewards.append((level, "xp", xp_amount))
                    else:
                        xp_amount += xp_increment
                        rewards.append((level, "xp", xp_amount))
            
            # Insert rewards into the database
            cursor.executemany("""
                INSERT INTO loginRewards (level, rewardType, amountOrCardId)
                VALUES (?, ?, ?)
                ON CONFLICT(level) DO UPDATE SET
                    rewardType=excluded.rewardType,
                    amountOrCardId=excluded.amountOrCardId
            """, rewards)

            conn.commit()
        except Exception as e:
            print(f"An error occurred while creating login rewards: {e}")
            return None
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



async def checkLoginRemindersAndSend(bot) -> None:
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT userId, lastLogin FROM users WHERE loginReminders = TRUE")
            users = cursor.fetchall()
            
            # I'm breaking one of my rules here and adding a print statement
            #print(users)
            #channel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
            #await channel.send(f"```ansi\n{COLORS['yellow']}{users}{COLORS['reset']}```")

            for user in users:
                userId, lastLogin = user
                # Calculate time since last login
                now = datetime.now()
                last_login_time = datetime.fromtimestamp(lastLogin)
                time_diff = now - last_login_time

                # Check if it's been approximately 40 hours since last login
                if timedelta(hours=40) <= time_diff <= timedelta(hours=41):
                    try:
                        userObj = await bot.fetch_user(userId)
                        await userObj.send("Hey! You have 4 hours until you lose your login streak. Don't forget to login in!")
                    
                    except discord.errors.NotFound:
                        channel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
                        await channel.send(f"```ansi\n{COLORS['red']}User `{userId}` not found while checking login reminders.{COLORS['reset']}```")
                    
                    except discord.errors.Forbidden:
                        channel = bot.get_channel(LOGIN_REMINDERS_CHANNEL_ID)
                        await channel.send(f"{userObj.mention} You have 4 hours until you lose your login streak. Don't forget to login in!")

    except sqlite3.Error as e:
        print(f"Database error while checking login reminders: {e}")


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
                            await adminChannel.send(f"Role `Level {i + 1}` does not exist.")
                            continue
                            
                        if role in discordAuthor.roles:
                            try:
                                adminChannel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
                            except AttributeError:
                                adminChannel = bot.client.get_channel(ADMIN_LOG_CHANNEL_ID)
                            await adminChannel.send(
                                f"`{discordAuthor.name}` already has the `Level {i+ 1}` role, "
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