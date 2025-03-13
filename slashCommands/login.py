import discord
from discord import app_commands
import sqlite3
import time

from const import DATABASE_PATH
from helperFunctions.main import updateXpAndCheckLevelUp, copyCard

async def loginFunc(interaction: discord.Interaction) -> None:
    authorId: int = interaction.user.id

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor: sqlite3.Cursor = conn.cursor()

        cursor.execute("SELECT lastLogin, daysLoggedInInARow FROM users WHERE userId = ?", (authorId,))
        result: tuple[int, int] | None = cursor.fetchone()
        
        if result is not None:
            lastLogin: int = result[0]
            daysLoggedInInARow: int = result[1]
        else:
            lastLogin: int | None = None
            daysLoggedInInARow: int = 0
        
        if lastLogin is None:
            await interaction.response.send_message("You have made your first daily login!")
            cursor.execute("UPDATE users SET lastLogin = ? WHERE userId = ?", (time.time(), authorId))
            cursor.execute("UPDATE users SET daysLoggedInInARow = ? WHERE userId = ?", (1, authorId))
            conn.commit()
        else:
            if time.time() - lastLogin > 172800:
                await interaction.response.send_message("You have lost your daily login streak!")
                cursor.execute("UPDATE users SET daysLoggedInInARow = ? WHERE userId = ?", (1, authorId))
                cursor.execute("UPDATE users SET lastLogin = ? WHERE userId = ?", (time.time(), authorId))
                conn.commit()
            elif time.time() - lastLogin > 86400:
                await interaction.response.send_message("You have made your daily login!")
                cursor.execute("UPDATE users SET lastLogin = ? WHERE userId = ?", (time.time(), authorId))
                cursor.execute("UPDATE users SET daysLoggedInInARow = ? WHERE userId = ?", (daysLoggedInInARow + 1, interaction.author.id))
                conn.commit()
            else:
                await interaction.response.send_message("You have already logged in today!")
                return
        
        cursor.execute("SELECT daysLoggedInInARow FROM users WHERE userId = ?", (authorId,))
        result: tuple[int] | None = cursor.fetchone()
        daysLoggedInInARow: int = result[0]

        cursor.execute("SELECT rewardType, amountOrCardId FROM loginRewards WHERE level = ?", (daysLoggedInInARow,))
        result: tuple[str, int] | None = cursor.fetchone()
        type: str = result[0]
        amount: int = result[1]

        match type:
            case "xp":
                await updateXpAndCheckLevelUp(ctx=interaction, bot=interaction, xp=amount, add=True)
                await interaction.channel.send(f"Congratulations! You have received {amount} XP for logging in {daysLoggedInInARow} days in a row!")
            case "money":
                cursor.execute("UPDATE users SET money = money + ? WHERE userId = ?", (amount, authorId))
                conn.commit()
                await interaction.channel.send(f"Congratulations! You have received ${amount} for logging in {daysLoggedInInARow} days in a row!")
            case "card":
                copyCard(amount, authorId)
                
                cursor.execute("SELECT itemName FROM cards WHERE itemId = ?", (amount,))
                cardName: str = cursor.fetchone()[0]
                
                await interaction.channel.send(f"Congratulations! You have received {cardName} for logging in {daysLoggedInInARow} days in a row!")


slashCommandLogin: app_commands.Command = app_commands.Command(
    name="login",
    description="Complete your daily login.",
    callback=loginFunc,
)