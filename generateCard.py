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

from const import COLORS, DATABASE_PATH, CARD_TEMPLATE_PATH

client = OpenAI(api_key=OPENAI_KEY)

async def generatePlayingCardWithImage(description: str, health: int=50, damage: int=20, type: str='standard') -> list: # Json schema imageUrl
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
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf", 48)
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
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf", 32)
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

def generateCardImageFromItemId(cardId: str) -> Image:
    # Connect to database and fetch card data
   #with sqlite3.connect('/home/daniel/Documents/myCode/Omniplexium-Eternal/discorddb.db') as conn:
    with sqlite3.connect('./discorddb.db') as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM cards WHERE cardId = ?", (cardId,))
        cardData = cursor.fetchone() # (cardId, itemName, userId, itemId, description, health, imagePrompt, imageUrl)
        if not cardData:
            raise ValueError(f"No card found with ID {cardId}")

        cursor.execute("SELECT * FROM attacks WHERE cardId = ?", (cardId,))
        attackData = cursor.fetchall() # [(attackId, cardId, attackName, attackDescription, attackDamage, attackSpeed, attackCooldown, attackHitrate), ...]
        if not cardData:
            raise ValueError(f"No attacks found for card ID {cardId}")

        attackNames = [attack[2] for attack in attackData]
        attackDescriptions = [attack[3] for attack in attackData]
        attackStats = [(attack[4], attack[5], attack[6], attack[7]) for attack in attackData]

    # Get the image URL and health from card data
    itemName = cardData[1]
    imageUrl = cardData[7]
    health = cardData[5] # Get health value from database

    try:
        # Download the image from URL
        #response = requests.get(imageUrl)
        #response.raise_for_status() # Raise an exception for bad status codes
        # response.content is the image data in bytes
        #card_image = Image.open('/home/daniel/Documents/myCode/Omniplexium-Eternal/img-BXjQYa1Nh2znIoEbFT9t7HQq.png')
        card_image = Image.open('./img-BXjQYa1Nh2znIoEbFT9t7HQq.png')

        # Open the card template
        #template = Image.open('/home/daniel/Documents/myCode/Omniplexium-Eternal/cardTemplate.png')
        template = Image.open('./cacheDir/cardTemplate.png')

        # Ensure both images are in RGBA mode for proper overlay
        card_image = card_image.convert('RGBA')
        template = template.convert('RGBA')

        # Resize the card image to fit the template
        card_image = card_image.resize((845, 845), Image.Resampling.LANCZOS)

        # Create a new image with the same size as the template
        final_image = Image.new('RGBA', template.size)

        # Calculate position to center the card image on the template
        x = (template.width - card_image.width) // 2
        y = (template.height - card_image.height) - 1034

        # Paste the template first
        final_image.paste(template, (0, 0))

        # Paste the card image on top
        final_image.paste(card_image, (x, y), card_image)

        # Add text (health and item name)
        draw = ImageDraw.Draw(final_image)
        
        # Load fonts with different sizes
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
        attack_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        description_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)  # Smaller size for descriptions

        # Position for health text (top right corner)
        health_x = template.width - 200  # Adjust X coordinate for right alignment
        health_y = 150  # Adjust Y coordinate for top alignment

        # Position for item name (top left corner)
        name_x = 250  # Adjust X coordinate for left alignment
        name_y = 120  # Same Y coordinate as health for alignment

        # Draw health value with white text and black outline
        outline_color = "black"
        # Draw health outline
        for offset_x, offset_y in [(2,2), (-2,2), (2,-2), (-2,-2)]:
            draw.text((health_x + offset_x, health_y + offset_y), str(health),
                     fill=outline_color, font=font, anchor="mm")
        # Draw health main text
        draw.text((health_x, health_y), str(health),
                 fill="white", font=font, anchor="mm")

        # Draw item name with the same style
        # Draw item name outline
        for offset_x, offset_y in [(2,2), (-2,2), (2,-2), (-2,-2)]:
            draw.text((name_x + offset_x, name_y + offset_y), itemName,
                     fill=outline_color, font=font, anchor="mm")
        # Draw item name main text
        draw.text((name_x, name_y), itemName,
                 fill="white", font=font, anchor="mm")

        # Draw attack names and descriptions
        attack_start_y = 1200  # Starting Y position for first attack name
        attack_x = 50  # Same X alignment as item name
        spacing = 250  # Vertical spacing between attack names
        description_offset_y = 50  # Vertical offset for description below attack name

        # Draw each attack name and description
        for i, (attack_name, attack_description) in enumerate(zip(attackNames, attackDescriptions)):
            current_y = attack_start_y + (i * spacing)
            
            # Draw outline for attack name
            for offset_x, offset_y in [(1,1), (-1,1), (1,-1), (-1,-1)]:
                draw.text((attack_x + offset_x, current_y + offset_y), attack_name,
                         fill=outline_color, font=attack_font, anchor="lm")
            # Draw attack name main text
            draw.text((attack_x, current_y), attack_name,
                     fill="white", font=attack_font, anchor="lm")
            
            # Draw attack description below the name
            description_y = current_y + description_offset_y
            # Draw outline for description
            for offset_x, offset_y in [(1,1), (-1,1), (1,-1), (-1,-1)]:
                draw.text((attack_x + offset_x, description_y + offset_y), attack_description,
                         fill=outline_color, font=description_font, anchor="lm")
            # Draw description main text
            draw.text((attack_x, description_y), attack_description,
                     fill="white", font=description_font, anchor="lm")

        return final_image

    except requests.RequestException as e:
        raise Exception(f"Failed to download image: {str(e)}")
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

if __name__ == '__main__':
    genStartTime = time.time()
    imgObj = generateCardImageFromItemId(1)
    print(f"Time taken: {time.time() - genStartTime:.2f}s")
    # save the image
    imgSaveTime = time.time()
    imgObj.save("card.png")
    print(f"Time taken to save: {time.time() - imgSaveTime:.2f}s")