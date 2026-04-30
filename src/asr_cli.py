"""独立进程 ASR 命令行入口。

TTS helper 当前依赖 transformers==4.57.3，而 Qwen3-ASR 依赖
transformers==4.57.6。Notebook 中用独立进程运行 ASR，避免同一个
Python 进程里已经加载的 transformers 版本影响 processor 初始化。
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
