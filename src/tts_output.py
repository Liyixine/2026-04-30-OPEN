"""TTS 播报文本生成。

第一版先输出可被 TTS 模型消费的文本。真实音频合成可在灵感流环境中
接入官方 lab3-text-to-speech baseline。
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
    text = re.sub(r"\s+", " ", text)
    return text
