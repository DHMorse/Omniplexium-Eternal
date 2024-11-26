import discord
from discord.ui import Button, View
from discord.ui import View, Button
from discord import Interaction, Thread, ButtonStyle, app_commands

from const import ADMIN_LOG_CHANNEL_ID, pool, updateXpAndCheckLevelUp

class CardView(View):
    def __init__(self, pool):
        super().__init__(timeout=None)
        self.pool = pool
        self.locked_in_users = {}  # Track locked-in users and their selected cards

    @discord.ui.button(label="View Your Cards", style=ButtonStyle.primary)
    async def view_cards(self, interaction: Interaction, button: Button):
        user_id = interaction.user.id
        conn = self.pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT itemName FROM cards WHERE userId = %s", (user_id,))
            cards = cursor.fetchall()

            if not cards:
                await interaction.response.send_message("You have no cards.", ephemeral=True)
            else:
                card_names = "\n".join(f'{i + 1}. {card["itemName"]}' for i, card in enumerate(cards))
                await interaction.response.send_message(
                    f"Your cards:\n{card_names}\n\nReply with the numbers of 3 cards separated by commas (e.g., `1,2,3`) to choose them for the battle.",
                    ephemeral=True
                )

        finally:
            cursor.close()
            conn.close()

    async def handle_card_selection(self, message: discord.Message):
        user_id = message.author.id

        # Validate message format
        try:
            selected_indices = [int(x.strip()) for x in message.content.split(",")]
            if len(selected_indices) != 3 or len(set(selected_indices)) != 3:
                raise ValueError("Invalid format or duplicate numbers")

            # Check if selected indices are within the range of the user's cards
            conn = self.pool.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) AS card_count FROM cards WHERE userId = %s", (user_id,))
            card_count = cursor.fetchone()["card_count"]

            if not all(1 <= idx <= card_count for idx in selected_indices):
                raise ValueError("Numbers out of range")

            # Lock in the user's cards
            self.locked_in_users[user_id] = selected_indices
            await message.channel.send(
                content=f"{message.author.mention} has locked in their cards!",
                ephemeral=False
            )

            # Check if both players have locked in
            if len(self.locked_in_users) == 2:
                await message.channel.send("Both players have locked in their cards. Let the battle begin!", ephemeral=False)
                # Proceed to battle logic here...

        except ValueError as e:
            await message.channel.send(
                f"{message.author.mention} Invalid selection. Please reply with 3 unique card numbers separated by commas (e.g., `1,2,3`).",
                ephemeral=True
            )



class ChallengeView(View):
    def __init__(self, member: discord.Member, message=None):
        super().__init__(timeout=30)  # Set the timeout for the View
        self.member = member
        self.message = message  # Store the message object
        self.response = None  # To track the button pressed

    async def on_timeout(self):
        # Action when the timeout occurs
        if self.message:  # Check if the message is set
            for item in self.children:
                item.disabled = True  # Disable buttons
            await self.message.edit(content="Challenge timed out. No response received.", view=self)
        else:
            print("No message to edit on timeout.")  # Debug message

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