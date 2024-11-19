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
import json
from datetime import datetime, timezone

from secret_const import TOKEN

from const import CACHE_DIR_PFP, LEADERBOARD_PIC, DEFUALT_PROFILE_PIC, LOG_CHANNEL_ID, ADMIN_LOG_CHANNEL_ID, CARD_DATA_JSON_PATH, CARD_DATA_IMAGES_PATH
from const import pool 
from const import xpToLevel, updateXpAndCheckLevelUp

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
        cursor.execute("SELECT xp, money FROM stats WHERE userId = %s", (user_id,))
        result = cursor.fetchone()

        if result:
            # Directly call level-up update function and get level-up flag
            await updateXpAndCheckLevelUp(ctx=message, bot=bot, xp=1, add=True)
        else:
            # Insert new user record if they don't exist
            cursor.execute(
                "INSERT INTO stats (userId, username, xp, money, items) VALUES (%s, %s, %s, %s, %s)",
                (user_id, username, 1, 0, '[]')
            )
            conn.commit()

    finally:
        cursor.close()
        conn.close()

    # Continue processing other commands if any
    await bot.process_commands(message)

@bot.event
async def on_member_join(member: discord.Member):
    # Calculate account age
    now = datetime.now(timezone.utc)
    account_creation_date = member.created_at
    account_age = now - account_creation_date
    years = account_age.days // 365
    months = (account_age.days % 365) // 30
    days = (account_age.days % 365) % 30

    # Format date and time
    join_time = now.strftime("Today at %I:%M %p")

    # Embed setup
    embed = discord.Embed(
        title="Member Joined",
        description=f"**Member:** {member.mention}\n"
                    f"**Account Age:** {years} Years, {months} Months, {days} Days\n",
        color=discord.Color.green(),
        timestamp=now  # Automatically add the timestamp to the footer
    )
    embed.set_footer(text=join_time)
    embed.set_thumbnail(url=member.display_avatar.url)

    channel = bot.get_channel(LOG_CHANNEL_ID)

    # Send the embed to the server's system channel (or any specific channel)
    if channel:
        await channel.send(embed=embed)

@bot.tree.command(name="leaderboard", description="Display the leaderboard based on level or money.")
@app_commands.describe(type="Choose between 'level' or 'money' for the leaderboard type.")
async def leaderboard(interaction: discord.Interaction, type: str = "level"):
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        # Determine the query based on the selected type
        if type == "money":
            cursor.execute("SELECT userId, username, money FROM stats ORDER BY money DESC, xp DESC LIMIT 10")
            leaderboard_data = cursor.fetchall()
        else:  # Default to "level"
            type = 'level' # handles edge case where the user types something other than 'money' or 'level'
            cursor.execute("SELECT userId, username, xp FROM stats ORDER BY xp DESC, xp DESC LIMIT 10")
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

    output = await genAiCard(prompt) # returns a list, the first item is the json data, the second is the image url
    card = await makeCardFromJson(output[0], output[1]) # output[1] is doing nothing we over write the varible in the file

    # Update the user's items in the database
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:

        # Fetch the current highest itemID
        cursor.execute("SELECT MAX(itemId) FROM cards")
        result = cursor.fetchone()
        currentItemId = result[0] + 1 if result[0] is not None else 0

        cursor.execute("INSERT INTO cards (itemName, userId) VALUES (%s, %s)", (output[0]['name'], interaction.user.id))
        conn.commit()


        # Save the card data as a JSON file
        output_filename = f"{currentItemId}.json"
        output_path = os.path.join(CARD_DATA_JSON_PATH, output_filename)

        if not os.path.exists(CARD_DATA_JSON_PATH):
            os.makedirs(CARD_DATA_JSON_PATH)

        with open(output_path, 'w') as json_file:
            json.dump(output[0], json_file, indent=4)


        # Save the card image
        card_name = f"{currentItemId}.png"
        
        if not os.path.exists(CARD_DATA_IMAGES_PATH):
            os.makedirs(CARD_DATA_IMAGES_PATH)

        cardFilePath = f'{CARD_DATA_IMAGES_PATH}/{card_name}'
        
        card.save(cardFilePath)

    finally:
        cursor.close()
        conn.close()

    file = discord.File(cardFilePath, filename="card.png")

    # Edit the initial deferred response to include the embed with the image file
    await interaction.followup.send(file=file)



bot.run(TOKEN)
