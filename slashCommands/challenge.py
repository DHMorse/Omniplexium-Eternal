import discord
from discord import app_commands
import sqlite3
import random

from const import DATABASE_PATH

class DuelButtons(discord.ui.View):
    def __init__(self, challenger: discord.Member, target: discord.Member):
        super().__init__(timeout=60)
        self.challenger = challenger
        self.target = target
        self.message = None

    async def on_timeout(self):
        # Disable all buttons
        for button in self.children:
            button.disabled = True
        
        # Edit the original message to show timeout
        if self.message:
            await self.message.edit(
                content=f"Challenge timed out! {self.target.name} didn't respond in time.",
                view=self
            )

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message(
                "Only the challenged player can accept!",
                ephemeral=True
            )
            return

        # Create a new thread for the battle
        thread = await interaction.channel.create_thread(
            name=f"Battle: {self.challenger.name} vs {self.target.name}",
            type=discord.ChannelType.public_thread,
            auto_archive_duration=60
        )

        # Disable the buttons
        for button in self.children:
            button.disabled = True
        await self.message.edit(view=self)

        # Send confirmation messages
        await interaction.response.send_message(
            f"Duel accepted! Moving to thread {thread.mention}"
        )
        
        # Send initial message in the thread
        await thread.send(
            f"Battle thread created for {self.challenger.mention} vs {self.target.mention}!\n"
            "You can now start your Pokemon battle here."
        )
        
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            userPartyId = cursor.execute("SELECT member1, member2, member3, member4, member5, member6 FROM party WHERE userId = ?", (self.challenger.id,)).fetchone() # userId, pokemon1, pokemon2, pokemon3, pokemon4, pokemon5, pokemon6
            targetPartyId = cursor.execute("SELECT member1, member2, member3, member4, member5, member6 FROM party WHERE userId = ?", (self.target.id,)).fetchone()
            userParty: list = [None] * 6
            targetParty: list = [None] * 6

            for i in range(5):
                userParty[i] = cursor.execute("SELECT * FROM cards WHERE itemId = ?", (userPartyId[i+1],)).fetchone()
                targetParty[i] = cursor.execute("SELECT * FROM cards WHERE itemId = ?", (targetPartyId[i+1],)).fetchone()

            print(userParty)
            print(targetParty)

        goesFirst = random.choice([self.challenger, self.target])

        # Send the initial message
        await thread.send(
            f"{goesFirst.mention} goes first!"
        )

        # Send the party information
        await thread.send(
            f"{self.challenger.mention} party:\n"
            f"1. {userParty[0][1]}\n"
            f"2. {userParty[1][1]}\n"
            f"3. {userParty[2][1]}\n"
            f"4. {userParty[3][1]}\n"
            f"5. {userParty[4][1]}\n"
            f"6. {userParty[5][1]}\n"
        )

        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message(
                "Only the challenged player can decline!",
                ephemeral=True
            )
            return

        # Disable the buttons
        for button in self.children:
            button.disabled = True
        await self.message.edit(view=self)

        await interaction.response.send_message(
            f"{self.target.name} declined the duel!"
        )
        self.stop()

async def challengeFunc(interaction: discord.Interaction, member: discord.Member) -> None:
    if member == interaction.user:
        await interaction.response.send_message(
            "You can't challenge yourself!",
            ephemeral=True
        )
        return

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM party WHERE userId = ?", (interaction.user.id,))
        userParty = cursor.fetchone()
        cursor.execute("SELECT * FROM party WHERE userId = ?", (member.id,))
        targetParty = cursor.fetchone()

    if not userParty:
        await interaction.response.send_message(
            "You must set your party before challenging another player! Use the `/set-party` command.",
            ephemeral=True
        )
        return

    if not targetParty:
        await interaction.response.send_message(
            f"{member.mention} hasn't set their party yet! They need to use the `/set-party` command.",
            ephemeral=False
        )
        return

    view = DuelButtons(interaction.user, member)
    response = await interaction.response.send_message(
        f"{member.mention}, you've been challenged to a Pokemon battle by {interaction.user.name}!",
        view=view
    )
    
    # Store the message for timeout handling
    view.message = await interaction.original_response()

slashCommandChallenge = app_commands.Command(
    name="challenge",
    description="Challenge another player to a pokemon type battle!",
    callback=challengeFunc,
)