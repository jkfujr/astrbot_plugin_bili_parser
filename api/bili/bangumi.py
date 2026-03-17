import re
from typing import Dict, Any
from .client import BiliClient

def bgm_type_parse(id: str):
    ep_match = re.match(r'ep([0-9]+)', id, re.IGNORECASE)
    if ep_match:
        return 'ep', ep_match.group(1)
    
    ss_match = re.match(r'ss([0-9]+)', id, re.IGNORECASE)
    if ss_match:
        return 'ss', ss_match.group(1)
        
    return None, None

async def fetch_web_api(client: BiliClient, id: str) -> Dict[str, Any]:
    type_, bgm_id = bgm_type_parse(id)
    
    if type_ == 'ep':
        url = f"https://api.bilibili.com/pgc/view/web/season?ep_id={bgm_id}"
    elif type_ == 'ss':
        url = f"https://api.bilibili.com/pgc/view/web/season?season_id={bgm_id}"
    else:
        # 如果类型未知但 ID 为纯数字，则默认为 season_id
        if id.isdigit():
             url = f"https://api.bilibili.com/pgc/view/web/season?season_id={id}"
        else:
             raise ValueError(f"Unknown bangumi type: {id}")

    ret = await client.get(url, headers={"Host": "api.bilibili.com"})
    # 兼容性处理：将 result 字段映射到 data 字段，以便统一处理逻辑
    if 'result' in ret:
        ret['data'] = ret['result']
    return ret

async def fetch_mdid_api(client: BiliClient, id: str) -> Dict[str, Any]:
    media_id = re.sub(r'^md', '', id, flags=re.IGNORECASE)
    md_url = f"https://api.bilibili.com/pgc/review/user?media_id={media_id}"
    
    md_info = await client.get(md_url, headers={"Host": "api.bilibili.com"})
    
    if not md_info.get('result'):
        raise ValueError("Fetch bangumi information via mdid failed!")
        
    season_id = md_info['result']['media']['season_id']
    url = f"https://api.bilibili.com/pgc/view/web/season?season_id={season_id}"
    
    ret = await client.get(url, headers={"Host": "api.bilibili.com"})
    if 'result' in ret:
        ret['data'] = ret['result']
    return ret
