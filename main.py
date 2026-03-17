from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

import jinja2
from typing import Dict, Any

from .link_parser import link_parser, short_link_parser
from .api.bili.client import BiliClient
from .api.bili import video, live, bangumi, article, opus, space, audio

@register("astrbot_plugin_bili_parser", "BiliParser", "Bilibili Link Parser Plugin", "1.0.0", "https://github.com/Soulter/astrbot-plugin-bili-parser")
class BiliParser(Star):
    def __init__(self, context: Context, config: Dict[str, Any]):
        super().__init__(context)
        self.config = config
        self.client = BiliClient(config.get("user_agent", "Mozilla/5.0"))
        
        # 初始化 Jinja2 环境
        self.env = jinja2.Environment()
        self.env.filters['format_number'] = self.format_number
        self.env.filters['format_live_status'] = self.format_live_status
        
        # API 映射
        self.api_map = {
            "Video": video.fetch_api,
            "Live": live.fetch_api,
            "BangumiEp": bangumi.fetch_web_api,
            "BangumiSs": bangumi.fetch_web_api,
            "BangumiMd": bangumi.fetch_mdid_api,
            "Article": article.fetch_api,
            "Opus": opus.fetch_api,
            "Space": space.fetch_api,
            "Audio": audio.fetch_api,
            "AudioMenu": audio.fetch_am_api,
        }

    def format_number(self, value):
        if not isinstance(value, (int, float)):
            return value
        if value >= 100000000:
             return f"{value/100000000:.1f}亿"
        if value >= 10000:
            return f"{value/10000:.1f}万"
        return str(value)

    def format_live_status(self, value):
        return live.get_status_text(value)

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent):
        message_str = event.message_str
        if not message_str:
            return

        links = link_parser(message_str, self.config)
        if not links:
            return
            
        # 解析限制
        limit = self.config.get("parse_limit", 3)
        if len(links) > limit:
            links = links[:limit]
            
        # 解析短链接
        if self.config.get("b_short_enable", True):
            links = await short_link_parser(links, self.config)
            
        results = []
        for link in links:
            fetch_func = self.api_map.get(link.type)
            if not fetch_func:
                continue
                
            try:
                # 获取数据
                data = await fetch_func(self.client, link.id)
                if not data or data.get('code') != 0:
                    logger.warning(f"Failed to fetch {link.type} {link.id}: {data}")
                    continue
                
                # 渲染模板
                template_key_map = {
                    "Video": "b_video_ret_preset",
                    "Live": "b_live_ret_preset",
                    "BangumiEp": "b_episode_ret_preset",
                    "BangumiSs": "b_bangumi_ret_preset",
                    "BangumiMd": "b_bangumi_ret_preset",
                    "Article": "b_article_ret_preset",
                    "Opus": "b_opus_ret_preset",
                    "Space": "b_space_ret_preset",
                    "Audio": "b_audio_ret_preset",
                    "AudioMenu": "b_audio_menu_ret_preset",
                }
                
                template_key = template_key_map.get(link.type)
                if not template_key:
                    continue
                    
                template_str = self.config.get(template_key)
                if not template_str:
                    continue

                # 准备上下文
                context = data.get('data', {})
                if 'result' in data and not context: 
                     context = data['result']
                
                # 辅助函数
                def get_current_episode(key):
                    if link.type == 'BangumiEp':
                        try:
                            ep_id_str = re.sub(r'^ep', '', link.id, flags=re.IGNORECASE)
                            ep_id = int(ep_id_str)
                            episodes = context.get('episodes', [])
                            for ep in episodes:
                                if ep.get('ep_id') == ep_id:
                                    return ep.get(key)
                        except Exception:
                            pass
                    return ""

                def get_article_id():
                    return re.sub(r'^cv', '', link.id, flags=re.IGNORECASE)

                rendered = self.env.from_string(template_str).render(
                    **context,
                    get_current_episode=get_current_episode,
                    get_article_id=get_article_id
                )
                results.append(rendered)
                
            except Exception as e:
                logger.error(f"Error processing {link.type} {link.id}: {e}")
                
        if results:
            delimiter = self.config.get("custom_delimiter", "\n------\n")
            reply = delimiter.join(results)
            yield event.plain_result(reply)
