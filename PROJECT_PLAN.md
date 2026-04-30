# 现场交付状态自动说明助手

## 1. 项目是什么

本项目面向弱网、内网和隐私敏感场景，构建一个基于 OpenVINO 的端侧
“现场交付状态自动说明助手”。

用户拍摄交付现场照片后，系统通过 VLM 理解图片中的物品、放置位置、
环境参照物和交付状态，并自动生成可发送给收件人的送达说明。同时输出
适合 TTS 播报的文本，便于配送人员在现场快速确认。

项目重点覆盖三个场景：

- 企业园区：文件、快递、办公设备交付
- 医院科室：药品、检验材料、家属物品交接
- 工厂仓库：物料、工具、备件配送确认

项目不主打外卖平台集成，而是抽象为更通用的“现场交付凭证生成”能力。

## 2. 我们要做什么

最终交付内容包括：

1. 研习社文章
2. 项目仓库
3. 可提交到魔搭灵感流的 Notebook
4. OpenClaw Skill 的 `SKILL.md`

核心功能链路：

```text
交付现场照片
  -> VLM 图片理解
  -> 结构化交付信息抽取
  -> 生成送达通知
  -> 生成 TTS 播报文本
  -> 导出 Markdown 交付记录
  -> Skill 封装
```

第一版主功能：

- 使用官方 OpenVINO baseline 的 VLM 思路完成图片理解
- 将图片理解结果整理为结构化字段
- 根据不同场景生成标准送达说明
- 输出适合语音播报的 TTS 文本
- 生成可复现 Notebook
- 编写研习社文章草稿
- 编写可用于 Copaw/OpenClaw 的 Skill 文件

ASR 暂不作为主链路强依赖，只预留为二次交互能力：

```text
用户追问 / 配送员语音备注
  -> ASR 转文字
  -> 结合原图和上下文重新生成说明
```

## 3. 当前已有内容

当前目录已有：

```text
demo-notebook.ipynb
skill示例.md
```

其中：

- `demo-notebook.ipynb` 可作为灵感流 Notebook 的结构参考
- `skill示例.md` 可作为 OpenClaw Skill 写法参考
- 官方 baseline 参考仓库为：
  `https://github.com/openvino-dev-samples/modelscope-workshop`

官方 baseline 中重点参考：

- `lab1-multimodal-vlm`
- `lab2-speech-recognition`
- `lab3-text-to-speech`

## 4. 当前缺什么

### 4.1 场景素材

后续需要补充测试素材。建议每个场景至少 3 组，总计 9 组。

每组素材包括：

```json
{
  "id": "office_001",
  "scene": "enterprise_office",
  "image_path": "samples/office_001.jpg",
  "image_description": "文件袋放在 A 座 3 楼前台右侧桌面，旁边有蓝色文件架。",
  "delivery_context": {
    "recipient": "张工",
    "item_hint": "文件袋 1 个",
    "extra_note": "收件人暂时不在工位"
  },
  "expected_message": "张工您好，您的文件袋已送达 A 座 3 楼前台右侧桌面，旁边有蓝色文件架，方便您查找。请您方便时领取。",
  "expected_tts": "张工您好，您的文件袋已送达 A 座三楼前台右侧桌面，旁边有蓝色文件架，请您方便时领取。",
  "followup_cases": [
    {
      "question": "我还是找不到，旁边还有什么标志？",
      "expected_answer": "可以留意桌面旁边的蓝色文件架和前台访客登记牌。"
    }
  ]
}
```

推荐素材：

- 企业园区：文件袋、快递箱、办公设备
- 医院科室：药品袋、检验材料、家属物品
- 工厂仓库：物料箱、工具箱、备件

### 4.2 真实运行环境

本机没有 Intel CPU，不能完成最终 OpenVINO 端侧推理验证。

因此当前策略是：

- 本地生成代码、Notebook、文章、Skill
- 参考官方 baseline 写安装与推理逻辑
- 后续提交到 GitHub
- 在魔搭灵感流环境中完成真实运行测试

## 5. 实施计划

### 阶段一：仓库骨架

创建项目结构：

```text
delivery-proof-assistant/
├── README.md
├── requirements.txt
├── delivery-proof-assistant.ipynb
├── article/
│   └── modelscope-learn-article.md
├── src/
│   ├── delivery_schema.py
│   ├── delivery_prompts.py
│   ├── delivery_generator.py
│   ├── tts_output.py
│   └── asr_followup_stub.py
├── samples/
│   ├── README.md
│   ├── manifest.example.json
│   └── .gitkeep
├── outputs/
│   └── .gitkeep
└── skills/
    └── delivery-proof-assistant/
        └── SKILL.md
```

### 阶段二：核心代码

实现以下模块：

- `delivery_schema.py`：定义交付结果结构
- `delivery_prompts.py`：定义 VLM 和通知生成 prompt
- `delivery_generator.py`：根据 VLM 结果生成送达说明
- `tts_output.py`：生成 TTS 播报文本
- `asr_followup_stub.py`：预留二次追问/语音备注接口

### 阶段三：Notebook

生成 `delivery-proof-assistant.ipynb`，内容包括：

1. 项目说明
2. 环境安装
3. 模型加载
4. 样例数据说明
5. 图片理解
6. 送达说明生成
7. TTS 文本生成
8. 二次追问演示
9. Markdown 留档导出
10. 总结

### 阶段四：Skill

生成：

```text
skills/delivery-proof-assistant/SKILL.md
```

Skill 用于指导 Agent 根据交付图片、场景和补充备注生成：

- 交付状态
- 物品信息
- 放置位置
- 环境参照物
- 收件人通知
- TTS 播报文本
- 追问回答

### 阶段五：研习社文章

生成文章草稿：

```text
article/modelscope-learn-article.md
```

文章结构：

1. 项目基础信息
2. 应用场景说明
3. 整体方案设计
4. Baseline 跑通过程
5. 从 Baseline 到交付助手的创新改造
6. 运行效果展示
7. Skill 封装展示
8. 总结与展望

## 6. 最近工作记录

### 2026-04-30：真实推理 Notebook 打通

已完成：

- 加入三张示例图片：
  - `samples/office_001.png`
  - `samples/hospital_001.png`
  - `samples/warehouse_001.png`
- 将 `samples/manifest.example.json` 改为只保留必要上下文：
  - 图片路径
  - 场景
  - 收件对象
  - 物品提示
  - 补充备注
  - 可选追问
- 移除样例中的预置最终回复：
  - 不再预置 `expected_message`
  - 不再预置 `expected_tts`
  - 不再预置 `expected_structured_result`
- Notebook 改为真实推理优先：
  - 下载并加载 `snake7gun/Qwen3-VL-4B-Instruct-int4-ov`
  - 对三张图片实时生成 VLM 结构化观察
  - 生成送达通知、TTS 文本、追问回答和 Markdown 留档

### 2026-04-30：修复 `qwen3_vl` 加载问题

灵感流中出现：

```text
KeyError: 'qwen3_vl'
```

原因：

- 当前环境中的 `transformers / optimum-intel` 版本不认识 Qwen3-VL 架构。

处理：

- 参考官方 `openvino-dev-samples/modelscope-workshop`
- 将依赖切换到官方兼容组合：
  - `openvino==2026.0`
  - 官方固定 commit 的 `optimum-intel`
  - `torch==2.8`
  - `transformers==4.57.3`
- VLM 调用方式改为官方 Lab 1 风格：
  - 使用 `OVModelForVisualCausalLM.from_pretrained`
  - 使用 `processor.apply_chat_template(..., tokenize=True, return_dict=True, return_tensors="pt")`

### 2026-04-30：优化 VLM Prompt 和 TTS 文本

观察到 VLM 输出可能把字段写成数组字符串，例如：

```json
{
  "location": "['前台接待台', 'A座3F服务台前']"
}
```

导致通知和 TTS 变得机械。

处理：

- 新增 `build_vlm_observation_prompt`
- 将收件对象、目标交付物品、补充备注写入 VLM prompt
- 明确要求所有字段值必须是自然语言字符串，不允许输出数组
- 后处理兼容数组、列表字符串和空数组
- TTS 不再朗读完整通知，而是生成更短、更自然的播报稿

### 2026-04-30：接入 TTS 与 ASR

TTS：

- 参考官方 Lab 3
- 自动下载 `snake7gun/Qwen3-TTS-CustomVoice-0.6B-fp16-ov`
- 使用 `generate_custom_voice` 生成音频
- 输出音频、耗时、音频时长和 RTF

ASR：

- 参考官方 Lab 2
- 自动下载 `snake7gun/Qwen3-ASR-0.6B-fp16-ov`
- 初始版本在同一 Kernel 中出现：

```text
RuntimeError: Processor not loaded. Cannot transcribe.
```

原因：

- Qwen3-TTS 和 Qwen3-ASR 官方源码当前依赖的 `transformers` 小版本不同：
  - TTS 依赖 `transformers==4.57.3`
  - ASR 依赖 `transformers==4.57.6`
- 同一 Python 进程中先加载 TTS 后，再加载 ASR，可能导致 ASR processor 初始化失败。

处理：

- 新增 `src/asr_cli.py`
- 新增 `transcribe_audio_subprocess`
- ASR 改为独立 Python 子进程运行，避免和 TTS 在同一进程中抢依赖版本
- Notebook 中 ASR 用于回读 TTS 音频，也可扩展为语音追问入口
