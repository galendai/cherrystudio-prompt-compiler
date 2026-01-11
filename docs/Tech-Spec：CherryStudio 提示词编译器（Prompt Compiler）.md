---
author: Galen Dai
version: 1.1
title: 技术规范：CherryStudio 提示词编译器（Prompt Compiler）- 基于 Claude Skills Best Practices
description: 使用 Claude Code 内置模型能力，将本地 Markdown 格式的 LLM 提示词批量转换为 CherryStudio 兼容的 Remote JSON 格式，无需外部脚本依赖
category:
  - Tech Spec
tag: cherry-tag-compiler
date_created: 2026-01-11
date_modified: 2026-01-11
---

# CherryStudio 提示词编译器 - Claude Code Skill 技术规范

> **方案版本**: 1.1 - 基于 Claude Skills Best Practices（渐进式披露、评估驱动开发）
> **官方文档**: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
---

## 1. 项目概述

### 1.1 目标
创建一个 Claude Code 插件，**完全使用 Claude Code 内置模型能力**，将本地 Markdown 格式的 LLM 提示词批量转换为 CherryStudio 兼容的 Remote JSON 格式，并支持一键同步至 GitHub Gist。

- **零外部依赖**：无需 Python 脚本，仅使用 Claude Code 内置工具（Read、Glob、Write、Bash）
- **智能语义理解**：利用 Claude 模型的语义理解能力生成更准确的 emoji
- **自然语言交互**：用户可通过自然语言调整输出格式

### 1.3 核心功能
- 解析 Markdown 文件中的 YAML frontmatter
- 智能映射字段到 CherryStudio JSON 格式
- 批量处理整个文件夹
- **智能生成**语义相关的 emoji（基于 Claude 语义理解）
- 可选的 GitHub Gist 同步（使用 curl）

---

## 2. Skill 目录结构（简化版）

> **v1.1 更新**：仅使用 Skills，无需插件或命令结构

根据 [Claude Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)，Skills 可以独立存在，Claude Code 会自动发现和加载。

```
cherry-prompt-compiler/
└── skills/
    └── compiling-prompts/       # v1.1: 使用动名词形式
        ├── SKILL.md             # 主技能文件（< 500 行，渐进式披露）
        ├── reference/           # v1.1: 参考文档目录（按需加载）
        │   ├── cherry-studio-schema.md   # JSON Schema 详细规范
        │   ├── field-mapping.md          # 字段映射规则
        │   ├── emoji-generation.md       # Emoji 生成策略
        │   └── error-handling.md         # 错误处理指南
        └── examples/           # 示例文件
            ├── basic-prompt.md          # 基础提示词示例
            ├── advanced-prompt.md       # 高级提示词示例（含复杂 YAML）
            └── example-output.json      # 期望输出示例
```

**v1.1 架构改进：**

| 变更项 | v2.0 | v1.1 |
|--------|------|------|
| 技能目录名 | `prompt-compiler/` | `compiling-prompts/` (动名词形式) |
| 技能名称 | `prompt-compiler` | `compiling-prompts` |
| 参考文档目录 | `references/` | `reference/` |
| 参考文档数量 | 1 个 | 4 个（拆分为独立主题） |
| SKILL.md 行数 | ~525 行 | < 500 行（渐进式披露） |
| 插件结构 | 需要 `.claude-plugin/` 和 `commands/` | **不需要**，Skill 独立运行 |

---

## 3. 核心文件设计

### 3.1 SKILL.md（核心解析逻辑）

> **v1.1 更新**：采用渐进式披露设计，保持 < 500 行

```markdown
---
name: compiling-prompts
description: Compile local Markdown LLM prompts to CherryStudio-compatible Remote JSON format with batch processing support. Use when user wants to convert prompts, batch process Markdown files, prepare prompts for CherryStudio import, or mentions CherryStudio, prompt compilation, or JSON conversion. Supports semantic emoji matching and optional GitHub Gist sync.
version: 1.1.0
author: Galen Dai
---

# CherryStudio Prompt Compiler Skill

## Overview

This skill compiles local Markdown-formatted LLM prompts into CherryStudio-compatible Remote JSON format using Claude Code's native model capabilities.

## When to Use

Activate this skill when:
- User wants to compile Markdown prompts to JSON format
- User needs to batch process an entire folder of prompt files
- User asks about CherryStudio prompt format requirements
- User wants to sync prompts to GitHub Gist

## Compilation Process

### Step 1: Scan for Markdown Files

Use the `Glob` tool to find all `.md` files in the target directory:

```
Glob: **/*.md in the specified path
```

### Step 2: Read and Parse Each File

Use the `Read` tool to read each Markdown file. Extract:

1. **YAML Frontmatter** (between `---` markers):
   - `description`: Assistant description
   - `category`: Group classification (default: `["General"]`)
   - Other metadata (author, version, tags, etc.)

2. **Full Content**: Include the complete Markdown content (frontmatter + body)

### Step 3: Field Mapping

Map extracted data to CherryStudio JSON format:

| CherryStudio Field | Source | Notes |
|-------------------|--------|-------|
| `id` | Auto-generated | Sequential numbers: "1", "2", "3"... |
| `name` | Filename | Without `.md` extension |
| `description` | YAML `description` | Fallback to empty string if missing |
| `emoji` | **AI-generated** | Use semantic understanding of description to pick relevant emoji |
| `group` | YAML `category` | Convert to array if string; default to `["General"]` |
| `prompt` | Full content | Include YAML frontmatter + Markdown body |

### Step 4: Generate JSON Array

Output a JSON array with all compiled prompts:

```json
[
  {
    "id": "1",
    "name": "example-prompt",
    "description": "A helpful AI assistant",
    "emoji": "🤖",
    "group": ["Template"],
    "prompt": "---\nauthor: ...\n---\n\n# Content here"
  }
]
```

### Step 5: Write Output File

Use the `Write` tool to save the result as `cherry-studio-prompts.json`.

## Emoji Generation Guidelines

Use semantic understanding to match emojis to descriptions:

| Description Pattern | Emoji |
|-------------------|-------|
| Product manager, PM, business | 👨‍💼 |
| Developer, engineer, coding | 👨‍💻 |
| Writer, content, copy | ✍️ |
| Designer, creative, art | 🎨 |
| Analytics, data, metrics | 📊 |
| Assistant, helper, copilot | 🤖 |
| Chat, support, communication | 💬 |
| General/default | 🔧 |

## Error Handling

- **Missing YAML frontmatter**: Use defaults (empty description, `["General"]` group)
- **Malformed YAML**: Log warning, skip file with error message
- **Empty description**: Use generic emoji based on filename or content
- **File read errors**: Report specific file and continue with remaining files

## Output Schema (CherryStudio)

Each compiled prompt must follow this structure:

```json
{
  "id": "string",      // Required: Sequential number
  "name": "string",    // Required: Filename without extension
  "description": "string",  // Required: From YAML or empty
  "emoji": "string",   // Required: Single emoji character
  "group": ["string"], // Required: Array of category strings
  "prompt": "string"   // Required: Full Markdown content
}
```

## Example Workflow

```
User: /compile ./prompts/

1. Glob: ./prompts/**/*.md → [file1.md, file2.md, ...]
2. Read: file1.md → Extract metadata + content
3. Generate: JSON object with fields mapped
4. Repeat for all files
5. Write: cherry-studio-prompts.json
6. Report: "Compiled X prompts successfully to cherry-studio-prompts.json"
```

## Next Steps for User

After compilation:
- Review the generated JSON file
- Use `/sync-gist` to upload to GitHub Gist (optional)
- Import the JSON or Gist URL into CherryStudio
```

### 3.2 reference/ 目录（v1.1 新增）

> **渐进式披露设计**：详细规范拆分为独立参考文档，按需加载

| 文件 | 用途 |
|------|------|
| `cherry-studio-schema.md` | 完整的 JSON Schema 规范 |
| `field-mapping.md` | 详细的字段映射逻辑和边界情况处理 |
| `emoji-generation.md` | 高级 Emoji 匹配策略和扩展规则 |
| `error-handling.md` | 错误类型、恢复策略和日志记录 |

### 3.3 examples/ 目录（v1.1 新增）

> **示例文件**：提供参考示例和预期输出

| 文件 | 用途 |
|------|------|
| `basic-prompt.md` | 基础提示词示例 |
| `advanced-prompt.md` | 高级提示词示例（含复杂 YAML） |
| `example-output.json` | 期望输出示例 |

---

## 4. 字段映射规则

| CherryStudio 字段 | 来源 | 处理方式 |
|-------------------|------|----------|
| id | 自动生成 | 按编译顺序从 '1' 开始递增 |
| name | 文件名 | 文件名不含 `.md` 扩展名 |
| description | YAML frontmatter | `description` 字段，缺失则为空字符串 |
| emoji | **AI 生成** | 基于 description 语义智能匹配 |
| group | YAML frontmatter | `category` 字段，字符串转数组，默认 `['General']` |
| prompt | 完整内容 | 包含 YAML frontmatter + Markdown 正文 |

---

## 5. Emoji 生成规则（基于语义理解）

| 描述语义 | Emoji |
|---------|-------|
| Product manager, PM, business, strategy | 👨‍💼 |
| Developer, engineer, coding, programming | 👨‍💻 |
| Writer, content, copy, writing | ✍️ |
| Designer, creative, art, UI/UX | 🎨 |
| Analytics, data, metrics, analysis | 📊 |
| Assistant, helper, copilot, aid | 🤖 |
| Chat, support, communication | 💬 |
| Teacher, education, learning | 📚 |
| Finance, money, trading | 💰 |
| Science, research, lab | 🔬 |
| Default fallback | 🔧 |

---

## 6. MCP GitHub 工具配置（可选）

### .mcp.json

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

---

## 7. 输出示例

### 输入 (example-prompt.md)

```markdown
---
author: Galen Dai
version: 2.0
description: PM Copilot，专注于协助移动、互联网和软件产品（特别是SaaS）的产品经理完成日常工作，涵盖战略、需求、执行与沟通。
category:
  - Template
tags:
  - AI
  - Prompt
---

# 互联网产品经理助手

## Role

你是一位经验丰富的互联网产品经理，专注于移动应用、SaaS产品和软件产品的全生命周期管理。

## Goals

1. **战略辅助**: 提供市场分析、竞品调研、SWOT分析及价值主张设计
2. **需求管理**: 协助编写PRD、用户故事、验收标准
3. **执行支持**: 协助项目排期、优先级排序、跨部门沟通
```

### 输出 (cherry-studio-prompts.json)

```json
[
  {
    "id": "1",
    "name": "example-prompt",
    "description": "PM Copilot，专注于协助移动、互联网和软件产品（特别是SaaS）的产品经理完成日常工作，涵盖战略、需求、执行与沟通。",
    "emoji": "👨‍💼",
    "group": ["Template"],
    "prompt": "---\nauthor: Galen Dai\nversion: 2.0\ndescription: PM Copilot，专注于协助移动、互联网和软件产品（特别是SaaS）的产品经理完成日常工作，涵盖战略、需求、执行与沟通。\ncategory:\n  - Template\ntags:\n  - AI\n  - Prompt\n---\n\n# 互联网产品经理助手\n\n## Role\n\n你是一位经验丰富的互联网产品经理，专注于移动应用、SaaS产品和软件产品的全生命周期管理。\n\n## Goals\n\n1. **战略辅助**: 提供市场分析、竞品调研、SWOT分析及价值主张设计\n2. **需求管理**: 协助编写PRD、用户故事、验收标准\n3. **执行支持**: 协助项目排期、优先级排序、跨部门沟通"
  }
]
```

---

## 8. 实施计划（v1.1 更新）

> **评估驱动开发（Evaluation-Driven Development）**：遵循 Claude Skills Best Practices

### Phase 1: 评估驱动开发

> **目标**：先建立评估场景和基准，再编写 Skill 内容

**任务清单：**
- [ ] 创建 3 个代表性评估场景
  - 场景 1：编译单个简单提示词文件
  - 场景 2：批量处理多个文件（包含缺失 YAML frontmatter 的情况）
  - 场景 3：处理复杂 YAML 字段（多分类、多标签）
- [ ] 建立 baseline（无 Skill 时的表现）
- [ ] 定义成功标准
  - 编译成功率 ≥ 95%
  - Emoji 语义匹配准确率 > 90%
  - JSON 100% 符合 CherryStudio Schema

### Phase 2: 核心实现

**任务清单：**
- [ ] 创建 Skill 目录结构（符合 v1.1 规范）
  - `skills/compiling-prompts/SKILL.md` (< 500 行)
  - `skills/compiling-prompts/reference/` 目录
  - `skills/compiling-prompts/examples/` 目录
- [ ] 编写核心 `SKILL.md`
  - YAML frontmatter（符合最佳实践）
  - 快速入门章节
  - 工作流步骤（含验证清单）
  - 参考文档链接（单层深度）
- [ ] 创建参考文档（渐进式披露）
  - `cherry-studio-schema.md`
  - `field-mapping.md`
  - `emoji-generation.md`
  - `error-handling.md`
- [ ] 创建示例文件
  - `basic-prompt.md`
  - `advanced-prompt.md`
  - `example-output.json`

### Phase 3: 迭代优化

> **核心方法**：Claude A（专家） + Claude B（测试者）的迭代循环

**任务清单：**
- [ ] 用 Claude B 测试真实场景
  - 观察技能是否能正确触发
  - 记录错误选择或失败场景
  - 收集具体问题案例
- [ ] 用 Claude A 优化 Skill
  - 根据观察到的问题调整描述
  - 优化触发条件（description 字段）
  - 改进工作流步骤的清晰度
- [ ] 重复测试-优化循环
  - 直到 Claude B 在所有评估场景中表现稳定

### Phase 4: 文档与验证

**任务清单：**
- [ ] 编写 `README.md`
  - 快速开始指南
  - 安装说明
  - 使用示例
- [ ] 运行完整评估
  - 测试 Haiku、Sonnet、Opus 三个模型
  - 验证所有最佳实践检查项
- [ ] 团队反馈收集
  - 分享给团队成员试用
  - 收集使用场景和问题
  - 最后迭代优化

### 最佳实践检查清单

**核心质量：**
- [ ] Description 使用第三人称，包含触发关键词
- [ ] SKILL.md < 500 行
- [ ] 参考文档单层引用（无嵌套）
- [ ] 工作流包含验证清单
- [ ] 使用一致的术语

**内容组织：**
- [ ] 快速入门在前
- [ ] 渐进式披露（主文档 + 参考文档）
- [ ] 具体示例（非抽象）
- [ ] 避免 Windows 风格路径（使用 `/`）

**测试验证：**
- [ ] 创建至少 3 个评估场景
- [ ] 测试 Haiku、Sonnet、Opus 模型
- [ ] 真实使用场景测试

---

## 9. 关键文件清单（v1.1 更新）

| 文件路径 | 用途 | 优先级 |
|----------|------|--------|
| `skills/compiling-prompts/SKILL.md` | **核心技能定义（渐进式披露）** | 🔴 高 |
| `skills/compiling-prompts/reference/cherry-studio-schema.md` | JSON Schema 规范 | 🟡 中 |
| `skills/compiling-prompts/reference/field-mapping.md` | 字段映射规则 | 🟡 中 |
| `skills/compiling-prompts/reference/emoji-generation.md` | Emoji 生成策略 | 🟡 中 |
| `skills/compiling-prompts/reference/error-handling.md` | 错误处理指南 | 🟡 中 |
| `skills/compiling-prompts/examples/basic-prompt.md` | 基础输入示例 | 🟢 低 |
| `skills/compiling-prompts/examples/advanced-prompt.md` | 高级输入示例 | 🟢 低 |
| `skills/compiling-prompts/examples/example-output.json` | 输出示例 | 🟢 低 |
| `README.md` | 用户文档 | 🟡 中 |

---

## 10. 技术优势

| 维度 | 纯模型能力方案 | 原脚本方案 |
|------|---------------|-----------|
| **代码维护** | 极简（仅 Markdown 文件） | 需维护 Python 脚本 |
| **外部依赖** | 无 | python-frontmatter, requests 等 |
| **Emoji 质量** | 语义理解，更准确 | 简单关键词匹配 |
| **灵活性** | 自然语言交互即可调整 | 需修改代码重跑 |
| **执行成本** | 消耗 token | 免费 |
| **适用场景** | 中小批量、频繁调整 | 大批量、固定流程 |

---

## 11. 成功指标

- 编译成功率 ≥ 95%
- 单次处理 10+ 文件响应时间 < 30 秒
- 生成的 JSON 100% 符合 CherryStudio Schema
- Emoji 匹配准确率 > 90%（基于语义理解）
