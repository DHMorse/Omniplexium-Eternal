from discord.ext import commands
import discord

from const import copyCard
from const import pool 

@commands.command()
async def copycard(ctx, cardId: int, member: discord.Member = None):
    if ctx.author.guild_permissions.administrator != True:
        await ctx.send("You do not have the required permissions to use this command.")
        return

    if member is None:
        member = ctx.author

    try:
        copyCard(int(cardId), int(member.id))
        await ctx.send(f"Card with ID {cardId} has been successfully copied to {member.name}.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
