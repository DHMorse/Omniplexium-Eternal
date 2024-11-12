# this is how the itemIDs column is going to work in the data base

# I'm doing this becasue the idea of a list doesn't exist in sql land

# and anyother way of doing this would be a pain

import ast

mylist = [1, 2, 3, 4, 5]

print(repr(str(mylist)))

print(ast.literal_eval('[1, 2, 3, 4, 5]'))