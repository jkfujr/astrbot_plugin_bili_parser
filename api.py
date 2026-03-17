import aiohttp
import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger("astrbot_plugin_bili_parser")

class BiliAPIClient:
    def __init__(self, user_agent: str):
        self.user_agent = user_agent

    async def _get(self, url: str, host: str) -> Dict[str, Any]:
        headers = {
            "User-Agent": self.user_agent,
            "Host": host
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except Exception as e:
            logger.error(f"BiliAPIClient Failed to fetch {url}: {e}")
            raise

    async def fetch_video(self, id_str: str) -> Dict[str, Any]:
        """获取视频信息"""
        av_match = re.match(r'av([0-9]+)', id_str, re.IGNORECASE)
        bv_match = re.match(r'bv([0-9a-zA-Z]+)', id_str, re.IGNORECASE)
        
        if av_match:
            url = f"https://api.bilibili.com/x/web-interface/view?aid={av_match.group(1)}"
        elif bv_match:
            url = f"https://api.bilibili.com/x/web-interface/view?bvid={bv_match.group(1)}"
        else:
            # 默认视为 BV 号
            url = f"https://api.bilibili.com/x/web-interface/view?bvid={id_str}"
            
        return await self._get(url, "api.bilibili.com")

    async def fetch_live(self, id_str: str) -> Dict[str, Any]:
        """获取直播间信息"""
        url = f"https://api.live.bilibili.com/room/v1/Room/get_info?room_id={id_str}"
        return await self._get(url, "api.live.bilibili.com")

    async def fetch_bangumi_ep_ss(self, id_str: str) -> Dict[str, Any]:
        """获取番剧 EP/SS 信息"""
        ep_match = re.match(r'ep([0-9]+)', id_str, re.IGNORECASE)
        ss_match = re.match(r'ss([0-9]+)', id_str, re.IGNORECASE)
        
        if ep_match:
            url = f"https://api.bilibili.com/pgc/view/web/season?ep_id={ep_match.group(1)}"
        elif ss_match:
            url = f"https://api.bilibili.com/pgc/view/web/season?season_id={ss_match.group(1)}"
        else:
            if id_str.isdigit():
                 url = f"https://api.bilibili.com/pgc/view/web/season?season_id={id_str}"
            else:
                 raise ValueError(f"Unknown bangumi type: {id_str}")

        ret = await self._get(url, "api.bilibili.com")
        if 'result' in ret:
            ret['data'] = ret['result']
        return ret

    async def fetch_bangumi_md(self, id_str: str) -> Dict[str, Any]:
        """获取番剧 MD 信息"""
        media_id = re.sub(r'^md', '', id_str, flags=re.IGNORECASE)
        md_url = f"https://api.bilibili.com/pgc/review/user?media_id={media_id}"
        
        md_info = await self._get(md_url, "api.bilibili.com")
        if not md_info.get('result'):
            raise ValueError("Fetch bangumi information via mdid failed!")
            
        season_id = md_info['result']['media']['season_id']
        url = f"https://api.bilibili.com/pgc/view/web/season?season_id={season_id}"
        
        ret = await self._get(url, "api.bilibili.com")
        if 'result' in ret:
            ret['data'] = ret['result']
        return ret

    async def fetch_article(self, id_str: str) -> Dict[str, Any]:
        """获取专栏信息"""
        url = f"https://api.bilibili.com/x/article/viewinfo?id={id_str}"
        return await self._get(url, "api.bilibili.com")

    async def fetch_opus(self, id_str: str) -> Dict[str, Any]:
        """获取动态信息"""
        url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/detail?id={id_str}"
        return await self._get(url, "api.bilibili.com")

    async def fetch_space(self, id_str: str) -> Dict[str, Any]:
        """获取空间信息"""
        url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?host_mid={id_str}"
        return await self._get(url, "api.bilibili.com")

    async def fetch_audio(self, id_str: str) -> Dict[str, Any]:
        """获取音频信息"""
        url = f"https://www.bilibili.com/audio/music-service-c/web/song/info?sid={id_str}"
        return await self._get(url, "www.bilibili.com")

    async def fetch_audio_menu(self, id_str: str) -> Dict[str, Any]:
        """获取歌单信息"""
        url = f"https://www.bilibili.com/audio/music-service-c/web/menu/info?sid={id_str}"
        return await self._get(url, "www.bilibili.com")

    async def get_short_redir_url(self, short_id: str) -> str:
        """获取短链接跳转真实地址"""
        url = f"https://b23.tv/{short_id}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, allow_redirects=True) as resp:
                    return str(resp.url)
        except Exception:
            return ""
