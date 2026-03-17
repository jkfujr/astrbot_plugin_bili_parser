import re
from typing import Dict, Any
from .client import BiliClient

def vid_type_parse(id: str):
    av_match = re.match(r'av([0-9]+)', id, re.IGNORECASE)
    if av_match:
        return 'av', av_match.group(1)
    
    bv_match = re.match(r'bv([0-9a-zA-Z]+)', id, re.IGNORECASE)
    if bv_match:
        return 'bv', bv_match.group(1)
        
    return None, None

async def fetch_api(client: BiliClient, id: str) -> Dict[str, Any]:
    type_, vid = vid_type_parse(id)
    
    if type_ == 'av':
        url = f"https://api.bilibili.com/x/web-interface/view?aid={vid}"
    elif type_ == 'bv':
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={vid}"
    else:
        # 如果未匹配到类型，则默认为 bvid
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={id}"
        
    return await client.get(url, headers={"Host": "api.bilibili.com"})
