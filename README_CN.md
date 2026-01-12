[English](./README.md)

# CherryStudio 提示词编译器 (Prompt Compiler)

> 一个用于将本地 Markdown LLM 提示词编译为 CherryStudio 兼容的远程 JSON 格式的 Claude Code 技能。

## 概览

CherryStudio 提示词编译器是一个零依赖工具，可将本地 Markdown 格式的 LLM 提示词转换为 [CherryStudio](https://github.com/CherryHQ/cherry-studio) 所需的 JSON 格式。它利用 Claude Code 的原生模型能力来智能解析 YAML frontmatter，生成语义化的表情符号，并批量处理整个文件夹的提示词文件。

## 特性

- **零外部依赖**：仅使用 Claude Code 内置工具（Read, Glob, Write, Bash）
- **智能表情符号生成**：利用 Claude 的语义理解能力，根据提示词描述匹配表情符号
- **批量处理**：一次性处理整个文件夹的 Markdown 文件
- **完整内容保留**：保留 YAML frontmatter 和所有 Markdown 格式
- **容错性**：即使个别文件有问题，也能继续处理

## 安装

### 前置条件

- 已安装 [Claude Code](https://claude.ai/code)
- 一个包含 Markdown 提示词文件的项目文件夹

### 设置

1. 克隆或复制此仓库到本地机器
2. 确保技能目录结构已就绪：

```
cherrystudio-prompt-compiler/
└── skills/
    └── compiling-prompts/
        ├── SKILL.md
        ├── reference/
        └── examples/
```

3. Claude Code 将自动发现此技能

## 快速开始

### 基本用法

只需告诉 Claude Code 编译你的提示词：

```
Compile all prompts in ./prompts/ folder
```

或使用技能触发器：

```
/compiling-prompts ./my-prompts/
```

### 输入格式

你的 Markdown 文件应包含 YAML frontmatter：

```markdown
---
author: Your Name
version: 1.0
description: A helpful assistant for coding tasks
category:
  - Development
tags:
  - coding
  - programming
---

# Code Assistant

You are a helpful coding assistant...
```

### 输出

编译器生成 `cherry-studio-prompts.json`：

```json
[
  {
    "id": "1",
    "name": "code-assistant",
    "description": "A helpful assistant for coding tasks",
    "emoji": "👨‍💻",
    "group": ["Development"],
    "prompt": "---\nauthor: ...\n---\n\n# Code Assistant\n..."
  }
]
```

## 字段映射

| CherryStudio 字段 | 来源 | 备注 |
|-------------------|--------|-------|
| `id` | 自动生成 | 顺序编号: "1", "2", "3"... |
| `name` | 文件名 | 不带 `.md` 扩展名 |
| `description` | YAML `description` | 如果缺失则为空字符串 |
| `emoji` | AI 生成 | 语义匹配 |
| `group` | YAML `category` | 如果缺失则为 `["General"]` |
| `prompt` | 完整内容 | YAML + Markdown 正文 |

## 使用示例

### 编译单个文件夹

```
Compile prompts in ./my-prompts/
```

### 指定输出位置

```
Compile prompts in ./prompts/ and save to ./output/prompts.json
```

### 优雅地处理错误

即使某些文件有问题，编译器也会继续处理：

```
Compilation complete with warnings:
- missing-yaml.md: No frontmatter found, using defaults
Successfully compiled: 5 files
Output: cherry-studio-prompts.json
```

## 表情符号生成

编译器使用语义理解根据你的提示词描述匹配表情符号：

| 描述关键词 | 表情符号 |
|---------------------|-------|
| Product manager, PM, business | 👨‍💼 |
| Developer, engineer, coding | 👨‍💻 |
| Writer, content, writing | ✍️ |
| Designer, creative, art | 🎨 |
| Analytics, data, metrics | 📊 |
| Assistant, helper, copilot | 🤖 |
| Chat, support, communication | 💬 |
| Teacher, education, learning | 📚 |

## 目录结构

```
skills/compiling-prompts/
├── SKILL.md                    # 主要技能文件
├── reference/                  # 详细文档
│   ├── cherry-studio-schema.md # JSON Schema 规范
│   ├── field-mapping.md        # 字段映射规则
│   ├── emoji-generation.md     # 表情符号生成策略
│   └── error-handling.md       # 错误处理指南
└── examples/                   # 示例文件
    ├── basic-prompt.md         # 简单提示词示例
    ├── advanced-prompt.md      # 复杂提示词示例
    └── example-output.json     # 预期输出格式
```

## 导入 CherryStudio

1. 运行编译器生成 `cherry-studio-prompts.json`
2. 打开 CherryStudio
3. 转到 设置 → 提示词
4. 点击 "导入" 并选择 JSON 文件
5. 你的提示词将在 CherryStudio 中可用

## 高级用法

### 自定义分类处理

如果你的提示词使用非标准分类格式：

```yaml
# 字符串格式（将被转换为数组）
category: Template

# 数组格式（保持原样）
category:
  - Template
  - Product
```

### 处理缺失元数据

没有 YAML frontmatter 的文件将使用合理的默认值：
- `description`: 空字符串
- `group`: `["General"]`
- `emoji`: 基于文件名或内容分析

## 故障排除

**问题**: 未找到 Markdown 文件
- **解决方案**: 验证目录路径是否包含 `.md` 文件

**问题**: 部分提示词缺少表情符号
- **解决方案**: 在 YAML frontmatter 中添加 `description` 字段

**问题**: 分类未被识别
- **解决方案**: 确保 YAML frontmatter 中存在 `category` 字段

**问题**: JSON 输出为空
- **解决方案**: 检查源文件是否为有效的 Markdown 且包含内容

## 技术规范

有关详细技术信息，请参阅：
- [产品需求文档](docs/PRD：CherryStudio%20提示词编译器（Prompt%20Compiler）.md)
- [技术规范](docs/Tech-Spec：CherryStudio%20提示词编译器（Prompt%20Compiler）.md)

## 贡献

欢迎贡献！请随时提交 issues 或 pull requests。

## 许可证

MIT License - 详情请参阅 LICENSE 文件

## 作者

由 Galen Dai 创建

## 版本

1.1.0
