import discord
from discord import app_commands
from discord.ext import commands

class ChallengeView(discord.ui.View):
    def __init__(self, challenger, challenged, timeout_message):
        super().__init__(timeout=60)  # Timeout for the buttons (in seconds)
        self.challenger = challenger
        self.challenged = challenged
        self.timeout_message = timeout_message
        self.accepted = False

    async def on_timeout(self):
        if not self.accepted:
            for child in self.children:  # Disable buttons after timeout
                child.disabled = True
            await self.timeout_message.edit(content="The duel invite has timed out.", view=self)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.challenged.id:
            await interaction.response.send_message(
                "You can't accept the challenge for someone else!", ephemeral=True
            )
            return

        self.accepted = True
        for child in self.children:  # Disable buttons after acceptance
            child.disabled = True
        await interaction.response.edit_message(content=f"{self.challenged.mention} has accepted the duel!", view=self)

        # Create a thread for the duel
        thread_name = f"Duel: {self.challenger.name} vs {self.challenged.name}"
        thread = await interaction.channel.create_thread(name=thread_name, type=discord.ChannelType.public_thread)
        await thread.send(f"The duel between {self.challenger.mention} and {self.challenged.mention} has begun!")
        self.stop()  # Stops the view and disables buttons

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.challenged.id:
            await interaction.response.send_message(
                "You can't decline the challenge for someone else!", ephemeral=True
            )
            return

        for child in self.children:  # Disable buttons after declining
            child.disabled = True
        await interaction.response.edit_message(content=f"{self.challenged.mention} has declined the duel.", view=self)
        self.stop()  # Stops the view and disables buttons