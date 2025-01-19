import discord
from discord import app_commands
import os
import sqlite3
from PIL import Image

from const import DATABASE_PATH, CARD_DATA_IMAGES_PATH

from helperFunctions.generateCard import generatePlayingCardWithImage, makeCardFromJson

async def generateCardFunc(interaction: discord.Interaction, prompt: str = "prompt") -> None:
    # Defer the response to allow more time for processing
    await interaction.response.defer()
    
    cardData: list = await generatePlayingCardWithImage(prompt) # returns a list of the card data and the image URL

    card: Image = await makeCardFromJson(cardData[0], cardData[1]) # returns a PIL Image object

    print(cardData[0])

    # Update the user's items in the database
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        # Fetch the current highest itemID
        cursor.execute("SELECT MAX(itemId) FROM cards")
        result = cursor.fetchone()
        currentItemId = result[0] + 1 if result[0] is not None else 1
        
        cursor.execute(
            "INSERT INTO cards (itemName, userId, cardId, description, health, imagePrompt, imageUrl) VALUES (?, ?, ?, ?, ?, ?, ?)", 
            (cardData[0]['name'], interaction.user.id, currentItemId, cardData[0]['description'], cardData[0]['health'], prompt, cardData[1]))
        conn.commit()
        
        cursor.execute(
            "INSERT INTO attacks (cardId, attackName, attackDescription, attackDamage, attackSpeed, attackCooldown, attackHitrate) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (currentItemId, cardData[0]['attacks'][0]['name'], cardData[0]['attacks'][0]['description'], cardData[0]['attacks'][0]['attack_damage'], 
            cardData[0]['attacks'][0]['attack_speed'], cardData[0]['attacks'][0]['attack_cooldown'], cardData[0]['attacks'][0]['attack_hitrate'])
            )

        # Save the card image
        card_name = f"{currentItemId}.png"
        
        if not os.path.exists(CARD_DATA_IMAGES_PATH):
            os.makedirs(CARD_DATA_IMAGES_PATH)
        cardFilePath = f'{CARD_DATA_IMAGES_PATH}/{card_name}'
        
        card.save(cardFilePath)

    file = discord.File(cardFilePath, filename="card.png")
    # Edit the initial deferred response to include the embed with the image file
    await interaction.followup.send(file=file)

slashCommandGenerateCard = app_commands.Command(
    name="generate-card", # no spaces or capitals allowed
    description="Generate a new Card based off a prompt!",
    callback=generateCardFunc,
)