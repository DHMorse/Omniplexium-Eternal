import discord
from discord import app_commands

async def guess_the_number(interaction: discord.Interaction, player: discord.Member):
    await interaction.response.send_message(f"Guess a number between 1 and 100.")

guess_the_number_command = app_commands.Command(
    name="guess_the_number",
    description="Guess a number between 1 and 100.",
    callback=guess_the_number,
)