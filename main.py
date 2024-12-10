'''
## PixelSherbet Sherbet 3.5
based on VoltaBot 2.2
made by shashaping_love
original bot made by shashaping_love
'''

import sys
import os

sep = os.path.sep

sys.path.append(sep.join(sys.argv[0].split("/")[:-1]))

import discord
from discord.ext import commands, tasks
import lib.botsetup as botset
import lib.vars as vars
import random
import asyncio
import datetime
from launchio import ln, lndir

print("Starting...")

botset.varset()

pingnum = 0
nexttime = 0

desc = '''
기능 문의 : shashaping_love
개발 페이지 : <https://github.com/volta1147/PixelMalang>'''

class HelpBtn(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, helps: list):
        self.interaction = interaction
        self.helps = helps
        self.page = 0
        super().__init__()

    @discord.ui.button(label='⬅️', style=discord.ButtonStyle.blurple)
    async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self.page %= len(self.helps)
        await self.interaction.edit_original_response(content=f"{self.helps[self.page]}")

    @discord.ui.button(label='➡️', style=discord.ButtonStyle.blurple)
    async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self.page %= len(self.helps)
        await self.interaction.edit_original_response(content=f"{self.helps[self.page]}")

def getuserid(user):
    return int(user[2:len(user)-1])

bot = commands.Bot(command_prefix=botset.prefix, intents=discord.Intents.all())

async def load_extensions():
    cogsnum = 0
    errd = []
    for filename in lndir("Cogs").listdir():
        if filename.endswith(".py"):
            cogsnum += 1
            try:
                await bot.load_extension(f"Cogs.{filename[:-3]}")
                print("{} 불러오기 완료.".format(filename[:-3]))
            except Exception as err:
                print("{} 불러오기 실패.".format(filename[:-3]))
                errd[filename[:-3]] = err
    if len(errd) == 0:
        print("{0}개 중 {0}개 추가 기능 불러오기 완료.".format(cogsnum))
    else:
        print("{0}개 중 {1}개 추가 기능에서 오류가 발생했습니다. ".format(cogsnum, len(errd)))
        for i in list(errd.items()):
            print(i[0]+" :"+str(i[1]).split(":")[2])
    synced = await bot.tree.sync()
    print(f"{len(synced)}개의 슬래시 커맨드 활성화")

@bot.event
async def on_ready():
    global nexttime
    print(f'Login bot: {bot.user}')
    
    nexttime = 60 - datetime.datetime.now().second - datetime.datetime.now().microsecond/1000000
    activityu.start()

    await load_extensions()
    await bot.change_presence(activity=discord.Game(name=random.choice(vars.activity)))
    
@tasks.loop(minutes=1)
async def activityu():
    await asyncio.sleep(nexttime)
    await bot.change_presence(activity=discord.Game(name=random.choice(vars.activity)))

@bot.event
async def on_message(message:discord.Message):
    global pingnum
    if bot.user.mentioned_in(message):
        pingnum += 1
        if random.randrange(3**pingnum) == 0:
            await message.channel.send("이몸 등장!")
        else:
            await message.channel.send(random.choice(vars.ping))
    await bot.process_commands(message)

@bot.command(help = "테스트")
async def ping(ctx):
    await ctx.send(f'pong! {round(round(bot.latency, 4)*1000)}ms')

@bot.command(help = "입력한 내용을 출력합니다")
async def echo(ctx, *, abc):
    await ctx.send(abc)

@bot.command(help = "핑 당한 횟수를 출력합니다")
async def mention(ctx):
    await ctx.send(f"{pingnum}번 핑했어 그만 좀 해")

@bot.command(help = "봇의 정보를 출력합니다. ")
async def info(ctx):
    embed = discord.Embed(title = "PixelMalang", description = f"{desc}", color = 0x747F00)
    embed.set_footer(text = botset.version + ", By shashaping_love")
    await ctx.send(embed=embed)

@bot.command(help = "봇을 종료합니다. 봇 관리자만 이용 가능")
async def shutdown(ctx):
    if ctx.message.author.id == int(botset.myid):
        await ctx.send("종료중...")
        await bot.close()
    else:
        await ctx.send("개발자만 종료할 수 있습니다. ")

@bot.tree.command(name = "help", description="도움말을 출력합니다")
async def help2(interaction: discord.Interaction):
    helps = [ln('res', 'help', i).read() for i in lndir('res', 'help').listdir()]
    await interaction.response.send_message(f"{helps[0]}", view=HelpBtn(interaction=interaction, helps = helps))

bot.run(botset.token)

# PixelSherbet Sherbet 3.5
# based on VoltaBot 2.2
# made by shashaping_love
# original bot made by shashaping_love