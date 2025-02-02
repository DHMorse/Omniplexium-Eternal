import discord
from discord import app_commands

@app_commands.checks.has_permissions(administrator=True)  # Restrict to admins
async def admin_command(interaction: discord.Interaction):
    await interaction.response.send_message("You are an admin!", ephemeral=True)

# Error handler for permission issues
@admin_command.error
async def admin_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)

adminSlashCommandTest = app_commands.Command(
    name="admin_command", 
    description="This command is only for admins",
    callback=admin_command,
)