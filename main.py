'''
Two (three?) forms of currency:
- Points: for sending messages and playing easy games (karma, aura, social status)
- MONEY money: for leveling up, doing useful crap, etc. (money, stocks, economic crap)
(- REAL MONEY MONEY money: buy with USD lol)

EXTREME rewards for inviting people (automatic? manual?)

we make some sort of minigame per every 10 levels or what ever we decide our floors to be

each level has a cooler mini game then the last, and the rewards are better, but the difficulty could be higher

and the amount of points needed for each level is exponential, so even tho you have better games it will still take longer to level up

'''

import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import os
import requests
import ast

from secret_const import TOKEN

from const import CACHE_DIR_PFP, LEADERBOARD_PIC, DEFUALT_PROFILE_PIC, LOG_CHANNEL_ID, ADMIN_LOG_CHANNEL_ID
from const import pool 
from const import xpToLevel, update_xp_and_check_level_up, getCurrentItemID, incrementCurrentItemID

from adminCommands.set import set
from adminCommands.stats import stats
from adminCommands.reset import reset

from floor10_game_concept import guess_the_number_command

from generateCardAI import genAiCard
from cardImageMaker import makeCardFromJson

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.all())

    async def setup_hook(self):
        # Add the imported command to the bot’s command tree
        self.tree.add_command(guess_the_number_command)
        await self.tree.sync()  # Sync commands with Discord

bot = MyBot()

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot is ready. Logged in as {bot.user}')

### ADMIN COMMANDS ###

bot.add_command(set)
bot.add_command(stats)
bot.add_command(reset)

### ADMIN COMMANDS ###

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    username = message.author.name

    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        # Check if user exists in the database
        cursor.execute("SELECT xp, money FROM stats WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()

        if result:
            # Directly call level-up update function and get level-up flag
            level_up, new_level = await update_xp_and_check_level_up(ctx=message, xp=1, add=True)
            if level_up:
                # Send the level-up message with the correct level
                channel = bot.get_channel(LOG_CHANNEL_ID)

                if new_level == 1 or new_level > 9:
                    await channel.send(f"Congratulations, {message.author.mention}! You have leveled up to level {new_level}!")
                else:
                    await channel.send(f"Congratulations, {message.author}! You have leveled up to level {new_level}!")
                
                role = discord.utils.get(message.guild.roles, name=f"Level {new_level}")
                
                if role is None:
                    channel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
                    await channel.send(f"Role 'Level {new_level}' does not exist.")
                    return
                if role in message.author.roles:
                    channel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
                    await channel.send(f"{message.author.name} already has the 'Level {new_level}' role, but we tried to give it to them again.")
                    return
                else:
                    await message.author.add_roles(role)
        else:
            # Insert new user record if they don't exist
            cursor.execute(
                "INSERT INTO stats (user_id, username, xp, money, items) VALUES (%s, %s, %s, %s, %s)",
                (user_id, username, 1, 0, '[]')
            )
            conn.commit()

    finally:
        cursor.close()
        conn.close()

    # Continue processing other commands if any
    await bot.process_commands(message)

@bot.tree.command(name="leaderboard", description="Display the leaderboard based on level or money.")
@app_commands.describe(type="Choose between 'level' or 'money' for the leaderboard type.")
async def leaderboard(interaction: discord.Interaction, type: str = "level"):
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        # Determine the query based on the selected type
        if type == "money":
            cursor.execute("SELECT user_id, username, money FROM stats ORDER BY money DESC, xp DESC LIMIT 10")
            leaderboard_data = cursor.fetchall()
        else:  # Default to "level"
            type = 'level' # handles edge case where the user types something other than 'money' or 'level'
            cursor.execute("SELECT user_id, username, xp FROM stats ORDER BY xp DESC, xp DESC LIMIT 10")
            leaderboard_data = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    # Create an image for the leaderboard
    image_width = 600
    image_height = 770
    background_color = (54, 57, 62)  # Dark grey background
    image = Image.new("RGB", (image_width, image_height), background_color)

    # Load font for text
    font_size = 30
    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", font_size)

    # Initialize drawing context
    draw = ImageDraw.Draw(image)

    # Set up leaderboard rendering variables
    count = 0
    y_offset = 10
    for user_id, username, value in leaderboard_data:
        if user_id == 1175890644191957013:
            continue

        user = bot.get_user(user_id)
        count += 1

        # Ensure the directory exists
        profile_picture_dir = os.path.join(os.path.expanduser(CACHE_DIR_PFP))
        if not os.path.exists(profile_picture_dir):
            os.makedirs(profile_picture_dir)

        # Check if profile picture is in cache
        profile_picture_path = os.path.join(profile_picture_dir, f"{user_id}.png")

        if os.path.exists(profile_picture_path):
            profile_picture = Image.open(profile_picture_path)
        else:
            # Download profile picture if available; otherwise, use default
            if user and user.avatar:
                profile_picture_response = requests.get(user.avatar.url, stream=True)
                profile_picture_response.raise_for_status()
                profile_picture = Image.open(profile_picture_response.raw)
            else:
                profile_picture = Image.open(DEFUALT_PROFILE_PIC)

            # Save profile picture to cache
            profile_picture.save(profile_picture_path)

        # Resize profile picture and draw on the image
        profile_picture = profile_picture.resize((70, 70))
        image.paste(profile_picture, (10, y_offset))

        # Determine color based on rank
        if count == 1:
            rank_color = (255, 215, 0)  # Gold
        elif count == 2:
            rank_color = (192, 192, 192)  # Silver
        elif count == 3:
            rank_color = (205, 127, 50)  # Bronze
        else:
            rank_color = (255, 255, 255)  # White


        # what the fuck is value?

        value = xpToLevel(value) if type == "level" else value

        # Draw rank, username, and value (level or money)
        display_value = f"Level {value}" if type == "level" else f"${value:,}"
        draw.text((100, y_offset + 10), f"•  #{count} • {username}", fill=rank_color, font=font)
        draw.text((390, y_offset + 10), display_value, fill=(255, 255, 255), font=font)  # Value in white

        # Increment y_offset for next user
        y_offset += 75
        if count == 10:
            break

    # Save the leaderboard image
    image.save(LEADERBOARD_PIC)

    # Create an embed for the leaderboard
    embed = discord.Embed(title=f"{type.capitalize()} Leaderboard", color=0x282b30)
    embed.set_image(url="attachment://leaderboard.png")

    # Send the embed with the leaderboard image
    await interaction.response.send_message(embed=embed, file=discord.File(LEADERBOARD_PIC))


@bot.tree.command(name="generatecard", description="Generate a custom playing card. (demo)")
@app_commands.describe(prompt="Choose the type for the card.")
async def genCard(interaction: discord.Interaction, prompt: str = "prompt"):
    
    # Defer the response to allow more time for processing
    await interaction.response.defer()

    output = await genAiCard(prompt)
    cardFilePath = await makeCardFromJson(output[0], output[1]) # output[1] is doing nothing we over write the varible in the file

    # Update the user's items in the database
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        # Retrieve the current items from the database
        cursor.execute("SELECT itemIDs FROM stats WHERE user_id = %s", (interaction.user.id,))
        result = cursor.fetchone()

        # Parse the current items into a list, or use an empty list if there are no items
        if result:
            items = ast.literal_eval(result)
        else:
            items = []

        currentItemID = getCurrentItemID()

        # Append the new item to the list
        items.append(currentItemID)

        # Update the items field by appending the new item
        cursor.execute(
            "UPDATE stats SET itemIDs = %s WHERE user_id = %s", str(items), interaction.user.id)
        conn.commit()

        # insert itemID and card name into the cards table

        cursor.execute("INSERT INTO cards (itemID, cardName) VALUES (%s, %s)", (currentItemID, output[0]))
        conn.commit()

        # Increment the current item ID for the next item
        incrementCurrentItemID()

    finally:
        cursor.close()
        conn.close()

    file = discord.File(cardFilePath, filename="card.png")

    # Edit the initial deferred response to include the embed with the image file
    await interaction.followup.send(file=file)



bot.run(TOKEN)
