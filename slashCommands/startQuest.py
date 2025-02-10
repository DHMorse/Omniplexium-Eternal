import discord
from discord import app_commands

from adventureStoryTime import *

async def startQuestFunc(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(hi.startStory('You are a bear looking at the eclipse.', 169))

slashCommandStartQuest = app_commands.Command(
    name="start-quest", # no spaces or capitals allowed
    description="Start a quest!",
    callback=startQuestFunc,
)