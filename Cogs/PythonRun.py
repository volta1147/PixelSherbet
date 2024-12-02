import discord
from discord import app_commands
from discord.ext import commands
import sys
import asyncio
import subprocess
import lib.botsetup as botset
import lib.file as file
import lib.PythonUI as PythonUI

class PySelect(PythonUI.PySelect):
    def __init__(self):
        super().__init__()

    async def callback(self, interaction: discord.Interaction):
        # await interaction.response.send_message(content=f"{self.values}", ephemeral=True)
        # if self.values[0] == "열기":
        #     await interaction.response.send_modal(OpenModal())
        if self.values[0] == "수정":
            await interaction.response.send_modal(PyWriteModal())
        if self.values[0] == "종료":
            await interaction.delete_original_response()

class Select(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(PySelect())

class PyWriteModal(PythonUI.PyModal.PyWriteModal):
    async def on_submit(self, interaction: discord.Interaction):
        filename = str(self.code_title)
        code     = str(self.code_contx)
        file.editfile("python", filename, code)
        file.rev("pyrev", filename, code)
        embed = discord.Embed(title = filename, description = file.openfile("python", filename), color = 0xbdb092)
        embed.set_footer(text = f"{file.memover('python', filename, file.getver('pyrev', filename))}, Python ver {sys.version.split()[0]}")
        return await interaction.response.send_message(embed=embed, ephemeral=True)

class PythonRun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    pyrun = app_commands.Group(name="python", description="파이썬 실험용 (미완)")

    @pyrun.command(name = "menu", description = "메뉴창 테스트 (미완)")
    async def pyselect(self, interaction:discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send(content="실행할 동작을 골라주세요. 어차피 실행 못함", view=Select(), ephemeral=True)
        # await interaction.response.send_message(content="실행할 동작을 골라주세요. ", view=Select(), ephemeral=True)

async def setup(bot:commands.bot):
    await bot.add_cog(PythonRun(bot))