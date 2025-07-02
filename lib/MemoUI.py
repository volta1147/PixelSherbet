import discord
from launchio import ln, sep
from discord.ext import commands
import lib.file as file

pf = ln("res", "memoprefix.txt").read()

def getusercolor(ctx, userid):
    color = 0x000000
    for i in ctx.guild.roles:
        if userid in [j.id for j in i.members]:
            color = str(i.color)
    return int("0x"+color[1:], 16)

def open_name(filenamein: str):
    if ln("community", "memo", filenamein).isfile():
        if (file.openfile("memo", filenamein).split())[0] == pf + "redirect":
            filename = " ".join((file.openfile("memo", filenamein).split())[1:])
        else:
            filename = filenamein
        return filename
    else:
        return filenamein

def memo_embed(filename:str, cmd:str='memo', title='', guild_id=-1):
    support_title = ['memo', 'guild_memo']
    footer = cmd.split(sep)[0]
    title_display = filename if footer in support_title else title
    if ln("community", cmd, filename, form='txt').isfile():
        embed = discord.Embed(title = title_display, description = file.openfile(cmd, filename), color = 0x5662F6)
        embed.set_footer(text = file.memo_footer(footer, filename))
        state = "OK"
    else:
        embed = discord.Embed(title = title_display, description = "찾으려는 문서가 없어요. ", color = 0xFF0000)
        embed.set_footer(text = "Error")
        state = "NoMemo"
    
    return state, embed

def profile_embed(ctx:commands.Context, userinfo):
    name = userinfo.name
    userid = userinfo.id
    if ln("community", "profile", str(userid)).isfile():
        embed = discord.Embed(title = name, description = file.openfile("profile", str(userid)), color = getusercolor(ctx, userid))
        embed.set_footer(text = f"profile - {name} | exp = {file.userlvl(userid, ctx.guild.id)}")
        state = "OK"
    else:
        embed = discord.Embed(title = name, description = "아직 자기소개가 없어요. ", color = 0xFF0000)
        embed.set_footer(text = "Error")
        state = "NoMemo"
    
    return state, embed

'''========== 여기까지 메모 기본 엔진, 아래부터 메모 틀 관련 =========='''

class WriteModal(discord.ui.Modal, title = "글쓰기"):
    def __init__(self, memo_title):
        self.memo_title = memo_title
        super().__init__()

    memo_contx = discord.ui.TextInput(label="내용", placeholder="내용을 적어주세요. ", style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"{self.memo_contx}")

class OpenModal(discord.ui.Modal, title = "불러오기"):
    memo_contx = discord.ui.TextInput(label="제목", placeholder="제목을 적어주세요. ", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"제목 : {self.memo_title}\n"+"="*20+"\n{self.memo_contx}")