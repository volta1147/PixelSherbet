import discord
from launchio import lndir, ln
import lib.botsetup as botset
import lib.file as file

class PySelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label="열기",description="코드를 엽니다. ", emoji="📕"),
                discord.SelectOption(label="실행",description="코드를 실행합니다. ", emoji="▶️"),
                discord.SelectOption(label="수정",description="코드를 수정합니다. ", emoji="🖊️"),
                discord.SelectOption(label="바로 실행",description="코드를 작성하고 바로 실행합니다. ", emoji="⚡"),
                discord.SelectOption(label="입력",description="입력 목록을 작성합니다. ", emoji="⌨️"),
                discord.SelectOption(label="종료",description="나가", emoji="❌")]
        super().__init__(placeholder = "메뉴 선택하기.", options = options) # , min_values=1, max_values=3)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(content=f"{self.values}", ephemeral=True)

class Select(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(PySelect())

class PyModal:
    class PyWriteModal(discord.ui.Modal, title = "Python Run"):
        code_title = discord.ui.TextInput(label="제목", placeholder="제목을 적어주세요. ", style=discord.TextStyle.short)
        code_contx = discord.ui.TextInput(label="코드", placeholder="코드를 적어주세요. ", style=discord.TextStyle.long)

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.send_message(f"제목 : {self.code_title}\n"+"="*20+"\n{self.code_contx}")

    class PyRunModal(discord.ui.Modal, title = "Python Run"):
        code_title = discord.ui.TextInput(label="제목", placeholder="제목을 적어주세요. ", style=discord.TextStyle.short)

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.send_message(f"제목 : {self.code_title}")

    class PyInputModal(discord.ui.Modal, title = "Python Run"):
        code_contx = discord.ui.TextInput(label="코드", placeholder="입력 내용을 적어주세요. 엔터로 구분함", style=discord.TextStyle.long)

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.send_message(f"입력\n"+"="*20+"\n{self.code_contx}")