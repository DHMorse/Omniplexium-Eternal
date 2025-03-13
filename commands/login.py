from discord.ext import commands
import discord
import sqlite3
import time

from const import DATABASE_PATH
from helperFunctions.main import updateXpAndCheckLevelUp, copyCard

@commands.command()
async def login(ctx: commands.Context, day: float | None = None) -> None:
    """
    Command to handle daily user logins and provide rewards based on login streak.
    
    Args:
        ctx: The command context
        day: Optional float to override the login day (admin only)
    
    Returns:
        None
    """
    if not ctx.author.guild_permissions.administrator:
        day: float = 0

    if day is not None:
        # everything is a string
        day = float(day)

    if day is None:
        day: float = 0

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor: sqlite3.Cursor = conn.cursor()

        cursor.execute("SELECT lastLogin, daysLoggedInInARow FROM users WHERE userId = ?", (ctx.author.id,))
        result: tuple[float, int] | None = cursor.fetchone()
        
        if result is not None:
            lastLogin: float | None = result[0]
            daysLoggedInInARow: int = result[1]
        else:
            lastLogin: float | None = None
            daysLoggedInInARow: int = 0
        
        if lastLogin is None:
            await ctx.send("You have made your first daily login!")
            cursor.execute("UPDATE users SET lastLogin = ? WHERE userId = ?", (time.time(), ctx.author.id))
            cursor.execute("UPDATE users SET daysLoggedInInARow = ? WHERE userId = ?", (1, ctx.author.id))
            conn.commit()
        else:
            if time.time() - lastLogin > 172800 or (day * 86400) > 172800:
                await ctx.send("You have lost your daily login streak!")
                cursor.execute("UPDATE users SET daysLoggedInInARow = ? WHERE userId = ?", (1, ctx.author.id))
                cursor.execute("UPDATE users SET lastLogin = ? WHERE userId = ?", (time.time(), ctx.author.id))
                conn.commit()
            elif time.time() - lastLogin > 86400 or (day * 86400) > 86400:
                await ctx.send("You have made your daily login!")
                cursor.execute("UPDATE users SET lastLogin = ? WHERE userId = ?", (time.time(), ctx.author.id))
                cursor.execute("UPDATE users SET daysLoggedInInARow = ? WHERE userId = ?", (daysLoggedInInARow + 1, ctx.author.id))
                conn.commit()
            else:
                await ctx.send("You have already logged in today!")
                return
        
        cursor.execute("SELECT daysLoggedInInARow FROM users WHERE userId = ?", (ctx.author.id,))
        result: tuple[int] | None = cursor.fetchone()
        daysLoggedInInARow: int = result[0]

        cursor.execute("SELECT rewardType, amountOrCardId FROM loginRewards WHERE level = ?", (daysLoggedInInARow,))
        result: tuple[str, int] | None = cursor.fetchone()
        if result is None:
            await ctx.send("No rewards for this login streak!")
            return
        rewardType: str = result[0]
        amount: int = result[1]

        match rewardType:
            case "xp":
                await updateXpAndCheckLevelUp(ctx=ctx, bot=ctx.bot, xp=amount, add=True)
                await ctx.send(f"Congratulations! You have received {amount} XP for logging in {daysLoggedInInARow} days in a row!")
            case "money":
                cursor.execute("UPDATE users SET money = money + ? WHERE userId = ?", (amount, ctx.author.id))
                conn.commit()
                await ctx.send(f"Congratulations! You have received ${amount} for logging in {daysLoggedInInARow} days in a row!")
            case "card":
                copyCard(amount, ctx.author.id)
                
                cursor.execute("SELECT itemName FROM cards WHERE itemId = ?", (amount,))
                cardName: str = cursor.fetchone()[0]
                
                await ctx.send(f"Congratulations! You have received {cardName} for logging in {daysLoggedInInARow} days in a row!")
