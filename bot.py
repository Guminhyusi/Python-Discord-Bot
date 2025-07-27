# bot.py (phiên bản đơn giản, dùng constants.py)

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))
RIOT_API_KEY = os.getenv('RIOT_API_KEY')

from utils.riot_api import RiotAPI

class OptimalBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())
        self.riot_api: RiotAPI = None

    async def setup_hook(self):
        self.riot_api = RiotAPI(api_key=RIOT_API_KEY)
        print("Đã tạo session RiotAPI thành công.")

        # Tải các Cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f"Đã tải cog: {filename}")
        
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print(f"Đã đồng bộ lệnh cho server ID: {GUILD_ID}")
    
    async def on_ready(self):
        print(f'Bot đã đăng nhập với tên {self.user}')

    async def close(self):
        if self.riot_api:
            await self.riot_api.close()
        await super().close()

bot = OptimalBot()

async def main():
    async with bot:
        await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    if not DISCORD_TOKEN or not RIOT_API_KEY:
        print("LỖI: Vui lòng thiết lập DISCORD_TOKEN và RIOT_API_KEY trong file .env")
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("Bot đang tắt...")