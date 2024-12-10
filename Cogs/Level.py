import discord
from discord import app_commands
from discord.ext import commands
import json
import random
import time
import lib.file as file
import matplotlib.pyplot as plt
from launchio import ln

# 여기에 사용자 정의 라이브러리 넣기

gap = 1000
timeout = 60

class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message:discord.message.Message):
        adminc = file.read_json("adminc")["admins"]
        msgchannel = message.channel
        channelid  = (msgchannel.parent_id) if (type(msgchannel) == discord.Thread) else (msgchannel.id)
        if channelid not in adminc and not message.author.bot:
            a = json.load(ln("community", "chats", form="json").open())
            exp0 = 0
            exp1 = 0
            upgrade = random.randrange(10, 20)
            newpoint = random.randrange(1, 5)
            if message.author.id not in [i['id'] for i in a[str(message.guild.id)]['users']]:
                a[str(message.guild.id)]['users'].append({
                    'id'    : message.author.id,
                    'nick'  : message.author.name,
                    'chats' : upgrade,
                    'points': newpoint,
                    'stock' : {},
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
                        i['points']+= newpoint
                        i['min']    = True # False
                        i['last']   = time.time()
                        exp1        = i['chats']//gap

            if exp1 > exp0:
                await message.channel.send(f"{message.author.mention} 님이 {exp1} 레벨로 레벨업했습니다. ")

            with ln("community", "chats", form="json").open(mode='w') as fle:
                json.dump(a, fle, indent=2)

    @app_commands.command(name = "rank", description = "레벨 정보를 출력합니다. ")
    async def rank(self, interaction: discord.Interaction, user:discord.Member|discord.User|None=None, ephemeral:bool=False):
        user2 = interaction.user if user == None else user
        a = json.load(ln("community", "chats", form="json").open())
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
    async def leaderboard(self, interaction: discord.Interaction, top10:bool=True, ephemeral:bool=False):
        a = json.load(ln("community", "chats", form="json").open())
        usernames = [i['nick']  for i in a[str("1196753753618010162")]['users']]
        userexps  = [i['chats'] for i in a[str(interaction.guild.id)]['users']]
        users = zip(usernames, userexps)

        userids = sorted(users, key=lambda x:x[1], reverse=True)
        userids2 = userids[:10] if top10 else userids

        res = f"### {interaction.guild.name} Leaderboard\n```"
        rank = 0
        for i in userids2:
            rank += 1
            res  += f"\n{str(rank).rjust(2)}. {i[0].ljust(16)} : {str(i[1]).ljust(5)} (Level {i[1]//gap})"
        res += "```"

        await interaction.response.send_message(res, ephemeral=ephemeral)

async def setup(bot:commands.bot):
    await bot.add_cog(Level(bot))
    rest = ln("community", "chats", form="json").read().replace("\"min\": false", "\"min\": true")
    ln("community", "chats", form="json").write(rest)
