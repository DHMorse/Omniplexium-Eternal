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
        # Create canvas with same dimensions but better spacing
        card_width, card_height = 800, 1500
        card = Image.new("RGB", (card_width, card_height), "white")
        draw = ImageDraw.Draw(card)

        # Increased font sizes significantly
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 48)  # Increased from 36
            stat_font = ImageFont.truetype("arialbd.ttf", 36)   # Increased from 28
            text_font = ImageFont.truetype("arialbd.ttf", 32)   # Increased from 22
        except IOError:
            print("Failed to load Arial Bold, falling back to default font")
            title_font = ImageFont.load_default()
            stat_font = ImageFont.load_default()
            text_font = ImageFont.load_default()

        # Border
        border_color = (220, 220, 220)
        draw.rectangle([(10, 10), (card_width - 10, card_height - 10)], outline=border_color, width=10)

        # Character Image - maintained same size but adjusted positioning
        image_max_width = card_width - 80  # Slightly smaller to add padding
        image_max_height = 480
        character_image.thumbnail((image_max_width, image_max_height))
        # Center the image
        image_x = (card_width - character_image.width) // 2
        card.paste(character_image, (image_x, 30))

        # Title and Health Box
        y_offset = 520

        # Title Box - wider to use more space
        draw.rectangle([(40, y_offset), (card_width - 40, y_offset + 70)], fill="lightgrey")
        # Center the title text
        title_width = draw.textlength(card_data['name'], font=title_font)
        title_x = (card_width - title_width) // 2
        draw.text((title_x, y_offset + 10), card_data['name'], font=title_font, fill="black")
        y_offset += 90

        # Health - positioned with more space
        health_text = f"Health: {card_data['health']}"
        health_width = draw.textlength(health_text, font=stat_font)
        health_x = (card_width - health_width) // 2
        draw.text((health_x, y_offset), health_text, font=stat_font, fill="red")
        y_offset += 70

        # Description - using more horizontal space
        description_text = card_data['description']
        # Reduced wrap width to create longer lines
        wrapped_description = textwrap.fill(description_text, width=40)
        # Add padding from both sides
        draw.text((60, y_offset), wrapped_description, font=text_font, fill="black")
        y_offset += 160  # Increased spacing after description

        # Attacks - better formatted with more space
        for attack in card_data['attacks']:
            # Attack Name
            draw.text((60, y_offset), attack['name'], font=stat_font, fill="black")
            y_offset += 45

            # Attack Description
            wrapped_attack_text = textwrap.fill(attack['description'], width=40)
            draw.text((60, y_offset), wrapped_attack_text, font=text_font, fill="black")
            y_offset += 70

            # Attack Stats with better spacing
            stats_text = f"Damage: {attack['attack_damage']}  Speed: {attack['attack_speed']}  Cooldown: {attack['attack_cooldown']}"
            draw.text((60, y_offset), stats_text, font=text_font, fill="grey")
            y_offset += 80

        return card
    else:
        print("Unable to create card image due to image loading failure.")
        return None
