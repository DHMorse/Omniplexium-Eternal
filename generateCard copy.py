import requests
import sqlite3
import time
from PIL import Image, ImageDraw, ImageFont


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