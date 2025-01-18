import discord
from discord import app_commands
import json
import datetime
import io
import sqlite3
from typing import List, Dict, Union

from const import COLORS, DATABASE_PATH, ADMIN_LOG_CHANNEL_ID
from helperFunctions import xpToLevel

async def statsFunc(interaction: discord.Interaction) -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
    
        member = interaction.user
    
        try:
            cursor.execute("SELECT xp, money, lastLogin, daysLoggedInInARow FROM users WHERE userId = ?", (member.id,))
            result = cursor.fetchone()

            if result:
                xp, money, lastLogin, daysLoggedInInARow = result
                level = xpToLevel(xp)

                formatedXp = "{:,}".format(xp)
                formatedMoney = "{:,}".format(money)

                if lastLogin != None:
                    # Convert lastLogin to human-readable format
                    last_login_datetime = datetime.datetime.utcfromtimestamp(lastLogin)
                    last_login_readable = last_login_datetime.strftime("%Y-%m-%d %H:%M:%S UTC")
                else:
                    last_login_readable = None

                # Create a list of dictionaries for the items
                itemsList: List[Dict[str, Union[int, str]]] = []

                cursor.execute("SELECT * FROM cards WHERE userId = ?", (member.id,))
                cards = cursor.fetchall()

                for card in cards:
                    item = {
                        "cardId": card[3],
                        "itemId": card[0],
                        "itemName": card[1],
                        "userId": card[2]
                    }
                    itemsList.append(item)

                items_json = json.dumps(itemsList, indent=4)
                json_file = io.BytesIO(items_json.encode('utf-8'))

                await interaction.response.send_message(
                                f"{member.name}'s Stats:\n"
                                f"```ansi\n"
                                f"\u001b[0;34mXp: {formatedXp}\n"
                                f"\u001b[0;34mLevel: {level}\n"
                                f"\u001b[0;36mMoney: ${formatedMoney}\n"
                                f"\u001b[0;36mLast Login (Seconds Since Epoch): {lastLogin}\n"
                                f"\u001b[0;34mLast Login (UTC): {last_login_readable}\n"
                                f"\u001b[0;36mDays Logged In In A Row: {daysLoggedInInARow}\n"
                                f"```",
                                file=discord.File(json_file, filename=f"{member.name}_items.json"), 
                                ephemeral=True
                                )    
            else:
                await interaction.response.send_message(f'''```ansi
{COLORS['red']}{member.name} has no records in the database.{COLORS['reset']}
```''')
                channel = interaction.client.get_channel(ADMIN_LOG_CHANNEL_ID)
                await channel.send(f'''```ansi
{COLORS['red']}{member.name} has no records in the database.{COLORS['reset']}
```''')
        except Exception as e:
            print(f"{COLORS['red']} {e} {COLORS['reset']}")
            await interaction.response.send_message(f'''```ansi
{COLORS['red']}An error occurred. {COLORS['reset']}
```''')
            channel = interaction.client.get_channel(ADMIN_LOG_CHANNEL_ID)
            await channel.send(f'''```ansi
{COLORS['red']}An error occurred: {e} {COLORS['reset']}
```''')
            return

slashCommandStats = app_commands.Command(
    name="stats", # no spaces or capitals allowed
    description="Get the stats of your user!",
    callback=statsFunc,
)