from discord.ext import commands
import discord

@commands.command()
async def killme(ctx) -> None:
    await ctx.author.kick(reason="User killed themselves.")