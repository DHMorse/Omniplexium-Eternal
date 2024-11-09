import discord
from discord import app_commands
import random

from main import update_xp_and_check_level_up

async def guess_the_number(interaction: discord.Interaction, guess: int):
    number = random.randint(1, 100)
    await interaction.response.send_message(f"Guess a number between 1 and 100.")
    if guess == number:
        await update_xp_and_check_level_up(ctx=interaction, xp=25, add=True)
        await interaction.response.send_message(f"Congratulations! You guessed the number correctly. `+25 XP`")
    elif abs(guess - number) <= 25:
        await update_xp_and_check_level_up(ctx=interaction, xp=10, add=True)
        await interaction.response.send_message(f"Close! The number was {number}. `+10 XP`")
    else:
        await update_xp_and_check_level_up(ctx=interaction, xp=5, add=False)
        await interaction.response.send_message(f"Sorry! The number was {number}. `-5 XP`")

guess_the_number_command = app_commands.Command(
    name="guess_the_number",
    description="Guess a number between 1 and 100.",
    callback=guess_the_number,
)