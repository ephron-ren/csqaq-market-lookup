---
name: csqaq-market-lookup
description: "CS2市场数据查询 - 使用 CSQAQ API 查询 CS2 饰品市场价格、交易数据等"
version: 1.0.3
author: ephron_ren
tags: [cs2, market, gaming, api, data-query]
requires:
  python: ">=3.8"
  env:
    - CSQAQ_API_TOKEN
---

# CSQAQ Market Lookup

CS2 市场数据查询技能，使用 CSQAQ API 查询 CS2 饰品市场价格、交易数据等。

## 概述

该技能允许你通过 CSQAQ API 查询 CS2 市场数据，包括：
- 饰品当前价格
- 历史价格走势
- 市场交易数据
- 饰品详细信息

## 配置

### 获取 API Token

1. 访问 https://csqaq.com/
2. 登录你的账号
3. 在账号设置中找到 API Token 管理页面
4. 复制你的 `ApiToken`

### 设置环境变量

```bash
# Linux/macOS
export CSQAQ_API_TOKEN="<your_token>"

# Windows PowerShell
$env:CSQAQ_API_TOKEN="<your_token>"
```

## 使用方法

### 同步 API 文档

首次使用前，需要同步 CSQAQ 的 API 文档：

```bash
python scripts/csqaq_api.py sync
```

### 查看可用接口

```bash
python scripts/csqaq_api.py list --limit 200
```

### 调用 API

通过 operation ID 调用：
```bash
python scripts/csqaq_api.py call --operation-id ______________api_v1_current_data_get --query type=init
```

通过路径和方法调用：
```bash
python scripts/csqaq_api.py call --path /api/v1/current_data --method GET --query type=init
```

如果 operationId 不唯一，添加 `--doc-id`：
```bash
python scripts/csqaq_api.py call --operation-id __good_____api_v1_info_good_get --doc-id 327138094
```

## 工作流程

1. 运行 `sync` 从 https://docs.csqaq.com/sitemap.xml 拉取所有 API 文档
2. 使用 `list` 查找目标接口的元数据（path, method, operationId, tags, summary）
3. 使用 `call` 调用接口，支持 `--operation-id` 或 `--path` + `--method` 两种方式
4. 对于写入操作，使用 `--json-body`、`--body-file` 或 `--raw-body` 传递请求体
5. 如果接口集合变化，重新运行 `sync` 刷新本地数据

## 文件结构

- `SKILL.md` - 本文件，技能说明文档
- `scripts/csqaq_api.py` - 统一 CLI 工具
- `references/endpoints.json` - 结构化接口目录
- `references/endpoints.md` - 人类可读的接口列表
- `references/merged_openapi.json` - 合并后的 OpenAPI 文档
- `references/sync_meta.json` - 同步元数据和诊断信息

## 依赖

- Python 3.8+
- pyyaml

安装依赖：
```bash
pip install pyyaml
```

## 示例

### 查询当前市场价格

```bash
# 同步文档
python scripts/csqaq_api.py sync

# 查看所有接口
python scripts/csqaq_api.py list

# 调用特定接口
python scripts/csqaq_api.py call --path /api/v1/current_data --method GET --query type=init --pretty
```

## 注意事项

- API Token 是敏感信息，请勿泄露或提交到代码仓库
- 默认 Token 来源：环境变量 `CSQAQ_API_TOKEN`
- 如果遇到问题，请检查 Token 是否正确设置

## 许可证

MIT License

## 作者

ephron_ren

## 链接

- CSQAQ 官网: https://csqaq.com/
- API 文档: https://docs.csqaq.com/
- SkillHub: https://skillhub.cn/skills/csqaq-market-lookup
