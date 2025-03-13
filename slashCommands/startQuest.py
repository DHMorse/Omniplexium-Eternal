import discord
from discord import app_commands
from adventureStoryTime import StoryMaker

async def startQuestFunc(interaction: discord.Interaction) -> None:
    thread: discord.Thread = await interaction.channel.create_thread(
        name=f"Quest with {interaction.user.display_name}",
        type=discord.ChannelType.private_thread,
        invitable=False
    )
    await thread.add_user(interaction.user)
    await interaction.response.defer()
    hi: StoryMaker = StoryMaker()
    var: str = await hi.startStory('You are a bear looking at the eclipse.', 169)
    await thread.send(var)
    await interaction.followup.send("Quest started!", ephemeral=True)

slashCommandStartQuest: app_commands.Command = app_commands.Command(
    name="start-quest", # no spaces or capitals allowed
    description="Start a quest!",
    callback=startQuestFunc,
)