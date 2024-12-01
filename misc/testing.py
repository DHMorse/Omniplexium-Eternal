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