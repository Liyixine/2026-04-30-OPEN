"""Prompt 模板。

Prompt 重点是约束 VLM 不编造不可见信息，并让输出便于后续结构化解析。
"""

from __future__ import annotations

from src.delivery_schema import SCENE_LABELS, DeliveryContext


VLM_DELIVERY_PROMPT = """你是一个端侧现场交付状态识别助手。

请观察交付现场图片，只根据图片可见信息输出 JSON，不要编造看不到的内容。
如果图片中出现门牌、姓名、电话、病区号、设备编号等隐私信息，只做必要概括，
不要完整复述敏感字段。

请输出字段：
- item: 可见物品
- location: 放置位置
- landmark: 周围参照物
- status: 交付状态或包装状态
- confidence_note: 不确定或需要人工确认的部分
- raw_description: 一句话图片描述

只输出 JSON，不要输出 Markdown，不要输出解释。
"""


def build_delivery_prompt(context: DeliveryContext, observation_json: str) -> str:
    scene_label = SCENE_LABELS.get(context.scene, "企业园区")
    return f"""你是现场交付状态自动说明助手。

业务场景：{scene_label}
收件对象：{context.recipient}
物品提示：{context.item_hint or "无"}
现场补充备注：{context.extra_note or "无"}
通知语气：{context.tone}

VLM 图片理解结果：
{observation_json}

请生成：
1. 给收件人的简短送达通知
2. 适合 TTS 播报的文本
3. 内部留档 Markdown
4. 如信息不足，给出一条澄清追问建议

要求：
- 不编造图片中不可见的信息
- 语气专业、简洁、可直接发送
- 医院场景避免医疗建议，只描述交接位置和状态
- 工厂场景强调位置、工位、物料状态
- 企业场景强调前台、货架、会议室等易找参照物
- 最终回复必须由当前 VLM 图片理解结果和补充备注生成，不要照抄样例期望答案
"""
