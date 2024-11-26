import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View

from const import ADMIN_LOG_CHANNEL_ID, pool, updateXpAndCheckLevelUp

async def fight(interaction: discord.Interaction):
    pass

class ChallengeView(View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=30)  # Set the timeout for the View
        self.member = member
        self.response = None  # To track the button pressed

    async def on_timeout(self):
        # Action when the timeout occurs
        for item in self.children:
            item.disabled = True
        await self.message.edit(content="Challenge timed out. No response received.", view=self)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.member:
            await interaction.response.send_message("Only the mentioned user can respond!", ephemeral=True)
            return
        self.response = "Accepted"
        self.stop()  # Stop listening for interactions
        await interaction.response.send_message(f"{self.member.mention} accepted the challenge!", ephemeral=False)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.member:
            await interaction.response.send_message("Only the mentioned user can respond!", ephemeral=True)
            return
        self.response = "Declined"
        self.stop()  # Stop listening for interactions
        await interaction.response.send_message(f"{self.member.mention} declined the challenge.", ephemeral=False)