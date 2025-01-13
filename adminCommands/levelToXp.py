from const import COLORS
from helperFunctions import levelToXp

def create_level_to_xp_command(bot):
    @bot.command()
    async def leveltoxp(ctx, level: int = None) -> None:
        """Converts a level to the amount of XP required to reach that level."""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send(f'''```ansi
{COLORS['yellow']}You do not have the required permissions to use this command.{COLORS['reset']}
```''')
            return
        
        if level is None:
            await ctx.send(f'''```ansi
{COLORS['red']}Please provide a level to convert to XP.{COLORS['reset']}
```''')
            return
        
        try:
            level = int(level)
        except:
            await ctx.send(f'''```ansi
{COLORS['red']}Level must be a valid integer. i.e. 1-100{COLORS['reset']}
```''')
            return

        if level < 1:
            await ctx.send(f'''```ansi
{COLORS['red']}Level must be 1 or higher.{COLORS['reset']}
```''')
            return
        if level > 100:
            await ctx.send(f'''```ansi
{COLORS['red']}Level must be 100 or lower.{COLORS['reset']}
```''')
            return
        
        xp = levelToXp(level)
        
        await ctx.send(f'''```ansi
{COLORS['blue']}Level {level} requires {xp} XP.{COLORS['reset']}
```''')