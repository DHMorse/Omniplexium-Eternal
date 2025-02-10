import discord
from discord import app_commands
import asyncio
from adventureStoryTime import *

async def startQuestFunc(interaction: discord.Interaction) -> None:
    hi = StoryMaker()
    await interaction.response.send_message(asyncio.run(hi.startStory('You are a bear looking at the eclipse.', 169)))

slashCommandStartQuest = app_commands.Command(
    name="start-quest", # no spaces or capitals allowed
    description="Start a quest!",
    callback=startQuestFunc,
)