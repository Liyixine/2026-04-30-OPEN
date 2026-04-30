"""数据结构定义。

这些结构既服务 Notebook 演示，也服务后续 Skill/应用封装。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


SCENE_LABELS = {
    "enterprise_office": "企业园区",
    "hospital_station": "医院科室",
    "factory_warehouse": "工厂仓库",
}


@dataclass
class DeliveryContext:
    """配送员或业务系统提供的补充信息。"""

    scene: str
    recipient: str = "收件人"
    item_hint: str = ""
    extra_note: str = ""
    operator: str = "现场交付人员"


@dataclass
class VisionObservation:
    """VLM 从交付现场照片中提取的信息。"""

    item: str = "待确认物品"
    location: str = "待确认位置"
    landmark: str = "暂无明显参照物"
    status: str = "已拍照记录"
    confidence_note: str = "图片信息有限，请以现场确认为准"
    raw_description: str = ""


@dataclass
class DeliveryResult:
    """最终交付说明结果。"""

    scene: str
    scene_label: str
    item: str
    location: str
    landmark: str
    status: str
    risk_note: str
    recipient_message: str
    tts_text: str
    archive_markdown: str
    followup_answer: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_scene(scene: str) -> str:
    """将未知场景收敛到企业园区，避免模板分支失效。"""

    return scene if scene in SCENE_LABELS else "enterprise_office"
