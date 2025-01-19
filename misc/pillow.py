from PIL import Image, ImageDraw, ImageFont
import os

# Create a new image with a white background
width = 800
height = 400
background_color = (255, 255, 255)  # White
image = Image.new('RGB', (width, height), background_color)

# Create a draw object
draw = ImageDraw.Draw(image)

# Set up the font
# Note: The actual font path may need to be adjusted based on your system
font_size = 48
try:
    # Try to use DejaVu Sans as it's often the default Sans Serif font in GIMP
    font = ImageFont.truetype("DejaVuSans.ttf", font_size)
except OSError:
    try:
        # Alternative path for DejaVu Sans
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except OSError:
        # Fallback to default font if DejaVu Sans is not available
        print("DejaVu Sans font not found, using default font")
        font = ImageFont.load_default()

# Add text to the image
text = "Hello, World!"
text_color = (0, 0, 0)  # Black

# Get text size
text_bbox = draw.textbbox((0, 0), text, font=font)
text_width = text_bbox[2] - text_bbox[0]
text_height = text_bbox[3] - text_bbox[1]

# Calculate center position
x = (width - text_width) // 2
y = (height - text_height) // 2

# Draw the text
draw.text((x, y), text, font=font, fill=text_color)

# Save the image
output_path = "hello_world.png"
image.save(output_path)
print(f"Image saved as {output_path}")