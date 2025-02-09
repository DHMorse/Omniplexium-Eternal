import discord
from discord import app_commands

from const import SERVER_ID, CREDITS_CHANNEL_ID

async def challengeFunc(interaction: discord.Interaction, member: discord.Member) -> None:
    class DuelButtons(discord.ui.View):
        def __init__(self, challenger: discord.Member, target: discord.Member):
            super().__init__(timeout=60)
            self.challenger = challenger
            self.target = target

        @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
        async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != self.target.id:
                await interaction.response.send_message("Only the challenged player can accept!", ephemeral=True)
                return
            await interaction.response.send_message(f"Duel accepted! {self.challenger.name} vs {self.target.name}")
            self.stop()

        @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
        async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != self.target.id:
                await interaction.response.send_message("Only the challenged player can decline!", ephemeral=True)
                return
            await interaction.response.send_message(f"{self.target.name} declined the duel!")
            self.stop()

    if member == interaction.user:
        await interaction.response.send_message("You can't challenge yourself!", ephemeral=True)
        return

    view = DuelButtons(interaction.user, member)
    await interaction.response.send_message(f"{member.mention}, you've been challenged to a Pokemon battle by {interaction.user.name}!", view=view)

slashCommandChallenge = app_commands.Command(
    name="challenge", # no spaces or capitals allowed
    description="Challenge another player to a pokemon type battle!",
    callback=challengeFunc,
)