from discord.ext import commands

from const import levelToXp

def create_level_to_xp_command(bot):
    @bot.command()
    async def leveltoxp(ctx, level: int) -> None:
        """Converts a level to the amount of XP required to reach that level."""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You do not have the required permissions to use this command.")
            return
        try:
            level = int(level)
        except:
            await ctx.send("Level must be a valid integer. i.e. 1-100")
            return

        if level < 1:
            await ctx.send("Level must be 1 or higher.")
            return
        if level > 100:
            await ctx.send("Level must be 100 or lower.")
            return
        
        xp = levelToXp(level)
        
        await ctx.send(f"Level {level} requires {xp} XP.")
