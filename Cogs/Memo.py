import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import lib.botsetup as botset
import lib.file as file
import lib.MemoUI as MemoUI
from launchio import lndir

class MemoSelect(MemoUI.MemoSelect):
    def __init__(self):
        super().__init__()

    async def callback(self, interaction: discord.Interaction):
        # await interaction.response.send_message(content=f"{self.values}", ephemeral=True)
        if self.values[0] == "열기":
            await interaction.response.send_modal(OpenModal())
        if self.values[0] == "수정":
            await interaction.response.send_modal(WriteModal())
        if self.values[0] == "종료":
            await interaction.response.send_message("메모를 정지합니다. ")

class Select(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(MemoSelect())

class WriteModal(MemoUI.WriteModal):
    async def on_submit(self, interaction: discord.Interaction):
        filename = str(self.memo_title)
        memo     = str(self.memo_contx)
        file.editfile("memo", filename, memo)
        file.rev("rev", filename, memo)
        embed = discord.Embed(title = filename, description = file.openfile("memo", filename), color = 0xbdb092)
        embed.set_footer(text = file.memover('memo', filename, file.getver('rev', filename)))
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
class WriteModal2(MemoUI.WriteModal2):
    def __init__(self, memo_title):
        super().__init__(memo_title = memo_title)
    
    async def on_submit(self, interaction: discord.Interaction):
        filename = str(self.memo_title)
        memo     = str(self.memo_contx)
        file.editfile("memo", filename, memo)
        file.rev("rev", filename, memo)
        embed = discord.Embed(title = filename, description = file.openfile("memo", filename), color = 0xbdb092)
        embed.set_footer(text = file.memover('memo', filename, file.getver('rev', filename)))
        return await interaction.response.send_message(embed=embed, ephemeral=True)

async def openfile(interaction: discord.Interaction, memo_title):
    memo_state, embed = MemoUI.memo_embed(memo_title)
    if not memo_state == "OK":
        return await interaction.response.send_message(content="메모를 찾지 못했습니다. ", embed=embed, ephemeral=True)
    else:
        return await interaction.response.send_message(embed=embed)
    
class OpenModal(MemoUI.OpenModal):
    async def on_submit(self, interaction: discord.Interaction):
        memo_title = str(self.memo_title)
        await openfile(interaction, memo_title)

class AppendModal(MemoUI.WriteModal2):
    def __init__(self, memo_title):
        super().__init__(memo_title = memo_title)
    
    async def on_submit(self, interaction: discord.Interaction):
        filename = str(self.memo_title)
        memo     = str(self.memo_contx)
        file.appendfile("memo", filename, "\n"+memo)
        file.rev("rev", filename, memo, 'a')
        embed = discord.Embed(title = filename, description = file.openfile("memo", filename), color = 0xbdb092)
        embed.set_footer(text = file.memover('memo', filename, file.getver('rev', filename)))
        return await interaction.response.send_message(embed=embed, ephemeral=True)

class Memo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(help = "메모 입출력 관련")
    async def memo(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("명령어가 올바르지 않습니다. ")

    @memo.command(name = "open", help = "메모를 출력합니다.")
    async def openm(self, ctx:commands.Context, *, filenamein):
        filename = MemoUI.open_name(filenamein)
        if file.ismemo(filename):
            embed = discord.Embed(title = filename, description = file.openfile("memo", filename), color = 0xbdb092)
            embed.set_footer(text = file.memover('memo', filename, file.getver('rev', filename)))
            memoembed = await ctx.send(embed = embed)
            await asyncio.sleep(30)
            await memoembed.edit(view=None)
        else:
            await ctx.send(filename+" 메모가 없습니다. "+filename+" 메모를 생성하려면 \n```"+botset.prefix+"memo edit "+filename+" 메모 내용```\n 을 입력하세요.")

    @memo.command(name = "open2")
    async def openm2(self, ctx:commands.Context, *, filenamein):
        memo_state, embed = MemoUI.memo_embed(filenamein)
        memo_cont = await ctx.send(embed=embed)
        if memo_state == "OK":
            await asyncio.sleep(30)
            await memo_cont.edit(view=None)

    @memo.command(help = "메모를 작성/수정합니다. ")
    async def edit(self, ctx, filenamein, *, memoin):
        if filenamein[0] == "'":
            tmpmemolist = memoin.split("'")
            filename = filenamein[1:] + " " + tmpmemolist[0]
            memo = ("'".join(tmpmemolist[1:]))[1:]
        else:
            filename = filenamein
            memo = memoin
        isexist = file.ismemo(filename)
        file.editfile("memo", filename, memo)
        file.rev("rev", filename, memo)
        if isexist:
            await ctx.send("**{}** 수정됨".format(filename))
        else:
            await ctx.send("**{}** 생성됨".format(filename))
    
    @memo.command(help = "메모를 삭제합니다. ")
    async def delete(self, ctx, filename):
        file.delfile("memo", filename)
        await ctx.send("삭제됨")

    @commands.command(help = "맨션한 사람(또는 자신)의 유저 정보를 출력합니다. ")
    async def profile(self, ctx, user = " "):
        if user == " ":
            userinfo = ctx.message.author
        else:
            userinfo = await commands.MemberConverter.convert(self=commands.MemberConverter, ctx=ctx, argument=user)
        await MemoUI.profile_embed(ctx, userinfo, -1)

    @commands.command(help = "자기소개를 작성/수정합니다. ")
    async def introduce(self, ctx, *, memo):
        userid = ctx.message.author.id
        file.editfile("profile", str(userid), memo)
        file.rev("profilerev", str(userid), memo)
        await ctx.send("수정 완료")

    @commands.group(help = "메모 리버전 관련")
    async def rev(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("명령어가 올바르지 않습니다. ")

    @rev.command(name = "memo", help = "메모 리버전을 엽니다. ")
    async def memo2(self, ctx, filename, ver):
        if file.isrev("rev", filename, ver):
            embed = discord.Embed(title = filename, description = file.openrev("rev", filename, ver), color = 0xbdb092)
            embed.set_footer(text = file.memover('memo', filename, ver))
            await ctx.send(embed = embed)
        else:
            await ctx.send("해당 버전이 없습니다. ")

    # @rev.command(name = "memohistory", help = "메모 리버전 목록을 엽니다. ")
    # async def imemo(self, ctx, filename, ver):
    #     if file.isrev("rev", filename, ver):
    #         embed = discord.Embed(title = filename, description = file.openrev("rev", filename, ver), color = 0xbdb092)
    #         embed.set_footer(text = file.memover('memo', filename, ver))
    #         await ctx.send(embed = embed)
    #     else:
    #         await ctx.send("해당 버전이 없습니다. ")

    @rev.command(name = "profile", help = "맨션한 유저의 유저 정보 리버전을 불러옵니다. ")
    async def pfrev(self, ctx, user, pfver = -1):
        userinfo = await commands.MemberConverter.convert(self=commands.MemberConverter, ctx=ctx, argument=user)
        await MemoUI.profile_embed(ctx, userinfo, pfver)

    @rev.command(name = "myprofile", help = "자신의 유저 정보 리버전을 불러옵니다. ")
    async def mypfrev(self, ctx, pfver = -1):
        userinfo = ctx.message.author
        await MemoUI.profile_embed(ctx, userinfo, pfver)
    
    @commands.group(name = "back", help = "메모 되돌리기 관련")
    async def backrev(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("명령어가 올바르지 않습니다. ")

    @backrev.command(name = "memo", help = "메모를 해당 버전으로 되돌립니다. ")
    async def memo3(self, ctx, filename, ver):
        if file.isrev("rev", filename, ver):
            file.editfile("memo", filename, file.openrev("rev", filename, ver))
            file.rev("rev", filename, file.openrev("rev", filename, ver))
            await ctx.send("되돌리기 완료!")
        else:
            await ctx.send("해당 버전이 없습니다. ")

    '''========== 여기까지 메모 기본 엔진, 아래부터 메모 틀 관련 =========='''

    uitest = app_commands.Group(name="memoui", description="인터페이스 실험용")

    @uitest.command(name = "menu", description = "메뉴창을 엽니다. ")
    async def selecttest(self, interaction:discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send(content="실행할 동작을 골라주세요. ", view=Select(), ephemeral=True)

    # @uitest.command(name = "editor", description = "메시지 수정 테스트")
    # async def modaltest(self, interaction:discord.Interaction):
    #     await interaction.response.send_modal(WriteModal())

    '''========== 여기까지 메모 틀, 아래부터 메모 슬래시 명령어 관련 =========='''

    memocom = app_commands.Group(name="memo", description="메모 관련")

    @memocom.command(name="edit", description="메모 편집")
    @app_commands.describe(title='제목')
    async def edits(self, interaction:discord.Interaction, title:str):
        await interaction.response.send_modal(WriteModal2(memo_title=title))

    @memocom.command(name="open", description="메모 열기")
    @app_commands.describe(title='제목')
    async def opens(self, interaction:discord.Interaction, title:str):
        await openfile(interaction, title)

    @memocom.command(name="append", description="메모 줄 추가")
    @app_commands.describe(title='제목')
    async def appends(self, interaction:discord.Interaction, title:str):
        await interaction.response.send_modal(AppendModal(memo_title=title))

    @memocom.command(name="search", description="메모 검색")
    @app_commands.describe(title='검색어')
    async def search2(self, interaction:discord.Interaction, title:str):
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
            resp  = f"```\n{title}에 대한 검색결과가 없습니다. "
        await interaction.response.send_message(resp)

async def setup(bot):
    await bot.add_cog(Memo(bot))
