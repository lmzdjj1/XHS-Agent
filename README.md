# XHS Content Agent

![XHS Content Agent 宣传封面图](./XHS%20Content%20Agent%E5%AE%A3%E4%BC%A0%E5%B0%81%E9%9D%A2%E5%9B%BE.png)

一个基于 LangGraph + FastAPI + Vue 的小红书内容智能生成 Agent。项目把一篇小红书笔记的生产流程拆成多个可观测节点，覆盖内容框架、标题生成、标题选择、关键词标签、正文去 AI 味和封面图提示词生成，并提供 Web 页面、CLI、本地 Python 调用和 HTTP API 多种使用方式。

## 项目定位

这个项目不是单次 Prompt 调用，而是一个多步骤内容工作流：

```text
用户指令 / OpenClaw JSON
  -> 内容框架与正文草稿
  -> 标题候选
  -> 最佳标题选择
  -> 搜索关键词与话题标签
  -> 去 AI 味最终正文
  -> 封面图提示词
```

Web 前端默认只展示用户最关心的主要产物：标题、关键词/标签、最终正文和封面图提示词。模型中间回答、标签理由、避坑检查等过程性内容不会作为主内容直接展示。

适合用于展示：

- LangGraph 工作流编排
- LLM 应用节点拆分
- FastAPI 服务化封装
- 简洁 Web 前端接入 Agent 输出
- Pydantic 请求模型校验
- Prompt 模板集中管理
- Mock 模式下的本地调试与演示
- OpenClaw 风格结构化输入适配

## 技术栈

| 模块 | 技术 |
|---|---|
| 工作流编排 | LangGraph |
| LLM 调用 | LangChain Core, langchain-deepseek |
| API 服务 | FastAPI, Pydantic |
| Web 前端 | Vue 3 CDN, Tailwind CSS CDN |
| 命令行入口 | argparse |
| 配置管理 | python-dotenv, 环境变量 |
| 模型 | DeepSeek API，支持 mock 模式 |

## 项目结构

```text
.
├── api_server.py          # FastAPI HTTP 服务入口，同时返回 Web 首页
├── cli.py                 # 命令行入口，支持按节点流式输出
├── xhs_workflow.py        # SDK 风格聚合入口，方便外部 Python 代码 import
├── requirements.txt       # Python 依赖
├── static/
│   └── index.html         # Vue + Tailwind 前端页面
├── examples/
│   ├── sample_request.json
│   ├── openclaw_request.json
│   └── sample_output_mock.md
└── xhs_agent/
    ├── __init__.py
    ├── graph.py           # LangGraph 节点编排与工作流执行入口
    ├── nodes.py           # 各个工作流节点的业务逻辑
    ├── prompts.py         # System/User Prompt 模板
    ├── llm.py             # LLM 调用封装与 mock 模式
    ├── io.py              # 普通文本 / OpenClaw JSON 输入适配
    └── state.py           # 工作流状态结构定义
```

## 核心工作流

工作流定义在 `xhs_agent/graph.py`：

```text
START
  -> build_framework
  -> generate_titles
  -> select_title
  -> generate_keywords
  -> humanize_copy
  -> generate_cover_prompt
  -> END
```

每个节点定义在 `xhs_agent/nodes.py`：

| 节点 | 作用 |
|---|---|
| `build_framework` | 根据输入指令生成内容框架和第一版正文草稿 |
| `generate_titles` | 基于正文生成小红书标题候选 |
| `select_title` | 从标题候选中选择最适合发布的标题 |
| `generate_keywords` | 生成搜索关键词和话题标签组合 |
| `humanize_copy` | 对正文做去 AI 味改写 |
| `generate_cover_prompt` | 生成可用于图片模型的小红书封面提示词 |

## 快速开始

### 1. 创建虚拟环境

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. 安装依赖

```powershell
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`：

```powershell
Copy-Item .env.example .env
```

`.env.example` 示例：

```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_TEMPERATURE=0.7
XHS_WORKFLOW_MOCK=1
XHS_LLM_MAX_RETRIES=3
XHS_LLM_RETRY_BACKOFF_BASE=1

# Optional cover prompt branding
XHS_BRAND_NAME=内容方法实验室
XHS_BRAND_TAGLINE=内容方法 × AI 工作流
XHS_BRAND_STYLE=内容方法论、AI 辅助创作、轻手绘、实用但不死板
XHS_BRAND_BOOK_1=内容方法论
XHS_BRAND_BOOK_2=AI 辅助创作
XHS_BRAND_BOOK_3=工作流笔记
```

复制后请将 `DEEPSEEK_API_KEY` 替换为自己的 API Key。如果不设置 `DEEPSEEK_MODEL`，代码会使用 `deepseek-v4-flash` 作为默认模型。

如果只是本地演示或测试，可以保留：

```env
XHS_WORKFLOW_MOCK=1
```

此时项目不会真实调用模型 API，而是返回 mock 输出。

如果要调用真实模型：

```env
XHS_WORKFLOW_MOCK=0
DEEPSEEK_API_KEY=your_real_api_key
```

## Web 使用

启动 FastAPI 服务：

```powershell
uvicorn api_server:app --reload
```

打开 Web 页面：

```text
http://127.0.0.1:8000
```

页面提供：

- 文本指令输入
- 服务健康状态展示
- 标题候选与选中标题
- 关键词与话题标签展示
- 去 AI 味最终正文预览
- 封面图提示词展示
- 一键复制主要内容

前端会对模型返回内容做轻量清洗，例如去掉 Markdown 加粗标记、编号、标签解释段落，只保留适合直接使用的主要内容。

## Docker 部署

项目提供了 `Dockerfile` 和 `docker-compose.yml`，可以直接构建镜像并通过 `.env` 注入运行时配置。

构建镜像：

```powershell
docker build -t xhs-content-agent .
```

使用 `.env` 启动容器：

```powershell
docker run --rm -p 8000:8000 --env-file .env xhs-content-agent
```

也可以使用 Docker Compose：

```powershell
docker compose up -d --build
```

打开页面：

```text
http://127.0.0.1:8000
```

如果只想用 mock 模式快速演示，可以确保 `.env` 中包含：

```env
XHS_WORKFLOW_MOCK=1
```

如果要调用真实 DeepSeek 模型，请设置：

```env
XHS_WORKFLOW_MOCK=0
DEEPSEEK_API_KEY=your_real_api_key
```

容器默认启动命令是：

```text
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

`.dockerignore` 会排除 `.env`、虚拟环境、缓存和本地日志，避免把密钥或无关文件打进镜像。

## CLI 使用

普通运行：

```powershell
python cli.py "帮我写一篇关于 RPA 开发工程师转型 AI 应用工程师的小红书笔记"
```

流式查看每个节点输出：

```powershell
python cli.py "帮我写一篇关于 RPA 开发工程师转型 AI 应用工程师的小红书笔记" --stream
```

不传参数时进入交互模式：

```powershell
python cli.py
```

交互模式默认按节点流式输出，输入 `quit`、`exit` 或 `q` 退出。

## FastAPI 使用

接口文档：

```text
http://127.0.0.1:8000/docs
```

健康检查：

```http
GET /health
```

调用内容工作流：

```http
POST /invoke
Content-Type: application/json

{
  "instruction": "帮我写一篇关于 RPA 开发工程师转型 AI 应用工程师的小红书笔记"
}
```

也支持 OpenClaw 风格结构化输入：

```json
{
  "openclaw": {
    "task": "generate_xhs_note",
    "topic": "RPA 开发工程师转型 AI 应用工程师",
    "audience": "想转型 AI 应用岗位的自动化工程师",
    "style": "真实经验分享"
  }
}
```

响应字段：

```json
{
  "source": "text",
  "framework": "...",
  "titles": "...",
  "selected_title": "...",
  "keywords": "...",
  "final_copy": "...",
  "cover_prompt": "..."
}
```

其中 `source` 可能是：

| 值 | 含义 |
|---|---|
| `text` | 普通文本指令 |
| `openclaw` | 结构化 JSON / OpenClaw 风格输入 |

如果 `instruction` 和 `openclaw` 都不传，接口会返回 `400`：

```json
{
  "detail": "Either instruction or openclaw is required."
}
```

## Python 调用

`xhs_workflow.py` 提供 SDK 风格聚合入口，方便其他 Python 代码直接调用：

```python
from xhs_workflow import format_result, run_xhs_workflow

result = run_xhs_workflow("帮我写一篇关于 AI 自动化的笔记")
print(format_result(result))
```

也可以使用流式输出：

```python
from xhs_workflow import stream_xhs_workflow

for event in stream_xhs_workflow("帮我写一篇小红书笔记"):
    print(event)
```

## 示例文件

项目提供了两个请求样例和一个 mock 输出样例：

```text
examples/
├── sample_request.json       # 普通 instruction 请求
├── openclaw_request.json     # OpenClaw 风格结构化请求
└── sample_output_mock.md     # mock 模式输出结构示例
```

可以在 FastAPI `/docs` 页面中复制 `sample_request.json` 或 `openclaw_request.json` 的内容进行测试。

## Mock 模式

Mock 模式在 `xhs_agent/llm.py` 中实现。

当环境变量为：

```env
XHS_WORKFLOW_MOCK=1
```

`invoke_llm()` 不会请求真实模型，而是返回包含 System Prompt 和 User Prompt 摘要的模拟结果。

这个设计用于：

- 无 API Key 时本地演示
- 避免开发阶段消耗模型额度
- 支持自动化测试
- 快速验证 LangGraph 节点流转是否正常

需要注意：mock 输出不是高质量的小红书成稿，只用于验证流程和接口是否可用。

真实模型调用会在 `invoke_llm()` 中做有限次数重试、指数退避等待和空内容检测。可通过环境变量调整：

```env
XHS_LLM_MAX_RETRIES=3
XHS_LLM_RETRY_BACKOFF_BASE=1
```

## 封面品牌配置

封面图提示词默认使用通用账号配置，可以通过环境变量自定义：

```env
XHS_BRAND_NAME=内容方法实验室
XHS_BRAND_TAGLINE=内容方法 × AI 工作流
XHS_BRAND_STYLE=内容方法论、AI 辅助创作、轻手绘、实用但不死板
XHS_BRAND_BOOK_1=内容方法论
XHS_BRAND_BOOK_2=AI 辅助创作
XHS_BRAND_BOOK_3=工作流笔记
```

这些配置会被 `generate_cover_prompt` 节点写入封面图提示词。

## 输入设计

`/invoke` 接口支持两种输入：

| 字段 | 用途 |
|---|---|
| `instruction` | 普通文本指令，适合 Web 页面、本地调试和普通用户调用 |
| `openclaw` | 结构化 JSON，适合接入上层 Agent、自动化平台或 OpenClaw 指挥官 |

底层的 `normalize_openclaw_instruction()` 也支持传入 JSON 字符串。如果字符串能解析为 JSON object，会被视为 `openclaw` 来源；否则会被视为普通文本。

## 前端展示说明

`static/index.html` 是一个轻量单页前端：

- Vue 通过 CDN 加载，没有额外前端构建步骤。
- Tailwind 通过 CDN 加载，适合本地演示和小型项目。
- 页面调用 `/health` 判断服务状态。
- 页面调用 `/invoke` 生成内容。
- 页面会隐藏工作流中的过程性草稿，只展示主要产物。
- 关键词卡片会优先提取 `#标签` 和搜索关键词，过滤模型解释性文本。

如果后续要做生产级结构化展示，建议后端直接返回数组字段，例如：

```json
{
  "titles": ["标题 1", "标题 2"],
  "hashtags": ["#AI工具", "#小红书运营"],
  "search_keywords": ["AI 编程工具", "独立开发者"],
  "final_copy": "...",
  "cover_prompt": "..."
}
```

这样前端就不需要从模型长文本里做正则提取。

## 项目亮点

1. **多节点 Agent 工作流**：用 LangGraph 将内容生成拆成可维护、可观测的节点，而不是单次 Prompt 调用。
2. **服务化封装**：通过 FastAPI 提供 HTTP API，便于前端、自动化平台或其他 Agent 调用。
3. **轻量 Web 前端**：无需前端构建流程，直接通过 FastAPI 提供可用页面。
4. **输入适配**：同时支持普通文本和 OpenClaw 风格 JSON，为后续多 Agent 编排预留接口。
5. **Prompt 工程化管理**：将不同节点的 Prompt 统一放在 `prompts.py`，方便迭代和版本管理。
6. **Mock 调试模式**：不依赖真实 API Key 也能验证流程，适合演示、调试和测试。
7. **流式输出**：CLI 支持按节点查看中间结果，方便观察工作流执行过程。

## 当前限制

- 后端响应字段目前仍是字符串，前端需要做轻量清洗和提取。
- mock 模式只返回 Prompt 摘要，不代表真实生成质量。
- 当前没有提交自动化测试目录。
- 前端使用 CDN，离线环境或生产部署时建议改成本地构建资源。

## 后续计划

- 增加 `tests/`，覆盖输入适配、mock workflow、API health
- 增加内容质量评测样例，记录标题、标签、正文改写效果
- 增加更多平台内容模板，例如公众号、知乎、视频脚本
- 将 `/invoke` 响应升级为更明确的结构化 schema
- 将 `openclaw` 输入扩展为更明确的任务 schema
