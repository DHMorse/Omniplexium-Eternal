# this is how the itemIDs column is going to work in the data base

# I'm doing this becasue the idea of a list doesn't exist in sql land

# and anyother way of doing this would be a pain

import ast

mylist = [1, 2, 3, 4, 5]

print(repr(str(mylist)))

print(ast.literal_eval('[1, 2, 3, 4, 5]'))

print(type(input("Enter a python list: ")))

print("""\u001b[0;30mGray\u001b[0;0m
\u001b[0;31mRed\u001b[0;0m
\u001b[0;32mGreen\u001b[0;0m
\u001b[0;33mYellow\u001b[0;0m
\u001b[0;34mBlue\u001b[0;0m
\u001b[0;35mPink\u001b[0;0m
\u001b[0;36mCyan\u001b[0;0m
\u001b[0;37mWhite\u001b[0;0m
\u001b[0;40mFirefly dark blue background\u001b[0;0m
\u001b[0;41mOrange background\u001b[0;0m
\u001b[0;42mMarble blue background\u001b[0;0m
\u001b[0;43mGreyish turquoise background\u001b[0;0m
\u001b[0;44mGray background\u001b[0;0m
\u001b[0;45mIndigo background\u001b[0;0m
\u001b[0;46mLight gray background\u001b[0;0m
\u001b[0;47mWhite background\u001b[0;0m""")

'''
ChatCompletion(
    id='chatcmpl-AsFL19rjYb9Epu8iVVsUgd6zGSlCi', 
    choices=[
        Choice(
            finish_reason='stop', 
            index=0, 
            logprobs=None, 
            message=ChatCompletionMessage(
                content='false', 
                refusal=None, 
                role='assistant', 
                audio=None, 
                function_call=None, 
                tool_calls=None
                    )
                )
            ], 
            created=1737492035, 
            model='gpt-4o-mini-2024-07-18', 
            object='chat.completion', 
            service_tier='default', 
            system_fingerprint='fp_72ed7ab54c', 
            usage=CompletionUsage(
                completion_tokens=2, 
                prompt_tokens=389, 
                total_tokens=391, 
                completion_tokens_details=CompletionTokensDetails(
                    accepted_prediction_tokens=0, 
                    audio_tokens=0, 
                    reasoning_tokens=0, 
                    rejected_prediction_tokens=0
                ), 
                prompt_tokens_details=PromptTokensDetails(
                    audio_tokens=0, 
                    cached_tokens=0
                    )
                    
                )
            )
'''