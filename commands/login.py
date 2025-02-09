from discord.ext import commands
import sqlite3
import time

from const import DATABASE_PATH
from helperFunctions.main import updateXpAndCheckLevelUp, copyCard

@commands.command()
async def login(ctx, day: float = None) -> None:
    if not ctx.author.guild_permissions.administrator:
        day = 0

    if day is not None:
        # everything is a string
        float(day)

    if day is None:
        day = 0

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT lastLogin, daysLoggedInInARow FROM users WHERE userId = ?", (ctx.author.id,))
        result = cursor.fetchone()
        
        if result is not None:
            lastLogin = result[0]
            daysLoggedInInARow = result[1]
        else:
            lastLogin = None
            daysLoggedInInARow = 0
        
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
        result = cursor.fetchone()
        daysLoggedInInARow = result[0]

        cursor.execute("SELECT rewardType, amountOrCardId FROM loginRewards WHERE level = ?", (daysLoggedInInARow,))
        result = cursor.fetchone()
        type, amount = result

        match type:
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
                cardName = cursor.fetchone()[0]
                
                await ctx.send(f"Congratulations! You have received {cardName} for logging in {daysLoggedInInARow} days in a row!")
