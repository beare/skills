# Skills（技能）
Skills 是包含指令、脚本和资源的文件夹，Claude 可以动态加载这些内容以提高在专业任务上的表现。Skills 教会 Claude 如何以可重复的方式完成特定任务，无论是使用公司品牌指南创建文档、使用组织的特定工作流程分析数据，还是自动化个人任务。

更多信息，请查看：
- [什么是 skills？](https://support.claude.com/en/articles/12512176-what-are-skills)
- [在 Claude 中使用 skills](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [如何创建自定义 skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [使用 Agent Skills 为现实世界装备智能体](https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

# Skill Sets（技能集）
- [./skills](./skills): 创意与设计、开发与技术、企业与通信以及文档技能的示例
- [./spec](./spec): Agent Skills 规范
- [./template](./template): 技能模板

# 在 Claude Code 和 Vercel Skills CLI 中使用

## Claude Code
您可以通过在 Claude Code 中运行以下命令将此仓库注册为 Claude Code 插件市场：
```
/plugin marketplace add anthropics/skills
```

然后，安装特定的技能集：
1. 选择 `Browse and install plugins`
2. 选择 `anthropic-agent-skills`
3. 选择 `document-skills` 或 `example-skills`
4. 选择 `Install now`

或者，直接通过以下方式安装插件：
```
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
```

安装插件后，您只需提及技能即可使用它。例如，如果您从市场安装了 `document-skills` 插件，您可以要求 Claude Code 执行类似操作："使用 PDF 技能从 `path/to/some-file.pdf` 中提取表单字段"

## Vercel Skills CLI

您也可以使用 [Vercel Skills CLI](https://github.com/vercel-labs/skills) 来管理和使用技能。这是一个方便的命令行工具，可以快速添加技能到您的项目中。

### 安装和使用

从 GitHub 仓库添加技能：
```bash
npx skills add anthropics/skills --skill docx
npx skills add anthropics/skills --skill pdf
npx skills add anthropics/skills --skill pptx
npx skills add anthropics/skills --skill xlsx
```

从本地路径添加技能：
```bash
npx skills add ./skills/docx
```

列出已安装的技能：
```bash
npx skills list
```

删除技能：
```bash
npx skills remove docx
```

更多使用方法，请访问 [Vercel Skills CLI 仓库](https://github.com/vercel-labs/skills)。

# 创建基本技能

创建技能很简单 - 只需一个包含 YAML 前置元数据和指令的 `SKILL.md` 文件的文件夹。您可以使用本仓库中的 **template-skill** 作为起点：

```markdown
---
name: my-skill-name
description: 清晰描述此技能的功能以及何时使用它
---

# My Skill Name

[在此添加 Claude 在此技能激活时将遵循的指令]

## Examples
- 示例用法 1
- 示例用法 2

## Guidelines
- 指南 1
- 指南 2
```

前置元数据只需要两个字段：
- `name` - 技能的唯一标识符（小写，空格用连字符）
- `description` - 技能功能和使用时机的完整描述

下面的 markdown 内容包含 Claude 将遵循的指令、示例和指南。更多详情，请参阅 [如何创建自定义 skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)。

