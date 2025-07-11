import asyncio
import os
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import discord
from discord.ext import commands
from dotenv import load_dotenv

from constant import constants
from character.roka import Roka

load_dotenv()

roka_ai = Roka()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)


async def update_status():
    activity_type, text = random.choice(constants.ROKA_STATUS)

    if activity_type == "playing":
        activity = discord.Game(text)
    else:
        # Map string to ActivityType enum
        activity_types = {
            "listening": discord.ActivityType.listening,
            "watching": discord.ActivityType.watching
        }
        activity = discord.Activity(type=activity_types[activity_type], name=text)

    await bot.change_presence(
        status=discord.Status.online,
        activity=activity
    )


async def status_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await update_status()
        await asyncio.sleep(600)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has awakened from her slumber!')
    await update_status()
    bot.loop.create_task(status_loop())


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if not message.content.startswith('$'):
        return

    if (message.content.startswith('$test')
            or message.content.startswith('$forget')
            or message.content.startswith('webSearch')
            or message.content.startswith('$affection')):
        await bot.process_commands(message)
        return

    user_message = message.content[1:].strip()
    if user_message:  # Make sure it's not just "$"
        response = roka_ai.get_response_with_affection(user_message, message.author.id)
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


@bot.command(name='webSearch')
async def websearch_command(ctx, *, query):
    async with ctx.typing():
        result = roka_ai.web_search(query)
    await ctx.send(result)

@bot.command(name='affection')
async def affection_command(ctx):
    level = roka_ai.affection_system.get_relationship(ctx.author.id)
    tier = roka_ai.affection_system.get_affection_tier(level)
    await ctx.send(f"**{ctx.author.display_name}**'s relationship with Roka: **{tier}** ({level}/100)")

@bot.command(name='wipeRelationship')
async def wipe_relationship_command(ctx):
    roka_ai.db.clear_affection(ctx.author.id)
    level = roka_ai.affection_system.get_relationship(ctx.author.id)
    tier = roka_ai.affection_system.get_affection_tier(level)
    await ctx.send(f"**{ctx.author.display_name}**'s relationship reset with Roka: **{tier}** ({level}/100)")

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>Roka Bot is Online!</h1><p>Discord bot is running successfully.</p>')

    def log_message(self, format, *args):
        # Suppress HTTP logs to keep console clean
        pass


def start_health_server():
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"Health server starting on port {port}")
    server.serve_forever()


threading.Thread(target=start_health_server, daemon=True).start()
bot.run(os.getenv('DISCORD_TOKEN'))
