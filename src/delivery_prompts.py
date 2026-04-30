"""Prompt 模板。

Prompt 重点是约束 VLM 不编造不可见信息，并让输出便于后续结构化解析。
"""

from __future__ import annotations

from src.delivery_schema import SCENE_LABELS, DeliveryContext


VLM_DELIVERY_PROMPT = """你是一个端侧现场交付状态识别助手。

请观察交付现场图片，只根据图片可见信息输出 JSON，不要编造看不到的内容。
如果图片中出现门牌、姓名、电话、病区号、设备编号等隐私信息，只做必要概括，
不要完整复述敏感字段。

请输出字段，所有字段值都必须是中文字符串，不要输出数组：
- item: 重点识别目标交付物品，不要把文件架、绿植、登记牌等参照物当成物品
- location: 一个最清楚、最具体的放置位置
- landmark: 用顿号连接 2-3 个最容易帮助收件人定位的参照物
- status: 只描述包装、摆放、可见状态；不要写“待交付”
- confidence_note: 不确定或需要人工确认的部分，没有则写“无”
- raw_description: 一句话图片描述

只输出 JSON，不要输出 Markdown，不要输出解释。
"""


def build_vlm_observation_prompt(context: DeliveryContext, image_description: str = "") -> str:
    """为交付图片构造更稳定的 VLM 观察 prompt。"""

    scene_label = SCENE_LABELS.get(context.scene, "企业园区")
    return f"""你是一个端侧现场交付状态识别助手。

这张图片是现场人员完成物品放置后拍摄的交付凭证照。
请重点围绕“目标交付物品”判断它放在哪里、旁边有什么参照物。

业务场景：{scene_label}
目标交付物品：{context.item_hint or "请根据图片判断"}
收件对象：{context.recipient}
人工补充备注：{context.extra_note or "无"}
人工图片说明：{image_description or "无"}

请只根据图片可见信息和人工补充信息输出 JSON。
所有字段值都必须是自然语言字符串，不要输出数组、列表或 Python 表达式。
如果图片中出现门牌、姓名、电话、病区号、设备编号等隐私信息，只做必要概括，
不要完整复述敏感字段。

字段要求：
- item: 目标交付物品，例如“文件袋 1 个”。不要把蓝色文件架、绿植、登记牌等参照物写进 item。
- location: 一个最清楚、最具体的放置位置，例如“A座3F服务台前台桌面”。
- landmark: 2-3 个定位参照物，用顿号连接，例如“蓝色文件架、访客登记牌、绿植”。
- status: 交付物品的可见状态，例如“已放在桌面，外观完整”。不要写“待交付”。
- confidence_note: 不确定项；如果没有明显不确定，写“无”。
- raw_description: 一句话描述现场。

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
