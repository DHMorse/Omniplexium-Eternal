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

    async def checkMember(member: str) -> int | None:
        if member is None:
            return None
        
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            if member.isdigit():
                member = int(member)
                cursor.execute("SELECT itemId FROM cards WHERE itemId = ?", (member,))
                memberData = cursor.fetchone()
            else:
                cursor.execute("SELECT itemId FROM cards WHERE LOWER(itemName) = ?", (member.lower(),))
                memberData = cursor.fetchone()
        
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

    member1itemId: int = await checkMember(member1)
    if not member1itemId:
        interaction.response.send_message("No card with that ID was found!", ephemeral=True)
        return
    member2itemId: int = await checkMember(member2)
    member3itemId: int = await checkMember(member3)
    member4itemId: int = await checkMember(member4)
    member5itemId: int = await checkMember(member5)
    member6itemId: int = await checkMember(member6)
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
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

slashCommandSetParty = app_commands.Command(
    name="set-party", # no spaces or capitals allowed
    description="Set your party members in your party!",
    callback=setPartyFunc,
)