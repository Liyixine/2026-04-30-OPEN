"""交付说明生成核心逻辑。"""

from __future__ import annotations

import json
from dataclasses import asdict

from src.delivery_schema import (
    SCENE_LABELS,
    DeliveryContext,
    DeliveryResult,
    VisionObservation,
    normalize_scene,
)
from src.tts_output import make_tts_text


RISK_NOTES = {
    "enterprise_office": "照片可能包含门牌、工位或收件人信息，建议仅在内网或授权范围内流转。",
    "hospital_station": "照片可能包含科室、患者或药品相关信息，建议本地处理并避免外传。",
    "factory_warehouse": "照片可能包含产线、工位或设备信息，建议在企业内网留档。",
}


def _clean(value: str, fallback: str) -> str:
    text = (value or "").strip()
    return text if text else fallback


def build_recipient_message(context: DeliveryContext, observation: VisionObservation) -> str:
    """根据场景生成可直接发送给收件人的通知。"""

    scene = normalize_scene(context.scene)
    recipient = _clean(context.recipient, "收件人")
    item = _clean(context.item_hint, observation.item)
    location = _clean(observation.location, "现场指定位置")
    landmark = _clean(observation.landmark, "附近参照物请以照片为准")
    status = _clean(observation.status, "已完成拍照记录")
    note = f"补充说明：{context.extra_note}。" if context.extra_note else ""
    prefix = f"{recipient}您好"

    if scene == "hospital_station":
        return (
            f"{prefix}，{item}已送达{location}，{status}。"
            f"可参考现场参照物：{landmark}。请相关人员按交接流程领取。{note}"
        )

    if scene == "factory_warehouse":
        return (
            f"{prefix}，{item}已送达{location}，{landmark}，{status}。"
            f"现场位置已拍照留档，请按工单或仓储流程确认。{note}"
        )

    return (
        f"{prefix}，{item}已送达{location}，旁边可参考：{landmark}，"
        f"{status}。请您方便时领取。{note}"
    )


def build_archive_markdown(context: DeliveryContext, observation: VisionObservation, message: str) -> str:
    """生成用于内部留档的 Markdown 文本。"""

    scene = normalize_scene(context.scene)
    lines = [
        "# 现场交付记录",
        "",
        f"- 场景：{SCENE_LABELS[scene]}",
        f"- 收件对象：{_clean(context.recipient, '收件人')}",
        f"- 物品：{_clean(context.item_hint, observation.item)}",
        f"- 放置位置：{_clean(observation.location, '待确认位置')}",
        f"- 环境参照物：{_clean(observation.landmark, '暂无明显参照物')}",
        f"- 交付状态：{_clean(observation.status, '已拍照记录')}",
        f"- 现场备注：{context.extra_note or '无'}",
        f"- 风险提示：{RISK_NOTES[scene]}",
        "",
        "## 收件人通知",
        "",
        message,
    ]
    return "\n".join(lines)


def answer_followup(question: str, result: DeliveryResult) -> str:
    """基于已生成结果回答二次追问。"""

    if not question.strip():
        return ""

    return (
        f"可以重点查看{result.location}，附近参照物是{result.landmark}。"
        f"物品信息为{result.item}，当前状态为{result.status}。"
    )


def generate_delivery_result(
    context: DeliveryContext,
    observation: VisionObservation,
    followup_question: str = "",
) -> DeliveryResult:
    """生成完整交付结果。"""

    scene = normalize_scene(context.scene)
    context.scene = scene
    message = build_recipient_message(context, observation)
    tts_text = make_tts_text(message)
    archive = build_archive_markdown(context, observation, message)

    result = DeliveryResult(
        scene=scene,
        scene_label=SCENE_LABELS[scene],
        item=_clean(context.item_hint, observation.item),
        location=_clean(observation.location, "待确认位置"),
        landmark=_clean(observation.landmark, "暂无明显参照物"),
        status=_clean(observation.status, "已拍照记录"),
        risk_note=RISK_NOTES[scene],
        recipient_message=message,
        tts_text=tts_text,
        archive_markdown=archive,
    )
    result.followup_answer = answer_followup(followup_question, result)
    return result


def demo() -> DeliveryResult:
    """无模型环境下的最小演示。"""

    context = DeliveryContext(
        scene="enterprise_office",
        recipient="张工",
        item_hint="文件袋 1 个",
        extra_note="收件人暂时不在工位",
        tone="简短、礼貌、可直接发给收件人",
    )
    observation = VisionObservation(
        item="文件袋",
        location="A 座 3 楼前台右侧桌面",
        landmark="旁边有蓝色文件架和访客登记牌",
        status="包装完整，已放置妥当",
        raw_description="一个文件袋放在前台右侧桌面，附近有蓝色文件架。",
    )
    return generate_delivery_result(context, observation, "我还是找不到，旁边还有什么标志？")


if __name__ == "__main__":
    print(json.dumps(demo().to_dict(), ensure_ascii=False, indent=2))
