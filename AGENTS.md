# FlexPilot —— CMES 项目的 AI 辅助开发环境

FlexPilot 是 CMES 制造执行系统（基于某 Low-code platform）的 AI 辅助开发环境，业务源码托管在 Low-code platform 服务器上，本地主要维护 AI 工具规范与知识库。

## 项目知识库（所有 AI 工具必读）

**`wiki/`** 目录是完整的项目知识库（40 篇文档），任何开发任务前先按需查阅：

- 整体认识：`wiki/项目概述.md`、`wiki/技术栈与依赖.md`、`wiki/目录结构详解.md`
- 开发规范：`wiki/技能规范体系/`（基础规范层 → 架构规范层 → 业务规范层）
- API 参考：`wiki/API参考文档/`（公共资源管理、接口管理、认证授权、错误码）
- 排障：`wiki/故障排除与FAQ.md`
- 完整索引见 `wiki/README.md`

知识库由 Qoder 生成，源文件在 `.qoder/repowiki/zh/content/`（`.qoder/repowiki/zh/meta/` 为 Qoder 内部元数据，勿动）。**请勿直接编辑 `wiki/` 下的文档**；源文档更新后运行同步：

```bash
node scripts/sync-repowiki.js          # 同步 .qoder/repowiki → wiki/
node scripts/sync-repowiki.js --dry-run  # 预览
```

## 目录说明

- `wiki/` — 项目知识库（同步产物，见上）
- `scripts/sync-repowiki.js` — repowiki 同步脚本
- `scripts/sync-skills.js` — skills 规范同步脚本（`.opencode/skills/` → `.qoder/skills/`）
- `.opencode/skills/` — AI skills 规范的**权威来源**（foundation / architecture / business 三层），修改规范请改这里再同步
- `.kimi-code/skills/flexpilot/` — Low-code platform 服务器文件上传/下载/执行工具（Kimi Code 用）
- `.codex/`、`.opencode/`、`.qoder/`、`.kimi-code/` — 各 AI 工具的配置目录

## 业务系统速览

CMES 基于 Low-code platform，采用 BZC（Groovy 业务组件）+ Domain（JSON 领域模型）双轨架构，核心域：

- **公共资源管理**：物理建模（企业→工厂→园区→厂区→车间→工段→生产线，七级层级带删除引用校验）、人员管理、工艺建模
- **接口管理**：应用令牌、接口配置、接口日志

业务文件（`bzc/`、`Domain/`、微流 `.mf.json`）通过 `.kimi-code/skills/flexpilot/` 的工具与服务器同步，本地文件放在 `src/` 下。
