import discord
from discord import app_commands
import asyncio
from adventureStoryTime import *

async def startQuestFunc(interaction: discord.Interaction) -> None:
    await interaction.response.defer()
    hi = StoryMaker()
    var = await hi.startStory('You are a bear looking at the eclipse.', 169)
    await interaction.followup.send(var)

slashCommandStartQuest = app_commands.Command(
    name="start-quest", # no spaces or capitals allowed
    description="Start a quest!",
    callback=startQuestFunc,
)