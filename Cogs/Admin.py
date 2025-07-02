import discord
from discord     import app_commands
from discord.ext import commands
from datetime    import timedelta

# 여기에 사용자 정의 라이브러리 넣기

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    admin2 = app_commands.Group(name="admin", description="관리 시스템")

    @admin2.command(name = "timeout", description = "타임아웃")
    @app_commands.describe(user='타임아웃 당할 사용자', reason='이유', duration='적용 기간(초)')
    async def timeout2(self, interaction:discord.Interaction, user:discord.Member, reason:str='없음', duration:int=60):
        role1 = [i.position for i in interaction.user.roles][-1]
        role2 = [i.position for i in user.roles][-1]
        if not (interaction.guild and interaction.user.guild_permissions.moderate_members):
            await interaction.response.send_message("권한이 없습니다. ")
        elif role1 < role2:
            await interaction.response.send_message("권한이 없습니다. ")
        else:
            await user.timeout(timedelta(seconds=duration), reason=reason)
            await interaction.response.send_message(f"`{user.name}` 님이 {duration}초 타임아웃되었습니다.\n이유 : {reason}")

    @admin2.command(name = 'add_role', description = '멤버에게 역할을 부여합니다. ')
    @app_commands.describe(user='사용자', role='역할 ID', reason='설명')
    async def add_role(self, interaction:discord.Interaction, user:discord.Member, role:str, reason:str=''):
        role_ = interaction.guild.get_role(int(role))
        if user in role_.members:
            await interaction.response.send_message("이미 추가되어 있습니다. ")
        else:
            reason_ = reason if reason != '' else None
            await user.add_roles(role_, reason=reason_)
            await interaction.response.send_message("완료! ")

    @admin2.command(name = 'remove_role', description = '멤버에게 역할을 제거합니다. ')
    @app_commands.describe(user='사용자', role='역할 ID', reason='설명')
    async def del_role(self, interaction:discord.Interaction, user:discord.Member, role:str, reason:str=''):
        role_ = interaction.guild.get_role(int(role))
        if user not in role_.members:
            await interaction.response.send_message("역할이 부여되지 않았습니다. ")
        else:
            reason_ = reason if reason != '' else None
            await user.add_roles(role_, reason=reason_)
            await interaction.response.send_message("완료! ")

async def setup(bot):
    await bot.add_cog(Admin(bot))