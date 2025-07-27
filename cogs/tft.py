import discord
from discord.ext import commands
from discord import app_commands
from utils.riot_api import RiotAPI
# Import từ điển từ constants.py
from utils.constants import TFT_QUEUE_IDS

class TFTCog(commands.Cog):
    def __init__(self, bot: commands.Bot, riot_api: RiotAPI):
        self.bot = bot
        self.riot_api = riot_api

    @app_commands.command(name="tft_profile", description="Kiểm tra lịch sử đấu 10 trận gần nhất của người chơi TFT")
    @app_commands.describe(
        riot_id="Tên Riot ID của người chơi", 
        tagline="Tagline (không có #)"
    )
    async def tft_profile(self, interaction: discord.Interaction, riot_id: str, tagline: str):
        await interaction.response.defer()

        # Luôn mặc định tìm kiếm ở khu vực 'ap' cho người chơi Việt Nam
        puuid = await self.riot_api.get_puuid(riot_id, tagline, 'ap')
        if not puuid:
            await interaction.followup.send(f"Không tìm thấy người chơi: `{riot_id}#{tagline}`. Hãy chắc chắn bạn đã nhập đúng.")
            return

        matches = await self.riot_api.get_tft_matches(puuid, 10)
        if not matches:
            await interaction.followup.send(f"Không tìm thấy lịch sử đấu gần đây cho `{riot_id}#{tagline}`.")
            return

        embed = discord.Embed(
            title=f"Thông Tin TFT - {riot_id}#{tagline}",
            description="Lịch sử 10 trận đấu gần nhất:",
            color=discord.Color.purple()
        )

        for match in matches:
            info = match['info']
            player_info = next((p for p in info['participants'] if p['puuid'] == puuid), None)
            if not player_info:
                continue

            # Tra cứu tên chế độ chơi từ constants.py, chuyển queueId thành chuỗi để khớp key
            queue_name = TFT_QUEUE_IDS.get(str(info['queueId']), f"Chế độ lạ ({info['queueId']})")
            placement = player_info.get('placement', 'N/A')
            
            # Giữ tên Tộc/Hệ gốc từ API để đảm bảo ổn định
            traits = [trait['name'] for trait in player_info.get('traits', []) if trait.get('tier_current', 0) > 0]
            traits_str = ', '.join(traits) if traits else "Không có"

            embed.add_field(
                name=f"🎲 {queue_name} - Hạng #{placement}",
                value=f"**Tộc/Hệ:** {traits_str}",
                inline=False
            )
        
        embed.set_footer(text="Dữ liệu 10 trận gần nhất.")
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    riot_api_instance = bot.riot_api
    await bot.add_cog(TFTCog(bot, riot_api_instance))