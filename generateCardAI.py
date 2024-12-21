from openai import OpenAI
from secret_const import openai_key
import json

client = OpenAI(api_key=openai_key)

async def genAiCard(description: str, health: int=50, damage: int=20, type: str='standard') -> list:
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
                    "attack_cooldown"
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
