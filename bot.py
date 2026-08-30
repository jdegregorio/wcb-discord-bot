import asyncio
import logging
import os
from collections import deque
from datetime import datetime, timedelta, timezone
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from insult import insult_jim
from truax import generate_truax
from truaxbot import generate_truax_reply
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

AUTO_MIN_INTERVAL_HOURS = float(os.getenv("TRUBOT_AUTO_MIN_INTERVAL_HOURS", "2"))
AUTO_RESPONSE_MIN_INTERVAL = timedelta(hours=AUTO_MIN_INTERVAL_HOURS)
AUTO_RESPONSE_DAILY_LIMIT = int(os.getenv("TRUBOT_AUTO_DAILY_LIMIT", "3"))
AUTO_RESPONSE_ROLLING_WINDOW = timedelta(hours=1)
AUTO_RESPONSE_DELAY = timedelta(minutes=10)
AUTO_RESPONSE_HISTORY_LIMIT = 15

_channel_states = {}
READY_FILE = Path(os.getenv("HEALTH_READY_FILE", "/tmp/wcb-bot-ready"))
_health_task = None

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("wcb_bot")


def _ensure_utc(dt):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _get_channel_state(channel_id):
    state = _channel_states.get(channel_id)
    if state is None:
        state = {
            "recent_messages": deque(),
            "last_response_time": datetime.min.replace(tzinfo=timezone.utc),
            "daily_count": 0,
            "count_reset_date": datetime.now(timezone.utc).date(),
            "pending_task": None,
            "last_human_message_time": None,
        }
        _channel_states[channel_id] = state
    return state


def _trim_recent_messages(state, reference_time):
    recent_messages = state["recent_messages"]
    while recent_messages and reference_time - recent_messages[0][0] > AUTO_RESPONSE_ROLLING_WINDOW:
        recent_messages.popleft()


async def _schedule_auto_response(channel_id, channel):
    state = _get_channel_state(channel_id)
    expected_last_human = state["last_human_message_time"]
    try:
        await asyncio.sleep(AUTO_RESPONSE_DELAY.total_seconds())
        state = _get_channel_state(channel_id)

        if state["last_human_message_time"] != expected_last_human:
            return

        now = datetime.now(timezone.utc)
        if state["count_reset_date"] != now.date():
            state["daily_count"] = 0
            state["count_reset_date"] = now.date()

        _trim_recent_messages(state, now)

        unique_users = {user_id for _, user_id in state["recent_messages"]}
        if len(unique_users) < 2:
            return

        if now - state["last_response_time"] < AUTO_RESPONSE_MIN_INTERVAL:
            return

        if state["daily_count"] >= AUTO_RESPONSE_DAILY_LIMIT:
            return

        history = []
        async for msg in channel.history(limit=AUTO_RESPONSE_HISTORY_LIMIT):
            if msg.author == bot.user:
                history.append({"role": "assistant", "content": f"{bot.user.display_name}: {msg.content}"})
            else:
                history.append({"role": "user", "content": f"{msg.author.display_name}: {msg.content}"})

        history.reverse()

        if not history:
            return

        response = await asyncio.to_thread(generate_truax_reply, history)
        await channel.send(response)

        state["last_response_time"] = now
        state["daily_count"] += 1
        logger.info("Sent auto-response in channel %s; daily count=%s", channel_id, state["daily_count"])
    except asyncio.CancelledError:
        logger.debug("Auto-response task for channel %s cancelled", channel_id)
        raise
    except Exception as exc:
        logger.exception("Error while preparing auto-response: %s", exc)
    finally:
        state = _get_channel_state(channel_id)
        if state.get("pending_task") is asyncio.current_task():
            state["pending_task"] = None


async def _handle_auto_participation(message, *, allow_schedule=True):
    channel_id = message.channel.id
    state = _get_channel_state(channel_id)
    message_time = _ensure_utc(message.created_at)

    if state["count_reset_date"] != message_time.date():
        state["daily_count"] = 0
        state["count_reset_date"] = message_time.date()

    state["last_human_message_time"] = message_time

    state["recent_messages"].append((message_time, message.author.id))
    _trim_recent_messages(state, message_time)

    if not allow_schedule:
        if state["pending_task"]:
            state["pending_task"].cancel()
            state["pending_task"] = None
        return

    unique_users = {user_id for _, user_id in state["recent_messages"]}
    if len(unique_users) < 2:
        if state["pending_task"]:
            state["pending_task"].cancel()
            state["pending_task"] = None
        return

    now = datetime.now(timezone.utc)
    if now - state["last_response_time"] < AUTO_RESPONSE_MIN_INTERVAL:
        return

    if state["daily_count"] >= AUTO_RESPONSE_DAILY_LIMIT:
        return

    if state["pending_task"]:
        state["pending_task"].cancel()

    state["pending_task"] = asyncio.create_task(_schedule_auto_response(channel_id, message.channel))

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

@bot.event
async def on_ready():
    """
    Print bot information when connected to Discord
    and log the connection.
    """
    global _health_task
    READY_FILE.touch()
    if _health_task is None or _health_task.done():
        _health_task = asyncio.create_task(_refresh_health_file())
    logger.info("%s has connected to Discord", bot.user.name)


async def _refresh_health_file():
    while True:
        READY_FILE.touch()
        await asyncio.sleep(60)


@bot.event
async def on_disconnect():
    global _health_task
    if _health_task is not None:
        _health_task.cancel()
        _health_task = None
    READY_FILE.unlink(missing_ok=True)
    logger.warning("Disconnected from Discord")

async def create_feature_request(message):
    """
    Function to handle messages containing 'feature'.
    This function is called when a message containing 'feature' is detected.
    """
    logger.info("Creating Trello Card with feature request")
    card = await asyncio.to_thread(
        create_trello_card,
        list_id=TRELLO_FEATURE_REQUEST_LIST,
        name=f'{message.author} - {message.created_at}',
        desc=str(message.content),
        key=TRELLO_KEY,
        token=TRELLO_TOKEN,
    )
    logger.info("Created Trello feature request card id=%s", card.get("id", "unknown"))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.channel.id not in ALLOWED_CHANNELS:
        return

    logger.debug("Received message metadata author=%s channel=%s", message.author, message.channel.id)

    is_direct_ping = bot.user in message.mentions or "🤖" in message.content

    await _handle_auto_participation(message, allow_schedule=not is_direct_ping)

    if "feature" in message.content.lower():
        logger.info("Feature request received from %s", message.author)
        await create_feature_request(message)
        await message.reply("I've created a Trello card on the WCB Discord Bot Feature Request Board (https://trello.com/b/Z1ksC5ke/wcb-discord-bot-feature-requests)")
    elif is_direct_ping:
        logger.info("Bot mentioned by %s", message.author)
        
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
        response = await asyncio.to_thread(generate_truax, messages)
        await message.channel.send(response)
    
    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
    """
    Log payload information and send a response when a specific emoji reaction is added to a message.
    """
    logger.debug("Reaction event channel=%s message=%s", payload.channel_id, payload.message_id)

    if payload.channel_id not in ALLOWED_CHANNELS:
        return

    if payload.emoji.name == EMOJI_TJ or payload.emoji.name == '🍆':
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        logger.info("Truax reaction received from %s", payload.member)
        response = await asyncio.to_thread(generate_truax, message.content)
        output = f"I see someone reacted with a {EMOJI_TJ} emoji! Here is a Truax-inspired one-liner!\n\n> {message.content}\n\n{response}"
        await channel.send(output)

@bot.command(name='insultjim')
async def _insult_jim(ctx):
    """Generate and send an insult for Jim, and log the generated insult."""
    if ctx.channel.id not in ALLOWED_CHANNELS:
        return
    result = await asyncio.to_thread(insult_jim)
    logger.info("Generated requested Jim insult")
    await ctx.send(result['output'])


@bot.event
async def on_command_error(ctx, error):
    """
    Handle command errors and log them.
    """
    if isinstance(error, commands.CommandNotFound):
        logger.warning("Unknown command from %s", ctx.message.author)
    else:
        logger.error("Command failed for %s: %s", ctx.message.author, error)

    await ctx.send(f"An error occurred: {error}")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is required")

READY_FILE.unlink(missing_ok=True)
bot.run(TOKEN, log_handler=None)
