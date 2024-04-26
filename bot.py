import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from random import randint
from insult import insult_jim
from truax import generate_truax
from truaxbot import generate_truax_reply
from loguru import logger
from utils import create_trello_card

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TRELLO_KEY = os.getenv('TRELLO_KEY')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
TRELLO_FEATURE_REQUEST_LIST = os.getenv('TRELLO_FEATURE_REQUEST_LIST')
EMOJI = '🏈'
EMOJI_TJ = 'ThomasJones'
ALLOWED_CHANNELS = [1042804140490883084, 1042804380354752592, 1043023451482505229, 1171482001275093112]
DEFAULT_MESSAGE = f"""
Hello! My chat functionality is still under development, but here are a few
things I know how to do! 
  - I can help you insult Jim if you want, just type `!insultjim` into a new message and I'll get right on it!
  - Add {EMOJI_TJ} to a message, and I will provide you a classic Truax-Inspired one-liner response. Ussually about Thomas Jones.

Want me to do other things?  If you include the word "feature" in your message to me, I will create a card on the Feature Request board (https://trello.com/b/Z1ksC5ke/wcb-discord-bot-feature-requests) for you.
"""

# Specify intents
intents = discord.Intents.all()

# Initialize bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Configure logging
logger.add("bot.log", rotation="10 MB")


@bot.event
async def on_ready():
    """
    Print bot information when connected to Discord
    and log the connection.
    """
    logger.info(f'{bot.user.name} has connected to Discord!')
    print(f'{bot.user.name} has connected to Discord!')

async def create_feature_request(message):
    """
    Function to handle messages containing 'feature'.
    This function is called when a message containing 'feature' is detected.
    """
    logger.info("Creating Trello Card with feature request")
    card = create_trello_card(
        list_id=TRELLO_FEATURE_REQUEST_LIST, 
        name=f'{message.author} - {message.created_at}', 
        desc=str(message.content), 
        key=TRELLO_KEY, token=TRELLO_TOKEN
    )
    logger.info(str(card))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.channel.id not in ALLOWED_CHANNELS:
        return

    logger.debug(f"Received message: {message.content} from {message.author}")

    if "feature" in message.content.lower():
        logger.info(f"Feature mentioned in message: {message.content} by {message.author}")
        await create_feature_request(message)
        await message.reply("I've created a Trello card on the WCB Discord Bot Feature Request Board (https://trello.com/b/Z1ksC5ke/wcb-discord-bot-feature-requests)")
    elif bot.user in message.mentions or "🤖" in message.content:
        logger.info(f"Bot mentioned in message: {message.content} by {message.author}")
        
        # Retrieve the last 10 messages in the channel
        messages = []
        async for msg in message.channel.history(limit=10):
            if msg.author == bot.user:
                messages.append({"role": "assistant", "content": f"{bot.user.display_name}: {msg.content}"})
            else:
                messages.append({"role": "user", "content": f"{msg.author.display_name}: {msg.content}"})
        
        # Reverse the order of messages to maintain chronological order
        messages.reverse()
        
        # Generate Truax's response
        response = generate_truax(messages)
        await message.channel.send(response)
    
    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
    """
    Log payload information and send a response when a specific emoji reaction is added to a message.
    """
    logger.debug(f"Reaction payload: {payload}")

    if payload.channel_id not in ALLOWED_CHANNELS:
        return

    if payload.emoji.name == EMOJI_TJ or payload.emoji.name == '🍆':
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        logger.info(f"Emoji {EMOJI_TJ} reaction detected on message: {message.content} by {payload.member}")
        response = generate_truax(message.content)
        output = f"I see someone reacted with a {EMOJI_TJ} emoji! Here is a Truax-inspired one-liner!\n\n> {message.content}\n\n{response}"
        await channel.send(output)

@bot.command(name='insultjim')
async def _insult_jim(ctx):
    """Generate and send an insult for Jim, and log the generated insult."""
    if ctx.channel.id not in ALLOWED_CHANNELS:
        return
    result = insult_jim()
    logger.info(f"Generated insult: {str(result)} for Jim")
    await ctx.send(result['output'])


@bot.event
async def on_command_error(ctx, error):
    """
    Handle command errors and log them.
    """
    if isinstance(error, commands.CommandNotFound):
        logger.warning(f"Command not found: {ctx.message.content}")
    else:
        logger.exception(f"Error occurred while executing command: {ctx.message.content}", exc_info=error)

    await ctx.send(f"An error occurred: {error}")

# Run Application
bot.run(TOKEN)
