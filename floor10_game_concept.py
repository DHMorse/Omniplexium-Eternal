import discord
from discord import app_commands
import random
import sqlite3

from const import ADMIN_LOG_CHANNEL_ID, DATABASE_PATH, COLORS
from helperFunctions import updateXpAndCheckLevelUp

async def guess_the_number(interaction: discord.Interaction, guess: app_commands.Range[int, 1, 10]):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        role = discord.utils.get(interaction.guild.roles, name='Level 10')

        if role is None:
            channel = interaction.client.get_channel(ADMIN_LOG_CHANNEL_ID)
            await channel.send(f"{COLORS['red']}Role 'Level 10' does not exist.{COLORS['reset']}")
            cursor.close()
            conn.close()
            return

        if role not in interaction.user.roles:
            await interaction.response.send_message(f"{COLORS['yellow']}You must be at least level 10 to play this game.{COLORS['reset']}")
            cursor.close()
            conn.close()
            return

        # Check if user exists in the database
        number: int = random.randint(1, 10)
        

        if guess == number:
            await updateXpAndCheckLevelUp(ctx=interaction, bot=interaction, xp=25, add=True)
            await interaction.response.send_message(f"Your guess of {guess} is right, Congratulations!`+25 XP`")

        elif abs(guess - number) <= 2:
            await updateXpAndCheckLevelUp(ctx=interaction, bot=interaction, xp=10, add=True)
            await interaction.response.send_message(f"Your guess of {guess} is close! The number was {number}. `+10 XP`")

        else:
            await updateXpAndCheckLevelUp(ctx=interaction, bot=interaction, xp=5, add=False)
            await interaction.response.send_message(f"Your guess of {guess} is wrong, Sorry! The number was {number}. `-5 XP`")


guess_the_number_command = app_commands.Command(
    name="guess_the_number",
    description="Guess a number between 1 and 10.",
    callback=guess_the_number,
)