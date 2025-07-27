# utils/riot_api.py (Phiên bản nâng cấp với tự động fallback region và xử lý dấu cách)

import aiohttp
import urllib.parse

def get_account_region(region: str):
    if region in ['na', 'br', 'lan', 'las']:
        return 'americas'
    if region in ['ap', 'kr', 'sea']:
        return 'asia'
    if region in ['eune', 'euw', 'tr', 'ru']:
        return 'europe'
    return 'asia'

class RiotAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"X-Riot-Token": self.api_key}
        self.session = aiohttp.ClientSession()

    async def close(self):
        await self.session.close()

    async def _get(self, url: str):
        async with self.session.get(url, headers=self.headers) as response:
            if response.status == 200:
                return await response.json()
            print(f"Lỗi API: URL {url} trả về mã trạng thái {response.status}")
            return None

    async def get_puuid(self, riot_id: str, tagline: str, region: str = 'ap'):
        account_region = get_account_region(region)
        # Mã hóa Riot ID để xử lý các ký tự đặc biệt như dấu cách
        encoded_riot_id = urllib.parse.quote(riot_id)
        url = f"https://{account_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encoded_riot_id}/{tagline}"
        data = await self._get(url)
        return data.get('puuid') if data else None

    async def get_valorant_matches(self, puuid: str, region: str = 'ap', count: int = 5):
        regions_to_try = [region]
        # Nếu khu vực chính là 'ap', thêm 'sea' làm phương án dự phòng
        if region == 'ap' and 'sea' not in regions_to_try:
            regions_to_try.append('sea')
        # Nếu khu vực chính là 'sea', thêm 'ap' làm phương án dự phòng
        elif region == 'sea' and 'ap' not in regions_to_try:
            regions_to_try.append('ap')

        match_list_response = None
        final_region = None

        # Lặp qua các khu vực để thử
        for r in regions_to_try:
            print(f"Đang thử tìm trận đấu Valorant ở khu vực: {r}")
            url = f"https://{r}.api.riotgames.com/val/match/v1/matchlists/by-puuid/{puuid}?filter=competitive"
            response = await self._get(url)
            # Nếu tìm thấy lịch sử đấu, dùng nó và dừng tìm kiếm
            if response and response.get('history'):
                match_list_response = response
                final_region = r
                print(f"Đã tìm thấy trận đấu ở khu vực: {final_region}")
                break
        
        if not match_list_response:
            return []
        
        match_ids = [match['matchId'] for match in match_list_response['history']]
        
        matches_data = []
        for match_id in match_ids[:count]:
            match_details_url = f"https://{final_region}.api.riotgames.com/val/match/v1/matches/{match_id}"
            details = await self._get(match_details_url)
            if details:
                matches_data.append(details)
                
        return matches_data

    async def get_lol_matches(self, puuid: str, count: int = 10):
        url = f"https://sea.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
        match_ids = await self._get(url)
        if not match_ids:
            return []
        matches_data = []
        for match_id in match_ids:
            match_details_url = f"https://sea.api.riotgames.com/lol/match/v5/matches/{match_id}"
            details = await self._get(match_details_url)
            if details:
                matches_data.append(details)
        return matches_data
    
    async def get_tft_matches(self, puuid: str, count: int = 10):
        url = f"https://sea.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?start=0&count={count}"
        match_ids = await self._get(url)
        if not match_ids:
            return []
        matches_data = []
        for match_id in match_ids:
            match_details_url = f"https://sea.api.riotgames.com/tft/match/v1/matches/{match_id}"
            details = await self._get(match_details_url)
            if details:
                matches_data.append(details)
        return matches_data