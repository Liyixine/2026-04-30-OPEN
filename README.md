# Delivery Proof Assistant

基于 OpenVINO 的端侧现场交付状态自动说明助手。

本项目面向企业园区、医院科室、工厂仓库等弱网、内网和隐私敏感场景。
系统根据交付现场照片生成结构化交付信息、收件人通知、TTS 播报文本和
Markdown 留档记录。

## 交付内容

- `delivery-proof-assistant.ipynb`：魔搭灵感流可复现 Notebook
- `src/`：核心业务逻辑
- `samples/`：样例素材清单模板
- `article/modelscope-learn-article.md`：研习社文章草稿
- `skills/delivery-proof-assistant/SKILL.md`：OpenClaw Skill

## 快速开始

```bash
python -m pip install -r requirements.txt
python -m src.delivery_generator
```

真实 VLM/TTS 推理需要在魔搭灵感流或已配置 OpenVINO baseline 的环境中运行。
本机如果没有 Intel CPU/GPU/NPU，也可以先运行纯模板生成逻辑。

## 官方 Baseline

本项目参考：

```text
https://github.com/openvino-dev-samples/modelscope-workshop
```

重点参考：

- Lab 1：Qwen3-VL 多模态视觉语言理解
- Lab 2：Qwen3-ASR 语音识别，作为二次交互预留
- Lab 3：Qwen3-TTS 语音合成

## 素材要求

后续请将真实测试图片放入 `samples/`，并按
`samples/manifest.example.json` 补充图片描述、期望输出和追问用例。
