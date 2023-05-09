import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import datetime
from random import randint
from llm import insult_jim

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
EMOJI = '🏈' 
DEFAULT_MESSAGE = "Hello! My chat functionality is still under development, but I can help you insult Jim if you want, just type `!insultjim` into a new message and I'll get right on it!"

# Specify intents
intents = discord.Intents.all()

# Initialize bot
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Print bot information when connected to Discord."""
    print(f'{bot.user.name} has connected to Discord!')

# Send message after a message is sent
@bot.event
async def on_message(message):
    """
    Handle bot mentions or specific emoji in messages.
    Fetch and display the last N messages (excluding the current one) for context.
    """
    if message.author == bot.user:
        return

    if bot.user in message.mentions or "🤖" in message.content:
        await message.reply(DEFAULT_MESSAGE)
    await bot.process_commands(message)

# Send message after a specific emoji reaction is added to a message
@bot.event
async def on_raw_reaction_add(payload):
    print(str(payload))
    print(str(payload.emoji))
    print(str(payload.emoji.name))
    if payload.emoji.name == EMOJI:
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        # response = f'{payload.member.mention} reacted with {EMOJI} to the message:\n> {message.content}\n> —{message.author.mention}'
        response = "Go football! Woo"
        await channel.send(response)

@bot.command(name='insultjim')
async def _insult_jim(ctx):
    """Generate and send an insult for Jim."""
    insult = insult_jim()
    await ctx.send(insult)

bot.run(TOKEN)
