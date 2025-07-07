import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from roka import Roka

load_dotenv()

roka_ai = Roka()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has awakened from her slumber!')


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if not message.content.startswith('$'):
        return

    if message.content.startswith('$test') or message.content.startswith('$forget'):
        await bot.process_commands(message)
        return

    user_message = message.content[1:].strip()
    if user_message:  # Make sure it's not just "$"
        response = roka_ai.get_response(user_message, message.author.id)
        await message.channel.send(response)


@bot.command(name='test')
async def test_command(ctx):
    await ctx.send("Yeah, I'm working. What do you want?")


@bot.command(name='forget')
async def forget_command(ctx):
    if roka_ai.clear_history(ctx.author.id):
        await ctx.send("Fine, I'll forget our conversation. Happy now?")
    else:
        await ctx.send("There's nothing to forget, genius.")


bot.run(os.getenv('DISCORD_TOKEN'))
