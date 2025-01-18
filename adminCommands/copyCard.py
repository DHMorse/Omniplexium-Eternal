from discord.ext import commands
import discord
import sqlite3

from const import DATABASE_PATH, COLORS
from helperFunctions.main import copyCard

@commands.command()
async def copycard(ctx, *cardIdOrName: str, member: discord.Member = None) -> None:
    if not ctx.author.guild_permissions.administrator:
        await ctx.send(f'''```ansi
{COLORS['yellow']}You do not have the required permissions to use this command.{COLORS['reset']}
```''')
        return
    
    if member is None:
        member = ctx.author
    
    try:
        # Join multiple word arguments into a single string for card name
        card_name = " ".join(cardIdOrName)
        
        # Check if the input is a digit (card ID)
        if card_name.isdigit():
            card_id = int(card_name)
        else:
            # If not a digit, look up the card ID by name
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT itemId FROM cards WHERE itemName = ?", (card_name,))
                result = cursor.fetchone()
                
                if result is None:
                    await ctx.send(f'''```ansi
{COLORS['red']}No card found with the name "{card_name}".{COLORS['reset']}
```''')
                    return
                
                card_id = result[0]
        
        # Copy the card
        copyCard(card_id, int(member.id))
        await ctx.send(f'''```ansi
{COLORS['blue']}Card with ID {card_id} has been successfully copied to {member.name}.{COLORS['reset']}
```''')

    except Exception as e:
        #await ctx.send(f"An error occurred: {e}")
        await ctx.send(f'''```ansi
{COLORS['red']}An error occurred: {e}\u001b[0m{COLORS['reset']}
```''')