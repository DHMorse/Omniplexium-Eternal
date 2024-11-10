from cardAI import playingCard
from imageMaker import makeCard

async def generate_card(prompt, type='standard'):
    output = await playingCard(prompt, type=type)
    return await makeCard(output[0], output[1])