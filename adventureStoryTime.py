from openai import OpenAI
from secret_const import OPENROUTER_API_KEY
import asyncio
import time

class StoryMaker:

    def __init__(self):
        self.histories: dict[int, list[dict[str, str]]] = {}

    async def requestBroadener(self, request: str) -> str:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )

        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                "X-Title": "Omniplexium", # Optional. Site title for rankings on openrouter.ai.
            },
            model="sophosympatheia/rogue-rose-103b-v0.2:free",
            messages=[
                {
                    "role": "system",
                    "content": '''You are a detailed plot generator.

You are going to be given a vague, undescriptive story prompt and respond with a detailed starting position for a story to go forward.

Don't generate any dialogue or move the story forward - create a detailed snippet in time for a future "choose your own adventure" story.

Don't be overly terse. Don't add dialogue. This is just a general description of the setting and the character's starting position.'''
                },
                {
                    "role": "user",
                    "content": request
                }
            ]
        )

        return completion.choices[0].message.content

    async def startStory(self, plot: str, id: int, message: str = ''):
        plot = await self.requestBroadener(plot)
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        if id not in self.histories:
            self.histories[id] = [{
                "role": "system",
                "content": f'''This is a choose your own adventure story.
                
This is the plot of the current story:
"""
{plot}
"""
You are going to generate a "first message" for the story. This is going to introduce the plot to the user and give them their first four options.

You are always going to give A, B, C, and D options at the end of the message which details what the last action did and what the next actions will do.

You are going to make it clear to the user who their character is and what the options are, what they do after choosing their option and the effect it has, and what the next options are.

The user has to input A, B, D, or C; OR an obvious description of one of the four choices. The user CANNOT choose anything custom or different than the four choices. If they try; do not let them do anything custom. Tell them to choose a choice, A-D.

Do not let the user type a custom choice or mess with you. If they do, tell them this exactly:

"""
That is not one of the four options. Choose A, B, C, or D.
"""'''
            },
            {
                "role": "user",
                "content": 'Generate the first message for the user.'
            }]
            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                    "X-Title": "Omniplexium", # Optional. Site title for rankings on openrouter.ai.
                },
                model="sophosympatheia/rogue-rose-103b-v0.2:free",
                messages=self.histories[id]
            )
        else:
            self.histories[id].append({
                "role": "user",
                "content": message
            })
            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                    "X-Title": "Omniplexium", # Optional. Site title for rankings on openrouter.ai.
                },
                model="sophosympatheia/rogue-rose-103b-v0.2:free",
                messages=self.histories[id]
            )
        self.histories[id].append({
            "role": "assistant",
            "content": completion.choices[0].message.content})

        return completion.choices[0].message.content

if __name__ == '__main__':
    hi = StoryMaker()
    print(asyncio.run(hi.startStory('You are a bear looking at the eclipse.', 169)))
    while True:
        next = input('Choose: ')
        print(asyncio.run(hi.startStory('', 169, message=next)))