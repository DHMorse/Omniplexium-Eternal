import discord
from discord.ui import Button, View
from discord.ui import View, Button
from discord import Interaction, Thread, ButtonStyle, app_commands

from const import ADMIN_LOG_CHANNEL_ID, pool, updateXpAndCheckLevelUp

class CardView(View):
    def __init__(self, member_id, pool):
        super().__init__(timeout=None)
        self.member_id = member_id
        self.pool = pool

    @discord.ui.button(label="View Your Cards", style=ButtonStyle.primary)
    async def view_cards(self, interaction: Interaction, button: Button):
        conn = self.pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT itemName FROM cards WHERE userId = %s", (self.member_id,))
            cards = cursor.fetchall()

            if not cards:
                await interaction.response.send_message("You have no cards.", ephemeral=True)
            else:
                card_names = ""
                for i in range(len(cards)):
                    card_names += f'{i + 1}. {cards[i]['itemName']} \n'
                await interaction.response.send_message(f"Your cards:\n{card_names}", ephemeral=True)

        finally:
            cursor.close()
            conn.close()

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
        print('fight was here first timeout')

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.member:
            await interaction.response.send_message("Only the mentioned user can respond!", ephemeral=True)
            return
        self.response = "Accepted"
        self.stop()  # Stop listening for interactions
        await interaction.response.send_message(f"{self.member.mention} accepted the challenge!", ephemeral=False)
        print('fight was here first accepted')

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.member:
            await interaction.response.send_message("Only the mentioned user can respond!", ephemeral=True)
            return
        self.response = "Declined"
        self.stop()  # Stop listening for interactions
        await interaction.response.send_message(f"{self.member.mention} declined the challenge.", ephemeral=False)
        print('fight was here first declined')