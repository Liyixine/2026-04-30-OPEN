---
name: delivery-proof-assistant
description: 调用基于 OpenVINO 的端侧交付凭证生成工具。该工具接收现场交付照片，利用 Qwen3-VL 多模态模型在本地完成图片理解，自动输出结构化交付信息、收件人通知、TTS 播报文本和 Markdown 留档记录。适用于企业园区、医院科室、工厂仓库等弱网或隐私敏感场景，全程端侧运行，数据不出本地。
---

# 端侧现场交付凭证生成工具

## 工具简介

本工具基于 Intel OpenVINO 加速的 Qwen3-VL 多模态模型，在端侧本地完成
交付现场照片的理解与分析。无需调用云端 API，所有推理均在本地 CPU/GPU/NPU
上完成，适合弱网、内网和隐私敏感的交付场景。

当用户提供一张交付现场照片并描述交付场景时，调用本工具完成以下任务：

- 识别照片中的物品、放置位置、环境参照物和交付状态
- 生成可直接发送给收件人的送达通知
- 生成适合语音播报的 TTS 短文本
- 导出结构化 Markdown 留档记录
- 回答收件人关于取件位置的追问

**支持的业务场景：**

| 场景标识 | 说明 | 典型交付物 |
|----------|------|-----------|
| `enterprise_office` | 企业园区 | 文件袋、快递箱、办公设备 |
| `hospital_station` | 医院科室 | 药品袋、检验材料、家属物品 |
| `factory_warehouse` | 工厂仓库 | 物料箱、工具箱、备件 |

**技术特点：**

- 全部端侧推理，零 API 成本
- 基于 OpenVINO 量化模型，普通 Intel 硬件即可运行
- 隐私数据不上传、不外传
- 支持 VLM 图片理解 + TTS 语音合成 + ASR 语音回读验证

## 环境要求

- **Python**: 3.10 - 3.11
- **处理器**: Intel CPU（推荐 12 代及以上）；如有 Intel GPU/NPU 可加速
- **内存**: 最低 16 GB
- **磁盘**: 约 5 GB（VLM 模型）+ 可选 TTS/ASR 模型

## 环境准备

### 第一步：获取项目代码

```bash
git clone https://github.com/Liyixine/2026-04-30-OPEN.git
cd 2026-04-30-OPEN
```

如果目录已存在，直接进入即可。

### 第二步：安装依赖

```bash
pip install -r requirements.txt
```

核心依赖包括 `openvino==2026.0`、官方固定 commit 的 `optimum-intel`、
`transformers>=4.57.0`。如遇依赖冲突，可分步安装：

```bash
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

### 第三步：下载 VLM 模型

```python
from src.openvino_vlm_service import download_vlm_model

model_dir = download_vlm_model(
    model_id="snake7gun/Qwen3-VL-4B-Instruct-int4-ov",
    local_dir="models/Qwen3-VL-4B-Instruct-int4-ov",
)
print(f"模型已就绪: {model_dir}")
```

模型约 2.5 GB，首次下载后会缓存到本地。

---

## 核心功能调用

### 功能 1：交付现场图片分析

这是最核心的能力。传入一张交付现场照片和业务上下文，工具会调用 VLM
识别图片内容，并生成完整的交付说明。

```python
import json
from src.openvino_vlm_service import OpenVINODeliveryVLM
from src.delivery_schema import DeliveryContext
from src.delivery_prompts import build_vlm_observation_prompt
from src.delivery_generator import generate_delivery_result

# 加载 VLM（首次加载约 30-60 秒，后续复用）
vlm = OpenVINODeliveryVLM(model_dir="models/Qwen3-VL-4B-Instruct-int4-ov", device="AUTO")

# 构造业务上下文
context = DeliveryContext(
    scene="enterprise_office",        # 场景：enterprise_office / hospital_station / factory_warehouse
    recipient="张工",                  # 收件对象
    item_hint="文件袋 1 个",           # 物品提示（可选，辅助 VLM 聚焦目标物品）
    extra_note="收件人暂时不在工位",    # 补充备注（可选）
)

# 用业务上下文构造更精准的 VLM prompt
prompt = build_vlm_observation_prompt(context)

# 对图片进行 VLM 推理
observation = vlm.observe_delivery_image(
    image_path="samples/office_001.png",
    question=prompt,
)

# 生成完整交付结果（通知、TTS、留档、追问回答）
result = generate_delivery_result(
    context=context,
    observation=observation,
    followup_question="我还是找不到，旁边还有什么标志？",  # 可选
)

# 输出结构化结果
print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
```

**输出字段说明：**

| 字段 | 含义 |
|------|------|
| `scene` / `scene_label` | 场景标识和中文名称 |
| `item` | 交付物品 |
| `location` | 放置位置 |
| `landmark` | 环境参照物（帮助收件人定位） |
| `status` | 交付状态 |
| `risk_note` | 隐私风险提示 |
| `recipient_message` | 可直接发送给收件人的通知文本 |
| `tts_text` | 适合语音播报的短文本 |
| `archive_markdown` | 内部留档 Markdown |
| `followup_answer` | 对收件人追问的回答 |

### 功能 2：批量处理样例清单

项目内置了样例清单文件 `samples/manifest.example.json`，可以批量处理
多张交付图片。

```python
import json
from src.sample_loader import load_manifest, context_from_sample
from src.openvino_vlm_service import OpenVINODeliveryVLM
from src.delivery_prompts import build_vlm_observation_prompt
from src.delivery_generator import generate_delivery_result

vlm = OpenVINODeliveryVLM(model_dir="models/Qwen3-VL-4B-Instruct-int4-ov", device="AUTO")
samples = load_manifest("samples/manifest.example.json")

for sample in samples:
    context = context_from_sample(sample)
    prompt = build_vlm_observation_prompt(context)
    observation = vlm.observe_delivery_image(sample["image_path"], question=prompt)

    followup_q = ""
    if sample.get("followup_cases"):
        followup_q = sample["followup_cases"][0].get("question", "")

    result = generate_delivery_result(context, observation, followup_q)
    print(f"\n{'='*60}")
    print(f"样例: {sample['id']}")
    print(f"通知: {result.recipient_message}")
    print(f"TTS:  {result.tts_text}")
```

### 功能 3：TTS 语音合成

将生成的 TTS 文本合成为音频文件，便于配送人员现场播放确认。

```python
from src.workshop_services import load_tts_model

tts_model = load_tts_model(device="CPU")

tts_text = result.tts_text  # 使用功能 1 生成的 TTS 文本
audio = tts_model.generate_custom_voice(tts_text)

import soundfile as sf
sf.write("outputs/delivery_tts.wav", audio, samplerate=24000)
print("语音文件已保存: outputs/delivery_tts.wav")
```

首次运行会自动下载 TTS 模型（约 1.2 GB）和官方 helper 源码。

### 功能 4：ASR 语音回读验证

对 TTS 生成的音频进行 ASR 转写，验证播报内容的准确性。ASR 在独立子进程
中运行，避免与 TTS 的 transformers 版本冲突。

```python
from src.workshop_services import transcribe_audio_subprocess

asr_result = transcribe_audio_subprocess(
    audio_path="outputs/delivery_tts.wav",
    output_path="outputs/asr_result.json",
    device="CPU",
)
print(f"ASR 回读结果: {asr_result['text']}")
```

### 功能 5：无模型环境快速验证

在没有 OpenVINO 运行环境的机器上，可以用内置 demo 数据验证业务逻辑：

```bash
python -m src.delivery_generator
```

该命令使用硬编码的模拟数据走通"上下文 → 通知 → TTS 文本 → 留档"全流程，
输出 JSON 格式的完整交付结果。

### 功能 6：Gradio 交互界面

启动一个本地 Web 界面，支持上传图片、选择场景、填写备注并一键生成交付说明：

```bash
python -m src.gradio_service
```

界面默认运行在 `http://0.0.0.0:7860`，可在浏览器中直接访问。

---

## 调用示例

### 场景 A：用户提供了一张办公区交付照片

```bash
# 环境准备（首次）
git clone https://github.com/Liyixine/delivery-proof-assistant.git
cd delivery-proof-assistant
pip install -r requirements.txt
```

```python
from src.openvino_vlm_service import OpenVINODeliveryVLM, download_vlm_model
from src.delivery_schema import DeliveryContext
from src.delivery_prompts import build_vlm_observation_prompt
from src.delivery_generator import generate_delivery_result
import json

download_vlm_model()
vlm = OpenVINODeliveryVLM(model_dir="models/Qwen3-VL-4B-Instruct-int4-ov")

context = DeliveryContext(
    scene="enterprise_office",
    recipient="李经理",
    item_hint="快递箱 2 个",
    extra_note="已放在前台旁边的柜子上",
)
prompt = build_vlm_observation_prompt(context)
observation = vlm.observe_delivery_image("用户提供的图片路径.jpg", question=prompt)
result = generate_delivery_result(context, observation)

print(result.recipient_message)
# → 李经理您好，快递箱 2 个已送达前台旁边的柜子上，旁边可参考：...
print(result.tts_text)
# → 李经理您好，快递箱两个已放在前台旁边的柜子上...
```

### 场景 B：用户只描述了交付情况，没有照片

没有照片时可以跳过 VLM 推理，直接用用户描述构造结构化结果：

```python
from src.delivery_schema import DeliveryContext, VisionObservation
from src.delivery_generator import generate_delivery_result

context = DeliveryContext(
    scene="hospital_station",
    recipient="护士站值班人员",
    item_hint="药品袋 1 个",
    extra_note="已放在 9F 护士站物品交接区",
)
observation = VisionObservation(
    item="药品袋",
    location="9F 护士站物品交接区台面",
    landmark="交接登记本、消毒液",
    status="外包装完好，已放置妥当",
)
result = generate_delivery_result(context, observation)
print(result.recipient_message)
```

### 场景 C：运行内置完整流水线

```bash
python -m src.delivery_generator
```

直接输出 JSON 格式的完整结果，包含通知、TTS、留档、追问回答。

---

## 输出格式参考

所有功能的结构化输出均为如下 JSON：

```json
{
  "scene": "enterprise_office",
  "scene_label": "企业园区",
  "item": "文件袋 1 个",
  "location": "A 座 3 楼前台右侧桌面",
  "landmark": "蓝色文件架、访客登记牌",
  "status": "包装完整，已放置妥当",
  "risk_note": "照片可能包含门牌、工位或收件人信息，建议仅在内网或授权范围内流转。",
  "recipient_message": "张工您好，您的文件袋已送达 A 座 3 楼前台右侧桌面，旁边可参考：蓝色文件架、访客登记牌，包装完整，已放置妥当。请您方便时领取。",
  "tts_text": "张工您好，您的文件袋已放在A座三楼前台右侧桌面。旁边有蓝色文件架、访客登记牌，方便您查找，请您方便时领取。",
  "archive_markdown": "# 现场交付记录\n\n- 场景：企业园区\n- 收件对象：张工\n...",
  "followup_answer": "可以重点查看 A 座 3 楼前台右侧桌面，附近参照物是蓝色文件架、访客登记牌。",
  "created_at": "2026-04-30T21:00:00"
}
```

## 故障排除

### `ModuleNotFoundError: No module named 'optimum'`

依赖安装时出现冲突导致 `optimum-intel` 未安装成功。请分步安装：

```bash
pip install openvino==2026.0 "transformers>=4.57.0" accelerate
pip install git+https://github.com/openvino-dev-samples/optimum-intel.git@2f62e5aee74b4acba3836e1f26678c0db0a09c00 --no-deps
```

### `KeyError: 'qwen3_vl'`

当前环境中 `transformers` 或 `optimum-intel` 版本不认识 Qwen3-VL 架构。
请确保使用官方 workshop 的依赖组合，然后重启 Python/Kernel。

### ASR 加载失败（`RuntimeError: Processor not loaded`）

TTS 和 ASR 对 `transformers` 小版本要求不同，不能在同一进程中共存。
项目已内置 `transcribe_audio_subprocess` 函数，ASR 会在独立子进程中运行。
请使用该函数而非直接调用 `load_asr_model`。

### 内存不足

VLM 模型推理约需 8-12 GB 内存。如内存不足：
- 关闭其他占用内存的程序
- 确保系统可用内存 ≥ 16 GB
