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

真实推理请在魔搭灵感流或已配置 OpenVINO baseline 的环境中运行
`delivery-proof-assistant.ipynb`。Notebook 会完成：

1. 从 ModelScope 下载 `snake7gun/Qwen3-VL-4B-Instruct-int4-ov`
2. 使用 OpenVINO VLM 对 `samples/` 中三张示例图实时推理
3. 生成收件人通知、TTS 播报文本和 Markdown 留档
4. 下载并加载官方 TTS/ASR helper，生成语音并进行 ASR 回读验证

本机如果没有 Intel CPU/GPU/NPU，也可以先运行纯模板生成逻辑：

```bash
python -m src.delivery_generator
```

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

当前已包含三张示例图：

- `samples/office_001.png`
- `samples/hospital_001.png`
- `samples/warehouse_001.png`

`samples/manifest.example.json` 只保留必要上下文，不预置最终回复。
最终通知、TTS 文本和追问回答由 Notebook 运行时生成。

## 常见问题

### `KeyError: 'qwen3_vl'`

这是依赖版本问题，不是图片或模型目录问题。请重新运行 Notebook 的依赖安装单元：

```bash
python -m pip install -r requirements.txt --upgrade
```

然后重启 Kernel，再从头运行 Notebook。

本项目依赖官方 workshop 的固定版本组合：

- `openvino==2026.0`
- 官方固定 commit 的 `optimum-intel`
- `transformers>=4.57.0`

### ASR/TTS 为什么会 clone 官方仓库？

官方 ASR/TTS helper 依赖 `Qwen3-ASR` 和 `Qwen3-TTS` 源码包。
Notebook 会通过 `src/workshop_services.py` 自动 clone：

```text
openvino-dev-samples/modelscope-workshop
QwenLM/Qwen3-ASR
QwenLM/Qwen3-TTS
```

这些目录会写入 `vendor/`，不会提交到 GitHub。
