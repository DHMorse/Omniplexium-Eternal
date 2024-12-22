from discord.ext import commands
import discord
import asyncio
import sqlite3

from const import DATABASE_PATH
from const import updateXpAndCheckLevelUp

@commands.command()
async def reset(ctx, stat: str = "", member: discord.Member = None):
    # Check if the user has the required permission
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have the required permissions to use this command.")
        return

    # Get the member who is being reset, default to the author if not provided
    if member is None:
        member = ctx.author

    # Get the member's ID
    member_id = member.id


    # this error handling above is not needed as we catch any expections below
    # we could get rid of it later but it's not doing any harm for now.

    # List of valid columns in the table that can be reset
    valid_columns = ["xp", "money", "lastLogin", "daysLoggedInInARow"]  # Add more columns as needed

    # Check if the stat provided is a valid column
    if stat not in valid_columns:
        await ctx.send(f"Invalid stat specified. Please choose one from: {', '.join(valid_columns)}.")
        return

    # this error handling above is not needed as we catch any expections below
    # we could get rid of it later but it's not doing any harm for now.



    # Ask for confirmation to reset
    await ctx.send(f"Are you sure you want to reset '{stat}' for {member.name}? Type `confirm` to confirm.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'confirm'

    try:
        # Wait for the user's confirmation
        confirmation_msg = await ctx.bot.wait_for('message', timeout=60.0, check=check)

        # If confirmed, reset the stat to the default value
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()

            try:
                if stat != "xp":
                    cursor.execute(f"UPDATE users SET {stat} = DEFAULT WHERE userId = ?", (member_id,))

                elif stat == "xp":
                    cursor.execute("SELECT xp FROM users WHERE userId = ?", (member_id,))
                    xp = cursor.fetchone()[0]
                    await updateXpAndCheckLevelUp(ctx=ctx, bot=ctx.bot, xp=xp, add=False)

                # this should always work but it's not recommended because it's vulnerable to SQL injection
                # this is an admin only command however so we can look into it later

                conn.commit()
                # ANSI GREEN COLOR CODE: \033[92m
                await ctx.send(f"\033[92mSuccessfully reset '{stat}' for {member.name}.\033[0m")

            except Exception as e:
                # ANSI RED COLOR CODE: \033[91m
                await ctx.send(f"\033[91mAn error occurred: {e}\033[0m")

    
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. The action was canceled.")
