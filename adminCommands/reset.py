from discord.ext import commands
import discord
import asyncio

from const import pool

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

    # List of valid columns in the table that can be reset
    valid_columns = ["xp", "money", "lastLogin", "daysLoggedInInARow"]  # Add more columns as needed

    # Check if the stat provided is a valid column
    if stat not in valid_columns:
        await ctx.send(f"Invalid stat specified. Please choose one from: {', '.join(valid_columns)}.")
        return

    # Ask for confirmation to reset
    await ctx.send(f"Are you sure you want to reset '{stat}' for {member.name}? Type 'yes' to confirm.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'yes'

    try:
        # Wait for the user's confirmation
        confirmation_msg = await ctx.bot.wait_for('message', timeout=60.0, check=check)

        # If confirmed, reset the stat to the default value
        conn = pool.get_connection()
        cursor = conn.cursor()

        try:
            # Reset column to its default value (you might need to adjust this based on your database)
            if stat == "xp":
                cursor.execute("UPDATE users SET xp = DEFAULT WHERE userId = %s", (member_id,))
            elif stat == "money":
                cursor.execute("UPDATE users SET money = DEFAULT WHERE userId = %s", (member_id,))
            elif stat == "lastLogin":
                cursor.execute("UPDATE users SET lastLogin = DEFAULT WHERE userId = %s", (member_id,))
            elif stat == "daysLoggedInInARow":
                cursor.execute("UPDATE users SET daysLoggedInInARow = DEFAULT WHERE userId = %s", (member_id,))
            
            conn.commit()
            await ctx.send(f"Successfully reset '{stat}' for {member.name} to its default value.")
        finally:
            cursor.close()
            conn.close()
    
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. The action was canceled.")
