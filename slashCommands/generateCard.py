import discord
from discord import app_commands
import os
import sqlite3
from PIL import Image
import requests
import traceback

from typing import Tuple

from const import DATABASE_PATH, CARD_IMG_PFP_PATH, CARD_IMG_CARD_PATH

from helperFunctions.generateCard import generatePlayingCardWithImage, generateCardImageFromItemId
from helperFunctions.main import logError

async def generateCardFunc(interaction: discord.Interaction, prompt: str) -> None:
    try:
        # Defer the response to allow more time for processing
        await interaction.response.defer()
        
        cardData: Tuple[dict, str] = await generatePlayingCardWithImage(prompt) # returns a list of the card data and the image URL

        # Update the user's items in the database
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor: sqlite3.Cursor = conn.cursor()

            # Fetch the current highest itemID
            cursor.execute("SELECT MAX(itemId) FROM cards")
            result: tuple[int] | None = cursor.fetchone()
            currentItemId: int = result[0] + 1 if result[0] is not None else 1
            
            # Save the card image
            card_name: str = f"{currentItemId}.png"
            
            if not os.path.exists(CARD_IMG_PFP_PATH):
                os.makedirs(CARD_IMG_PFP_PATH)
            cardPfpPath: str = f'{CARD_IMG_PFP_PATH}/{card_name}'

            cardImage: requests.Response = requests.get(cardData[1])
            with open(cardPfpPath, 'wb') as card:
                card.write(cardImage.content)
            
            cardPath: str = f'{CARD_IMG_CARD_PATH}/{card_name}'

            cursor.execute(
                "INSERT INTO cards (itemName, userId, cardId, description, health, imagePrompt, imageUrl, imagePfpPath, imagePath) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                (
                    cardData[0]['name'], 
                    interaction.user.id, 
                    currentItemId, 
                    cardData[0]['description'], 
                    cardData[0]['health'], 
                    cardData[0]['image_prompt'],
                    cardData[1],
                    cardPfpPath, 
                    cardPath),
                )
            conn.commit()
            
            for attack in cardData[0]['attacks']:
                cursor.execute(
                    "INSERT INTO attacks (cardId, attackName, attackDescription, attackDamage, attackSpeed, attackCooldown, attackHitrate) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (currentItemId, attack['name'], attack['description'], attack['attack_damage'], attack['attack_speed'], attack['attack_cooldown'], 
                    attack['attack_hitrate'])
                    )
            conn.commit()

            card: Image.Image = generateCardImageFromItemId(currentItemId)

            card.save(cardPath)

        file: discord.File = discord.File(cardPath, filename="card.png")

        # Edit the initial deferred response to include the embed with the image file
        await interaction.followup.send(file=file)
    except Exception as e:
        await logError(interaction, e, traceback.format_exc(), "generateCardFunc")

slashCommandGenerateCard: app_commands.Command = app_commands.Command(
    name="generate-card", # no spaces or capitals allowed
    description="Generate a new Card based off a prompt!",
    callback=generateCardFunc,
)

# Example data for a card
exampleData: dict[str, str | int | list[dict[str, str | int]]] = {'name': 'The Stalwart Squire', 
        'description': 'A short man with a determined expression, dressed in a simple tunic and wielding a sturdy wooden sword, ready to prove his worth in battle.', 
        'health': 50, 
        'attacks': [
            {
                'name': 'Swift Slash', 
                'description': 'A quick strike with his wooden sword, aiming for a precise tap that catches his opponent off-guard.', 
                'attack_damage': 20, 
                'attack_speed': 40, 
                'attack_cooldown': 0, 
                'attack_hitrate': 90
                }, 
                {
                'name': 'Courageous Stab', 
                'description': 'A forward lunge that utilizes all his strength, driving the tip of his sword toward the foe with unwavering confidence.', 
                'attack_damage': 30, 
                'attack_speed': 20, 
                'attack_cooldown': 1, 
                'attack_hitrate': 85
                }, {
                'name': 'Heroic Charge', 
                'description': 'A powerful charge that combines speed and determination, delivering a heavier blow but requiring him a breath to regroup afterward.', 
                'attack_damage': 40, 
                'attack_speed': 10, 
                'attack_cooldown': 3, 
                'attack_hitrate': 80
                }
                ], 
                'image_prompt': 'A short man dressed in a tunic wielding a wooden sword, looking determined in a classic fantasy setting.', 
                'image_url': 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-mmJwXK6t0M8xnbz6QdLzHbqk/user-kSPgxUbWefOFLtDjBNig841G/img-VuOnjbdKVF50jKCk3qRmorZg.png?st=2025-01-19T17%3A51%3A21Z&se=2025-01-19T19%3A51%3A21Z&sp=r&sv=2024-08-04&sr=b&rscd=inline&rsct=image/png&skoid=d505667d-d6c1-4a0a-bac7-5c84a87759f8&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2025-01-19T01%3A15%3A00Z&ske=2025-01-20T01%3A15%3A00Z&sks=b&skv=2024-08-04&sig=W7%2Bi5621T2nliWHl/MwTPWkdOxSe/bSE%2Bzk8WiESMUY%3D'
                }