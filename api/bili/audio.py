from typing import Dict, Any
from .client import BiliClient

async def fetch_api(client: BiliClient, id: str) -> Dict[str, Any]:
    url = f"https://www.bilibili.com/audio/music-service-c/web/song/info?sid={id}"
    return await client.get(url, headers={"Host": "www.bilibili.com"})

async def fetch_am_api(client: BiliClient, id: str) -> Dict[str, Any]:
    url = f"https://www.bilibili.com/audio/music-service-c/web/menu/info?sid={id}"
    return await client.get(url, headers={"Host": "www.bilibili.com"})
