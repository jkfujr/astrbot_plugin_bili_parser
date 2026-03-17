import aiohttp
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("astrbot_plugin_bili_parser")

class BiliClient:
    def __init__(self, user_agent: str):
        self.user_agent = user_agent

    async def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        if headers is None:
            headers = {}
        headers["User-Agent"] = self.user_agent
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise
