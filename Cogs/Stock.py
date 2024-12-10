import discord
import lib.stock as stock
import lib.file as file
import datetime
import asyncio
from discord     import app_commands
from discord.ext import commands, tasks

# 여기에 사용자 정의 라이브러리 넣기

class Stock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stocks = {i[0]:stock.Stock(i[0], price=i[1]['price']) for i in file.read_json('stock').items()}
        self.nexttime = 60 - datetime.datetime.now().second - datetime.datetime.now().microsecond/1000000

        self.update_stocks.start()

    def cog_unload(self):
        self.update_stocks.cancel()

    @tasks.loop(minutes=1)
    async def update_stocks(self):
        await asyncio.sleep(self.nexttime)
        for i in self.stocks.items():
            i[1].day()
            file.edit_json('stock', i[0], {'price':i[1].price, 'name':i[1].nick})

    stock_app = app_commands.Group(name="stock", description="주식 시뮬")

    @stock_app.command(name = "create", description="만들기")
    @app_commands.describe(name="이름", nick="별명")
    async def create_stock(self, interaction:discord.Interaction, name:str, nick:str):
        if name in file.read_json('stock').keys():
            await interaction.response.send_message("이미 존재합니다") 
        elif name.isalnum and len(name) == 4:
            name_f = name.upper()
            file.edit_json('stock', name_f, {'price':1.00, 'name':nick})
            self.stocks[name_f] = stock.Stock(name_f, price=1.00, nick=nick)
            await interaction.response.send_message(f"{name_f} 생성 완료. ")
        else:
            await interaction.response.send_message("이름은 4글자 영어와 숫자만 가능합니다. ")

async def setup(bot):
    await bot.add_cog(Stock(bot))