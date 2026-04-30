"""Gradio 演示服务。

在魔搭灵感流或本地 OpenVINO 环境中运行：

python -m src.gradio_service
"""

from __future__ import annotations

import json
from pathlib import Path

import gradio as gr

from src.delivery_generator import generate_delivery_result
from src.delivery_schema import DeliveryContext, VisionObservation
from src.openvino_vlm_service import OpenVINODeliveryVLM


_vlm_service: OpenVINODeliveryVLM | None = None


def get_service() -> OpenVINODeliveryVLM:
    global _vlm_service
    if _vlm_service is None:
        _vlm_service = OpenVINODeliveryVLM.from_modelscope(device="AUTO")
    return _vlm_service


def run_delivery_demo(
    image_path: str,
    scene: str,
    recipient: str,
    item_hint: str,
    extra_note: str,
    followup_question: str,
) -> tuple[str, str, str, str]:
    context = DeliveryContext(
        scene=scene,
        recipient=recipient,
        item_hint=item_hint,
        extra_note=extra_note,
    )

    if image_path:
        observation = get_service().observe_delivery_image(Path(image_path))
    else:
        observation = VisionObservation()

    result = generate_delivery_result(context, observation, followup_question)
    return (
        json.dumps(observation.__dict__, ensure_ascii=False, indent=2),
        result.recipient_message,
        result.tts_text,
        result.archive_markdown,
    )


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="端侧现场交付状态自动说明助手") as demo:
        gr.Markdown("# 端侧现场交付状态自动说明助手")
        with gr.Row():
            image = gr.Image(type="filepath", label="交付现场图片")
            with gr.Column():
                scene = gr.Dropdown(
                    choices=[
                        ("企业园区", "enterprise_office"),
                        ("医院科室", "hospital_station"),
                        ("工厂仓库", "factory_warehouse"),
                    ],
                    value="enterprise_office",
                    label="场景",
                )
                recipient = gr.Textbox(value="张工", label="收件对象")
                item_hint = gr.Textbox(value="文件袋 1 个", label="物品提示")
                extra_note = gr.Textbox(value="收件人暂时不在工位", label="补充备注")
                followup = gr.Textbox(value="我还是找不到，旁边有什么标志？", label="二次追问")
                button = gr.Button("生成交付说明")

        observation = gr.Code(label="VLM 结构化观察", language="json")
        message = gr.Textbox(label="收件人通知", lines=4)
        tts = gr.Textbox(label="TTS 播报文本", lines=4)
        archive = gr.Markdown(label="Markdown 留档")

        button.click(
            run_delivery_demo,
            inputs=[image, scene, recipient, item_hint, extra_note, followup],
            outputs=[observation, message, tts, archive],
        )
    return demo


if __name__ == "__main__":
    build_demo().launch(server_name="0.0.0.0", server_port=7860)
