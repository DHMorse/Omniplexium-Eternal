import discord
from discord import app_commands
import sqlite3
from typing import Optional, Tuple, Any

from const import DATABASE_PATH, LOGIN_REMINDER_ROLE_ID, COLORS, ADMIN_LOG_CHANNEL_ID

async def setLoginRemindersFunc(interaction: discord.Interaction, boolen: bool = True) -> None:
    """
    Set login reminders for a user.
    
    Args:
        interaction: The Discord interaction object
        boolen: Boolean flag to turn reminders on (True) or off (False)
    
    Returns:
        None
    """
    authorId: int = interaction.user.id
    authorUsername: str = interaction.user.name

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor: sqlite3.Cursor = conn.cursor()

        cursor.execute("SELECT loginReminders FROM users WHERE userId = ?", (authorId,))
        result: Optional[Tuple[Any, ...]] = cursor.fetchone()
        
        loginReminders: bool = result[0]
        
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
                    role: Optional[discord.Role] = interaction.guild.get_role(LOGIN_REMINDER_ROLE_ID)
                    await interaction.user.add_roles(role)
                except Exception as e:
                    channel: Optional[discord.TextChannel] = interaction.client.get_channel(ADMIN_LOG_CHANNEL_ID)
                    await channel.send(f"{COLORS['red']}We tried to give user `{authorUsername}` role `Login Reminder` of id `{LOGIN_REMINDER_ROLE_ID}` but ```{e}```{COLORS['reset']}")

            case False:
                # Update the database
                await interaction.response.send_message("You have turned your login reminders off!")
                cursor.execute("UPDATE users SET loginReminders = ? WHERE userId = ?", (boolen, authorId))
                conn.commit()

                # Remove the role
                try:
                    role: Optional[discord.Role] = interaction.guild.get_role(LOGIN_REMINDER_ROLE_ID)
                    await interaction.user.remove_roles(role)
                except Exception as e:
                    channel: Optional[discord.TextChannel] = interaction.client.get_channel(ADMIN_LOG_CHANNEL_ID)
                    await channel.send(f"{COLORS['red']}We tried to remove user `{authorUsername}` role `Login Reminder` of id `{LOGIN_REMINDER_ROLE_ID}` but ```{e}```{COLORS['reset']}")

slashCommandSetLoginReminders: app_commands.Command = app_commands.Command(
    name="set-login-reminders", # no spaces or capitals allowed
    description="Turn your login reminders on or off.",
    callback=setLoginRemindersFunc,
)