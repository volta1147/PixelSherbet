import discord
from discord     import app_commands
from discord.ext import commands
from launchio.json import JSON
from lib.file import json_path

account_file = JSON(json_path.chifile('accounts.json'))

class PasswordModal(discord.ui.Modal, title = "가입"):
    pass_contx = discord.ui.TextInput(label="비밀번호", placeholder="비밀번호를 적어주세요. ", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        password = str(self.pass_contx)
        account_file.edit(interaction.user.id, 'password', value = password)
        await interaction.response.send_message("가입 완료!")

class Account(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    account = app_commands.Group(name="account", description="계정 연동")

    @account.command(name = "register", description = "가입")
    async def register(self, interaction:discord.Interaction):
        await interaction.response.send_modal(PasswordModal())

async def setup(bot):
    await bot.add_cog(Account(bot))