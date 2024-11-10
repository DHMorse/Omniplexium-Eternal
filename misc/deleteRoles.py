import discord
from discord.ext import commands

from secret_const import TOKEN

bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def delete_roles(ctx):
    guild = ctx.guild
    for i in range(1, 101):
        role_name = f"Level {i}"
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            await role.delete()
            print(f"Deleted role: {role_name}")
        else:
            print(f"Role {role_name} does not exist.")
    await ctx.send("Roles deleted successfully.")


# Run the bot
bot.run(TOKEN)
