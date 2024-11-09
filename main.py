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

from secret_const import TOKEN, DATABASE_CONFIG

from const import CACHE_DIR_PFP, LEADERBOARD_PIC, DEFUALT_PROFILE_PIC, LOG_CHANNEL_ID, pool, xpToLevel, update_xp_and_check_level_up

from floor10_game_concept import guess_the_number_command


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.all())

    async def setup_hook(self):
        # Add the imported command to the bot’s command tree
        self.tree.add_command(guess_the_number_command)
        await self.tree.sync()  # Sync commands with Discord

bot = MyBot()

#bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Connect to MariaDB database
#conn = mysql.connector.connect(**DATABASE_CONFIG)
#cursor = conn.cursor()

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot is ready. Logged in as {bot.user}')


# Increment xp on each message
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
        cursor.execute("SELECT xp, money FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()

        if result:
            level_up = await update_xp_and_check_level_up(ctx=message, xp=1, add=True)
            if level_up == True:
                cursor.execute("SELECT xp, money FROM users WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                
                channel = bot.get_channel(LOG_CHANNEL_ID)
                print(result[0])
                await channel.send(f"Congratulations, {message.author.mention}! You have leveled up to level {xpToLevel(result[0])}!")
        else:
            # Insert new user record if they don't exist
            cursor.execute(
                "INSERT INTO users (user_id, username, xp, money) VALUES (%s, %s, %s, %s, %s)",
                (user_id, username, 1, 0, 0.00)
            )

    finally:
        cursor.close()
        conn.close()

    # Continue processing other commands if any
    await bot.process_commands(message)

# Command to show user stats (optional)
@bot.command()
async def stats(ctx, member: discord.Member = None):
    member = member or ctx.author
    
    conn = pool.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT xp, money FROM users WHERE user_id = %s", (member.id,))
        result = cursor.fetchone()

        if result:
            xp, money = result
            level = xpToLevel(xp)
            await ctx.send(f"{member.name}'s Stats:\nxp: {xp}\nLevel: {level}\nMoney: ${money}")
        else:
            await ctx.send(f"{member.name} has no records in the database.")
    finally:
        cursor.close()
        conn.close()

@bot.command()
async def reset(ctx, field: str = ""):
    if ctx.author.guild_permissions.administrator != True:
        await ctx.send("You do not have the required permissions to use this command.")
        return
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        if field == "xp":
            cursor.execute("UPDATE users SET xp = %s WHERE user_id = %s", (0, ctx.author.id))
            conn.commit()
            await ctx.send(f"Reset {ctx.author.name}'s xp to 0.")
        elif field == "money":
            cursor.execute("UPDATE users SET money = %s WHERE user_id = %s", (0, ctx.author.id))
            conn.commit()
            await ctx.send(f"Reset {ctx.author.name}'s money to $0.")
        else:
            await ctx.send("Please specify a valid field to reset.")
    finally:
        cursor.close()
        conn.close()

@bot.tree.command(name="leaderboard", description="Display the leaderboard based on level or money.")
@app_commands.describe(type="Choose between 'level' or 'money' for the leaderboard type.")
async def leaderboard(interaction: discord.Interaction, type: str = "level"):
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        # Determine the query based on the selected type
        if type == "money":
            cursor.execute("SELECT user_id, username, money FROM users ORDER BY money DESC, xp DESC LIMIT 10")
            leaderboard_data = cursor.fetchall()
        else:  # Default to "level"
            type = 'level' # handles edge case where the user types something other than 'money' or 'level'
            cursor.execute("SELECT user_id, username, xp FROM users ORDER BY xp DESC, xp DESC LIMIT 10")
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
    font = ImageFont.truetype("arial.ttf", font_size)

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



bot.run(TOKEN)
