import discord
from discord import app_commands
import datetime
import sqlite3

from const import COLORS, DATABASE_PATH, ADMIN_LOG_CHANNEL_ID
from helperFunctions.main import xpToLevel

async def statsFunc(interaction: discord.Interaction) -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor: sqlite3.Cursor = conn.cursor()
    
        member: discord.Member = interaction.user
    
        try:
            cursor.execute("SELECT xp, money, lastLogin, daysLoggedInInARow FROM users WHERE userId = ?", (member.id,))
            result: tuple = cursor.fetchone() # add a proper type hint later

            if result:
                xp: int
                money: int
                lastLogin: int
                daysLoggedInInARow: int
                xp, money, lastLogin, daysLoggedInInARow = result
                level: int = xpToLevel(xp)

                formatedXp: str = "{:,}".format(xp)
                formatedMoney: str = "{:,}".format(money)

                if lastLogin != None:
                    # Convert lastLogin to human-readable format
                    last_login_datetime: datetime.datetime = datetime.datetime.utcfromtimestamp(lastLogin)
                    last_login_readable: str = last_login_datetime.strftime("%Y-%m-%d %H:%M:%S UTC")
                else:
                    last_login_readable: str | None = None

                # Create a list of dictionaries for the items
                itemsList: list[dict[str, int | str]] = []

                cursor.execute("SELECT * FROM cards WHERE userId = ?", (member.id,))
                cards: list[tuple[int, str]] = cursor.fetchall() # add a proper type hint later

                # Create a numbered list of card names
                card_names: list[str] = [f"{i+1}. {card[1]}" for i, card in enumerate(cards)]  # card[1] is itemName
                cards_text: str = "\n".join(card_names) if card_names else "No cards"

                await interaction.response.send_message(
                                f"{member.name}'s Stats:\n"
                                f"```ansi\n"
                                f"\u001b[0;34mXp: {formatedXp}\n"
                                f"\u001b[0;34mLevel: {level}\n"
                                f"\u001b[0;36mMoney: ${formatedMoney}\n"
                                f"\u001b[0;34mLast Login (UTC): {last_login_readable}\n"
                                f"\u001b[0;36mDays Logged In In A Row: {daysLoggedInInARow}\n"
                                f"\u001b[0;34mCards:\n{cards_text}\n"
                                f"```",
                                ephemeral=True
                                )
            else:
                await interaction.response.send_message(f'''```ansi\n{COLORS['red']}{member.name} has no records in the database.{COLORS['reset']}\n```''')
                
                channel: discord.TextChannel | None = interaction.client.get_channel(ADMIN_LOG_CHANNEL_ID)
                if channel:
                    await channel.send(f'''```ansi\n{COLORS['red']}{member.name} has no records in the database.{COLORS['reset']}\n```''')
        
        except Exception as e:
            print(f"{COLORS['red']} {e} {COLORS['reset']}")
            await interaction.response.send_message(f'''```ansi\n{COLORS['red']}An error occurred. {COLORS['reset']}\n```''')
            
            channel: discord.TextChannel | None = interaction.client.get_channel(ADMIN_LOG_CHANNEL_ID)
            if channel:
                await channel.send(f'''```ansi\n{COLORS['red']}An error occurred: {e} {COLORS['reset']}\n```''')
            return

slashCommandStats: app_commands.Command = app_commands.Command(
    name="stats", # no spaces or capitals allowed
    description="Get the stats of your user!",
    callback=statsFunc,
)