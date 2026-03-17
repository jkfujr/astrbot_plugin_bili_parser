import re
import aiohttp
from typing import List, Dict, Any, Optional
from .bv_av_converter import normalize_video_id

class Link:
    def __init__(self, type_: str, id_: str):
        self.type = type_
        self.id = id_
        self.data: Dict[str, Any] = {}

    def __repr__(self):
        return f"Link(type={self.type}, id={self.id})"

    def __eq__(self, other):
        if isinstance(other, Link):
            return self.type == other.type and self.id == other.id
        return False

    def __hash__(self):
        return hash((self.type, self.id))

def deduplicate_links(links: List[Link]) -> List[Link]:
    seen = set()
    unique_links = []
    for link in links:
        # 对于视频类型，使用标准化id进行去重
        if link.type == "Video":
            # 尝试标准化视频 ID
            normalized_id = normalize_video_id(link.id)
            key = (link.type, normalized_id)
        else:
            # 其他类型使用原有去重逻辑
            key = (link.type, link.id)
            
        if key not in seen:
            seen.add(key)
            unique_links.append(link)
            
    return unique_links

async def get_redir_url(url: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, allow_redirects=True) as resp:
                return str(resp.url)
    except Exception:
        return ""

def link_parser(content: str, config: Dict[str, Any]) -> List[Link]:
    link_regex = []

    if config.get("b_video_enable", True):
        pattern1 = r'bilibili\.com\/video\/((?<![a-zA-Z0-9])[aA][vV][0-9]+)' if config.get("b_video_full_url", True) else r'((?<![a-zA-Z0-9])[aA][vV][0-9]+)'
        pattern2 = r'bilibili\.com\/video\/((?<![a-zA-Z0-9])[bB][vV][0-9a-zA-Z]+)' if config.get("b_video_full_url", True) else r'((?<![a-zA-Z0-9])[bB][vV][0-9a-zA-Z]+)'
        link_regex.append({"pattern": re.compile(pattern1, re.I), "type": "Video"})
        link_regex.append({"pattern": re.compile(pattern2, re.I), "type": "Video"})

    if config.get("b_live_enable", True):
        link_regex.append({"pattern": re.compile(r'live\.bilibili\.com(?:\/h5)?\/(\d+)', re.I), "type": "Live"})

    if config.get("b_bangumi_enable", True):
        p1 = r'bilibili\.com\/bangumi\/play\/(ep\d+)' if config.get("b_bangumi_full_url", True) else r'(ep\d+)'
        p2 = r'bilibili\.com\/bangumi\/play\/(ss\d+)' if config.get("b_bangumi_full_url", True) else r'(ss\d+)'
        p3 = r'bilibili\.com\/bangumi\/media\/(md\d+)' if config.get("b_bangumi_full_url", True) else r'(md\d+)'
        link_regex.append({"pattern": re.compile(p1, re.I), "type": "BangumiEp"})
        link_regex.append({"pattern": re.compile(p2, re.I), "type": "BangumiSs"})
        link_regex.append({"pattern": re.compile(p3, re.I), "type": "BangumiMd"})

    if config.get("b_space_enable", True):
        link_regex.append({"pattern": re.compile(r'space\.bilibili\.com\/(\d+)', re.I), "type": "Space"})
        link_regex.append({"pattern": re.compile(r'bilibili\.com\/space\/(\d+)', re.I), "type": "Space"})

    if config.get("b_opus_enable", True):
        link_regex.append({"pattern": re.compile(r'bilibili\.com\/opus\/(\d+)', re.I), "type": "Opus"})

    if config.get("b_article_enable", True):
        pattern = r'bilibili\.com\/read\/cv(\d+)' if config.get("b_article_full_url", True) else r'cv(\d+)'
        link_regex.append({"pattern": re.compile(pattern, re.I), "type": "Article"})
        link_regex.append({"pattern": re.compile(r'bilibili\.com\/read\/mobile(?:\?id=|\/)(\d+)', re.I), "type": "Article"})

    if config.get("b_audio_enable", True):
        pattern = r'bilibili\.com\/audio\/au(\d+)' if config.get("b_audio_full_url", True) else r'au(\d+)'
        link_regex.append({"pattern": re.compile(pattern, re.I), "type": "Audio"})
        
        pattern = r'bilibili\.com\/audio\/am(\d+)' if config.get("b_audio_full_url", True) else r'am(\d+)'
        link_regex.append({"pattern": re.compile(pattern, re.I), "type": "AudioMenu"})

    if config.get("b_short_enable", True):
        link_regex.append({"pattern": re.compile(r'b23\.tv(?:\\)?\/([0-9a-zA-Z]+)', re.I), "type": "Short"})
        link_regex.append({"pattern": re.compile(r'bili(?:22|23|33)\.cn\/([0-9a-zA-Z]+)', re.I), "type": "Short"})

    results = []
    sanitized_content = re.sub(r'<[^>]+>', '', content)
    
    for item in link_regex:
        for match in item["pattern"].finditer(sanitized_content):
            results.append(Link(item["type"], match.group(1)))

    return deduplicate_links(results)

async def short_link_parser(links: List[Link], config: Dict[str, Any]) -> List[Link]:
    result = []
    for link in links:
        if link.type == "Short":
            short_url = f"https://b23.tv/{link.id}"
            redir_url = await get_redir_url(short_url)
            if redir_url:
                resolved_links = link_parser(redir_url, config)
                if resolved_links:
                    result.extend(resolved_links)
                    continue
        result.append(link)
    
    return deduplicate_links(result)
