import discord
from discord import app_commands
from discord.ext import commands
import random
import time
import matplotlib.pyplot as plt
from launchio import ln
from launchio.json import JSON
from lib.file import json_path

# 여기에 사용자 정의 라이브러리 넣기

gap = 1000
timeout = 60

user_file = JSON(json_path.chifile('users.json'))
adminc_file = JSON(json_path.chifile('adminc.json'))
server_file = JSON(json_path.chifile('servers.json'))

def top_rank(guild_id:int):
    if str(guild_id) not in list(server_file().keys()) or user_file()[str(guild_id)]['users'] == []:
        return '', False
    else:
        a = user_file()
        users = [(i['nick'], i['chats'])  for i in a[str(guild_id)]['users']]
        userids = sorted(users, key=lambda x:x[1], reverse=True)

        return userids[0][0], True
    
class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message:discord.message.Message):
        adminc_raw = adminc_file()["admins"]
        adminc = []

        for i in adminc_raw.values():
            adminc.extend(i)
            
        msgchannel  = message.channel
        channelid   = (msgchannel.parent_id) if (type(msgchannel) == discord.Thread) else (msgchannel.id)
        guildid     = message.guild.id if message.guild != None else None
        if str(guildid) not in list(server_file().keys()):
            server_file.edit(str(guildid), value={"exp_down": 20, "exp_up": 40, "top_notification": False})
            user_file.edit(str(guildid), "users", value=[])
        if channelid not in adminc and not message.author.bot:
            a = user_file()
            before, is_loud = top_rank(message.guild.id)
            
            exp_up   = server_file()[str(message.guild.id)]['exp_up']
            exp_down = server_file()[str(message.guild.id)]['exp_down']
            exp0 = 0
            exp1 = 0
            upgrade = random.randrange(exp_down, exp_up)
            # newpoint = random.randrange(1, 5)
            if message.author.id not in [i['id'] for i in a[str(message.guild.id)]['users']]:
                a[str(message.guild.id)]['users'].append({
                    'id'    : message.author.id,
                    'nick'  : message.author.name,
                    'chats' : upgrade,
                    'min'   : True, # False
                    'last'  : time.time()
                })
            else:
                for i in a[str(message.guild.id)]['users']:
                    if i['id'] == message.author.id and i['min']:
                        if time.time() - i['last'] < timeout:
                            break
                        exp0        = i['chats']//gap
                        i['nick']   = message.author.name
                        i['chats'] += upgrade
                        i['min']    = True # False
                        i['last']   = time.time()
                        exp1        = i['chats']//gap

            if exp1 > exp0:
                await message.channel.send(f"{message.author.mention} 님이 {exp1} 레벨로 레벨업했습니다. ")

            user_file.dump(a)

            after, tmp = top_rank(message.guild.id)

            if is_loud and before != after:
                await message.channel.send(f"## 순위 변동!\n🥇 `{before}` ➡️ {message.author.mention}")

    @app_commands.command(name = "rank", description = "레벨 정보를 출력합니다. ")
    async def rank(self, interaction: discord.Interaction, user:discord.Member|discord.User|None=None, ephemeral:bool=False):
        if interaction.channel.type == discord.ChannelType.private:
            await interaction.response.send_message('DM에서 사용이 불가능한 명령어에요. ', ephemeral=True)
            return
        user2 = interaction.user if user == None else user
        a = user_file()
        userids  = [i['id']    for i in a[str(interaction.guild.id)]['users']]
        userexps = [i['chats'] for i in a[str(interaction.guild.id)]['users']]
        users = zip(userids, userexps)

        userids2 = sorted(users, key=lambda x:x[1], reverse=True)
        ranklist:tuple = list(zip(*userids2))[0]

        if user2.id in userids:
            exp0 = 0
            exp2 = 0
            ranking = ranklist.index(user2.id) + 1
            for i in a[str(interaction.guild.id)]['users']:
                if i['id'] == user2.id:
                    exp0 = i['chats']//gap
                    exp2 = i['chats']% gap
            plt.figure(figsize = (10, 1))
            plt.barh([1], [exp2], height = 0.1)
            plt.title(f"{user2.name} Level {exp0} -> {exp0+1}")
            plt.xticks(list(range(0, 1100, 100)))
            plt.yticks([1], labels=[f"{exp2}"])

            plt.savefig('rank.png', bbox_inches='tight', pad_inches=0.2)
            await interaction.response.send_message(f"### `{user2.name}` 님의 레벨 정보\n레벨 : Level {exp0} ({exp2} points)\n순위 : {ranking}위", file=discord.File('rank.png'), ephemeral=ephemeral)
        else:
            await interaction.response.send_message("아직 채팅 기록이 없습니다. ")

    @app_commands.command(name = "leaderboard", description = "레벨 등수를 출력합니다. ")
    async def leaderboard(self, interaction: discord.Interaction, page:int=1, ephemeral:bool=False):
        if interaction.channel.type == discord.ChannelType.private:
            await interaction.response.send_message('DM에서 사용이 불가능한 명령어에요. ', ephemeral=True)
            return
        a = user_file()
        usernames = [i['nick']  for i in a[str(interaction.guild.id)]['users']]
        userexps  = [i['chats'] for i in a[str(interaction.guild.id)]['users']]
        users = zip(usernames, userexps)

        userids = sorted(users, key=lambda x:x[1], reverse=True)
        if page < 1 or page > (len(userids)+9)/10:
            await interaction.response.send_message('조회할 수 없는 페이지에요.')
            return
        if page > (len(userids)-1)/10:
            userids2 = userids[(page-1)*10:]
        else:
            userids2 = userids[(page-1)*10:page*10]

        res = f"### {interaction.guild.name} Leaderboard {page}/{int(len(userids)/10+0.9)}\n```"
        rank = (page-1)*10
        for i in userids2:
            rank += 1
            res  += f"\n{str(rank)}. {i[0]} : {str(i[1])} (Level {i[1]//gap})"
        res += "```"

        await interaction.response.send_message(res, ephemeral=ephemeral)

    admin = app_commands.Group(name="level", description="레벨 관리 시스템")

    @admin.command(name = "limit", description = "경험치 상승 범위를 결정합니다. ")
    @app_commands.describe(down='하한선', up='상한선')
    async def set_limit(self, interaction:discord.Interaction, down:int=-1, up:int=-1):
        if interaction.guild and interaction.user.guild_permissions.manage_guild:
            if abs(up+1) + abs(down+1) == up + down + 2:
                server_file.append(str(interaction.guild.id), 'exp_down', value=down)
                server_file.append(str(interaction.guild.id), 'exp_up'  , value=up  )
                await interaction.response.send_message("적용 완료!")
            else:
                await interaction.response.send_message("장난치지 마세요")
        else:
            await interaction.response.send_message("권한이 없어요. ")
    
    @admin.command(name = "top_rank", description = "1위 변동이 있을 때 알립니다. ")
    @app_commands.describe(notification='알림')
    async def iLoveTOP(self, interaction:discord.Interaction, notification:bool|None): # 빨주노초 I'm legend 타노스
        if interaction.guild and interaction.user.guild_permissions.manage_guild:
            changed = False
            if notification != None:
                changed = True
                server_file.edit(str(interaction.guild.id), "top_notification", value=notification)

            if changed:
                await interaction.response.send_message("수정 완료!")
            else:
                await interaction.response.send_message("변경사항이 없어요.")
        else:
            await interaction.response.send_message("권한이 없어요. ")

    @admin.command(name = 'disable_channel', description = '경험치 획득을 막을 채널을 지정합니다. ')
    @app_commands.describe(able='허용 여부')
    async def adminc(self, interaction:discord.Interaction, able:bool=False):
        if able:
            adminc_file.remove('admins', str(interaction.guild.id), value=interaction.channel.id)
        else:
            adminc_file.append('admins', str(interaction.guild.id), value=interaction.channel.id)
        await interaction.response.send_message(f"설정 완료! ")

async def setup(bot:commands.bot):
    await bot.add_cog(Level(bot))
    rest = ln("res", "json", "users", form="json").read().replace("\"min\": false", "\"min\": true")
    ln("res", "json", "users", form="json").write(rest)