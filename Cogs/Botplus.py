import discord
from discord import app_commands
from discord.ext import commands
from launchio import lndir
from launchio.json import JSON
from lib.file import community_path
import datetime

KST=datetime.timezone(datetime.timedelta(hours=9))

# 여기에 사용자 정의 함수/라이브러리 넣기

def char_number(string):
    iskorean = lambda x: ord(x) >= 44032 and ord(x) < 55024

    st_list = [2,4,2,3,6,5,4,4,8,2,4,1,3,6,4,3,4,4,3]
    md_list = [2,3,3,4,2,3,3,4,2,4,5,3,3,2,4,5,3,3,1,2,1]
    en_list = [0,2,4,4,2,5,5,3,5,7,9,9,7,9,9,8,4,4,6,2,4,1,3,4,3,4,4,3]

    cap_list   = [3,3,1,2,4,3,3,3,3,2,3,2,4,3,1,2,2,3,1,2,1,2,4,2,3,3]
    alpha_list = [2,2,1,2,2,2,2,2,2,2,3,1,3,2,1,2,2,2,1,2,2,2,4,2,2,3]

    num_list = [1,2,2,2,3,3,1,2,1,1]

    result = []

    for i in string:
        if iskorean(i):
            i_ = ord(i) - 44032
            st = int(i_//28//21)
            md = int(i_//28%21)
            en = int(i_%28)
            result.append(st_list[st] + md_list[md] + en_list[en])
        elif i.isalpha():
            i_ = ord(i) - 65
            if i_ > 27:
                i_ -= 32
                result.append(alpha_list[i_])
            else:
                result.append(cap_list[i_])
        elif i.isdecimal():
            result.append(num_list[int(i)])
    
    return result

def append_log(log_type:str, message:discord.Message, content:str, user:discord.User):
    logdir = lndir('community', 'anonymous', str(message.guild.id))
    file = logdir.chifile('log.json')
    if not logdir.isdir():
        logdir.makedirs()
        file.write('{}')
    log = JSON(file)
    content_ = ''
    if len(content) > 20:
        content_ = content[:20] + '...'
    else:
        content_ = content
    content_.replace('\n', ' ')
    
    info = {'type':log_type, 'channel':message.channel.jump_url, 'user':user.mention, 'content':content_, 'url':f'[link](<{message.jump_url}>)'}
    info['time'] = message.created_at.astimezone(tz=KST).isoformat(sep=' ', timespec='minutes')[:-6]
    if message.channel.type == discord.ChannelType.public_thread:
        info['channel'] = message.channel.parent.jump_url

    log.edit(str(message.id), value=info)
    return info

def append_lembed(log:dict, embed:discord.Embed):
    embed.add_field(name=f'{log['type']}: {log['content']} in {log['channel']} by {log['user']}', value=f'{log['time']} | {log['url']}')

class Botplus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Restarting...")

    @commands.command(name = "print", help = "입력한 내용을 출력합니다 (원본 메시지 삭제)")
    async def printctx(self, ctx:commands.Context, *, abc):
        author = ctx.message.author
        author_name = author.name
        await ctx.message.delete()
        resp = await ctx.send(abc, reference = ctx.message.reference)
        await ctx.send(f'-# `{author_name}` 님이 사용한 p?print 명령어')
        if ctx.channel.type != discord.ChannelType.private:
            append_log('p?print', resp, abc, author)

    @commands.command(name = "reaction", help = "메시지에 반응을 추가합니다. 답장을 이용하거나 메시지 ID를 이용하여 반응을 추가하고 싶은 메시지를 선택하세요.")
    async def reactionctx(self, ctx:commands.Context, abc, message_id=0):
        await ctx.message.delete()
        original_message = None
        if message_id == 0:
            original_message = ctx.message.reference.resolved
        else:
            original_message = await ctx.fetch_message(message_id)
        await original_message.add_reaction(abc)

    @app_commands.command(name = "print", description="입력한 내용을 출력합니다")
    @app_commands.describe(text='적을 내용')
    async def printctx2(self, interaction: discord.Interaction, text:str):
        chat = await interaction.channel.send(text)
        # await interaction.channel.send(f'-# `{interaction.user.name}` 님이 사용한 /print 명령어')
        await interaction.response.send_message(f'완료', ephemeral=True)
        append_log('/print', chat, text, interaction.user)

    @app_commands.command(name = "forum", description="포럼에 새 글을 남깁니다")
    @app_commands.describe(forum='포럼 채널', title='제목', text='적을 내용')
    async def forumchat(self, interaction: discord.Interaction, forum:discord.channel.ForumChannel, title:str, text:str):
        if interaction.channel.type == discord.ChannelType.private:
            await interaction.response.send_message('DM에서 사용이 불가능한 명령어에요. ', ephemeral=True)
            return
        post = await forum.create_thread(name=title, content=text)
        # await post.thread.send(f'-# `{interaction.user.name}` 님이 사용한 /forum 명령어')
        await interaction.response.send_message(f"`{title}` 생성 완료", ephemeral=True)
        append_log('/forum', post.message, text, interaction.user)

    @app_commands.command(name = "logs", description="익명 명령어 사용기록을 확인합니다. ")
    async def anonylog(self, interaction: discord.Interaction, ephemeral:bool=False):
        if interaction.channel.type == discord.ChannelType.private:
            await interaction.response.send_message('DM에서 사용이 불가능한 명령어에요. ', ephemeral=True)
            return
        if not (interaction.guild and interaction.user.guild_permissions.administrator):
            await interaction.response.send_message("권한이 없습니다. ", ephemeral=True)
            return
        community_log = community_path.chifile('anonymous', str(interaction.guild_id), 'log.json')
        embed = discord.Embed(title='PixelMalang Log')
        log_list = list(JSON(community_log).read().values())
        log_list.reverse()
        if len(log_list) > 10:
            log_list = log_list[:10]
        for i in log_list:
            append_lembed(i, embed)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        
    @app_commands.command(name = "love", description="이름 궁합")
    @app_commands.describe(name1='이름1', name2='이름2')
    async def love(self, interaction: discord.Interaction, name1:str, name2:str):
        num_a = char_number(name1)
        num_b = char_number(name2)

        if len(name1) > len(name2):
            num_b += [0] * (len(name1) - len(name2))
        elif len(name1) < len(name2):
            num_a += [0] * (len(name2) - len(name1))

        calc = []
        calc_tmp = []
        for i in range(len(num_a)):
            calc.append(num_a[i])
            calc.append(num_b[i])

        while True:
            calc_tmp = calc.copy()
            calc.clear()
            for i in range(len(calc_tmp)-1):
                calc.append(int((calc_tmp[i] +calc_tmp[i+1])%10))
            if len(calc) == 2:
                break

        result = ''.join(map(str, calc))

        await interaction.response.send_message(f"`{name1}`와(과) `{name2}`의 궁합 : `{result}%`")
    
async def setup(bot:commands.bot):
    await bot.add_cog(Botplus(bot))