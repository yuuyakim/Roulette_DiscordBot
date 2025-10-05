import random
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from keep import keep_alive

load_dotenv()
TOKEN=os.getenv("TOKEN")

intents = discord.Intents.all()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def roulette(ctx, *args):
    print(f'Start roulette {args}!')
    selected_item = select_random(*args)
    await ctx.send(f'Roulette結果: {selected_item}')


def select_random(*args):
    # 可変長引数をランダムで1つ選択して返す
    if not args:
        return None  # 引数がない場合は None を返す
    return random.choice(args)

keep_alive()
try:
    bot.run(os.environ['TOKEN'])
except:
    os.system("kill")
bot.run(TOKEN)