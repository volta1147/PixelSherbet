import discord
from discord import app_commands
from discord.ext import commands
from launchio import lndir, sep
import random
import lib.file as file
import lib.MemoUI as MemoUI

def guildCmd(guild_id:int):
    cmd = f'guild_memo{sep}{guild_id}'
    if not lndir('community', 'guild_memo', str(guild_id)).isdir():
        lndir('community', 'guild_memo', str(guild_id)).makedirs()
    return cmd

class WriteModal(MemoUI.WriteModal):
    def __init__(self, memo_title, cmd='memo'):
        super().__init__(memo_title = memo_title)
        self.cmd = cmd
    
    async def on_submit(self, interaction: discord.Interaction):
        filename = str(self.memo_title)
        memo     = str(self.memo_contx)
        footer   = self.cmd.split(sep)[0]
        file.editfile(self.cmd, filename, memo)
        embed = discord.Embed(title = filename, description = file.openfile(self.cmd, filename), color = 0x5662F6)
        embed.set_footer(text = file.memo_footer(footer, filename))
        return await interaction.response.send_message(embed=embed, ephemeral=True)

class WriteModal_profile(MemoUI.WriteModal):
    def __init__(self, userinfo:discord.User):
        super().__init__(memo_title = userinfo.name)
        self.userID = userinfo.id
    
    async def on_submit(self, interaction: discord.Interaction):
        filename  = str(self.userID    )
        memoTitle = str(self.memo_title)
        memo      = str(self.memo_contx)
        file.editfile('profile', filename, memo)
        embed = discord.Embed(title = memoTitle, description = file.openfile('profile', filename), color = 0x5662F6)
        embed.set_footer(text = file.memo_footer('profile', memoTitle))
        return await interaction.response.send_message(embed=embed, ephemeral=True)

async def openfile(interaction: discord.Interaction, memo_title:str, title = '', cmd='memo', raw=False, ephemeral=False):
    filename = MemoUI.open_name(memo_title)
    memo_state, embed = MemoUI.memo_embed(filename, title=title, cmd=cmd)
    if memo_state == "OK":
        if raw:
            return await interaction.response.send_message(f"# `{embed.title}`\n```"+embed.description+"```", ephemeral=ephemeral)
        else:
            return await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
    else:
        return await interaction.response.send_message(content="메모를 찾지 못했어요. ", embed=embed, ephemeral=True)

class Memo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    '''메모 명령어'''

    memo = app_commands.Group(name="memo", description="메모 명령어")

    @memo.command(name="edit", description="메모 편집")
    @app_commands.describe(title='제목')
    async def edits(self, interaction:discord.Interaction, title:str):
        await interaction.response.send_modal(WriteModal(memo_title=title))

    @memo.command(name="open", description="메모 열기")
    @app_commands.describe(title='제목', raw='원문')
    async def opens(self, interaction:discord.Interaction, title:str, raw:bool=False, ephemeral:bool=False):
        await openfile(interaction, title, raw=raw, ephemeral=ephemeral)

    @memo.command(name="random", description="메모의 아무 줄이나 긁어옵니다. ")
    @app_commands.describe(title='제목')
    async def randomline(self, interaction:discord.Interaction, title:str, ephemeral:bool=False):
        if file.ismemo(title):
            await interaction.response.send_message(random.choice(file.openfile("memo", title).splitlines()), ephemeral=ephemeral)
        else:
            await interaction.response.send_message(f'`{title}` 메모가 없어요. ', ephemeral=True)

    @memo.command(name="search", description="메모 검색")
    @app_commands.describe(title='검색어')
    async def search2(self, interaction:discord.Interaction, title:str, ephemeral:bool=False):
        resp = ""
        flst = lndir('community', 'memo').listdir()
        find = []
        for i in flst:
            if title in i:
                find.append(i[:-4])
        find.sort()
        if len(find) != 0:
            resp = f"```\n{title}에 대한 검색결과 : {len(find)} 건\n"
            cnt  = 0
            for i in find:
                cnt  += 1
                resp += f"{cnt}. {i}\n"
            resp += "```"
        else:
            resp  = f"```\n{title}에 대한 검색결과가 없어요. "
        await interaction.response.send_message(resp, ephemeral=ephemeral)

    '''서버 메모 명령어'''

    memo_private = app_commands.Group(name="private", description="서버 메모 명령어")

    @memo_private.command(name="edit", description="서버 메모 편집")
    @app_commands.describe(title='제목')
    async def editsp(self, interaction:discord.Interaction, title:str):
        guild_id = interaction.guild.id
        cmd = guildCmd(guild_id)
        await interaction.response.send_modal(WriteModal(memo_title=title, cmd=cmd))

    @memo_private.command(name="open", description="서버 메모 열기")
    @app_commands.describe(title='제목', raw='원문')
    async def opensp(self, interaction:discord.Interaction, title:str, raw:bool=False, ephemeral:bool=False):
        guild_id = interaction.guild.id
        cmd = guildCmd(guild_id)
        await openfile(interaction, title, cmd=cmd, raw=raw, ephemeral=ephemeral)

    @memo_private.command(name="random", description="서버 메모의 아무 줄이나 긁어옵니다. ")
    @app_commands.describe(title='제목')
    async def randomlinep(self, interaction:discord.Interaction, title:str, ephemeral:bool=False):
        guild_id = interaction.guild.id
        cmd = guildCmd(guild_id)
        
        if file.ismemo(title):
            await interaction.response.send_message(random.choice(file.openfile(cmd, title).splitlines()), ephemeral=ephemeral)
        else:
            await interaction.response.send_message(f'`{title}` 메모가 없어요. ', ephemeral=True)

    @memo_private.command(name="search", description="서버 메모 검색")
    @app_commands.describe(title='검색어')
    async def searchp(self, interaction:discord.Interaction, title:str, ephemeral:bool=False):
        guild_id = interaction.guild.id
        cmd = guildCmd(guild_id)

        resp = ""
        flst = lndir('community', 'guild_memo', str(guild_id)).listdir()
        find = []
        for i in flst:
            if title in i:
                find.append(i[:-4])
        find.sort()
        if len(find) != 0:
            resp = f"```\n{title}에 대한 검색결과 : {len(find)} 건\n"
            cnt  = 0
            for i in find:
                cnt  += 1
                resp += f"{cnt}. {i}\n"
            resp += "```"
        else:
            resp  = f"```\n{title}에 대한 검색결과가 없어요. "
        await interaction.response.send_message(resp, ephemeral=ephemeral)

    '''자기소개 명령어'''

    profile = app_commands.Group(name="profile", description="자기소개 명령어")

    @profile.command(name="edit", description="자기소개 편집")
    async def editpf(self, interaction:discord.Interaction):
        await interaction.response.send_modal(WriteModal_profile(interaction.user))

    @profile.command(name="open", description="자기소개 열기")
    @app_commands.describe(user='사용지지', raw='원문')
    async def openpf(self, interaction:discord.Interaction, user:discord.Member|discord.User|None=None, raw:bool=False, ephemeral:bool=False):
        user2 = interaction.user if user == None else user
        await openfile(interaction, str(user2.id), user2.name, cmd='profile', raw=raw, ephemeral=ephemeral)

async def setup(bot):
    await bot.add_cog(Memo(bot))