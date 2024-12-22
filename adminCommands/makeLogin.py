import sqlite3

from discord.ext import commands
from const import DATABASE_PATH

@commands.command()
async def makeloginrewards(ctx, numberOfLevels: int):
    if ctx.author.guild_permissions.administrator != True:
        await ctx.send("You do not have the required permissions to use this command.")
        return

    with sqlite3.connect(DATABASE_PATH) as conn:
        try:
            cursor = conn.cursor()
            
            # Prepare data for insertion
            rewards = []
            xp_amount = 10
            xp_increment = 20

            for level in range(1, numberOfLevels + 1):
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

            # Commit changes
            conn.commit()
            await ctx.send(f"Login rewards for {numberOfLevels} levels have been successfully created.")

        except Exception as e:
            # ANSI RED COLOR CODE: \033[91m
            await ctx.send(f"\033[91mAn error occurred: {e}\033[0m")
