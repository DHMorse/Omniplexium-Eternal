from openai import OpenAI
from secret_const import openai_key
import json
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

from const import COLORS

from typing import List

client = OpenAI(api_key=openai_key)

async def generatePlayingCardWithImage(description: str, health: int=50, damage: int=20, 
                    type: str='standard') -> List[dict, str]: # Json schema imageUrl
    true = True
    false = False

    if type == 'standard':
        prompt= f'Generate a playing card. It should have a health of {health}, and various attacks with damages ranging around {damage}. The card cannot reference random mechanics like "stunning the opponent, stopping them for a move" or "distracts the attacker, halving their damage" because you do not have access to these mechanics. You can describe the attack in detail for fun (which is required), but at the end of the day the only thing that matters is the integer values of the attack. Keep the descriptions concise and a maximum of one long sentence. Try to make attacks overall balanced with one great one with a high cooldown.\n\nHere is the prompt for the card: \"{description}\"\n'
    elif type == 'mega':
        prompt= f'Generate a playing card. It should have a health of {health}, a particularly good attack with a damage of {damage*2}, and various attacks with damages ranging around {damage}. The card cannot reference random mechanics like "stunning the opponent, stopping them for a move" or "distracts the attacker, halving their damage" because you do not have access to these mechanics. You can describe the attack in detail for fun (which is required), but at the end of the day the only thing that matters is the integer values of the attack. Keep the descriptions concise and a maximum of one long sentence.\n\nHere is the prompt for the card: \"{description}\"\n'
    
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": prompt
            }
        ]
        },
    ],
    temperature=1,
    max_tokens=1024,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    response_format={
        "type": "json_schema",
        "json_schema": {
        "name": "playing_card",
        "strict": true,
        "schema": {
            "type": "object",
            "properties": {
            "name": {
                "type": "string",
                "description": "The name of the playing card."
            },
            "description": {
                "type": "string",
                "description": "A description of the playing card."
            },
            "health": {
                "type": "number",
                "description": "The health points of the playing card, which must be a multiple of 10."
            },
            "attacks": {
                "type": "array",
                "description": "A list of attacks which the playing card can use.",
                "items": {
                "type": "object",
                "properties": {
                    "name": {
                    "type": "string",
                    "description": "The name of the attack."
                    },
                    "description": {
                    "type": "string",
                    "description": "Description of the attack."
                    },
                    "attack_damage": {
                    "type": "number",
                    "description": "Damage dealt by the attack, which must be a multiple of 10. When damage is higher, generally the attack speed is lower."
                    },
                    "attack_speed": {
                    "type": "number",
                    "description": "Speed of the attack, which must be a multiple of 10. When speed is higher, generally the attack damage is lower."
                    },
                    "attack_cooldown": {
                    "type": "number",
                    "description": "Cooldown of the attack, ranging from 0 to 3. Most attacks have a cooldown of 0 or 1. The best attack, if significantly better than the others, generally has a cooldown of 2 to 3."
                    },
                    "attack_hitrate": {
                    "type": "number",
                    "description": "The hitrate of an attack. Usually 80 to 90 percent. This is the chance that the attack actually does anything. Some attacks can be really powerful but have a low hitrate, and you don't need to compensate with a high cooldown."
                    }
                },
                "required": [
                    "name",
                    "description",
                    "attack_damage",
                    "attack_speed",
                    "attack_cooldown",
                    "attack_hitrate"
                ],
                "additionalProperties": false
                }
            },
            "image_prompt": {
                "type": "string",
                "description": "Prompt for generating an image of the playing card character based on its name and description."
            }
            },
            "required": [
            "name",
            "description",
            "health",
            "attacks",
            "image_prompt"
            ],
            "additionalProperties": false
        }
        }
    }
    )
    generated_text = response.choices[0].message.content
    data = json.loads(generated_text)

    imageResponse = client.images.generate(
        model="dall-e-3",
        prompt=data['image_prompt'],
        size="1024x1024",
        quality="standard",
        n=1,
        )

    image_url = imageResponse.data[0].url
    return [data, image_url]

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
            print(f"{COLORS['red']}Error opening image: {e}{COLORS['reset']}")
            return None
    else:
        print(f"{COLORS['red']}Failed to download the image. Check the URL.{COLORS['reset']}")
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
                    print(f"{COLORS['yellow']}Warning: Using default font for title{COLORS['reset']}")

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
                    print(f"{COLORS['yellow']}Warning: Using default font for text{COLORS['reset']}")

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
        print(f"{COLORS['red']}Unable to create card image due to image loading failure.{COLORS['reset']}")
        return None
