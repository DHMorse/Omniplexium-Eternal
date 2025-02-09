import discord
from discord import app_commands
import sqlite3
import os
import requests
from PIL import Image, ImageDraw, ImageFont

from const import DATABASE_PATH, CACHE_DIR_PFP, LEADERBOARD_PIC, DEFUALT_PROFILE_PIC
from helperFunctions.main import xpToLevel

async def leaderboardFunc(interaction: discord.Interaction, type: str = 'level') -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        # Determine the query based on the selected type
        if type == "money":
            cursor.execute("SELECT userId, username, money FROM users ORDER BY money DESC, xp DESC LIMIT 10")
            leaderboard_data = cursor.fetchall()
        else:  # Default to "level"
            type = 'level' # handles edge case where the user types something other than 'money' or 'level'
            cursor.execute("SELECT userId, username, xp FROM users ORDER BY xp DESC, xp DESC LIMIT 10")
            leaderboard_data = cursor.fetchall()

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

        user = await interaction.client.fetch_user(user_id)
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

slashCommandLeaderboard = app_commands.Command(
    name="leaderboard", # no spaces or capitals allowed
    description="Display the leaderboard based on level or money.",
    callback=leaderboardFunc,
)