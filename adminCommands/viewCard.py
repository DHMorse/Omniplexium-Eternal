from discord.ext import commands
import discord
import sqlite3

from const import COLORS, DATABASE_PATH

@commands.command()
async def viewcard(ctx, *, query: str = "") -> None:
    if not ctx.author.guild_permissions.administrator:
        await ctx.send(f'''```ansi\n{COLORS['yellow']}You do not have the required permissions to use this command.{COLORS['reset']}\n```''')

    if query == "":
        await ctx.send(f'''```ansi\n{COLORS['red']}Please specify a valid card name or ID to view.{COLORS['reset']}\n```''')
        return

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        if query.isdigit():
            cursor.execute("SELECT cardId, ImagePath, itemId, userId FROM cards WHERE itemId = ?", (int(query),))
            cardData = cursor.fetchone()

            if not cardData:
                await ctx.send(f'''```ansi\n{COLORS['red']}No card with that ID was found.{COLORS['reset']}\n```''')
                return
            
            cardId = cardData[0]
            cardPath = cardData[1]
            itemId = cardData[2]
            ownerUserId = cardData[3]

            file = discord.File(cardPath, filename="card.png")

            await ctx.send(file=file)
            await ctx.send(f'Card ID: {cardId}\nItem ID: {itemId}\nOwner ID: {ownerUserId}')

        else:
            cursor.execute("SELECT cardId, ImagePath, itemId, userId FROM cards WHERE itemName = ?", (query,))
            cardData = cursor.fetchone()

            if not cardData:
                await ctx.send(f'''```ansi\n{COLORS['red']}No card with that name was found.{COLORS['reset']}\n```''')
                return
            
            cardId = cardData[0]
            cardPath = cardData[1]
            itemId = cardData[2]
            ownerUserId = cardData[3]

            file = discord.File(cardPath, filename="card.png")

            await ctx.send(file=file)
            await ctx.send(f'Card ID: {cardId}\nItem ID: {itemId}\nOwner ID: {ownerUserId}')