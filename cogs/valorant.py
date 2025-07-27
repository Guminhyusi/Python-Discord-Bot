# cogs/valorant.py (Phiên bản đơn giản hóa cho người dùng Việt Nam)

import discord
from discord.ext import commands
from discord import app_commands
from utils.riot_api import RiotAPI

class ValorantCog(commands.Cog):
    def __init__(self, bot: commands.Bot, riot_api: RiotAPI):
        self.bot = bot
        self.riot_api = riot_api

    # Lệnh đã được đơn giản hóa, không còn chọn khu vực
    @app_commands.command(name="valorant_profile", description="Kiểm tra thông tin người chơi Valorant (khu vực VN)")
    @app_commands.describe(
        riot_id="Tên Riot ID của bạn", 
        tagline="Tagline của bạn (không có #)"
    )
    async def valorant_profile(self, interaction: discord.Interaction, riot_id: str, tagline: str):
        await interaction.response.defer()
        
        # Luôn sử dụng khu vực 'ap' cho người chơi Việt Nam
        vietnam_region = "ap"
        
        puuid = await self.riot_api.get_puuid(riot_id, tagline, vietnam_region)
        if not puuid:
            await interaction.followup.send(f"Không tìm thấy người chơi: `{riot_id}#{tagline}`. Hãy chắc chắn bạn đã nhập đúng.")
            return

        matches = await self.riot_api.get_valorant_matches(puuid, vietnam_region, 5)
        if not matches:
            await interaction.followup.send(f"Không tìm thấy lịch sử đấu xếp hạng nào gần đây cho `{riot_id}#{tagline}`.")
            return

        # Đoạn code tạo embed giữ nguyên như cũ
        player_info_latest_match = next((p for p in matches[0]['players'] if p['puuid'] == puuid), None)
        current_rank = player_info_latest_match['currenttierpatched'] if player_info_latest_match else "Chưa xác định"

        embed = discord.Embed(
            title=f"Thông Tin Valorant - {riot_id}#{tagline}",
            description=f"**Rank Hiện Tại:** {current_rank}",
            color=discord.Color.red()
        )

        for match in matches:
            player_info = next((p for p in match['players'] if p['puuid'] == puuid), None)
            if not player_info:
                continue

            team_result = "Thắng" if player_info.get('teamId') == 'Blue' and match['teams'][0].get('won') or \
                                    player_info.get('teamId') == 'Red' and match['teams'][1].get('won') else "Thua"
            
            map_name = match['matchInfo']['mapId'].split('/')[-1]
            score = f"{match['teams'][0]['roundsWon']} - {match['teams'][1]['roundsWon']}"
            stats = player_info.get('stats', {})
            kda = f"{stats.get('kills', 0)}/{stats.get('deaths', 0)}/{stats.get('assists', 0)}"
            acs = round(stats.get('score', 0) / match['matchInfo'].get('roundsPlayed', 1))

            embed.add_field(
                name=f"🗺️ {map_name} - {team_result} ({score})",
                value=f"**Agent:** {player_info.get('characterId', 'Unknown')} | **KDA:** {kda} | **ACS:** {acs}",
                inline=False
            )
        
        embed.set_footer(text="Dữ liệu 5 trận xếp hạng gần nhất.")
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    riot_api_instance = bot.riot_api
    await bot.add_cog(ValorantCog(bot, riot_api_instance))