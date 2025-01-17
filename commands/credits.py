from discord.ext import commands

from const import SERVER_ID, CREDITS_CHANNEL_ID

@commands.command()
async def credits(ctx) -> None:
    await ctx.send(f'https://discord.com/channels/{SERVER_ID}/{CREDITS_CHANNEL_ID}/')