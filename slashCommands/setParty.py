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
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM cards WHERE userId = ?", (interaction.user.id,))
        userCards = cursor.fetchall()
        if not userCards:
            await interaction.response.send_message(
                "You don't have any cards to set as your party members!",
                ephemeral=True
            )
            return

    async def checkMember(member: str) -> tuple:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            if member.isdigit():
                member = int(member1)
                cursor.execute("SELECT * FROM cards WHERE cardId = ?", (member,))
                memberData = cursor.fetchone()
                if not memberData:
                    await interaction.response.send_message(
                        "No card with that ID was found!",
                        ephemeral=True
                    )
                    return
            else:
                cursor.execute("SELECT * FROM cards WHERE itemName = ?", (member,))
                memberData = cursor.fetchone()
                if not memberData:
                    await interaction.response.send_message(
                        "No card with that name was found!",
                        ephemeral=True
                    )
                    return

    member1Data: tuple = await checkMember(member1)
    if not member1Data:
        return
    member2Data: tuple = await checkMember(member2)
    member3Data: tuple = await checkMember(member3)
    member4Data: tuple = await checkMember(member4)
    member5Data: tuple = await checkMember(member5)
    member6Data: tuple = await checkMember(member6)
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO party (userId, member1, member2, member3, member4, member5, member6) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                        (interaction.user.id, member1Data[0], member2Data[0], member3Data[0], member4Data[0], member5Data[0], member6Data[0])
                    )
        conn.commit()

    await interaction.response.send_message("Party members set successfully!")

slashCommandSetParty = app_commands.Command(
    name="set-party", # no spaces or capitals allowed
    description="Set your party members in your party!",
    callback=setPartyFunc,
)