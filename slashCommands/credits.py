import discord
from discord import app_commands

from const import SERVER_ID, CREDITS_CHANNEL_ID

async def credits(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(f'https://discord.com/channels/{SERVER_ID}/{CREDITS_CHANNEL_ID}')

slashCommandCredits = app_commands.Command(
    name="credits", # no spaces or capitals allowed
    description="Get the credits of who built this wonderful game!",
    callback=credits,
)