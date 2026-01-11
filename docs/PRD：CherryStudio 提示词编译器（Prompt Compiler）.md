---
author: Galen Dai
version: 1.1
title: PRD：CherryStudio 提示词编译器（Prompt Compiler）
description: 将本地 Markdown 格式的 LLM 提示词批量转换为 CherryStudio 兼容的 Remote JSON 格式，并支持一键同步至云端（GitHub Gist），实现跨设备访问与协作
category:
  - Product Requirement Document
tags: cherry-prompt-compiler
date_created: 2026-01-11
date_modified: 2026-01-11
---
## 1. 产品概述
开发一个自动化工具，将本地 Markdown 格式的 LLM 提示词批量转换为 CherryStudio 兼容的 Remote JSON 格式，并支持一键同步至云端（GitHub Gist），实现跨设备访问与协作。

---

## 1.1 设计理念（v1.1 更新）

本产品采用 Claude Code Agent Skills 最佳实践设计，确保插件的可发现性、可维护性和可扩展性：

### 核心设计原则

- **渐进式披露（Progressive Disclosure）**: 主技能文件（SKILL.md）保持简洁（< 500 行），详细规范独立为参考文档，按需加载
- **工作流驱动（Workflow-Driven）**: 提供清晰的步骤和验证清单，确保编译过程可追踪、可验证
- **语义智能（Semantic Intelligence）**: 利用 Claude 模型的语义理解能力，生成与描述内容高度相关的 emoji
- **评估驱动开发（Evaluation-Driven Development）**: 先建立评估场景和基准，再迭代优化技能内容

### 技术架构特点

| 特性 | 说明 |
|------|------|
| **零外部依赖** | 完全使用 Claude Code 内置工具（Read, Glob, Write, Bash），无需 Python 脚本 |
| **自然语言交互** | 用户可通过自然语言调整输出格式，无需修改代码 |
| **模块化设计** | 技能、命令、参考文档分离，便于维护和扩展 |
| **可验证性** | 每个编译步骤都有验证清单，确保数据完整性 |

---

## 2. 目标用户
- 使用 CherryStudio 管理多个 AI 助手提示词的产品经理、开发者或AI爱好者
- 需要在多设备间同步提示词配置的用户

## 3. 核心目标
- ✅ **标准化**：统一本地 Markdown 与 CherryStudio JSON 格式
- ✅ **自动化**：一键批量编译整个文件夹的提示词
- ✅ **可同步**：自动生成可在线访问的 Remote URL（通过 GitHub Gist）
- ✅ **零丢失**：完整保留原始提示词结构（含 YAML frontmatter）

---

## 4. 功能需求

| 功能模块 | 详细说明 |
|--------|--------|
| **文件解析** | 自动识别 `.md` 文件中的 YAML frontmatter（`description`, `category` 等）和正文内容 |
| **智能映射** | - `name` ← 文件名<br>- `description` ← YAML 中的 description<br>- `group` ← YAML 中的 `category`<br>- `prompt` ← 完整 Markdown 内容<br>- `id` ← 自动按序生成（1,2,3...）<br>- `emoji` ← 基于描述文本智能匹配 |
| **批量处理** | 支持指定文件夹内所有 `.md` 文件的一键编译 |
| **JSON 输出** | 生成符合 CherryStudio 规范的 JSON 数组格式 |
| **云端同步**（可选） | 通过 GitHub Token 自动上传至私有 Gist，返回 raw URL |
| **错误容错** | 单个文件解析失败不影响整体流程，记录错误日志 |

---

## 5. 输出格式规范（JSON Schema）

### 5.1 数据结构
输出为 **JSON 数组**，每个元素代表一个提示词助手配置。

### 5.2 JSON Schema 定义
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["id", "name", "description", "emoji", "group", "prompt"],
    "properties": {
      "id": {
        "type": "string",
        "description": "助手唯一标识符，按编译顺序从'1'开始递增"
      },
      "name": {
        "type": "string",
        "description": "助手名称，取自Markdown文件名（不含扩展名）"
      },
      "description": {
        "type": "string",
        "description": "助手简要描述，取自YAML frontmatter中的description字段"
      },
      "emoji": {
        "type": "string",
        "description": "与描述语义相关的emoji符号，由系统自动生成"
      },
      "group": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "分类标签数组，取自YAML frontmatter中的category字段；若为空则默认为['General']"
      },
      "prompt": {
        "type": "string",
        "description": "完整的提示词内容，包含原始YAML frontmatter和Markdown正文"
      }
    },
    "additionalProperties": false
  }
}
```

### 5.3 输出示例
```json
[
  {
    "id": "1",
    "name": "互联网产品经理",
    "description": "PM Copilot，专注于协助移动、互联网和软件产品（特别是SaaS）的产品经理完成日常工作，涵盖战略、需求、执行与沟通。",
    "emoji": "👨‍💼",
    "group": ["Template"],
    "prompt": "---\nauthor: Galen Dai\nversion: 2.0\ndescription: PM Copilot，专注于协助移动、互联网和软件产品（特别是SaaS）的产品经理完成日常工作，涵盖战略、需求、执行与沟通。\nlanguage: zh-CN\nsource:\ncategory:\n  - Template\ntags:\n  - AI\n  - Prompt\n---\n## Goals\n1.  **战略辅助**: 提供市场分析、竞品调研、SWOT分析及价值主张设计。\n..."
  }
]
```

---

## 6. 非功能需求
- **易用性**：命令行工具，配置简单（仅需指定文件夹路径）
- **安全性**：Gist 默认设为私有，保护提示词隐私
- **可维护性**：模块化代码结构，便于扩展新字段或存储后端
- **兼容性**：支持 UTF-8 编码，适配中英文提示词

---

## 7. 成功指标（KPIs）
- 编译成功率 ≥ 95%
- 单次处理 10+ 文件耗时 < 5 秒
- 生成的 JSON 100% 被 CherryStudio 正确加载

---

## 8. MVP 范围（第一版）
- [ ] 本地 Markdown → JSON 编译
- [ ] 智能 Emoji 生成
- [ ] 批量文件夹处理
- [ ] GitHub Gist 自动上传（可后续迭代）

> **备注**：Gist 同步功能依赖用户自行提供 GitHub Token，非强制依赖。

---

## 9. 后续迭代方向
- 支持腾讯云 COS / 其他云存储后端
- 增加 GUI 界面（Electron/Streamlit）
- 支持增量更新（仅编译修改过的文件）
- 提供 Webhook 自动触发编译