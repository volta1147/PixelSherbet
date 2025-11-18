import discord
from discord import app_commands
from discord.ext import commands
import random

# 여기에 사용자 정의 함수/라이브러리 넣기

class Botplus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Restarting...")

    @commands.command(name = "print", help = "입력한 내용을 출력합니다 (원본 메시지 삭제)")
    async def printctx(self, ctx:commands.Context, *, abc):
        author = ctx.message.author.name
        await ctx.message.delete() # ctx.channel.purge(limit=1)
        await ctx.send(abc, reference = ctx.message.reference)
        await ctx.send(f'-# `{author}` 님이 사용한 :>print 명령어')

    @commands.command(name = "reaction", help = "메시지에 반응을 추가합니다. 답장을 이용하거나 메시지 ID를 이용하여 반응을 추가하고 싶은 메시지를 선택하세요.")
    async def reactionctx(self, ctx:commands.Context, abc, message_id=0):
        await ctx.message.delete() # ctx.channel.purge(limit=1)
        original_message = None
        if message_id == 0:
            original_message = ctx.message.reference.resolved
        else:
            original_message = await ctx.fetch_message(message_id)
        await original_message.add_reaction(abc)

    @commands.command(name = "random", help = "주어진 단어 중 하나를 선택합니다. ")
    async def randomword(self, ctx, *words):
        await ctx.send(random.choice(words))

    @app_commands.command(name = "slashprint", description="입력한 내용을 출력합니다")
    @app_commands.describe(text='적을 내용')
    async def printctx2(self, interaction: discord.Interaction, text:str):
        await interaction.response.send_message(f"{text}")

    @app_commands.command(name = "randrange", description="a이상 b미만의 수 중 하나를 선택합니다. ")
    @app_commands.describe(a='시작점', b='끝점점')
    async def randrange(self, interaction: discord.Interaction, a:int, b:int):
        await interaction.response.send_message(f"{random.randrange(a, b)}")
    
async def setup(bot:commands.bot):
    await bot.add_cog(Botplus(bot))
