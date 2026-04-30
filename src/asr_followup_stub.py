"""ASR 语音追问接口。

收件人可以通过语音追问交付物品的具体位置，本模块负责将语音转为文本。
当前为接口预留，实际 ASR 推理通过 workshop_services.transcribe_audio_subprocess 完成。
"""

from __future__ import annotations


def transcribe_followup_audio(audio_path: str) -> str:
    """将追问语音转为文本。

    独立的 ASR 推理请使用 ``workshop_services.transcribe_audio_subprocess``，
    该函数会在独立子进程中加载 Qwen3-ASR 模型并完成转写。
    """

    raise NotImplementedError(
        "请使用 workshop_services.transcribe_audio_subprocess 进行 ASR 推理。"
        f"收到音频路径: {audio_path}"
    )
