import requests
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

async def makeCardFromJson(data: dict, url: str) -> Image:
    card_data = data
    card_data["image_url"] = url

    # Download the image with error handling
    response = requests.get(card_data['image_url'])
    if response.status_code == 200:
        try:
            image_data = io.BytesIO(response.content)
            character_image = Image.open(image_data)
        except Exception as e:
            print(f"Error opening image: {e}")
            return None
    else:
        print("Failed to download the image. Check the URL.")
        return None

    if character_image:
        # Create canvas
        card_width, card_height = 800, 1500
        card = Image.new("RGB", (card_width, card_height), "white")
        draw = ImageDraw.Draw(card)

        # Try multiple font options that should exist on most systems
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 48)
        except IOError:
            try:
                title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
            except IOError:
                try:
                    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                except IOError:
                    title_font = ImageFont.load_default()
                    print("Warning: Using default font for title")

        try:
            text_font = ImageFont.truetype("arial.ttf", 32)
        except IOError:
            try:
                text_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
            except IOError:
                try:
                    text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
                except IOError:
                    text_font = ImageFont.load_default()
                    print("Warning: Using default font for text")

        # Border
        border_color = (220, 220, 220)
        draw.rectangle([(10, 10), (card_width - 10, card_height - 10)], outline=border_color, width=10)

        # Character Image
        image_max_width = card_width - 80
        image_max_height = 480
        character_image.thumbnail((image_max_width, image_max_height))
        image_x = (card_width - character_image.width) // 2
        card.paste(character_image, (image_x, 30))

        # Calculate the number of characters that will fit
        # Using a simpler approach with a fixed character count that works well with the card width
        chars_per_line = 45  # This should work well with the given card width and font size

        y_offset = 520

        # Title Box
        draw.rectangle([(40, y_offset), (card_width - 40, y_offset + 70)], fill="lightgrey")
        title_width = draw.textlength(card_data['name'], font=title_font)
        title_x = (card_width - title_width) // 2
        draw.text((title_x, y_offset + 10), card_data['name'], font=title_font, fill="black")
        y_offset += 90

        # Health
        health_text = f"Health: {card_data['health']}"
        health_width = draw.textlength(health_text, font=text_font)
        health_x = (card_width - health_width) // 2
        draw.text((health_x, y_offset), health_text, font=text_font, fill="red")
        y_offset += 70

        # Description
        description_text = card_data['description']
        wrapped_description = textwrap.fill(description_text, width=chars_per_line)
        draw.text((50, y_offset), wrapped_description, font=text_font, fill="black")
        y_offset += 160

        # Attacks
        for attack in card_data['attacks']:
            # Attack Name
            draw.text((50, y_offset), attack['name'], font=text_font, fill="black")
            y_offset += 45

            # Attack Description
            attack_desc = textwrap.fill(attack['description'], width=chars_per_line)
            draw.text((50, y_offset), attack_desc, font=text_font, fill="black")
            y_offset += 70

            # Attack Stats
            stats_text = f"Damage: {attack['attack_damage']}  Speed: {attack['attack_speed']}  Cooldown: {attack['attack_cooldown']}"
            draw.text((50, y_offset), stats_text, font=text_font, fill="grey")
            y_offset += 80

        return card
    else:
        print("Unable to create card image due to image loading failure.")
        return None
