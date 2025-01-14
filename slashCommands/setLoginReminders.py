import discord
from discord import app_commands
import sqlite3

from const import DATABASE_PATH, LOGIN_REMINDER_ROLE_ID, COLORS, ADMIN_LOG_CHANNEL_ID

async def setLoginRemindersFunc(interaction: discord.Interaction, boolen: bool = True):
    authorId = interaction.user.id
    authorUsername = interaction.user.name

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT loginReminders FROM users WHERE userId = ?", (authorId,))
        result = cursor.fetchone()
        
        loginReminders = result[0]
        
        if boolen is True and loginReminders is True:
            await interaction.response.send_message("You have already turned your login reminders on!")
            return
        
        match boolen:
            case True:
                # Update the database
                await interaction.response.send_message("You have turned your login reminders on!")
                cursor.execute("UPDATE users SET loginReminders = ? WHERE userId = ?", (boolen, authorId))
                conn.commit()

                # Give the user a role
                try:
                    role = interaction.guild.get_role(LOGIN_REMINDER_ROLE_ID)
                    await interaction.user.add_roles(role)
                except Exception as e:
                    channel = interaction.client.get_channel(ADMIN_LOG_CHANNEL_ID)
                    await channel.send(f"{COLORS['red']}We tried to give user `{authorUsername}` role `Login Reminder` of id `{LOGIN_REMINDER_ROLE_ID}` but ```{e}```{COLORS['reset']}")

            case False:
                # Update the database
                await interaction.response.send_message("You have turned your login reminders off!")
                cursor.execute("UPDATE users SET loginReminders = ? WHERE userId = ?", (boolen, authorId))
                conn.commit()

                # Remove the role
                try:
                    role = interaction.guild.get_role(LOGIN_REMINDER_ROLE_ID)
                    await interaction.user.remove_roles(role)
                except Exception as e:
                    channel = interaction.client.get_channel(ADMIN_LOG_CHANNEL_ID)
                    await channel.send(f"{COLORS['red']}We tried to remove user `{authorUsername}` role `Login Reminder` of id `{LOGIN_REMINDER_ROLE_ID}` but ```{e}```{COLORS['reset']}")

slashCommandSetLoginReminders = app_commands.Command(
    name="Set Login Reminders",
    description="Turn your login reminders on or off.",
    callback=setLoginRemindersFunc,
)