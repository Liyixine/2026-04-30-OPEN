"""TTS 播报文本生成。

将收件人通知转换为更适合语音播报的文本格式，包括数字转中文读法、
去除 Markdown 符号等后处理。
"""

from __future__ import annotations

import re


_READABLE_REPLACEMENTS = {
    "A 座": "A 座",
    "B 区": "B 区",
    "3 楼": "三楼",
    "2 楼": "二楼",
    "1 楼": "一楼",
    "04 工位": "零四工位",
}


def make_tts_text(message: str) -> str:
    """把收件人通知改写成更适合语音播报的文本。"""

    text = message.strip()
    for source, target in _READABLE_REPLACEMENTS.items():
        text = text.replace(source, target)

    # 删除 Markdown/JSON 中常见但不适合播报的符号。
    text = re.sub(r"[`*_#>\[\]{}]", "", text)
    text = text.replace("'", "").replace('"', "")
    text = text.replace(", ", "、").replace(",", "、")
    text = re.sub(r"\s+", " ", text)
    return text
