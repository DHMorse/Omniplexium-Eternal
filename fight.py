import discord
from discord import app_commands
from discord.ext import commands

class ChallengeView(discord.ui.View):
    def __init__(self, challenger, challenged, timeout_message=None):
        super().__init__(timeout=60)  # Set the timeout to 60 seconds
        self.challenger = challenger
        self.challenged = challenged
        self.timeout_message = timeout_message

    async def on_timeout(self):
        if self.timeout_message:
            try:
                await self.timeout_message.edit(content="The duel invite has timed out.", view=None)
            except discord.NotFound:
                print("The message was deleted before the timeout occurred.")
        else:
            print("Timeout message was not set.")

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.challenged.id:
            await interaction.response.send_message("You can't accept this challenge for someone else.", ephemeral=True)
            return

        # Stop the timeout
        self.stop()

        # Disable the buttons and confirm acceptance
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(content=f"{self.challenged.mention} accepted the duel!", view=self)

        # Create a thread for the duel
        thread = await interaction.channel.create_thread(
            name=f"Duel: {self.challenger.display_name} vs {self.challenged.display_name}",
            type=discord.ChannelType.private_thread if isinstance(interaction.channel, discord.TextChannel) else discord.ChannelType.public_thread,
        )
        await thread.send(f"The duel between {self.challenger.mention} and {self.challenged.mention} begins!")

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.challenged.id:
            await interaction.response.send_message("You can't decline this challenge for someone else.", ephemeral=True)
            return

        # Stop the timeout
        self.stop()

        # Disable the buttons and confirm decline
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(content=f"{self.challenged.mention} declined the duel.", view=self)
