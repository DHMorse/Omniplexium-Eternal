import requests
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap


async def makeCard(data, url):
    # Example input data
    '''
    card_data = {
        'name': 'Toilet Warrior',
        'description': 'An overpowered fighting human toilet with a big grin, ready to unleash a barrage of amusing yet powerful attacks. Clad in a flashy gladiator outfit with toilet paper as a cape, this character takes pride in their unique fighting style, utilizing humor and strength to dominate in the arena.',
        'health': 100,
        'attacks': [
            {'name': 'Flush Smash', 'description': 'Unleashes a powerful downward strike, flushing enemies away with overwhelming force.', 'attack_damage': 40, 'attack_speed': 10, 'attack_cooldown': 2},
            {'name': 'Squeaky Clean Jab', 'description': 'A quick jab that leaves enemies stunned and slightly cleaner than before.', 'attack_damage': 20, 'attack_speed': 30, 'attack_cooldown': 0},
            {'name': 'Plunger Toss', 'description': 'Throws a plunger with incredible accuracy, causing a solid hit on target.', 'attack_damage': 20, 'attack_speed': 20, 'attack_cooldown': 1},
            {'name': 'Urine Trouble', 'description': 'A sneaky attack that makes foes slip, causing them to lose their balance.', 'attack_damage': 20, 'attack_speed': 25, 'attack_cooldown': 1}
        ],
        'image_url': 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-mmJwXK6t0M8xnbz6QdLzHbqk/user-kSPgxUbWefOFLtDjBNig841G/img-Y8yyEZV5KPih9JGl5foW8Cnq.png?st=2024-11-10T01%3A16%3A44Z&se=2024-11-10T03%3A16%3A44Z&sp=r&sv=2024-08-04&sr=b&rscd=inline&rsct=image/png&skoid=d505667d-d6c1-4a0a-bac7-5c84a87759f8&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-11-09T23%3A04%3A48Z&ske=2024-11-10T23%3A04%3A48Z&sks=b&skv=2024-08-04&sig=fMEsFL44TUEjrV2/QvWpRUoPfUzSSN9wKZM3GrSs1wI%3D'
    }'''

    card_data = data
    card_data["image_url"] = url

    # Download the image with error handling
    response = requests.get(card_data['image_url'])
    if response.status_code == 200:
        try:
            # Load image from the response content in-memory
            image_data = io.BytesIO(response.content)
            character_image = Image.open(image_data)
        except Exception as e:
            print(f"Error opening image: {e}")
    else:
        print("Failed to download the image. Check the URL.")
        character_image = None

    if character_image:
        # Step 2: Create a Canvas for the Card with Doubled Dimensions
        card_width, card_height = 800, 1500  # Double original width and height
        card = Image.new("RGB", (card_width, card_height), "white")
        draw = ImageDraw.Draw(card)

        # Load fonts with doubled sizes
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 36)  # Double font size
            stat_font = ImageFont.truetype("arialbd.ttf", 28)
            text_font = ImageFont.truetype("arialbd.ttf", 22)  # Double font size
        except IOError:
            title_font = ImageFont.load_default()
            stat_font = ImageFont.load_default()
            text_font = ImageFont.load_default()

        # Add Border
        border_color = (220, 220, 220)
        draw.rectangle([(10, 10), (card_width - 10, card_height - 10)], outline=border_color, width=10)  # Double border thickness

        # Step 3: Place Character Image in the Top Section with Increased Size
        image_max_width = card_width - 40  # Double original image width allowance
        image_max_height = 480  # Double original height
        character_image.thumbnail((image_max_width, image_max_height))
        card.paste(character_image, (40, 30))  # Double offsets

        # Step 4: Draw Title and Health Box
        y_offset = 520  # Adjust start position below the larger image

        # Title Box
        draw.rectangle([(40, y_offset), (760, y_offset + 60)], fill="lightgrey")  # Double dimensions
        draw.text((50, y_offset + 10), card_data['name'], font=title_font, fill="black")
        y_offset += 80  # Double spacing

        # Health
        draw.text((40, y_offset), f"Health: {card_data['health']}", font=stat_font, fill="red")
        y_offset += 60  # Double spacing

        # Step 5: Draw Description with Slightly Narrower Text Wrapping
        description_text = card_data['description']
        wrapped_description = textwrap.fill(description_text, width=48)  # Adjusted wrap width for no overflow
        draw.text((40, y_offset), wrapped_description, font=text_font, fill="black")
        y_offset += 220  # Increase space after description for better separation

        # Step 6: Draw Attacks with Stats and Adjusted Text Wrapping
        for attack in card_data['attacks']:
            # Attack Name and Description
            attack_text = f"{attack['name']} - {attack['description']}"
            wrapped_attack_text = textwrap.fill(attack_text, width=48)  # Adjusted wrap width
            draw.text((40, y_offset), wrapped_attack_text, font=text_font, fill="black")
            y_offset += 80  # Double spacing

            # Attack Stats
            stats_text = f"Damage: {attack['attack_damage']}  Speed: {attack['attack_speed']}  Cooldown: {attack['attack_cooldown']}"
            draw.text((40, y_offset), stats_text, font=text_font, fill="grey")
            y_offset += 60  # Double spacing

        # Save the card image
        card_name = f"{data['name']}.png"
        path = f'/home/botuser/bot/cardData/images/{card_name}'
        card.save(path)
        print(f"High-resolution playing card image created as '{card_name}'")
        return path
    else:
        print("Unable to create card image due to image loading failure.")
        return None
