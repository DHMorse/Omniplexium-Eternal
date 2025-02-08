import sqlite3
import requests
import time
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
from secret_const import OPENAI_KEY
import json
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import sqlite3
from io import BytesIO
import time
from typing import Tuple, Dict


from const import COLORS, DATABASE_PATH, CARD_TEMPLATE_PATH

client = OpenAI(api_key=OPENAI_KEY)

async def generatePlayingCardWithImage(description: str, health: int=50, damage: int=20, type: str='standard') -> Tuple[dict, str]: # Json schema imageUrl
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
    return (data, image_url)


def generateCardImageFromItemId(cardId: str) -> Image:
    # Connect to database and fetch card data
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM cards WHERE cardId = ?", (cardId,))
        cardData = cursor.fetchone()
        if not cardData:
            raise ValueError(f"No card found with ID {cardId}")

        cursor.execute("SELECT * FROM attacks WHERE cardId = ?", (cardId,))
        attackData = cursor.fetchall()
        if not cardData:
            raise ValueError(f"No attacks found for card ID {cardId}")


        attackNames = [attack[2] for attack in attackData]
        attackDescriptions = [attack[3] for attack in attackData]
        attackStats = [(attack[4], attack[5], attack[6], attack[7]) for attack in attackData]

    cardImgPath = cardData[8]
    itemName = cardData[1]
    health = cardData[5]

    try:
        card_image = Image.open(cardImgPath)
        template = Image.open(CARD_TEMPLATE_PATH)

        card_image = card_image.convert('RGBA')
        template = template.convert('RGBA')

        card_image = card_image.resize((845, 845), Image.Resampling.LANCZOS)

        final_image = Image.new('RGBA', template.size)

        x = (template.width - card_image.width) // 2
        y = (template.height - card_image.height) - 1034

        final_image.paste(template, (0, 0))
        final_image.paste(card_image, (x, y), card_image)

        draw = ImageDraw.Draw(final_image)
        
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
        attack_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        description_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)

        health_x = template.width - 200
        health_y = 150
        name_x = 250
        name_y = 120

        # Draw health outline and text
        outline_color = "black"
        for offset_x, offset_y in [(2,2), (-2,2), (2,-2), (-2,-2)]:
            draw.text((health_x + offset_x, health_y + offset_y), str(health),
                     fill=outline_color, font=font, anchor="mm")
        draw.text((health_x, health_y), str(health),
                 fill="white", font=font, anchor="mm")

        # Draw item name outline and text
        for offset_x, offset_y in [(2,2), (-2,2), (2,-2), (-2,-2)]:
            draw.text((name_x + offset_x, name_y + offset_y), itemName,
                     fill=outline_color, font=font, anchor="mm")
        draw.text((name_x, name_y), itemName,
                 fill="white", font=font, anchor="mm")

        # Helper function for text wrapping
        def wrap_text(text, font, max_width):
            words = text.split()
            lines = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                line = ' '.join(current_line)
                bbox = font.getbbox(line)[2]  # Get width of current line
                
                if bbox > max_width:
                    if len(current_line) == 1:
                        lines.append(line)
                        current_line = []
                    else:
                        current_line.pop()
                        lines.append(' '.join(current_line))
                        current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            return lines

        # Draw attack names and descriptions with wrapping
        attack_start_y = 1200
        attack_x = 50
        spacing = 250
        description_offset_y = 50
        max_width = template.width - 100  # Maximum width for text wrapping

        current_y = attack_start_y
        for attack_name, attack_description in zip(attackNames, attackDescriptions):
            # Draw attack name
            for offset_x, offset_y in [(1,1), (-1,1), (1,-1), (-1,-1)]:
                draw.text((attack_x + offset_x, current_y + offset_y), attack_name,
                         fill=outline_color, font=attack_font, anchor="lm")
            draw.text((attack_x, current_y), attack_name,
                     fill="white", font=attack_font, anchor="lm")
            
            # Draw wrapped description
            description_y = current_y + description_offset_y
            wrapped_lines = wrap_text(attack_description, description_font, max_width)
            
            for line in wrapped_lines:
                # Draw outline for each line
                for offset_x, offset_y in [(1,1), (-1,1), (1,-1), (-1,-1)]:
                    draw.text((attack_x + offset_x, description_y + offset_y), line,
                             fill=outline_color, font=description_font, anchor="lm")
                # Draw main text for each line
                draw.text((attack_x, description_y), line,
                         fill="white", font=description_font, anchor="lm")
                description_y += description_font.size + 5  # Add spacing between lines
            
            # Update Y position for next attack, accounting for wrapped text
            line_count = len(wrapped_lines)
            current_y += spacing + (line_count - 1) * (description_font.size + 5)

        return final_image

    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")