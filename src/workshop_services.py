"""官方 ModelScope workshop ASR/TTS 模型加载与推理服务。

自动下载并加载官方 workshop 中的 Qwen3-ASR 和 Qwen3-TTS helper，
提供语音合成和语音识别能力。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


WORKSHOP_REPO = "https://github.com/openvino-dev-samples/modelscope-workshop.git"
QWEN3_ASR_REPO = "https://github.com/QwenLM/Qwen3-ASR.git"
QWEN3_ASR_COMMIT = "c17a131fe028b2e428b6e80a33d30bb4fa57b8df"
QWEN3_TTS_REPO = "https://github.com/QwenLM/Qwen3-TTS.git"
QWEN3_TTS_COMMIT = "1ab0dd75353392f28a0d05d9ca960c9954b13c83"
DEFAULT_WORKSHOP_DIR = Path("vendor/modelscope-workshop")

ASR_MODEL_ID = "snake7gun/Qwen3-ASR-0.6B-fp16-ov"
ASR_MODEL_DIR = Path("models/Qwen3-ASR-0.6B-fp16-ov")

TTS_MODEL_ID = "snake7gun/Qwen3-TTS-CustomVoice-0.6B-fp16-ov"
TTS_MODEL_DIR = Path("models/Qwen3-TTS-CustomVoice-0.6B-fp16-ov")


def ensure_workshop(workshop_dir: str | Path = DEFAULT_WORKSHOP_DIR) -> Path:
    """确保官方 workshop helper 存在。"""

    target = Path(workshop_dir)
    if (target / "lab2-speech-recognition" / "qwen_3_asr_helper.py").exists():
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--depth", "1", WORKSHOP_REPO, str(target)], check=True)
    return target


def _run(cmd: list[str], cwd: Path | None = None) -> None:
    env = os.environ.copy()
    env.setdefault("PIP_ROOT_USER_ACTION", "ignore")
    env.setdefault("GIT_CONFIG_PARAMETERS", "'advice.detachedHead=false'")
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True, env=env)


def _ensure_editable_repo(repo: str, commit: str, target: Path) -> None:
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        _run(["git", "clone", repo, str(target)])
        _run(["git", "-c", "advice.detachedHead=false", "checkout", "--quiet", commit], cwd=target)
    _run([sys.executable, "-m", "pip", "install", "-q", "-e", str(target), "--root-user-action=ignore"])


def ensure_qwen_audio_libs(workshop_dir: str | Path = DEFAULT_WORKSHOP_DIR) -> Path:
    """安装官方 ASR/TTS helper 依赖的 Qwen3-ASR 和 Qwen3-TTS 源码包。"""

    root = ensure_workshop(workshop_dir)
    _ensure_editable_repo(
        QWEN3_ASR_REPO,
        QWEN3_ASR_COMMIT,
        root / "lab2-speech-recognition" / "Qwen3-ASR",
    )
    _ensure_editable_repo(
        QWEN3_TTS_REPO,
        QWEN3_TTS_COMMIT,
        root / "lab3-text-to-speech" / "Qwen3-TTS",
    )
    return root


def ensure_qwen_tts_lib(workshop_dir: str | Path = DEFAULT_WORKSHOP_DIR) -> Path:
    root = ensure_workshop(workshop_dir)
    _ensure_editable_repo(
        QWEN3_TTS_REPO,
        QWEN3_TTS_COMMIT,
        root / "lab3-text-to-speech" / "Qwen3-TTS",
    )
    return root


def ensure_qwen_asr_lib(workshop_dir: str | Path = DEFAULT_WORKSHOP_DIR) -> Path:
    root = ensure_workshop(workshop_dir)
    _ensure_editable_repo(
        QWEN3_ASR_REPO,
        QWEN3_ASR_COMMIT,
        root / "lab2-speech-recognition" / "Qwen3-ASR",
    )
    return root


def download_model(model_id: str, local_dir: str | Path) -> Path:
    from modelscope import snapshot_download

    target = Path(local_dir)
    if target.exists() and any(target.iterdir()):
        return target
    snapshot_download(model_id, local_dir=str(target))
    return target


def load_asr_model(
    workshop_dir: str | Path = DEFAULT_WORKSHOP_DIR,
    model_dir: str | Path = ASR_MODEL_DIR,
    device: str = "CPU",
):
    """加载官方 Qwen3-ASR OpenVINO helper。"""

    root = ensure_qwen_asr_lib(workshop_dir)
    asr_dir = root / "lab2-speech-recognition"
    sys.path.insert(0, str(asr_dir.resolve()))
    from qwen_3_asr_helper import OVQwen3ASRModel

    local_model_dir = download_model(ASR_MODEL_ID, model_dir)
    return OVQwen3ASRModel.from_pretrained(
        model_dir=str(local_model_dir),
        device=device,
        max_inference_batch_size=32,
        max_new_tokens=256,
    )


def load_tts_model(
    workshop_dir: str | Path = DEFAULT_WORKSHOP_DIR,
    model_dir: str | Path = TTS_MODEL_DIR,
    device: str = "CPU",
):
    """加载官方 Qwen3-TTS OpenVINO helper。"""

    root = ensure_qwen_tts_lib(workshop_dir)
    tts_dir = root / "lab3-text-to-speech"
    sys.path.insert(0, str(tts_dir.resolve()))
    from qwen_3_tts_helper import OVQwen3TTSModel

    local_model_dir = download_model(TTS_MODEL_ID, model_dir)
    return OVQwen3TTSModel.from_pretrained(model_dir=local_model_dir, device=device)


def transcribe_audio_subprocess(
    audio_path: str | Path,
    output_path: str | Path,
    device: str = "CPU",
    workshop_dir: str | Path = DEFAULT_WORKSHOP_DIR,
    asr_transformers_version: str = "4.57.6",
) -> dict:
    """在独立 Python 进程中运行 ASR，避免和 TTS 的 transformers 版本冲突。

    ASR 需要 transformers>=4.57.6，而 TTS 需要 4.57.3。本函数会先在
    子进程中把 transformers 升到 ASR 所需版本，运行完 ASR 后再装回来。
    """

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    # 先升级 transformers 到 ASR 需要的版本
    _run([
        sys.executable, "-m", "pip", "install", "-q",
        f"transformers=={asr_transformers_version}",
        "--root-user-action=ignore",
    ])

    cmd = [
        sys.executable,
        "-m",
        "src.asr_cli",
        "--audio",
        str(audio_path),
        "--output",
        str(output),
        "--device",
        device,
        "--workshop-dir",
        str(workshop_dir),
    ]

    try:
        _run(cmd)
    finally:
        # 装回 TTS 兼容的版本，避免影响后续 TTS 使用
        _run([
            sys.executable, "-m", "pip", "install", "-q",
            "transformers>=4.57.0",
            "--root-user-action=ignore",
        ])

    return json.loads(output.read_text(encoding="utf-8"))
