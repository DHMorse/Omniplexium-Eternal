import discord
from discord.ext import commands

from secret_const import TOKEN

# Colors for each level range
COLOR_RANGES = [
    (0, 10, 0xFFFF00, 0xFFA500),  # Yellow to Orange
    (11, 20, 0xFFA500, 0xFF4500), # Orange to Red-Orange
    (21, 30, 0xFF4500, 0x9ACD32), # Red-Orange to Yellow-Green
    (31, 40, 0x9ACD32, 0x008000), # Yellow-Green to Green
    (41, 50, 0x008000, 0x0000FF), # Green to Blue
    (51, 60, 0x0000FF, 0x20B2AA), # Blue to Blue-Green
    (61, 70, 0x20B2AA, 0x8A2BE2), # Blue-Green to Blue-Violet
    (71, 80, 0x8A2BE2, 0xC71585), # Blue-Violet to Red-Violet
    (81, 90, 0xC71585, 0x9400D3), # Red-Violet to Violet
    (91, 100, 0x9400D3, 0x9400D3) # Violet to Violet (end color remains constant)
]

bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def create_roles(ctx):
    guild = ctx.guild
    for i in range(1, 101):
        role_name = f"Level {i}"
        existing_role = discord.utils.get(guild.roles, name=role_name)
        if not existing_role:
            color = get_gradient_color(i)
            await guild.create_role(name=role_name, color=discord.Color(color), hoist=True)
            print(f"Created role: {role_name} with color: #{color:06x}")
        else:
            print(f"Role {role_name} already exists.")
    await ctx.send("Roles created successfully.")

def get_gradient_color(level):
    # Find the correct color range for the level
    for start, end, start_color, end_color in COLOR_RANGES:
        if start <= level <= end:
            # Calculate the blend factor between start and end colors
            blend_factor = (level - start) / (end - start)
            return blend_colors(start_color, end_color, blend_factor)
    return 0xFFFFFF  # Default color if something goes wrong

def blend_colors(start_color, end_color, blend_factor):
    # Extract RGB components from each color
    start_r = (start_color >> 16) & 0xFF
    start_g = (start_color >> 8) & 0xFF
    start_b = start_color & 0xFF
    end_r = (end_color >> 16) & 0xFF
    end_g = (end_color >> 8) & 0xFF
    end_b = end_color & 0xFF

    # Calculate the blended color components
    r = int(start_r + (end_r - start_r) * blend_factor)
    g = int(start_g + (end_g - start_g) * blend_factor)
    b = int(start_b + (end_b - start_b) * blend_factor)

    # Combine components back into a single integer color value
    return (r << 16) + (g << 8) + b

# Run the bot
bot.run(TOKEN)
