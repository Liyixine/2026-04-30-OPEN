"""样例清单读取工具。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.delivery_schema import DeliveryContext


def load_manifest(path: str | Path = "samples/manifest.example.json") -> list[dict[str, Any]]:
    manifest_path = Path(path)
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def context_from_sample(sample: dict[str, Any]) -> DeliveryContext:
    context = sample.get("delivery_context", {})
    return DeliveryContext(
        scene=sample.get("scene", "enterprise_office"),
        recipient=context.get("recipient", "收件人"),
        item_hint=context.get("item_hint", ""),
        extra_note=context.get("extra_note", ""),
        tone=context.get("tone", "简短、礼貌、可直接发送"),
    )
