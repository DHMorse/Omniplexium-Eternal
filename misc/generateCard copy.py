import sqlite3
from PIL import Image, ImageDraw, ImageFont
import requests
import os

DATABASE_PATH = '/home/daniel/Documents/myCode/Omniplexium-Eternal/discorddb.db'
CARD_TEMPLATE_PATH = '/home/daniel/Documents/myCode/Omniplexium-Eternal/img/cards/static/cardTemplate.png'

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        line = ' '.join(current_line)
        bbox = font.getbbox(line)[2]
        
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
def generateCardImageFromItemId(cardId: str, title_left_offset: int = 70) -> Image:
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

    cardPfpPath = '/home/daniel/Documents/myCode/Omniplexium-Eternal/img/cards/pfp/2.png'
    itemName = cardData[1]
    health = cardData[5]

    try:
        card_image = Image.open(cardPfpPath)
        template = Image.open(CARD_TEMPLATE_PATH)
        GRRimage = Image.open('/home/daniel/Documents/myCode/Omniplexium-Eternal/img/cards/static/GRR.png')
        FAFimage = Image.open('/home/daniel/Documents/myCode/Omniplexium-Eternal/img/cards/static/FAF.png')
        iceImage = Image.open('/home/daniel/Documents/myCode/Omniplexium-Eternal/img/cards/static/ice.png')
        osuImage = Image.open('/home/daniel/Documents/myCode/Omniplexium-Eternal/img/cards/static/osu.png')

        grr_size = 55
        GRRimage = GRRimage.resize((grr_size, grr_size), Image.Resampling.LANCZOS).convert('RGBA')
        FAFimage = FAFimage.resize((grr_size, grr_size), Image.Resampling.LANCZOS).convert('RGBA')
        iceImage = iceImage.resize((grr_size, grr_size), Image.Resampling.LANCZOS).convert('RGBA')
        osuImage = osuImage.resize((grr_size, grr_size), Image.Resampling.LANCZOS).convert('RGBA')

        card_image = card_image.convert('RGBA')
        template = template.convert('RGBA')
        card_image = card_image.resize((845, 845), Image.Resampling.LANCZOS)

        final_image = Image.new('RGBA', template.size)
        x = (template.width - card_image.width) // 2
        y = (template.height - card_image.height) - 1034

        final_image.paste(template, (0, 0))
        final_image.paste(card_image, (x, y), card_image)

        draw = ImageDraw.Draw(final_image)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        healthFont = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
        attack_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 55)
        description_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 35)
        damage_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 55)

        health_x = template.width - 200
        health_y = 150
        name_x = title_left_offset
        name_y = 120

        outline_color = "black"
        for offset_x, offset_y in [(2,2), (-2,2), (2,-2), (-2,-2)]:
            draw.text((health_x + offset_x, health_y + offset_y), str(health),
                     fill=outline_color, font=healthFont, anchor="mm")
        draw.text((health_x, health_y), str(health),
                 fill="white", font=healthFont, anchor="mm")

        for offset_x, offset_y in [(2,2), (-2,2), (2,-2), (-2,-2)]:
            draw.text((name_x + offset_x, name_y + offset_y), itemName,
                     fill=outline_color, font=font, anchor="lm")
        draw.text((name_x, name_y), itemName,
                 fill="white", font=font, anchor="lm")

        attack_start_y = 1150
        attack_x = 50
        spacing = 180
        description_offset_y = 50
        max_width = template.width - 100

        current_y = attack_start_y
        for attack_name, attack_description, attack_stat in zip(attackNames, attackDescriptions, attackStats):
            damage, attack_speed, cooldown, hitrate = attack_stat[0], attack_stat[1], attack_stat[2], attack_stat[3]
            
            for offset_x, offset_y in [(1,1), (-1,1), (1,-1), (-1,-1)]:
                draw.text((attack_x + offset_x, current_y + offset_y), attack_name,
                         fill=outline_color, font=attack_font, anchor="lm")
            draw.text((attack_x, current_y), attack_name,
                     fill="white", font=attack_font, anchor="lm")

            # Damage icon and value
            attack_name_width = attack_font.getbbox(attack_name)[2]
            grr_x = attack_x + attack_name_width + 20
            grr_y = current_y - (grr_size // 2)
            final_image.paste(GRRimage, (grr_x, grr_y), GRRimage)

            damage_x = grr_x + grr_size + 10
            for offset_x, offset_y in [(1,1), (-1,1), (1,-1), (-1,-1)]:
                draw.text((damage_x + offset_x, current_y + offset_y), str(damage),
                         fill=outline_color, font=damage_font, anchor="lm")
            draw.text((damage_x, current_y), str(damage),
                     fill="white", font=damage_font, anchor="lm")
            
            # Attack speed icon and value
            faf_x = damage_x + 100
            final_image.paste(FAFimage, (faf_x, grr_y), FAFimage)

            attack_speed_x = faf_x + grr_size + 10
            for offset_x, offset_y in [(1,1), (-1,1), (1,-1), (-1,-1)]:
                draw.text((attack_speed_x + offset_x, current_y + offset_y), str(attack_speed),
                         fill=outline_color, font=damage_font, anchor="lm")
            draw.text((attack_speed_x, current_y), str(attack_speed),
                     fill="white", font=damage_font, anchor="lm")
            
            # Cooldown icon and value
            ice_x = attack_speed_x + 100
            final_image.paste(iceImage, (ice_x, grr_y), iceImage)

            cooldown_x = ice_x + grr_size + 10
            for offset_x, offset_y in [(1,1), (-1,1), (1,-1), (-1,-1)]:
                draw.text((cooldown_x + offset_x, current_y + offset_y), str(cooldown),
                         fill=outline_color, font=damage_font, anchor="lm")
            draw.text((cooldown_x, current_y), str(cooldown),
                     fill="white", font=damage_font, anchor="lm")

            # Hitrate icon and value
            osu_x = cooldown_x + 100
            final_image.paste(osuImage, (osu_x, grr_y), osuImage)

            hitrate_x = osu_x + grr_size + 10
            for offset_x, offset_y in [(1,1), (-1,1), (1,-1), (-1,-1)]:
                draw.text((hitrate_x + offset_x, current_y + offset_y), str(hitrate),
                         fill=outline_color, font=damage_font, anchor="lm")
            draw.text((hitrate_x, current_y), str(hitrate),
                     fill="white", font=damage_font, anchor="lm")
            
            description_y = current_y + description_offset_y
            wrapped_lines = wrap_text(attack_description, description_font, max_width)
            for line in wrapped_lines:
                for offset_x, offset_y in [(1,1), (-1,1), (1,-1), (-1,-1)]:
                    draw.text((attack_x + offset_x, description_y + offset_y), line,
                             fill=outline_color, font=description_font, anchor="lm")
                draw.text((attack_x, description_y), line,
                         fill="white", font=description_font, anchor="lm")
                description_y += description_font.size + 3

            current_y += spacing + (len(wrapped_lines) - 1) * (description_font.size + 3)

        return final_image
    
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

if __name__ == '__main__':
    '''with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT imageUrl FROM cards")
        result = cursor.fetchone()
        if not result:
            raise ValueError("No cards found in database")
        imageUrl = result[0]
    response = requests.get(imageUrl)
    with open('downloaded_image.png', 'wb') as f:
        f.write(response.content)'''
    card = generateCardImageFromItemId(2)
    card.show()
    card.save('test_card.png')