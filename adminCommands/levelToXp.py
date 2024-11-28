import discord
from discord.ext import commands

@commands.command()
async def levelToXp(ctx, level: int) -> None:
    """Converts a level to the amount of XP required to reach that level."""
    if ctx.author.guild_permissions.administrator != True:
        await ctx.send("You do not have the required permissions to use this command.")
        return
    try:
        level = int(level)
    except:
        await ctx.send("Level must be a vaild integer. i.e. 1-100")
        return

    if level < 1:
        await ctx.send("Level must be 1 or higher.")
        return
    if level > 100:
        await ctx.send("Level must be 100 or lower.")
        return
    
    xp = levelToXp(level)
    
    await ctx.send(f"Level {level} requires {xp} XP.")

def levelToXp(level: int) -> int:
    # Constants
    TOTAL_LEVELS = 100
    XP_LEVEL_10 = 100
    XP_LEVEL_100 = 10e12  # 1 trillion

    # Calculate the exponential growth factor
    base = (XP_LEVEL_100 / XP_LEVEL_10) ** (1 / (TOTAL_LEVELS - 10))
    
    if level <= 10:
        # XP grows linearly for levels <= 10
        return level * 10
    elif level >= TOTAL_LEVELS:
        # XP caps at XP_LEVEL_100 for level 100
        return int(XP_LEVEL_100)

    # Calculate XP required for the level
    xp = XP_LEVEL_10 * (base ** (level - 10))
    return int(xp)

if __name__ == '__main__':
    # Example usage:
    print(levelToXp(1))  # Output: 10
    print(levelToXp(10))  # Output: 100
    print(levelToXp(50))  # Output: XP value for level 50
    print(levelToXp(100))  # Output: 1 trillion
