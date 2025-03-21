import discord
import sqlite3
from discord import app_commands

from const import DATABASE_PATH

async def setPartyFunc(interaction: discord.Interaction, member1: str, member2: str = None, member3: str = None, 
                        member4: str = None, member5: str = None, member6: str = None) -> None:
    if member1 == "":
        await interaction.response.send_message(
            "You must specify at least one party member!",
            ephemeral=True
        )
        return

    async def checkMember(userId: int, member: str) -> int | None:
        if member is None:
            return None
        
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor: sqlite3.Cursor = conn.cursor()
            if member.isdigit():
                member: int = int(member)
                cursor.execute("SELECT userId FROM cards WHERE itemId = ?", (member,))
                memberData: tuple[int] | None = cursor.fetchone()
                if memberData and memberData[0] != userId:
                    try:
                        await interaction.response.send_message(
                            f"You can only set party members that you own!",
                            ephemeral=True
                        )
                    except:
                        await interaction.followup.send(
                            f"You can only set party members that you own!",
                            ephemeral=True
                        )
                    return None
                cursor.execute("SELECT itemId FROM cards WHERE itemId = ?", (member,))
                memberData: tuple[int] | None = cursor.fetchone()
            else:
                cursor.execute("SELECT userId FROM cards WHERE LOWER(itemName) = ?", (member.lower(),))
                memberData: tuple[int] | None = cursor.fetchone()
                if memberData and memberData[0] != userId:
                    try:
                        await interaction.response.send_message(
                            f"You can only set party members that you own!",
                            ephemeral=True
                        )
                    except:
                        await interaction.followup.send(
                            f"You can only set party members that you own!",
                            ephemeral=True
                        )
                    return None
                cursor.execute("SELECT itemId FROM cards WHERE LOWER(itemName) = ?", (member.lower(),))
                memberData: tuple[int] | None = cursor.fetchone()
        
        if not memberData:
            try:
                await interaction.response.send_message(
                    f"No card with that ID was found for the member with the id or name {member}!",
                    ephemeral=True
                )
            except:
                await interaction.followup.send(
                    f"No card with that ID was found for the member with the id or name {member}!",
                    ephemeral=True
                )
            return None

        return memberData[0]

    userId: int = interaction.user.id

    member1itemId: int | None = await checkMember(userId, member1)
    if not member1itemId:
        return
    member2itemId: int | None = await checkMember(userId, member2)
    member3itemId: int | None = await checkMember(userId, member3)
    member4itemId: int | None = await checkMember(userId, member4)
    member5itemId: int | None = await checkMember(userId, member5)
    member6itemId: int | None = await checkMember(userId, member6)
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute("UPDATE party SET member1=?, member2=?, member3=?, member4=?, member5=?, member6=? WHERE userId=?", 
                        (member1itemId, member2itemId, member3itemId, member4itemId, member5itemId, member6itemId, interaction.user.id)
                    )
        if cursor.rowcount == 0:  # If no row was updated, insert a new one
            cursor.execute("INSERT INTO party (userId, member1, member2, member3, member4, member5, member6) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (interaction.user.id, member1itemId, member2itemId, member3itemId, member4itemId, member5itemId, member6itemId)
                    )
        conn.commit()

    try:
        await interaction.response.send_message("Party members set successfully!")
    except:
        await interaction.followup.send("Party members set successfully!")

slashCommandSetParty: app_commands.Command = app_commands.Command(
    name="set-party", # no spaces or capitals allowed
    description="Set your party members in your party!",
    callback=setPartyFunc,
)