import discord
from discord.ext import commands
from discord import app_commands
from utils.riot_api import RiotAPI
# Import từ điển từ constants.py
from utils.constants import LOL_QUEUE_IDS

class LeagueCog(commands.Cog):
    def __init__(self, bot: commands.Bot, riot_api: RiotAPI):
        self.bot = bot
        self.riot_api = riot_api

    @app_commands.command(name="lol_profile", description="Kiểm tra lịch sử đấu 10 trận gần nhất của người chơi LOL")
    @app_commands.describe(
        riot_id="Tên Riot ID của người chơi", 
        tagline="Tagline (không có #)"
    )
    async def lol_profile(self, interaction: discord.Interaction, riot_id: str, tagline: str):
        await interaction.response.defer()

        # Luôn mặc định tìm kiếm ở khu vực 'ap' cho người chơi Việt Nam
        puuid = await self.riot_api.get_puuid(riot_id, tagline, 'ap')
        if not puuid:
            await interaction.followup.send(f"Không tìm thấy người chơi: `{riot_id}#{tagline}`. Hãy chắc chắn bạn đã nhập đúng.")
            return

        matches = await self.riot_api.get_lol_matches(puuid, 10)
        if not matches:
            await interaction.followup.send(f"Không tìm thấy lịch sử đấu gần đây cho `{riot_id}#{tagline}`.")
            return

        embed = discord.Embed(
            title=f"Thông Tin LOL - {riot_id}#{tagline}",
            description="Lịch sử 10 trận đấu gần nhất:",
            color=discord.Color.blue()
        )

        for match in matches:
            info = match['info']
            player_info = next((p for p in info['participants'] if p['puuid'] == puuid), None)
            if not player_info:
                continue

            # Tra cứu tên chế độ chơi từ constants.py, chuyển queueId thành chuỗi để khớp key
            queue_name = LOL_QUEUE_IDS.get(str(info['queueId']), f"Chế độ lạ ({info['queueId']})")
            result = "Thắng" if player_info['win'] else "Thua"
            kda = f"{player_info['kills']}/{player_info['deaths']}/{player_info['assists']}"

            embed.add_field(
                name=f"🎮 {queue_name} - {result}",
                value=f"**Tướng:** {player_info['championName']} | **KDA:** {kda}",
                inline=False
            )
        
        embed.set_footer(text="Dữ liệu 10 trận gần nhất.")
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    riot_api_instance = bot.riot_api
    await bot.add_cog(LeagueCog(bot, riot_api_instance))