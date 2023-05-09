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
EMOJI = '😋'

# Specify intents
intents = discord.Intents.all()
# intents.messages = True
# intents.guilds = True

# Initialize bot
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Print bot information when connected to Discord."""
    print(f'{bot.user.name} has connected to Discord!')
    my_loop.start()
    my_scheduled_task.start()

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
        # last_n_messages = []
        # async for msg in message.channel.history(limit=5):  # Change the limit to desired N value
        #     if msg.id != message.id:
        #         last_n_messages.append(msg)

        # reply_text = f"Here are the last {len(last_n_messages)} messages:\n"
        # for msg in reversed(last_n_messages):
        #     reply_text += f"{msg.author.name} said this: {msg.content}\n"

        # await message.reply(reply_text)
        await message.reply('Hello! I hear you quiet and clear!')

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
        response = f'{payload.member.mention} reacted with {EMOJI} to the message:\n> {message.content}\n> —{message.author.mention}'
        await channel.send(response)


# Perform task at specific times (UTC)
times = [
    datetime.time(hour=15, minute=0, second=0)
]
@tasks.loop(time=times)
async def my_scheduled_task():
    print("My scheduled task is running!")
    channel = bot.get_channel(int('1105232705232322680'))
    await channel.send('This is your scheduled message!')

# Perform tasks on a loop
@tasks.loop(seconds=15)
async def my_loop():
    print('My looped message is running')
    channel = bot.get_channel(int('1105232705232322680'))
    insult = insult_jim()
    await channel.send(insult)

# async def openai_chat_reply(system_message, discord_messages):
#     """
#     Generate a response using OpenAI's Chat API given a custom system message and recent Discord messages.
#     :param system_message: The custom system message to set the behavior of the assistant.
#     :param discord_messages: The list of recent Discord messages to provide context for the assistant.
#     :return: The assistant's response as a string.
#     """
#     messages = [{"role": "system", "content": system_message}]
#     for msg in discord_messages:
#         messages.append({"role": "user", "content": msg.content})

#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=messages
#     )

#     reply = response['choices'][0]['message']['content']
#     return reply


# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return

#     if bot.user in message.mentions or "🤖" in message.content:
#         last_n_messages = []
#         async for msg in message.channel.history(limit=5):  # Change the limit to desired N value
#             if msg.id != message.id:
#                 last_n_messages.append(msg)

#         system_message = "You are a helpful assistant."
#         reply = await openai_chat_reply(system_message, last_n_messages)
#         await message.reply(reply)


bot.run(TOKEN)
