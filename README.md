# CSQAQ Market Lookup

CS2 市场数据查询技能，使用 CSQAQ API 查询 CS2 饰品市场价格、交易数据等。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub release](https://img.shields.io/github/v/release/ephron-ren/csqaq-market-lookup)](https://github.com/ephron-ren/csqaq-market-lookup/releases)

## 简介

这是一个为 [OpenClaw](https://github.com/OpenClaw)/[Hermes Agent](https://github.com/NousResearch/hermes-agent) 设计的技能，允许 AI 助手通过 CSQAQ API 查询 CS2 市场数据。

## 功能特性

- 🔍 查询 CS2 饰品当前价格
- 📊 获取历史价格走势
- 💰 查看市场交易数据
- 📦 获取饰品详细信息
- 🔄 自动同步 API 文档
- 🛡️ 安全的 Token 管理

## 快速开始

### 1. 获取 API Token

#### 步骤详解

1. **访问 CSQAQ 官网**
   - 打开 https://csqaq.com/
   - 确保使用最新版本的浏览器

2. **注册/登录账号**
   - 如果没有账号，点击"注册"创建新账号
   - 如果已有账号，点击"登录"

3. **获取 API Token**
   - 登录后，进入"个人中心"或"账号设置"
   - 找到"API Token"或"API 密钥"选项
   - 点击"生成 Token"或"查看 Token"
   - 复制生成的 Token（格式类似：`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`）

4. **保存 Token**
   - 将 Token 保存在安全的地方
   - **不要**将 Token 提交到代码仓库或分享给他人

### 2. 设置环境变量

#### Linux/macOS

```bash
# 临时设置（当前终端有效）
export CSQAQ_API_TOKEN="<your_token>"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export CSQAQ_API_TOKEN="<your_token>"' >> ~/.bashrc
source ~/.bashrc
```

#### Windows

```powershell
# PowerShell（当前会话有效）
$env:CSQAQ_API_TOKEN="<your_token>"

# PowerShell（永久设置）
[Environment]::SetEnvironmentVariable("CSQAQ_API_TOKEN", "<your_token>", "User")

# CMD（当前会话有效）
set CSQAQ_API_TOKEN=<your_token>
```

### 3. 安装依赖

```bash
# 使用 pip 安装
pip install pyyaml

# 或者使用 requirements.txt
pip install -r requirements.txt
```

### 4. 同步 API 文档

```bash
python scripts/csqaq_api.py sync
```

首次运行会从 CSQAQ 文档站点拉取所有 API 文档，生成本地参考文件。

### 5. 查询数据

```bash
# 查看所有可用接口
python scripts/csqaq_api.py list

# 查询当前市场价格
python scripts/csqaq_api.py call --path /api/v1/current_data --method GET --query type=init --pretty

# 通过 operation ID 调用
python scripts/csqaq_api.py call --operation-id ______________api_v1_current_data_get --query type=init
```

## 使用方法

### 同步 API 文档

```bash
python scripts/csqaq_api.py sync
```

这会从 https://docs.csqaq.com/sitemap.xml 拉取所有 API 文档并保存到本地。

### 查看可用接口

```bash
python scripts/csqaq_api.py list --limit 200
```

输出示例：
```
Showing 50 of 150 endpoints:

  GET    /api/v1/current_data
         Summary: 获取当前市场数据
         OperationId: api_v1_current_data_get

  POST   /api/v1/user/login
         Summary: 用户登录
         OperationId: api_v1_user_login_post
```

### 调用 API

#### 通过 operation ID 调用

```bash
python scripts/csqaq_api.py call --operation-id ______________api_v1_current_data_get --query type=init
```

#### 通过路径和方法调用

```bash
python scripts/csqaq_api.py call --path /api/v1/current_data --method GET --query type=init
```

#### 如果 operationId 不唯一

```bash
python scripts/csqaq_api.py call --operation-id __good_____api_v1_info_good_get --doc-id 327138094
```

#### 传递请求参数

```bash
# 查询参数
python scripts/csqaq_api.py call --path /api/v1/search --method GET --query keyword=ak47 --query limit=10

# JSON 请求体
python scripts/csqaq_api.py call --path /api/v1/user/login --method POST --json-body '{"username": "test", "password": "xxx"}'

# 从文件读取请求体
python scripts/csqaq_api.py call --path /api/v1/user/login --method POST --body-file request.json
```

## 在 OpenClaw/Hermes Agent 中使用

### 安装技能

#### 方式一：使用 hermes skills install（推荐）

```bash
hermes skills install https://github.com/ephron-ren/csqaq-market-lookup
```

#### 方式二：手动克隆

```bash
# 克隆仓库到技能目录
git clone https://github.com/ephron-ren/csqaq-market-lookup.git ~/.openclaw/skills/csqaq-market-lookup

# 或者在 Hermes Agent 中
git clone https://github.com/ephron-ren/csqaq-market-lookup.git ~/.hermes/skills/csqaq-market-lookup
```

### 配置环境变量

```bash
export CSQAQ_API_TOKEN="<your_token>"
```

### 使用技能

在 OpenClaw/Hermes Agent 中，你可以这样使用：

```
使用 csqaq-market-lookup 技能查询 CS2 饰品价格
```

或者：

```
Use $csqaq-market-lookup to sync CSQAQ docs, list endpoints, and call the endpoint I ask for.
```

### 示例对话

```
用户: 帮我查一下 AK-47 | 二西莫夫的当前价格
AI: 我来帮你查询。首先让我同步 CSQAQ API 文档...
    [调用 sync 命令]
    现在查询 AK-47 | 二西莫夫的价格...
    [调用 call 命令]
    查询结果显示：AK-47 | 二西莫夫当前市场价格约为 ¥2,500 - ¥3,000。
```

## 工作流程

1. **同步文档** - 运行 `sync` 从 sitemap 拉取所有 API 文档
2. **查找接口** - 使用 `list` 查找目标接口的元数据
3. **调用接口** - 使用 `call` 调用接口
4. **处理响应** - 解析返回的 JSON 数据
5. **刷新数据** - 如果接口集合变化，重新运行 `sync`

## 文件结构

```
csqaq-market-lookup/
├── SKILL.md                    # 技能说明文档
├── README.md                   # 本文件
├── LICENSE                     # MIT 许可证
├── requirements.txt            # Python 依赖
├── scripts/
│   └── csqaq_api.py           # 统一 CLI 工具
├── references/
│   ├── endpoints.json          # 结构化接口目录
│   ├── endpoints.md            # 人类可读的接口列表
│   ├── merged_openapi.json     # 合并后的 OpenAPI 文档
│   └── sync_meta.json          # 同步元数据和诊断信息
└── .github/
    └── workflows/
        └── ci.yml              # GitHub Actions CI/CD
```

## 依赖

- Python 3.8+
- pyyaml

安装依赖：
```bash
pip install pyyaml
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 作者

- **ephron_ren** - [GitHub](https://github.com/ephron-ren)

## 相关链接

- [CSQAQ 官网](https://csqaq.com/)
- [CSQAQ API 文档](https://docs.csqaq.com/)
- [SkillHub 页面](https://skillhub.cn/skills/csqaq-market-lookup)
- [OpenClaw](https://github.com/OpenClaw)
- [Hermes Agent](https://github.com/NousResearch/hermes-agent)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.3 (2026-05-14)
- 初始 GitHub 发布
- 支持 CSQAQ API 文档同步
- 支持通过 operation ID 或路径调用 API
- 支持查询参数和请求体
- 添加 GitHub Actions CI/CD
- 添加详细文档和示例
