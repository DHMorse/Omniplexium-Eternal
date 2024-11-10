import discord
from discord import app_commands
import random

from const import LOG_CHANNEL_ID, ADMIN_LOG_CHANNEL_ID, pool, update_xp_and_check_level_up, xpToLevel

async def guess_the_number(interaction: discord.Interaction, guess: app_commands.Range[int, 1, 10]):
    conn = pool.get_connection()
    cursor = conn.cursor()

    role = discord.utils.get(interaction.guild.roles, name='Level 10')

    if role is None:
        channel = interaction.client.get_channel(ADMIN_LOG_CHANNEL_ID)
        await channel.send("Role 'Level 10' does not exist.")
        cursor.close()
        conn.close()
        return

    if role not in interaction.user.roles:
        await interaction.response.send_message(f"You must be at least level 10 to play this game.")
        cursor.close()
        conn.close()
        return

    try:
        # Check if user exists in the database
        number = random.randint(1, 10)
        

        if guess == number:
            level_up, new_level = await update_xp_and_check_level_up(ctx=interaction, xp=25, add=True)
            await interaction.response.send_message(f"Your guess of {guess} is right, Congratulations!`+25 XP`")

        elif abs(guess - number) <= 2:
            level_up, new_level = await update_xp_and_check_level_up(ctx=interaction, xp=10, add=True)
            await interaction.response.send_message(f"Your guess of {guess} is close! The number was {number}. `+10 XP`")

        else:
            level_up, new_level = await update_xp_and_check_level_up(ctx=interaction, xp=5, add=False)
            await interaction.response.send_message(f"Your guess of {guess} is wrong, Sorry! The number was {number}. `-5 XP`")

        if level_up == True:
            channel = interaction.client.get_channel(LOG_CHANNEL_ID)
            
            cursor.execute("SELECT xp, money FROM stats WHERE user_id = %s", (interaction.user.id,))
            result = cursor.fetchone()

            await channel.send(f"Congratulations, {interaction.user.mention}! You have leveled up to level {xpToLevel(result[0])}!")

            role = discord.utils.get(interaction.guild.roles, name=f"Level {new_level}")
                
            if role is None:
                channel = interaction.client.get_channel(ADMIN_LOG_CHANNEL_ID)
                await channel.send(f"Role 'Level {new_level}' does not exist.")
                return
            if role in interaction.user.roles:
                channel = interaction.client.get_channel(ADMIN_LOG_CHANNEL_ID)
                await channel.send(f"{interaction.user.name} already has the 'Level {new_level}' role, but we tried to give it to them again.")
                return
            else:
                await interaction.user.add_roles(role)
    finally:
            cursor.close()
            conn.close()

guess_the_number_command = app_commands.Command(
    name="guess_the_number",
    description="Guess a number between 1 and 10.",
    callback=guess_the_number,
)