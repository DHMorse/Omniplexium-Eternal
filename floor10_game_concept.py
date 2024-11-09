import discord
from discord import app_commands
import random

from const import LOG_CHANNEL_ID, pool, update_xp_and_check_level_up, xpToLevel

async def guess_the_number(interaction: discord.Interaction, guess: int):
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        # Check if user exists in the database
        number = random.randint(1, 10)
        

        if guess == number:
            level_up = await update_xp_and_check_level_up(ctx=interaction, xp=25, add=True)
            await interaction.response.send_message(f"Your guess of {guess} is right, Congratulations!`+25 XP`")

        elif abs(guess - number) <= 2:
            level_up = await update_xp_and_check_level_up(ctx=interaction, xp=10, add=True)
            await interaction.response.send_message(f"Your guess of {guess} is close! The number was {number}. `+10 XP`")

        else:
            level_up = await update_xp_and_check_level_up(ctx=interaction, xp=5, add=False)
            await interaction.response.send_message(f"Your guess of {guess} is wrong, Sorry! The number was {number}. `-5 XP`")

        print(level_up)

        if level_up == True:
            channel = interaction.client.get_channel(LOG_CHANNEL_ID)
            
            cursor.execute("SELECT xp, money FROM users WHERE user_id = %s", (interaction.user.id,))
            result = cursor.fetchone()

            await channel.send(f"Congratulations, {interaction.user.mention}! You have leveled up to level {xpToLevel(result[0])}!")
    finally:
            cursor.close()
            conn.close()

guess_the_number_command = app_commands.Command(
    name="guess_the_number",
    description="Guess a number between 1 and 10.",
    callback=guess_the_number,
)