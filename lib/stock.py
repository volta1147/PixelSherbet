import numpy as np

class Stock:
    def __init__(self, name:str, price:float = 1.00, nick:str = '', vol:float = 0.015, r:float = 0.01):
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
        self.S      = np.append(self.S, self.price)
        self.pct = ((self.price-self.tmp)/self.tmp)*100

        pctcolor = '+' if self.pct > 0 else ''
        self.pctprint = f"{pctcolor}{self.pct:.2f}".rjust(10)

        self.cnt   += 1

if __name__ == '__main__':
    aa = Stock(name='asdf')
    for i in range(1440*30):
        aa.day()
    print(aa.price)