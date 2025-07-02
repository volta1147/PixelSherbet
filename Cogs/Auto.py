import discord
import lib.file as file
import time
import lib.MemoUI as MemoUI
from discord import app_commands
from discord.ext import commands
from discord.utils import get
from launchio.json import JSON
from lib.file import json_path

# 여기에 사용자 정의 라이브러리 넣기

auto_file = JSON(json_path.chifile('auto_message.json'))
category_file = JSON(json_path.chifile('categories.json'))
channel_file = JSON(json_path.chifile('channels.json'))
channel2_file = JSON(json_path.chifile('channels2.json'))
role_file = JSON(json_path.chifile('role.json'))

class WriteModal(MemoUI.WriteModal):
    def __init__(self, memo_title):
        super().__init__(memo_title = memo_title)
    
    async def on_submit(self, interaction: discord.Interaction):
        filename = str(self.memo_title)
        memo     = str(self.memo_contx)
        file.editfile("rules", filename, memo)
        embed = discord.Embed(title = 'Rules', description = file.openfile("rules", filename), color = 0x5662F6)
        embed.set_footer(text = f'update : {time.asctime(time.localtime())}')
        rule_channel = get(interaction.guild.channels, id=channel2_file()[str(interaction.guild.id)]['rules'])
        rule_message = rule_channel.get_partial_message(auto_file()[str(interaction.guild.id)]['rule_main'])
        await rule_message.edit(embed=embed)
        return await interaction.response.send_message('성공!', ephemeral=True)

class Auto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    settings = app_commands.Group(name="settings", description="관리 시스템")

    @settings.command(name = "subchannels", description = "서브채널 카테고리 지정")
    async def set_forum(self, interaction:discord.Interaction):
        if not (interaction.guild and interaction.user.guild_permissions.administrator):
            await interaction.response.send_message("권한이 없어요. ")
        else:
            category = interaction.channel.category_id
            if category == None:
                await interaction.response.send_message("카테고리가 없습니다.")
            else:
                category_file.append(str(interaction.guild.id), 'subchannels', value=category)
                await interaction.response.send_message("성공")

    @settings.command(name = "rules", description = "규칙 채널 지정")
    async def set_rules(self, interaction:discord.Interaction):
        if not (interaction.guild and interaction.user.guild_permissions.administrator):
            await interaction.response.send_message("권한이 없어요. ")
        else:
            channel = interaction.channel.id
            channel2_file.append(str(interaction.guild.id), 'rules', value=channel)
            file.editfile('rules', f'{interaction.guild.id}', f'**{interaction.guild.name}**에 오신 것을 환영합니다. ')
            memo_state, embed = MemoUI.memo_embed(str(interaction.guild.id), 'rules',  title='Rules')
            embed.set_footer(text = 'Update : None')
            await interaction.response.send_message("성공", ephemeral=True)
            rule_message = await interaction.channel.send(embed=embed)
            auto_file.edit(interaction.guild.id, 'rule_main', value=rule_message.id)

    @settings.command(name = "role_tag", description = "역할")
    @app_commands.describe(name="이름", role_id="id")
    async def set_role(self, interaction:discord.Interaction, name:str, role_id:str):
        if not (interaction.guild and interaction.user.guild_permissions.administrator):
            await interaction.response.send_message("권한이 없어요. ")
        else:
            if role_id.isdigit():
                role_file.append(name, str(interaction.guild.id), value=int(role_id))
                await interaction.response.send_message("성공")
            else:
                await interaction.response.send_message("id는 정수여야만 합니다. ")
    
    forums = app_commands.Group(name="subchannels", description="서브채널")
    
    @forums.command(name = "create", description="만들기")
    @app_commands.describe(title="제목", topic="주제")
    async def create_forum(self, interaction:discord.Interaction, title:str, topic:str|None = None):
        if title not in channel_file()[str(interaction.guild.id)]['sub'].keys():
            categoryId = category_file()[str(interaction.guild.id)]['subchannels']
            category = get(interaction.guild.categories, id=categoryId)
            newChannel = await interaction.guild.create_text_channel(title, topic=topic, category=category)
            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages = True
            overwrite.read_messages = True
            newRole = await interaction.guild.create_role(name=title)
            role_file.edit(title, str(interaction.guild.id), value=newRole.id)
            channel_file.edit('sub', str(interaction.guild.id), title, value=topic)
            await newChannel.set_permissions(newRole, overwrite=overwrite)
            embed = discord.Embed(title=title, description=f"`{title}` 채널에 오신 것을 환영합니다. "+(f"\n{topic}" if topic != None else ""))
            await newChannel.send(f"`{title}` 채널에 오신 것을 환영합니다.", embed=embed)
            await interaction.response.send_message(f"`{title}` 생성 완료. ")
        else:
            await interaction.response.send_message(f"`{title}` 채널은 이미 존재합니다. ")

    @forums.command(name = "join", description="채널 참가")
    @app_commands.describe(title="제목")
    async def join_channel(self, interaction:discord.Interaction, title:str):
        if title in channel_file()['sub'][str(interaction.guild.id)].keys():
            channelRole = interaction.guild.get_role(role_file()[str(interaction.guild.id)][title])
            await interaction.user.add_roles(channelRole)
            await interaction.response.send_message(f"`{title}` 참가 완료")
        else:
            await interaction.response.send_message(f"`{title}` 채널은 존재하지 않습니다. ")

    @forums.command(name = "leave", description="채널 탈퇴")
    @app_commands.describe(title="제목")
    async def leave_channel(self, interaction:discord.Interaction, title:str):
        if title in channel_file()['sub'][str(interaction.guild.id)].keys():
            channelRole = interaction.guild.get_role(role_file()[str(interaction.guild.id)][title])
            if channelRole in interaction.user.roles:
                await interaction.user.remove_roles(channelRole)
                await interaction.response.send_message(f"`{title}` 탈퇴 완료")
            else:
                await interaction.response.send_message(f"`{title}`에 참가하지 않았습니다. ")
        else:
            await interaction.response.send_message(f"`{title}` 채널은 존재하지 않습니다. ")

    @forums.command(name = "list", description="채널 목록")
    async def list_channel(self, interaction:discord.Interaction):
        await interaction.response.send_message("## 서브 채널 목록\n```"+"\n".join([f"{i[0]} : {i[1]}" for i in channel_file()['sub'][str(interaction.guild.id)].items()])+"```")

    rules = app_commands.Group(name="rules", description="규칙 채널")

    @rules.command(name="edit", description="메모 편집")
    async def edits(self, interaction:discord.Interaction):
        await interaction.response.send_modal(WriteModal(interaction.guild_id))

async def setup(bot):
    await bot.add_cog(Auto(bot))