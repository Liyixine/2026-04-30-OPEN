"""OpenVINO VLM 模型下载、加载和推理服务。

该模块参考官方 modelscope-workshop 的 Lab 1 多模态 VLM baseline。
在没有 OpenVINO 运行环境的机器上不要直接实例化服务；Notebook 中会先
检查依赖并提供 mock 路径。
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.delivery_schema import VisionObservation
from src.delivery_prompts import VLM_DELIVERY_PROMPT


DEFAULT_VLM_MODEL_ID = "snake7gun/Qwen3-VL-4B-Instruct-int4-ov"
DEFAULT_VLM_MODEL_DIR = "models/Qwen3-VL-4B-Instruct-int4-ov"


def download_vlm_model(
    model_id: str = DEFAULT_VLM_MODEL_ID,
    local_dir: str | Path = DEFAULT_VLM_MODEL_DIR,
) -> Path:
    """从 ModelScope 下载 OpenVINO VLM 模型。"""

    from modelscope import snapshot_download

    target_dir = Path(local_dir)
    if target_dir.exists() and any(target_dir.iterdir()):
        return target_dir

    snapshot_download(model_id, local_dir=str(target_dir))
    return target_dir


def extract_json_object(text: str) -> dict[str, Any]:
    """从模型输出中提取 JSON 对象。"""

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def observation_from_vlm_text(text: str) -> VisionObservation:
    """把 VLM 文本输出转为业务结构。"""

    data = extract_json_object(text)
    return VisionObservation(
        item=str(data.get("item", "")).strip() or "待确认物品",
        location=str(data.get("location", "")).strip() or "待确认位置",
        landmark=str(data.get("landmark", "")).strip() or "暂无明显参照物",
        status=str(data.get("status", "")).strip() or "已拍照记录",
        confidence_note=str(data.get("confidence_note", "")).strip()
        or "图片信息有限，请以现场确认为准",
        raw_description=str(data.get("raw_description", "")).strip(),
    )


class OpenVINODeliveryVLM:
    """Qwen3-VL OpenVINO 图片理解服务。"""

    def __init__(self, model_dir: str | Path, device: str = "AUTO") -> None:
        from optimum.intel.openvino import OVModelForVisualCausalLM
        from transformers import AutoProcessor

        self.model_dir = Path(model_dir)
        self.device = device
        try:
            self.model = OVModelForVisualCausalLM.from_pretrained(self.model_dir, device=device)
        except KeyError as exc:
            if "qwen3_vl" not in str(exc):
                raise
            raise RuntimeError(
                "当前环境不认识 Qwen3-VL 架构。请先按官方 workshop 依赖重装："
                "`pip install -r requirements.txt --upgrade`。关键依赖包括 "
                "`openvino==2026.0`、官方固定 commit 的 `optimum-intel`、"
                "`transformers>=4.57.0`。"
            ) from exc
        self.processor = AutoProcessor.from_pretrained(
            self.model_dir,
            min_pixels=256 * 28 * 28,
            max_pixels=1280 * 28 * 28,
        )

    @classmethod
    def from_modelscope(
        cls,
        model_id: str = DEFAULT_VLM_MODEL_ID,
        local_dir: str | Path = DEFAULT_VLM_MODEL_DIR,
        device: str = "AUTO",
    ) -> "OpenVINODeliveryVLM":
        model_dir = download_vlm_model(model_id=model_id, local_dir=local_dir)
        return cls(model_dir=model_dir, device=device)

    def ask_image(self, image_path: str | Path, question: str = VLM_DELIVERY_PROMPT) -> str:
        """对单张图片提问，返回模型原始文本。"""

        path = Path(image_path).resolve()
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": str(path)},
                    {"type": "text", "text": question},
                ],
            }
        ]
        inputs = self.processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        )
        generated_ids = self.model.generate(**inputs, max_new_tokens=512)
        output_ids = generated_ids[:, inputs["input_ids"].shape[1] :]
        return self.processor.tokenizer.decode(output_ids[0], skip_special_tokens=True)

    def observe_delivery_image(self, image_path: str | Path) -> VisionObservation:
        """识别交付现场图片并返回结构化观察。"""

        raw = self.ask_image(image_path=image_path, question=VLM_DELIVERY_PROMPT)
        return observation_from_vlm_text(raw)
