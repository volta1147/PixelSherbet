import discord
import lib.stock as stock
from launchio.json import PMjson
import datetime
import asyncio
from discord     import app_commands
from discord.ext import commands, tasks
from lib.file import json_path

# 여기에 사용자 정의 라이브러리 넣기

stock_file = PMjson(json_path.chifile('stock.json'))
acc_file = PMjson(json_path.chifile('accounts.json'))

class PriceBtn(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, stock: list):
        self.interaction = interaction
        self.stock = stock
        self.page = 0
        super().__init__()

    @discord.ui.button(label='⬅️', style=discord.ButtonStyle.blurple)
    async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self.page %= len(self.stock)
        await self.interaction.edit_original_response(embed=self.stock[self.page])

    @discord.ui.button(label='➡️', style=discord.ButtonStyle.blurple)
    async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self.page %= len(self.stock)
        await self.interaction.edit_original_response(embed=self.stock[self.page])

class Stock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stocks = {i[0]:stock.Stock(i[0], price=i[1]['price']) for i in stock_file.read().items()}
        self.nexttime = 60 - datetime.datetime.now().second - datetime.datetime.now().microsecond/1000000

        self.update_stocks.start()

    def cog_unload(self):
        self.update_stocks.cancel()

    @tasks.loop(minutes=1)
    async def update_stocks(self):
        await asyncio.sleep(self.nexttime)
        for i in self.stocks.items():
            i[1].day()
            stock_file.edit(i[0], value={'price':i[1].price, 'name':i[1].nick})

    stock_app = app_commands.Group(name="stock", description="주식 시뮬")

    @stock_app.command(name = "create", description="만들기")
    @app_commands.describe(name="코드", nick="별명")
    async def create_stock(self, interaction:discord.Interaction, name:str, nick:str):
        if name in stock_file.read().keys():
            await interaction.response.send_message("이미 존재합니다") 
        elif name.isalnum and len(name) == 4:
            name_f = name.upper()
            stock_file.edit(name_f, value={'price':10.0, 'name':nick})
            self.stocks[name_f] = stock.Stock(name_f, price=10.0, nick=nick)
            await interaction.response.send_message(f"{name_f} 생성 완료. ")
        else:
            await interaction.response.send_message("이름은 4글자 영어와 숫자만 가능합니다. ")

    @stock_app.command(name = "buy", description="매수")
    @app_commands.describe(name='코드', amount="수량")
    async def buy_stock(self, interaction:discord.Interaction, name:str, amount:int):
        if amount < 0:
            embed = discord.Embed(colour=0xff0000, title='오류', description=f'매도 명령어는 `/stock sell` 명령어를 이용해 주세요. ')
            
        elif amount == 0:
            embed = discord.Embed(colour=0xff0000, title='오류', description=f'적어도 1주 이상은 구매해야 합니다. ')
        else:
            name_f = name.upper()
            point = acc_file()['users'][str(interaction.user.id)]['point']
            stocks:dict = acc_file()['users'][str(interaction.user.id)]['stocks']
            price_n = self.stocks[name_f].price * amount
            if point > price_n:
                if name_f not in stocks.keys():
                    stocks[name_f] = 0
                stocks[name_f] += amount
                acc_file.edit('users', str(interaction.user.id), 'point', value=point-price_n)
                acc_file.edit('users', str(interaction.user.id), 'stocks', value=stocks)
                embed = discord.Embed(colour=0xdec0de, title='거래 성공', description=f'거래가 성공적으로 진행되었습니다. \n 남은 잔액 : {point-price_n:.2f}')
            else:
                embed = discord.Embed(colour=0xff0000, title='오류', description=f'잔액이 부족합니다. ')
        embed.set_footer(text=stock.footer(interaction.created_at))
        await interaction.response.send_message(embed=embed)

    @stock_app.command(name = "sell", description="매도")
    @app_commands.describe(name='코드', amount="수량")
    async def sell_stock(self, interaction:discord.Interaction, name:str, amount:int):
        if amount < 0:
            embed = discord.Embed(colour=0xff0000, title='오류', description=f'매수 명령어는 `/stock buy` 명령어를 이용해 주세요. ')
            
        elif amount == 0:
            embed = discord.Embed(colour=0xff0000, title='오류', description=f'적어도 1주 이상은 판매해야 합니다. ')
        else:
            name_f = name.upper()
            point = acc_file()['users'][str(interaction.user.id)]['point']
            stocks:dict = acc_file()['users'][str(interaction.user.id)]['stocks']
            price_n = self.stocks[name_f].price * amount
            if acc_file()['users'][str(interaction.user.id)]['stocks'][name_f] > amount:
                stocks[name_f] -= amount
                acc_file.edit('users', str(interaction.user.id), 'point', value=point+price_n)
                acc_file.edit('users', str(interaction.user.id), 'stocks', value=stocks)
                embed = discord.Embed(colour=0xdec0de, title='거래 성공', description=f'거래가 성공적으로 진행되었습니다. \n 남은 잔액 : {point+price_n:.2f}')
            else:
                embed = discord.Embed(colour=0xff0000, title='오류', description=f'주식 수량이 부족합니다. ')
        embed.set_footer(text=stock.footer(interaction.created_at))
        await interaction.response.send_message(embed=embed)

    @stock_app.command(name = "search", description="검색")
    @app_commands.describe(name='코드')
    async def price_stock(self, interaction:discord.Interaction, name:str|None=None):
        if name == None:
            stock_list = [i.embed(interaction) for i in self.stocks.values()]
            await interaction.response.send_message(embed=stock_list[0], view=PriceBtn(interaction=interaction, stock = stock_list))
        else:
            name_f = name.upper()
            embed = self.stocks[name_f].embed(interaction)
            await interaction.response.send_message(embed=embed)

    @stock_app.command(name = "profile", description="내 지갑")
    async def price_stock(self, interaction:discord.Interaction):
        if str(interaction.user.id) in acc_file()['users'].keys():
            embed = discord.Embed(colour=0xdec0de, title=f'{interaction.user.mention} 사용자 정보', description=f'내 잔액 : {acc_file()['users'][str(interaction.user.id)]['point']:.2f}pts')
            if len(acc_file()['users'][str(interaction.user.id)]['stocks'])>0:
                stock_text = '\n'.join([f'{i[0]} x{i[1]} -> {i[1]*self.stocks[i[0]].price:.2f} pts' for i in acc_file()['users'][str(interaction.user.id)]['stocks'].items()])
                embed.add_field(name='보유 주식', value=stock_text)
                total = acc_file()['users'][str(interaction.user.id)]['point'] + sum([i[1]*self.stocks[i[0]].price for i in acc_file()['users'][str(interaction.user.id)]['stocks'].items()])
                embed.add_field(name='총 재산', value=f'{total:.2f}pts')
        else:
            embed = discord.Embed(colour=0xdec0de, title=f'{interaction.user.mention} 사용자 정보', description=f'채팅 이력이 없습니다. 채팅을 시작하고 포인트를 획득해 보세요.')
        embed.set_footer(text=stock.footer(interaction.created_at))
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Stock(bot))