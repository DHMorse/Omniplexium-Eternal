import discord
from discord import app_commands
from discord.ext import commands

class ChallengeView(discord.ui.View):
    def __init__(self, challenger, challenged):
        super().__init__(timeout=60)  # Timeout for the buttons (in seconds)
        self.challenger = challenger
        self.challenged = challenged

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.challenged.id:
            await interaction.response.send_message(
                "You can't accept the challenge for someone else!", ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"{self.challenged.mention} has accepted the challenge from {self.challenger.mention}!",
            ephemeral=False
        )
        self.stop()  # Stops the view and disables buttons

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.challenged.id:
            await interaction.response.send_message(
                "You can't decline the challenge for someone else!", ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"{self.challenged.mention} has declined the challenge from {self.challenger.mention}.",
            ephemeral=False
        )
        self.stop()  # Stops the view and disables buttons