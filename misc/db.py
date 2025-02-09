import sqlite3

DATABASE_PATH = '/home/daniel/Documents/myCode/Omniplexium-Eternal/discorddb.db'

with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            userPartyId = cursor.execute("SELECT member1, member2, member3, member4, member5, member6 FROM party WHERE userId = ?", (1000422804585451640,)).fetchone() # userId, pokemon1, pokemon2, pokemon3, pokemon4, pokemon5, pokemon6
            targetPartyId = cursor.execute("SELECT member1, member2, member3, member4, member5, member6 FROM party WHERE userId = ?", (746842205347381338,)).fetchone()
            userParty: list = [None] * 6
            targetParty: list = [None] * 6

            print(userPartyId)
            print('-' * 50)
            print(f'userParty before: {userParty}')

            print('-' * 50)

            print(userPartyId[0])

            for i in range(5):
                userParty[i] = cursor.execute("SELECT * FROM cards WHERE itemId = ?", (userPartyId[i],)).fetchone()
                targetParty[i] = cursor.execute("SELECT * FROM cards WHERE itemId = ?", (targetPartyId[i],)).fetchone()

            print('-' * 50)
            print(f'userParty after: {userParty}')