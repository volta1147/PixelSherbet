import discord
import numpy as np
import datetime

KST=datetime.timezone(datetime.timedelta(hours=9))

season_text = 'Beta 1 Season (2026.01.03 - Next Update)'

def footer(message_time:datetime.datetime):
    time_text = message_time.astimezone(tz=KST).isoformat(sep=' ', timespec='minutes')[:-6]
    footer_text = f'{time_text} | {season_text}'
    return footer_text

class Stock:
    def __init__(self, name:str, price:float = 1.00, nick:str = '', vol:float = 0.3, r:float = 0.03):
        self.name = name
        self.price = price
        self.nick = nick if nick != '' else name
        self.S     = np.array([self.price])

        self.vol = vol # 0.015
        self.r   = r   # 0.001
        self.tmp = self.price
        self.pct = 0.00
        self.pctprint = "0.00%"
        self.cnt = 0
        self.prevz = 0.00

        self.yearcnt = {2000:0}

    dt  = 1/1440

    def __str__(self):
        return f"{self.name} : {self.price}"

    def day(self):
        z = np.random.normal(0, 1)
        self.prevz  = z
        self.tmp    = self.price
        self.price *= np.exp((self.r-0.5*self.vol**2)*self.dt+self.vol*z*np.sqrt(self.dt))
        self.price = round(self.price, 2)
        self.S      = np.append(self.S, self.price)
        self.pct = ((self.price-self.tmp)/self.tmp)*100

        pctcolor = '+' if self.pct > 0 else ''
        self.pctprint = f"{pctcolor}{self.pct:.2f}".rjust(10)

        self.cnt   += 1
            
    def embed(self, interaction):
        updown = '📈' if self.pct > 0 else ('📉' if self.pct < 0 else '🟰')
        embed = discord.Embed(colour=0xdec0de, title=f'{self.name} 종목 정보', description=f'* 이름 : `{self.nick}`\n* 가격 : {self.price}pts ({self.pct}%{updown})')
        embed.set_footer(text=footer(interaction.created_at))
        return embed

if __name__ == '__main__':
    aa = Stock(name='asdf')
    for i in range(1440*30):
        aa.day()
    print(aa.price)