import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import datetime
from random import randint
from llm import insult_jim
from loguru import logger

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
EMOJI = '🏈'
DEFAULT_MESSAGE = ("Hello! My chat functionality is still under development, "
                   "but I can help you insult Jim if you want, just type `!insultjim` "
                   "into a new message and I'll get right on it!")

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


@bot.event
async def on_message(message):
    """
    Handle bot mentions or specific emoji in messages.

    If the bot is mentioned or the robot emoji appears in the message,
    reply with the default message and log the event.
    """
    if message.author == bot.user:
        return

    logger.debug(f"Received message: {message.content} from {message.author}")

    if bot.user in message.mentions or "🤖" in message.content:
        logger.info(f"Bot mentioned in message: {message.content} by {message.author}")
        await message.reply(DEFAULT_MESSAGE)
    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
    """
    Log payload information and send a response when a specific emoji reaction is added to a message.
    """
    logger.debug(f"Reaction payload: {payload}")
    if payload.emoji.name == EMOJI:
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        logger.info(f"Emoji {EMOJI} reaction detected on message: {message.content} by {payload.member}")
        response = "Go football! Woo"
        await channel.send(response)


@bot.command(name='insultjim')
async def _insult_jim(ctx):
    """Generate and send an insult for Jim, and log the generated insult."""
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
