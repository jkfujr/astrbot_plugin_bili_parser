from typing import Dict, Any
from .client import BiliClient

def get_status_text(status_code: int) -> str:
    status_map = {
        0: "未开播",
        1: "直播中",
        2: "轮播中"
    }
    return status_map.get(status_code, "未知状态")

async def fetch_api(client: BiliClient, id: str) -> Dict[str, Any]:
    url = f"https://api.live.bilibili.com/room/v1/Room/get_info?room_id={id}"
    return await client.get(url, headers={"Host": "api.live.bilibili.com"})
