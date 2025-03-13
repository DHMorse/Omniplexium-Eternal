import discord
from discord import app_commands
import sqlite3
import random

from const import DATABASE_PATH

class DuelButtons(discord.ui.View):
    def __init__(self, challenger: discord.Member, target: discord.Member):
        super().__init__(timeout=60)
        self.challenger: discord.Member = challenger
        self.target: discord.Member = target
        self.message: discord.Message | None = None

    async def on_timeout(self) -> None:
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
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
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

        class PartyViewButton(discord.ui.Button):
            def __init__(self, challenger: discord.Member, target: discord.Member) -> None:
                super().__init__(label="View Party", style=discord.ButtonStyle.blurple)
                self.challenger: discord.Member = challenger
                self.target: discord.Member = target

            async def callback(self, interaction: discord.Interaction) -> None:
                with sqlite3.connect(DATABASE_PATH) as conn:
                    cursor: sqlite3.Cursor = conn.cursor()
                    # Get the party of the user who clicked
                    partyIds: tuple[int] | None = cursor.execute("SELECT member1, member2, member3, member4, member5, member6 FROM party WHERE userId = ?", 
                                            (interaction.user.id,)).fetchone()
                    
                    # this error handling is really not needed as we do the same check earlier but why not keep it lmao
                    if not partyIds:
                        await interaction.response.send_message(
                            "You don't have a party set up!",
                            ephemeral=True
                        )
                        return

                    party: list[str | None] = []
                    
                    for memberId in partyIds:
                        if memberId:
                            pokemon: tuple[int, str] | None = cursor.execute("SELECT * FROM cards WHERE itemId = ?",(memberId,)).fetchone()
                            party.append(pokemon[1] if pokemon else None)
                        
                        else:
                            party.append(None)

                    partyText: str = "\n".join(f"{i+1}. {pokemon}" for i, pokemon in enumerate(party))
                    await interaction.response.send_message(
                        f"Your party:\n{partyText}",
                        ephemeral=True
                    )

        # Create view with the custom button
        view: discord.ui.View = discord.ui.View()
        view.add_item(PartyViewButton(self.challenger, self.target))

        # Send initial message in the thread with the button
        await thread.send(
            f"Battle thread created for {self.challenger.mention} vs {self.target.mention}!\n"
            "You can now start your Pokemon battle here.",
            view=view
        )

        goesFirst = random.choice([self.challenger, self.target])
        
        # Send the initial message
        await thread.send(
            f"{goesFirst.mention} goes first!"
        )

        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
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
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute("SELECT * FROM party WHERE userId = ?", (interaction.user.id,))
        userParty: tuple[int] | None = cursor.fetchone()
        cursor.execute("SELECT * FROM party WHERE userId = ?", (member.id,))
        targetParty: tuple[int] | None = cursor.fetchone()

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

    view: DuelButtons = DuelButtons(interaction.user, member)
    response: discord.Message = await interaction.response.send_message(
        f"{member.mention}, you've been challenged to a Pokemon battle by {interaction.user.name}!",
        view=view
    )
    
    # Store the message for timeout handling
    view.message = await interaction.original_response()

slashCommandChallenge: app_commands.Command = app_commands.Command(
    name="challenge",
    description="Challenge another player to a pokemon type battle!",
    callback=challengeFunc,
)