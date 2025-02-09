import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Store invite counts
invite_counts = {}

@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}')
    # Store initial invite counts
    for guild in bot.guilds:
        invites = await guild.invites()
        invite_counts[guild.id] = {invite.code: invite.uses for invite in invites}

@bot.event
async def on_invite_create(invite):
    guild_invites = invite_counts.get(invite.guild.id, {})
    guild_invites[invite.code] = invite.uses
    invite_counts[invite.guild.id] = guild_invites
    print(f'New invite created by {invite.inviter}: {invite.code}')

@bot.event
async def on_member_join(member):
    # Get fresh invite data
    invites_before = invite_counts.get(member.guild.id, {})
    current_invites = await member.guild.invites()
    
    # Find used invite
    for invite in current_invites:
        if invite.code in invites_before:
            if invite.uses > invites_before[invite.code]:
                # Update invite counts
                invite_counts[member.guild.id] = {i.code: i.uses for i in current_invites}
                
                # Send notification
                channel = member.guild.system_channel
                if channel:
                    await channel.send(f'{member.mention} joined using invite code {invite.code} created by {invite.inviter.mention}')
                return

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot.run('')