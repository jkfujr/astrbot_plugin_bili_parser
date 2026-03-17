# AstrBot Bilibili Parser Plugin

移植自 [koishi-plugin-bili-parser](https://github.com/koishijs/koishi-plugin-bili-parser) 的 Bilibili 链接解析插件，适配 AstrBot。

## 功能

自动识别消息中的 Bilibili 链接，并回复详细的预览信息（标题、封面、UP主、数据等）。

支持的链接类型：

*   **视频 (Video)**: 支持 AV/BV 号，支持短链接。
*   **直播 (Live)**: 显示直播间状态、在线人数等。
*   **番剧 (Bangumi)**: 支持 EP/SS/MD 号。
*   **专栏 (Article)**: 支持 CV 号。
*   **动态 (Opus)**: 解析动态内容。
*   **空间 (Space)**: 解析用户空间链接。
*   **音频 (Audio)**: 支持 AU/AM 号。
*   **短链接 (Short)**: 自动解析 `b23.tv` 等短链接并还原为原始链接进行处理。

## 安装

1.  将本插件仓库克隆到 AstrBot 的 `data/plugins/` 目录下：
    ```bash
    git clone https://github.com/jkfujr/astrbot-plugin-bili-parser data/plugins/astrbot_plugin_bili_parser
    ```
2.  安装依赖：
    ```bash
    pip install -r data/plugins/astrbot_plugin_bili_parser/requirements.txt
    ```
3.  重启 AstrBot。

## 配置

插件提供了丰富的配置项，可以在 AstrBot 管理面板中进行设置：

*   **开关控制**：可以单独开启或关闭某种类型的解析（如只解析视频，不解析直播）。
*   **解析限制**：单条消息中最多解析的链接数量。
*   **回复模板**：支持使用 Jinja2 模板自定义回复内容。

### 模板变量

回复模板使用 Jinja2 语法。例如视频解析的默认模板：

```jinja2
{{ title }}
<img src="{{ pic }}" />
UP主：{{ owner.name }}
{{ desc | truncate(35) }}
点赞：{{ stat.like | format_number }}		投币：{{ stat.coin | format_number }}
收藏：{{ stat.favorite | format_number }}		转发：{{ stat.share | format_number }}
观看：{{ stat.view | format_number }}		弹幕：{{ stat.danmaku | format_number }}
https://www.bilibili.com/video/{{ bvid }}
```

## 许可证

AGPL-3.0
