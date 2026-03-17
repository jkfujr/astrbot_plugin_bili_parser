from typing import Dict, Any
from .client import BiliClient

async def fetch_api(client: BiliClient, id: str) -> Dict[str, Any]:
    url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?host_mid={id}"
    return await client.get(url, headers={"Host": "api.bilibili.com"})
