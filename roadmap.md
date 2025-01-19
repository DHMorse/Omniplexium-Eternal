Finished Demo:
    - Fully move the database to sqlite3


    - Login Demo: 
        - !login or /login
        - Gives rewards based of number of days logged in, in a row
        Optional:
            - Reminders to login
            - Opt in / Opt out system


    - Figure out Card Data Type
    probably (image, dict[stat: str, value: str | int | float])

    - View Stats:
        - !stats or /stats
        - View the players stats
        - View the players cards
        - View the players cards stats


    - Quests: 
        # - Generate Quest Data not needed for our current implomentation
        - Player accepts quest
        - Player gets dm'd or something
        - Player chooses one of 4 options or something 
        - Player does this a few times
        - get Ai cards from completing them 
        - Optional:
            - Over Arching Story quests.


    - Fights: 
        - Write play challenging logic with proper acceptance and decline logic
        - Check the players inventory for the cards they have
        - Turn based battle system

    fight friends in pokemon battles with cards


    - Optional:
        - Figure out Quest Data Type
        probably some custom json structure
        - Inviting a friend and getting them to join gets both users a bonus
        - Skills:
            - 1. combat or (attack and speed)
                - get this from killing stuffs
                - combat would make both attack and speed faster

            - 2. wisdom
                - you get this from talking in chat lmao
                - the higher this is the easier it is to talk to NPC's and get what you want

            - 3. rebate
                - when ever you trade you gain some rebate skill points 
                - the higher it is the less the player pays in fees or possibly earns money by doing certain things

            - 4. endurance
                - you get this from login streaks
                - maybe gives you a login reward multiplier or streak save items

                - maybe instead the higher endurance the more xp you gain from doing shit


        - Inventory:
            - Add other items than cards to the inventory


