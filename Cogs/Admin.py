import discord
from discord     import app_commands
from discord.ext import commands
from datetime    import timedelta

# 여기에 사용자 정의 라이브러리 넣기

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(help = "관리자 전용 명령어")
    async def admin(self, ctx):
        if not (ctx.guild and ctx.message.author.guild_permissions.administrator):
            await ctx.send("권한이 어ㅄ습니다. ")
        else:
            if ctx.invoked_subcommand is None:
                await ctx.send("사실 관리기능 아직 안넣음. ") # ||~~당신 관리자 맞습니까?~~||

    admin2 = app_commands.Group(name="admin", description="관리 시스템")

    @admin2.command(name = "timeout", description = "너 숙청")
    @app_commands.describe(user='타임아웃 당할새끼', reason='이유', duration='적용 기간')
    async def timeout2(self, interaction:discord.Interaction, user:discord.Member, reason:str='없음', duration:int=60):
        role1 = [i.position for i in interaction.user.roles][-1]
        role2 = [i.position for i in user.roles][-1]
        if not (interaction.guild and interaction.user.guild_permissions.moderate_members):
            await interaction.response.send_message("권한이 어ㅄ습니다. ")
        elif role1 < role2:
            await interaction.response.send_message("이 반동분자새끼! 짤라요 ")
        else:
            await user.timeout(timedelta(seconds=duration), reason=reason)
            await interaction.response.send_message(f"{user.name} 님이 {duration}초 타임아웃되었습니다.\n이유 : {reason}")

    # @admin.command(name = "clear", help = "메시지를 삭제합니다. ")
    # async def clearmessage(self, ctx, num = -4451):
    #     if num > 0:
    #         await ctx.channel.purge(limit=num)
    #     else:
    #         await ctx.send("전 그런 거 못하니까 님이 {}개 지워보세요".format(num))
    
    # @admin.command(name = "shutdown", help = "봇 종료. ")
    # async def byebye(self, ctx):
    #     await ctx.send("ㅂㅂ")
    #     quit()

    @admin.command(name = "KillYourSelf", help = "자폭")
    async def FuckDev(self, ctx:commands.Context, times, reason):
        await ctx.author.timeout(timedelta(seconds=float(times)), reason=reason)

    @commands.command(name = "istimedout", help = "공개처형")
    async def AverageNorthKorea9K1(self, ctx:commands.Context, user):
        userinfo = await commands.MemberConverter().convert(ctx, user)
        if userinfo.is_timed_out():
            await ctx.send(f"{user} 삼가 고인의 명복을 빕니다.")
        else:
            await ctx.send(f"{user} 잘만 살아 있습니다.")

async def setup(bot):
    await bot.add_cog(Admin(bot))