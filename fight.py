import discord
from discord.ui import Button, View
from discord.ui import View, Button
from discord import Interaction, Thread, ButtonStyle, app_commands

from const import ADMIN_LOG_CHANNEL_ID, pool, updateXpAndCheckLevelUp

class CardView(View):
    def __init__(self, member_id, pool, valid_cards):
        super().__init__(timeout=None)
        self.member_id = member_id
        self.pool = pool
        self.valid_cards = valid_cards
        self.locked_in_cards = {}

    @discord.ui.button(label="View Your Cards", style=ButtonStyle.primary)
    async def view_cards(self, interaction: Interaction, button: Button):
        conn = self.pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT itemName FROM cards WHERE userId = %s", (interaction.user.id,))
            cards = cursor.fetchall()

            if not cards:
                await interaction.response.send_message("You have no cards.", ephemeral=True)
            else:
                card_names = ""
                self.valid_cards[interaction.user.id] = [card["itemName"] for card in cards]
                for i, card in enumerate(cards):
                    card_names += f"{i + 1}. {card['itemName']} \n"
                await interaction.response.send_message(
                    f"Your cards:\n{card_names}\n\nSend a message in this thread with the numbers of 3 cards to choose them for battle (e.g., `1 3 5`).",
                    ephemeral=True,
                )
        finally:
            cursor.close()
            conn.close()


    async def handle_message(self, message: discord.Message):
        user_id = message.author.id

        # Check if the user is allowed to select cards
        if user_id not in self.selected_cards or self.selected_cards[user_id]["locked_in"]:
            return

        # Validate the input
        try:
            selected_indices = list(map(int, message.content.split()))
            if len(selected_indices) != 3:
                raise ValueError("You must select exactly 3 cards.")

            card_count = len(self.selected_cards[user_id]["available_cards"])
            if any(index < 1 or index > card_count for index in selected_indices):
                raise ValueError("One or more selected numbers are out of range.")

            # Get the selected cards
            selected_cards = [
                self.selected_cards[user_id]["available_cards"][index - 1]["itemName"]
                for index in selected_indices
            ]

            # Mark the cards as locked in
            self.selected_cards[user_id]["locked_in"] = True
            await message.channel.send(
                f"{message.author.mention} has locked in their cards: {', '.join(selected_cards)}"
            )

        except ValueError as e:
            # Inform the user of the invalid format ephemerally
            await message.author.send(f"Invalid selection: {e}")

class ChallengeView(View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=30)  # Set the timeout for the View
        self.member = member
        self.response = None  # To track the button pressed
        self.message = None  # To store the message object

    async def on_timeout(self):
        # Action when the timeout occurs
        if self.message:
            for item in self.children:
                item.disabled = True
            await self.message.edit(content="Challenge timed out. No response received.", view=self)
            print("Challenge timed out.")
        else:
            print("No message object to edit on timeout.")

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.member:
            await interaction.response.send_message("Only the mentioned user can respond!", ephemeral=True)
            return
        self.response = "Accepted"
        self.stop()  # Stop listening for interactions
        await interaction.response.send_message(f"{self.member.mention} accepted the challenge!", ephemeral=False)
        print("Challenge accepted.")

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.member:
            await interaction.response.send_message("Only the mentioned user can respond!", ephemeral=True)
            return
        self.response = "Declined"
        self.stop()  # Stop listening for interactions
        await interaction.response.send_message(f"{self.member.mention} declined the challenge.", ephemeral=False)
        print("Challenge declined.")
