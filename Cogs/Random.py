import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random

# 여기에 사용자 정의 함수/라이브러리 넣기

class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "random", help = "주어진 단어 중 하나를 선택합니다. ")
    async def randomword(self, ctx, *words):
        await ctx.send(random.choice(words))

    @app_commands.command(name = "randrange", description="a이상 b미만의 수 중 하나를 선택합니다. ")
    @app_commands.describe(a='시작점', b='끝점점')
    async def randrange(self, interaction: discord.Interaction, a:int, b:int):
        await interaction.response.send_message(f"{random.randrange(a, b)}")

    @app_commands.command(name = "qna", description="문답")
    @app_commands.describe(question='질문', answers='답변 (줄바꿈으로 구분)')
    async def malangqna(self, interaction: discord.Interaction, question:str, answers:str):
        await interaction.response.defer()
        answer_list = answers.splitlines()
        embed = discord.Embed(title=f'{interaction.user.mention}님의 질문 : {question}')
        embed.add_field(name='답변', value=f'{random.choice(answer_list)}')
        embed.set_footer(text = '픽셀말랑 질문답변 /qna')
        await asyncio.sleep(1)
        await interaction.followup.send(embed=embed)
    
async def setup(bot:commands.bot):
    await bot.add_cog(Random(bot))
