from cardAI import playingCard
from imageMaker import makeCard

def generate(prompt, type='standard'):
    output = playingCard(prompt, type=type)
    return makeCard(output[0], output[1])