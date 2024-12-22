from discord.ext import commands
import discord
import sqlite3

from const import COLORS, DATABASE_PATH
from const import updateXpAndCheckLevelUp

@commands.command()
async def set(ctx, stat: str = '', value: str = '', member: discord.Member = None) -> None:
    if ctx.author.guild_permissions.administrator != True:
        await ctx.send(f'''```ansi
{COLORS['yellow']}You do not have the required permissions to use this command.{COLORS['reset']}
```''')
        return
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        if member is None:
            member = ctx.author

        if value == '':
            await ctx.send(f'''```ansi
{COLORS['red']}Please specify a value to set.{COLORS['reset']}
```''')
            return
        
        try:
            if stat == "xp":
                value = int(value)
        except ValueError:
            await ctx.send(f'''```ansi
{COLORS['red']}Value's for xp must be integers.{COLORS['reset']}
```''')
            return

        try:
            if stat == "xp":
                cursor.execute("SELECT xp FROM users WHERE userId = ?", (member.id,))
                result = cursor.fetchone()
                current_xp = result[0]
                
                if value > current_xp:
                    await updateXpAndCheckLevelUp(ctx, ctx.bot, value - current_xp, True)
                elif value < current_xp:
                    await updateXpAndCheckLevelUp(ctx, ctx.bot, current_xp - value, False)

                await ctx.send(f'''```ansi
{COLORS['blue']}Set {member.name}'s xp to {value}.{COLORS['reset']}
```''')

            elif stat == "money":
                cursor.execute("UPDATE users SET money = ? WHERE userId = ?", (value, member.id))
                conn.commit()
                await ctx.send(f'''```ansi
{COLORS['blue']}Set {member.name}'s money to ${value}.{COLORS['reset']}
```''')
            else:
                #await ctx.send("Please specify a valid stat to set it's value.")
                await ctx.send(f'''```ansi
{COLORS['red']}Please specify a valid stat to set it's value.{COLORS['reset']}
```''')

        except Exception as e:
            await ctx.send(f'''```ansi
{COLORS['red']}Error: {e}{COLORS['reset']}
```''')
            return