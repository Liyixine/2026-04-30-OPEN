"""ASR 二次交互预留接口。

第一版比赛交付不强制跑通 ASR。这里保留接口，便于后续接入官方
lab2-speech-recognition 中的 Qwen3-ASR OpenVINO baseline。
"""

from __future__ import annotations


def transcribe_followup_audio(audio_path: str) -> str:
    """预留：把追问语音转为文本。

    后续可接入：
    `lab2-speech-recognition/qwen_3_asr_helper.py`
    中的 `OVQwen3ASRModel.from_pretrained(...).transcribe(...)`。
    """

    raise NotImplementedError(
        "ASR follow-up is reserved for the ModelScope/OpenVINO runtime. "
        f"Audio path received: {audio_path}"
    )
