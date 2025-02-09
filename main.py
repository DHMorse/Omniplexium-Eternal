'''
Two (three?) forms of currency:
- Points: for sending messages and playing easy games (karma, aura, social status)
- MONEY money: for leveling up, doing useful crap, etc. (money, stocks, economic crap)
(- REAL MONEY MONEY money: buy with USD lol)

EXTREME rewards for inviting people (automatic? manual?)

we make some sort of minigame per every 10 levels or what ever we decide our floors to be

each level has a cooler mini game then the last, and the rewards are better, but the difficulty could be higher

and the amount of points needed for each level is exponential, so even tho you have better games it will still take longer to level up

'''

import discord
from discord.ext import commands, tasks
from PIL import Image
import os
import requests
from datetime import datetime, timezone
import time
import sqlite3
import traceback
import asyncio

from secret_const import TOKEN

from const import CACHE_DIR_PFP, COLORS, DEFUALT_PROFILE_PIC, DATABASE_PATH
from const import SERVER_ID, ADMIN_LOG_CHANNEL_ID, MODEL_ERROR_LOG_CHANNEL_ID, CENSORSHIP_CHANNEL_ID, LOG_CHANNEL_ID

from helperFunctions.main import xpToLevel, updateXpAndCheckLevelUp, copyCard, censorMessage, checkLoginRemindersAndSend, logModelError, logError, logWarning
from helperFunctions.database import checkDatabase
from helperFunctions.verifyFilePaths import verifyFilePaths

from adminCommands.set import set
from adminCommands.stats import stats
from adminCommands.reset import reset
from adminCommands.vanity import vanity
from adminCommands.levelToXp import create_level_to_xp_command
from adminCommands.makeLogin import makeloginrewards
from adminCommands.copyCard import copycard
from adminCommands.viewCard import viewcard
from adminCommands.viewCardStats import viewcardstats

from slashCommands.login import slashCommandLogin
from slashCommands.setLoginReminders import slashCommandSetLoginReminders
from slashCommands.credits import slashCommandCredits
from slashCommands.stats import slashCommandStats
from slashCommands.generateCard import slashCommandGenerateCard
from slashCommands.challenge import slashCommandChallenge
from slashCommands.setParty import slashCommandSetParty
from slashCommands.leaderboard import slashCommandLeaderboard

from commands.killme import killme
from commands.credits import credits
from commands.login import login

from floor10_game_concept import guess_the_number_command

from fight import ChallengeView

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.all())

    async def setup_hook(self):
        # Add the imported command to the bot’s command tree
        self.tree.add_command(guess_the_number_command)
        self.tree.add_command(slashCommandLogin)
        self.tree.add_command(slashCommandSetLoginReminders)
        self.tree.add_command(slashCommandCredits)
        self.tree.add_command(slashCommandStats)
        self.tree.add_command(slashCommandGenerateCard)
        self.tree.add_command(slashCommandChallenge)
        self.tree.add_command(slashCommandSetParty)
        self.tree.add_command(slashCommandLeaderboard)

        await self.tree.sync()  # Sync commands with Discord

bot = MyBot()

@bot.event
async def on_ready():
    checkDatabaseStartTime = time.time()
    await checkDatabase(bot)
    print(f'The database check took {round(time.time() - checkDatabaseStartTime, 2)} seconds')

    verifyFilePathsStartTime = time.time()
    await verifyFilePaths(bot)
    print(f'The file path verification took {round(time.time() - verifyFilePathsStartTime, 2)} seconds')

    if not loginReminderTask.is_running():
        try:
            loginReminderTask.start()
            print(f"{COLORS['blue']}Login reminder task started{COLORS['reset']}")
        
        except Exception as e:
            print(f"{COLORS['red']}Login reminder task failed to start: {e}{COLORS['reset']}")
            await logError(bot, e, traceback.format_exc(), 'Login reminder task failed to start')

    botTreeSyncStartTime = time.time()
    await bot.tree.sync()
    print(f'Bot tree sync took {round(time.time() - botTreeSyncStartTime, 2)} seconds')

    print(f'Bot is ready. Logged in as {bot.user}')

# Define the task outside of the bot class
@tasks.loop(hours=1)
async def loginReminderTask():
    await checkLoginRemindersAndSend(bot)


### ADMIN COMMANDS ###

bot.add_command(set)
bot.add_command(stats)
bot.add_command(reset)
bot.add_command(vanity)
create_level_to_xp_command(bot)
bot.add_command(makeloginrewards)
bot.add_command(copycard)
#bot.add_command(leveltoxp)
bot.add_command(viewcard)
bot.add_command(viewcardstats)

### ADMIN COMMANDS ###



### Normal commands ###

bot.add_command(killme)
bot.add_command(credits)
bot.add_command(login)

### Normal commands ###



@bot.event
async def on_message(message):
    if message.author.bot:
        return

    userId = message.author.id
    username = message.author.name

    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            # Check if user exists in the database
            cursor.execute("SELECT * FROM users WHERE userId = ?", (userId,))
            result = cursor.fetchone()
            
            if not result:
                cursor.execute(
                    "INSERT INTO users (userId, username, xp, money, lastLogin, daysLoggedInInARow) VALUES (?, ?, ?, ?, ?, ?)",
                    (userId, username, 1, 0, None, 0)
                )
                conn.commit()
            
            if result:
                await updateXpAndCheckLevelUp(ctx=message, bot=bot, xp=1, add=True)
    except sqlite3.Error as e:
        print(f"Database error in on_message: {e}")
        channel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
        await channel.send(f'''```ansi{COLORS['red']}Database error in on_message: ```{e}```{COLORS['reset']}```''')

    finally:
        # Continue processing other commands regardless of database operation success
        await bot.process_commands(message)

        async def tryCensorMessageWithModel(message: str) -> str:
            censoredMessage = None
            try:
                try:
                    censoredMessage = await asyncio.wait_for(censorMessage(message), timeout=1.0)
                except asyncio.TimeoutError as e:
                    messageId = await logModelError(
                                    bot, e, traceback.format_exc(), 
                                    f"""{username} sent a message: {message}\nWhich was not censored in time!""", 'on_message event'
                                    )
                    channel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
                    await channel.send(f"https://discord.com/channels/{SERVER_ID}/{MODEL_ERROR_LOG_CHANNEL_ID}/{messageId}")

                    await logWarning(
                                    bot, f"""{username} sent a message: {message}\nWhich was not censored in time!""", 'on_message event'
                                    )
                    #return await tryCensorMessageWithModel(message, model=BACKUP_CENSORSHIP_MODEL)

            except Exception as e:
                messageId = await logModelError(bot, e, traceback.format_exc(), 'on_message event')
                channel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
                await channel.send(f"https://discord.com/channels/{SERVER_ID}/{MODEL_ERROR_LOG_CHANNEL_ID}/{messageId}")
                
                await logWarning(
                                bot, f"""{username} sent a message: {message} Which was not censored.""", 'on_message event'
                                )
                #return await tryCensorMessageWithModel(message, model=BACKUP_CENSORSHIP_MODEL)
            
            return 'false' if censoredMessage is None else censoredMessage

        censoredMessage = 'false'

        if message.content is not None and message.content.strip() != '':
            censoredMessage = await tryCensorMessageWithModel(message.content)
        
        if censoredMessage.strip() not in ['false', "'false'", '"false"', 'False', "'False'", '"False"'] and username != '404_5971':
            channel = bot.get_channel(CENSORSHIP_CHANNEL_ID)
            await channel.send(f'`{username}` sent a message: ```{message.content}```Which was censored to: ```{censoredMessage}```')
            await message.delete()
            await message.channel.send(f'`{username}:` {censoredMessage}')

@bot.event
async def on_member_join(member: discord.Member):
    memberId = member.id
    memberName = member.name
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        # see if the user is in the data base
        cursor.execute("SELECT xp FROM users WHERE userId = ?", (memberId,))
        result = cursor.fetchone()
        if result:
            xp = result[0]
            for i in range(xpToLevel(xp)):
                await member.add_roles(discord.utils.get(member.guild.roles, name=f"Level {i + 1}"))

        if not result:
            cursor.execute(
                "INSERT INTO users (userId, username, xp, money, lastLogin, daysLoggedInInARow) VALUES (?, ?, ?, ?, ?, ?)",
                (memberId, memberName, 0, 0, None, 0)
            )
            conn.commit()


    # Calculate account age
    now = datetime.now(timezone.utc)
    account_creation_date = member.created_at
    account_age = now - account_creation_date
    years = account_age.days // 365
    months = (account_age.days % 365) // 30
    days = (account_age.days % 365) % 30

    accountAgeStatus = 'normal'
    
    if years < 1:
        if months < 1:
            # account is brand new
            accountAgeStatus = 'brand new'
        else:
            # account is older than a month
            # and is new, but proably not dangerous
            accountAgeStatus = 'new'
        # account is older than a year old

    # test case for my alt
    #if member.id == 1000422804585451640:
    #    accountAgeStatus = 'brand new'

    # Embed setup
    match accountAgeStatus:
        case 'normal':
            discordColor = discord.Color.green()
        case 'new':
            discordColor = discord.Color.yellow()
        case 'brand new':
            discordColor = discord.Color.dark_orange()

    embed = discord.Embed(
            title="Member Joined",
            description=f"**Member:** \n{member.name}\n\n"
                        f"**Account Age:** \n{years} Years, {months} Months, {days} Days\n",
            color=discordColor,
            timestamp=now  # Automatically add the timestamp to the footer
        )
    embed.set_thumbnail(url=member.display_avatar.url)

    channel = bot.get_channel(LOG_CHANNEL_ID)

    # Send the embed to the server's system channel (or any specific channel)
    if channel:
        await channel.send(embed=embed)

@bot.event
async def on_member_remove(member: discord.Member):
    # Calculate account age
    now = datetime.now(timezone.utc)
    account_creation_date = member.created_at
    account_age = now - account_creation_date
    years = account_age.days // 365
    months = (account_age.days % 365) // 30
    days = (account_age.days % 365) % 30

    embed = discord.Embed(
            title="Member Left",
            description=f"**Member:** \n{member.name}\n\n"
                        f"**Account Age:** \n{years} Years, {months} Months, {days} Days\n",
            color=discord.Color.dark_magenta(),
            timestamp=now  # Automatically add the timestamp to the footer
        )
    embed.set_thumbnail(url=member.display_avatar.url)

    channel = bot.get_channel(LOG_CHANNEL_ID)

    # Send the embed to the server's system channel (or any specific channel)
    if channel:
        await channel.send(embed=embed)

@bot.event
async def on_user_update(before: discord.Member, after: discord.Member):

    # later if we run out of resources we can make it so that we check if the user is on the leaderboard or not
    # and if not we can just return

    # Check if the avatar has changed
    if before.avatar != after.avatar:
        user = await bot.fetch_user(after.id)
        # Ensure the directory exists
        profile_picture_dir = os.path.join(os.path.expanduser(CACHE_DIR_PFP))

        if not os.path.exists(profile_picture_dir):
            os.makedirs(profile_picture_dir)

        profile_picture_path = os.path.join(profile_picture_dir, f"{after.id}.png")

        if user and user.avatar:
            profile_picture_response = requests.get(user.avatar.url, stream=True)
            profile_picture_response.raise_for_status()
            profile_picture = Image.open(profile_picture_response.raw)
        else:
            profile_picture = Image.open(DEFUALT_PROFILE_PIC)

            # Save profile picture to cache
        profile_picture.save(profile_picture_path)

bot.run(TOKEN)
