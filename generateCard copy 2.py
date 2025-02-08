import sqlite3
import requests
import time
from PIL import Image, ImageDraw, ImageFont

def generateCardImageFromItemId(cardId: str) -> Image:
    # Connect to database and fetch card data
    with sqlite3.connect('./discorddb.db') as conn:
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

    itemName = cardData[1]
    imageUrl = cardData[7]
    health = cardData[5]

    try:
        card_image = Image.open('./img-BXjQYa1Nh2znIoEbFT9t7HQq.png')
        template = Image.open('./cacheDir/cardTemplate.png')

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