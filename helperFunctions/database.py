import os
import sqlite3
import traceback

from const import DATABASE_PATH, COLORS

from helperFunctions.main import logError, logWarning

async def createUsersTable(bot) -> None:
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()

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
    
    except Exception as e:
        await logError(bot, e, traceback.format_exc(), "createUsersTable")
        return None
    
    return None

async def createLoginRewardsTable(bot) -> None:
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS loginRewards (
                level INTEGER NOT NULL PRIMARY KEY, -- int(11) is INTEGER in SQLite
                rewardType TEXT NOT NULL, -- varchar(10) translates to TEXT
                amountOrCardId INTEGER NOT NULL -- int(11) is INTEGER in SQLite
            )
            ''')
    
    except Exception as e:
        await logError(bot, e, traceback.format_exc(), "createLoginRewardsTable")
        return None
    
    return None

async def createCardTables(bot) -> None:
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
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
                    imagePath TEXT                                    -- Path to the image
                )
            ''')

    except Exception as e:
        await logError(bot, e, traceback.format_exc(), "createCardTables")
        return None
    
    return None

async def createAttacksTable(bot) -> None:
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attacks (
                    attackId INTEGER PRIMARY KEY AUTOINCREMENT,        -- Auto-incremented primary key
                    cardId INTEGER NOT NULL,                           -- Card ID of the character this attack belongs to
                    attackName TEXT NOT NULL,                                -- Name of the attack
                    attackDescription TEXT NOT NULL,                         -- Description of the attack
                    attackDamage INTEGER NOT NULL,                     -- Damage dealt by the attack
                    attackSpeed INTEGER NOT NULL,                      -- Speed of the attack
                    attackCooldown INTEGER NOT NULL,                   -- Cooldown time for the attack
                    attackHitrate INTEGER NOT NULL,                    -- Hitrate for the attack
                    FOREIGN KEY (cardId) REFERENCES cards(itemId)     -- Reference to the 'cards' table
                )
            ''')

    except Exception as e:
        await logError(bot, e, traceback.format_exc(), "createAttacksTable")
        return None
    
    return None

async def makeLoginRewardsTable(bot) -> None:
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
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
        await logError(bot, e, traceback.format_exc(), "makeLoginRewardsTable")
        return None

    return None

async def createAllTables(bot) -> None:
    await createUsersTable(bot)
    await createLoginRewardsTable(bot)
    await createCardTables(bot)
    await createAttacksTable(bot)
    await makeLoginRewardsTable(bot)

async def checkDatabase(bot) -> None:
    try:
        if not os.path.exists(DATABASE_PATH):
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()
                print(f"{COLORS['red']}Database does not exist. Creating a new one...{COLORS['reset']}")
                await logError(bot, None, None, "Database does not exist. Creating a new one...")

                await createAllTables(bot)

                print(f"{COLORS['blue']}Database created successfully.{COLORS['reset']}")

    except Exception as e:
        print(f"{COLORS['red']}An error occurred while creating the database. {e}{COLORS['reset']}")
        await logError(bot, e, traceback.format_exc(), "An error occurred while creating the database.")
        return None
    
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            # Fetch all table names
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if not tables:
                print(f"{COLORS['red']}No tables found in the database.{COLORS['reset']}")
                await logError(bot, None, None, "No tables found in the database.")
                await createAllTables(bot)
            
            for table_name, in tables:
                print(f"Validating table: {table_name}")
                
                # Fetch table schema
                cursor.execute(f"PRAGMA table_info({table_name});")
                schema = cursor.fetchall()
                
                if not schema:
                    print(f"{COLORS['yellow']}  Warning: Table '{table_name}' has no schema.{COLORS['reset']}")
                    await logWarning(bot, f"Table '{table_name}' has no schema.")
                    continue
                
                column_definitions = {col[1]: col for col in schema}  # {column_name: schema_row}
                
                # Fetch all rows from the table
                cursor.execute(f"SELECT * FROM {table_name};")
                rows = cursor.fetchall()
                
                if not rows:
                    if table_name == 'loginRewards':
                        print(f"{COLORS['yellow']}  Warning: Table '{table_name}' is empty. Generating login rewards...{COLORS['reset']}")
                        await logWarning(bot, f"Table '{table_name}' is empty. Generating login rewards...")
                        await makeLoginRewardsTable(bot)
                        return await checkDatabase(bot)
                    else:
                        print(f"{COLORS['yellow']}  Info: Table '{table_name}' has no rows.{COLORS['reset']}")
                        await logWarning(bot, f"Table '{table_name}' has no rows.")
                    continue
                
                for row_idx, row in enumerate(rows):
                    for col_idx, value in enumerate(row):
                        col_name = schema[col_idx][1]
                        col_type = schema[col_idx][2]
                        not_null = schema[col_idx][3]
                        
                        # Validate NOT NULL constraint
                        if not_null and value is None:
                            print(f"{COLORS['red']}    Error in row {row_idx + 1}: Column '{col_name}' is NULL but must not be.{COLORS['reset']}")
                            await logError(bot, None, None, f"Error in row {row_idx + 1}: Column '{col_name}' is NULL but must not be.")
                            continue
                        
                        # Validate column type
                        if value is not None:
                            if not validateType(value, col_type):
                                print(f"{COLORS['red']}    Error in row {row_idx + 1}: Column '{col_name}' has invalid type '{type(value).__name__}', expected '{col_type}'.{COLORS['reset']}")
                                await logError(bot, None, None, f"Error in row {row_idx + 1}: Column '{col_name}' has invalid type '{type(value).__name__}', expected '{col_type}'.")

            print(f"{COLORS['blue']}Validation completed.{COLORS['reset']}")

    except sqlite3.Error as e:
        print(f"{COLORS['red']}Error while validating database: {e}{COLORS['reset']}")
        await logError(bot, e, traceback.format_exc(), "Error while validating database.")


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
