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
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import os
import requests
import mysql.connector  # Use mysql-connector-python for MariaDB/MySQL

from secret_const import TOKEN, DATABASE_CONFIG

from const import CACHE_DIR_PFP, LEADERBOARD_PIC, DEFUALT_PROFILE_PIC

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Connect to MariaDB database
conn = mysql.connector.connect(**DATABASE_CONFIG)
cursor = conn.cursor()

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

# Increment points on each message
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    username = message.author.name

    # Check if user exists in the database
    cursor.execute("SELECT points, level, money FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()

    if result:
        # Update points if the user already exists
        new_points = result[0] + 1
        cursor.execute("UPDATE users SET points = %s WHERE user_id = %s", (new_points, user_id))
    else:
        # Insert new user record if they don't exist
        cursor.execute(
            "INSERT INTO users (user_id, username, points, level, money) VALUES (%s, %s, %s, %s, %s)",
            (user_id, username, 1, 0, 0.00)
        )

    # Commit the transaction
    conn.commit()

    # Continue processing other commands if any
    await bot.process_commands(message)

# Command to show user stats (optional)
@bot.command()
async def stats(ctx, member: discord.Member = None):
    member = member or ctx.author
    cursor.execute("SELECT points, level, money FROM users WHERE user_id = %s", (member.id,))
    result = cursor.fetchone()

    if result:
        points, level, money = result
        await ctx.send(f"{member.name}'s Stats:\nPoints: {points}\nLevel: {level}\nMoney: ${money}")
    else:
        await ctx.send(f"{member.name} has no records in the database.")

@bot.command()
async def leaderboard(ctx):
    # Query the top 10 users by points
    cursor.execute("SELECT user_id, username, points FROM users ORDER BY points DESC LIMIT 10")
    leaderboard_data = cursor.fetchall()

    # Create an image for the leaderboard
    image_width = 600
    image_height = 770
    background_color = (54, 57, 62)  # Dark grey background
    image = Image.new("RGB", (image_width, image_height), background_color)
    
    # Load font for text
    font_size = 30
    
    # the font could be swapped for helvetica or something else, 
    # arial isn't installed on everything by default
    font = ImageFont.truetype("arial.ttf", font_size) 
    
    # Initialize drawing context
    draw = ImageDraw.Draw(image)

    # Set up leaderboard rendering variables
    count = 0
    y_offset = 10
    for user_id, username, points in leaderboard_data:
        # Skip the user with ID 1175890644191957013 this is eli bots id, and this bot is not eli bot lmao
        if user_id == 1175890644191957013:
            continue

        user = ctx.bot.get_user(user_id)
        count += 1

        # Ensure the directory exists
        profile_picture_dir = os.path.join(os.path.expanduser(CACHE_DIR_PFP))  # Assuming CACHE_DIR_PFP is the path to your cache dir
        if not os.path.exists(profile_picture_dir):
            os.makedirs(profile_picture_dir)

        # Check if profile picture is in cache
        profile_picture_path = os.path.join(os.path.expanduser(CACHE_DIR_PFP), f"{user_id}.png")

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

        # Draw rank, username, and points
        draw.text((100, y_offset + 10), f"•  #{count} • {username}", fill=rank_color, font=font)
        draw.text((390, y_offset + 10), f"{points:,} pts", fill=(255, 255, 255), font=font)  # Points in white

        # Increment y_offset for next user
        y_offset += 75
        if count == 10:
            break

    # Save the leaderboard image
    image.save(LEADERBOARD_PIC)

    # Create an embed for the leaderboard
    embed = discord.Embed(title="Points Leaderboard", color=0x282b30)
    embed.set_image(url="attachment://leaderboard.png")

    # Send the embed with the leaderboard image
    await ctx.send(embed=embed, file=discord.File(LEADERBOARD_PIC))

bot.run(TOKEN)
