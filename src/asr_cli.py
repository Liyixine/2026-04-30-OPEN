"""ASR 独立进程命令行入口。

Qwen3-TTS 和 Qwen3-ASR 对 transformers 的版本要求不同，在同一进程中
加载两者可能导致 processor 初始化失败。本模块作为独立进程运行 ASR 推理，
通过 JSON 文件输出转写结果。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.workshop_services import load_asr_model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--device", default="CPU")
    parser.add_argument("--workshop-dir", default="vendor/modelscope-workshop")
    args = parser.parse_args()

    model = load_asr_model(workshop_dir=args.workshop_dir, device=args.device)
    results = model.transcribe(audio=args.audio, language=None)
    payload = {
        "language": results[0].language if results else "",
        "text": results[0].text if results else "",
    }
    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
