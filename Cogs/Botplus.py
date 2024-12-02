import discord
from discord import app_commands
from discord.ext import commands
from launchio import ln
import random
import asyncio
import subprocess

# 여기에 사용자 정의 함수/라이브러리 넣기

class ButtonFunction(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)

    @discord.ui.button(label='엄 출력하기', style=discord.ButtonStyle.blurple)
    async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("엄")

class Botplus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Restarting...")

    @commands.command(name = "print", help = "입력한 내용을 출력합니다 (원본 메시지 삭제)")
    async def printctx(self, ctx:commands.Context, *, abc):
        await ctx.message.delete() # ctx.channel.purge(limit=1)
        rep = await ctx.send(abc, reference = ctx.message.reference)
        printlog = ln("community", "print", "print.txt")
        printlog.write(f"content = {abc} \t author = {ctx.message.author} \t [link](<https://discord.com/channels/{rep.guild.id}/{rep.channel.id}/{rep.id}>) \n", mode='a')

    @commands.command(name = "reaction", help = "입력한 내용을 출력합니다 (원본 메시지 삭제)")
    async def reactionctx(self, ctx:commands.Context, *, abc):
        await ctx.message.delete() # ctx.channel.purge(limit=1)
        rep = await ctx.message.reference.resolved.add_reaction(abc)
        # printlog = ln("community", "print", "print.txt")
        # printlog.write(f"content = +{abc} \t author = {ctx.message.author} \t [link](<https://discord.com/channels/{rep.guild.id}/{rep.channel.id}/{rep.id}>) \n", mode='a')

    @commands.command(name = "🤔", help = "?")
    async def thinking(self, ctx:commands.Context):
        await ctx.send(f"{ctx.author.mention} 사랑해~😍")

    @commands.command(name = "random", help = "주어진 단어 중 하나를 선택합니다. ")
    async def randomword(self, ctx, *words):
        await ctx.send(random.choice(words))

    @commands.group(name = "python_legacy", help = "파이썬 실행과 관련된 함수들. ") # **파이썬 명령어를 실행하기 위해서는 봇 작동 기기에 파이썬이 설치되어있어야 합니다.**
    async def pyrun(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("명령어가 올바르지 않습니다. ")

    @pyrun.command(name = "input", help = "파이썬 프로그램의 입력값을 설정합니다. ")
    async def editinput(self, ctx, *pyargs):
        stdinstr = ""
        for i in pyargs:
            stdinstr = stdinstr + "{}\n".format(str(i))
        stdfile = open("pythoncode\\stdin.txt", "w")
        stdfile.write(stdinstr)
        stdfile.close()
        await ctx.send("입력값 : \n " + pyargs)

    @pyrun.command(name = "code", help = "파이썬 코드를 작성합니다. ")
    async def editpycode(self, ctx, *, pythoncode):
        if pythoncode.find("import") != -1:
            await ctx.send("시스템 관련 모듈은 막아두었습니다. ")
        else:
            head = "import math\nimport random\nimport time\nimport sys\nsys.stdin = open(\"pythoncode\\\\stdin.txt\", \"r\")\n"
            pyfile = open("pythoncode\\test.py", "w")
            pyfile.write(head + pythoncode)
            pyfile.close()
            await ctx.send("작성 완료. \n>>> 파이썬 서비스는 베타 버전입니다. \n**시스템을 망가트리는 코드 / 랜섬웨어 등 악성 코드를 유포하는 코드 등을 입력할 시 기능이 삭제될 수 있습니다. **")

    @pyrun.command(name = "run", help = "파이썬 코드를 실행합니다. ")
    async def runpycode(self, ctx):
        result = subprocess.getoutput("python3 pythoncode\\test.py")
        await ctx.send(result)

    @pyrun.command(name = "runcode", help = "파이썬 코드를 작성하고 실행합니다. ")
    async def editrunpycode(self, ctx, *, pythoncode):
        if pythoncode.find("import") != -1:
            await ctx.send("시스템 관련 모듈은 막아두었습니다. ")
        else:
            head = "import math\nimport random\nimport time\nimport sys\nsys.stdin = open(\"pythoncode\\\\stdin.txt\", \"r\")\n"
            pyfile = open("pythoncode\\test.py", "w")
            pyfile.write(head + pythoncode)
            pyfile.close()

            result = subprocess.getoutput("python3 pythoncode\\test.py")
            await ctx.send(result)

    # @commands.group(name = "list", help = "리스트 랜덤추첨 관련")
    # async def levellist(self, ctx):
    #     if ctx.invoked_subcommand is None:
    #         await ctx.send("명령어가 올바르지 않습니다. ")
    # 
    # @levellist.command(name = "create", help = "리스트를 만듭니다. ")
    # async def createlist(self, ctx, *, listname):
    #     exi = file.islist(listname)
    #     file.openfile("levellist", listname, True)
    #     if exi:
    #         await ctx.send("{} 리스트가 이미 존재합니다. ".format(listname))
    #     else:
    #         await ctx.send("{} 리스트가 생성되었습니다. ".format(listname))
    # 
    # @levellist.command(name = "append", help = "리스트에 항목을 추가합니다. ")
    # async def appendlist(self, ctx, listname, *, level):
    #     if file.islist(listname):
    #         file.appendfile("levellist", listname, str(len(file.listsplit("levellist", listname))+1) + ". " + level + "\n")
    #         await ctx.send("완료")
    #     else:
    #         await ctx.send("{} 리스트가 존재하지 않습니다. ".format(listname))
    # 
    # @levellist.command(name = "file", help = "리스트에 첨부파일을 저장합니다. ")
    # async def appendlist(self, ctx, *, listname):
    #     if file.islist(listname):
    #         await discord.Attachment.save(fp="levellist\\input.txt")
    #         await ctx.send("완료")
    #     else:
    #         await ctx.send("{} 리스트가 존재하지 않습니다. ".format(listname))

    @commands.hybrid_command(name = "um", help = "엄")
    async def bttest(self, ctx:commands.Context):
        testmsg = await ctx.send("어음", view=ButtonFunction())
        await asyncio.sleep(5)
        await testmsg.edit(view=None)

    @app_commands.command(name = "slashprint", description="입력한 내용을 출력합니다")
    @app_commands.describe(text='적을 내용')
    async def printctx2(self, interaction: discord.Interaction, text:str):
        await interaction.response.send_message(f"{text}")
    
async def setup(bot:commands.bot):
    await bot.add_cog(Botplus(bot))
