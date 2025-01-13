from discord.ext import commands
import discord
import asyncio
import sqlite3

from const import DATABASE_PATH, COLORS
from helperFunctions import updateXpAndCheckLevelUp

@commands.command()
async def reset(ctx, stat: str = "", member: discord.Member = None) -> None:
    if not ctx.author.guild_permissions.administrator:
        await ctx.send(f'''```ansi
{COLORS['yellow']}You do not have the required permissions to use this command.{COLORS['reset']}
```''')
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
        await ctx.send(f'''```ansi
{COLORS['red']}Invalid stat specified. Please choose one from: {COLORS['reset']}{', '.join(valid_columns)}.
```''')
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
                await ctx.send(f'''```ansi
{COLORS['blue']}Successfully reset '{stat}' for {member.name}.{COLORS['reset']}
```''')

            except Exception as e:
                await ctx.send(f'''```ansi
{COLORS['red']}An error occurred: {e}\u001b[0m{COLORS['reset']}
```''')
                return

    except asyncio.TimeoutError:
        await ctx.send(f'''```ansi
{COLORS['yellow']}You took too long to respond. The action was canceled.{COLORS['reset']}
```''')
        return