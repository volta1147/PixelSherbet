import discord
from discord import app_commands
import time
import datetime
import lib.file as file
import asyncio
from discord.ext import commands, tasks
from datetime    import timedelta
from typing      import Literal

KST=datetime.timezone(datetime.timedelta(hours=9))

weekday2num = {'Mon':0, 'Tue':1, 'Wed':2, 'Thr':3, 'Fri':4, 'Sat':5, 'Sun':6}
weeknum2day = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thr', 4:'Fri', 5:'Sat', 6:'Sun'}

def alarm_list(user:discord.User|discord.Member):
    alarms = list(file.read_json('alarm').values())[0]
    my_alarms = []
    alarm_name_max = 0
    alarm_info = lambda x, a: f"{x['name'].ljust(a)} - {weeknum2day[x['weekday']]} {str(x['hour']).zfill(2)} : {str(x['minute']).zfill(2)}"
    for i in alarms:
        if i['id'] == user.id:
            my_alarms.append(i)
            alarm_name_max = len(i['name']) if len(i['name']) > alarm_name_max else alarm_name_max
    result = f"### {user.mention} 님의 알람 목록\n```" + '\n'.join([alarm_info(i, alarm_name_max) for i in my_alarms]) + '```'

    return result

def enabled_alarms(alarms:list[dict]):
    result = []
    for i in alarms:
        if i['activate']:
            result.append(i)
    return result

class AlarmSelect(discord.ui.Select):
    def __init__(self, title:str, alarms:list[dict]):
        options = [] # [discord.SelectOption(label="나가기", emoji="⬅️")]
        for i in alarms:
            emoji = "✅" if i['activate'] else "❌"
            options.append(discord.SelectOption(label=i['name'], description=f"{weeknum2day[i['weekday']]} {i['hour']} : {str(i['minute']).zfill(2)}", emoji=emoji, default=i['activate']))
        super().__init__(placeholder = title, options = options, min_values=0, max_values=len(alarms))

    # async def callback(self, interaction: discord.Interaction):
    #     # 몰라 씨발
    #     result = alarm_list(interaction.user)
    #     await interaction.response.edit_message(content=result, view=None)

class Select(discord.ui.View):
    def __init__(self, title:str, alarms:list[dict]):
        super().__init__()
        self.add_item(AlarmSelect(title, alarms))

# 여기에 사용자 정의 라이브러리 넣기

class Alarm(commands.Cog):
    WEEKDAYS = Literal['Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sat']
    HOURS    = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.alarms = {f'{i['id']}-{i['name']} {i['weekday']}-{i['hour']}-{i['minute']}':i for i in list(file.read_json('alarm').values())[0]}
        self.nexttime = 60 - datetime.datetime.now().second - datetime.datetime.now().microsecond/1000000

        self.update_alarms.start()

    def cog_unload(self):
        self.update_alarms.cancel()

    @tasks.loop(minutes=1)
    async def update_alarms(self):
        await asyncio.sleep(self.nexttime)
        now = datetime.datetime.now(tz=KST)+timedelta(seconds=1) # 59.999999초 방지
        tmstr = f'{now.weekday()}-{now.hour}-{now.minute}'
        for i in self.alarms.keys():
            if tmstr == i.split()[-1]:
                alarm:dict = self.alarms[i]
                if alarm['activate']:
                    result = f'### `{alarm['name']}`\n{weeknum2day[alarm['weekday']]} {alarm['hour']}시 {str(alarm['minute']).zfill(2)}분에 지정된 `{alarm['name']}` 알람'
                    print(result)

                    chat = await self.bot.get_user(alarm['id']).create_dm()

                    await chat.send(result)

    alarm = app_commands.Group(name="alarm", description="알람을 관리합니다.")

    @alarm.command(name = "new", description = "알람을 추가합니다.")
    @app_commands.describe(name='알람 이름', weekday='요일', hour='시간', minute='분')
    async def pyselect(self, interaction:discord.Interaction, name:str, weekday:WEEKDAYS, hour:HOURS, minute:int):
        weeknum = weekday2num[weekday]
        exist = False
        for i in self.alarms.values():
            if i['id'] == interaction.user.id and i['name'] == name:
                exist = True
                break
        if not exist:
            file.append_json('alarm', "alarms_forever", {'name':name, 'DM':True, 'activate':True, 'id':interaction.user.id, 'weekday':weeknum, 'hour':hour, 'minute':minute})
            self.alarms = {f'{i['id']}-{i['name']} {i['weekday']}-{i['hour']}-{i['minute']}':i for i in list(file.read_json('alarm').values())[0]}
            await interaction.response.send_message(f"{interaction.user.mention} {weekday} {str(hour).zfill(2)}:{str(minute).zfill(2)}에 `{name}` 알람이 추가되었습니다. ")
        else:
            await interaction.response.send_message(f"`{name}` 알람은 이미 존재합니다. ")

    @alarm.command(name = "list", description = "알람 목록을 출력합니다.")
    async def alarmlist(self, interaction:discord.Interaction):
        result = alarm_list(interaction.user)
        await interaction.response.send_message(result)

    @alarm.command(name='delete', description = "알람을 삭제합니다.")
    @app_commands.describe(name='알람 이름')
    async def nomorealarm(self, interaction:discord.Interaction, name:str):
        exist = False
        key_string = ''
        for i in self.alarms.values():
            if i['id'] == interaction.user.id and i['name'] == name:
                exist = True
                key_string = f'{i['id']}-{i['name']} {i['weekday']}-{i['hour']}-{i['minute']}'
                break
        if exist:
            del self.alarms[key_string]
            file.edit_json('alarm', key='alarms_forever', value=list(self.alarms.values()))
            time_str = f"{weeknum2day[i['weekday']]} {i['hour']} : {str(i['minute']).zfill(2)}"
            await interaction.response.send_message(f"{time_str} 에 있었던 `{name}` 알람을 삭제했습니다. ")
        else:
            await interaction.response.send_message(f"`{name}` 알람이 없습니다. ")
    
    # 알람 껐다켜는거 좆같이 어렵네 씨봉방
    # @alarm.command(name = "select", description = "알람을 선택합니다.")
    # async def alarmselect(self, interaction:discord.Interaction):
    #     alarm_select = Select('알람 목록', list(self.alarms.values()))
    #     await interaction.response.send_message(content=f"### {interaction.user.mention} 님의 알람 목록", view=alarm_select, ephemeral=True)
        
async def setup(bot):
    await bot.add_cog(Alarm(bot))
