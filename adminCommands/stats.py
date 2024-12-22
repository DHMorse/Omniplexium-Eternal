from discord.ext import commands
import discord
import json
import datetime
import pytz
import json
import io
import sqlite3
from typing import List, Dict, Union

from const import COLORS, DATABASE_PATH
from const import xpToLevel

@commands.command()
async def stats(ctx, member: discord.Member = None):
    if ctx.author.guild_permissions.administrator is not True:
        member = None

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
    
        member = member or ctx.author
    
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
                    # Convert to CST
                    cst_tz = pytz.timezone("America/Chicago")
                    last_login_CST = last_login_datetime.replace(tzinfo=pytz.utc).astimezone(cst_tz).strftime("%Y-%m-%d %H:%M:%S CST")
                    
                    # Convert to EST
                    est_tz = pytz.timezone("America/New_York")
                    last_login_EST = last_login_datetime.replace(tzinfo=pytz.utc).astimezone(est_tz).strftime("%Y-%m-%d %H:%M:%S EST")
                else:
                    last_login_readable = None
                    last_login_CST = None
                    last_login_EST = None

                # Create a list of dictionaries for the items
                itemsList: List[Dict[str, Union[int, str]]]

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

                # Send the stats with items as a JSON code block
                if ctx.author.guild_permissions.administrator is not True:
                    await ctx.send(
                                f"{member.name}'s Stats:\n"
                                f"```ansi\n"
                                f"\u001b[0;34mXp: {formatedXp}\n"
                                f"\u001b[0;34mLevel: {level}\n"
                                f"\u001b[0;36mMoney: ${formatedMoney}\n"
                                f"\u001b[0;34mLast Login (UTC): {last_login_readable}\n"
                                f"\u001b[0;36mDays Logged In In A Row: {daysLoggedInInARow}\n"
                                f"```",
                                file=discord.File(json_file, filename=f"{member.name}_items.json")
                                )
                else:    
                    await ctx.send(
                                    f"{member.name}'s Stats:\n"
                                    f"```ansi\n"
                                    f"\u001b[0;34mXp: {formatedXp}\n"
                                    f"\u001b[0;34mLevel: {level}\n"
                                    f"\u001b[0;36mMoney: ${formatedMoney}\n"
                                    f"\u001b[0;36mLast Login (Seconds Since Epoch): {lastLogin}\n"
                                    f"\u001b[0;34mLast Login (UTC): {last_login_readable}\n"
                                    f"\u001b[0;34mLast Login (CST): {last_login_CST}\n"
                                    f"\u001b[0;34mLast Login (EST): {last_login_EST}\n"
                                    f"\u001b[0;36mDays Logged In In A Row: {daysLoggedInInARow}\n"
                                    f"```",
                                    file=discord.File(json_file, filename=f"{member.name}_items.json")
                                    )    
            else:
                await ctx.send(f'''```ansi
{COLORS['red']}{member.name} has no records in the database.{COLORS['reset']}
```''')
        except Exception as e:
            print({COLORS['red']}, e, {COLORS['reset']})
            await ctx.send(f'''```ansi
{COLORS['red']}An error occurred: {e}{COLORS['reset']}
```''')
            return