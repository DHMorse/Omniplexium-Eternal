from discord.ext import commands

@commands.command()
async def killme(ctx: commands.Context) -> None:
    await ctx.author.kick(reason="User killed themselves.")