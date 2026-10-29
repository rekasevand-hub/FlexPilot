# FlexPilot

> AI-assisted development environment for a low-code MES platform — layered skill specs, server-side code sync & execution, and a shared project knowledge base, usable across multiple AI coding tools.

**FlexPilot** 是一个面向低代码 MES（制造执行系统）平台的 AI 辅助开发环境。它解决的核心问题是：业务代码托管在低代码平台服务器上（Groovy 业务组件、JSON 领域模型、微流），本地没有完整源码，AI 编程工具"看不懂平台、够不着服务器"。FlexPilot 通过三件事补齐这条链路：

1. **分层技能规范（Skills）** —— 把平台开发规范、架构约定、业务规则结构化地喂给 AI，保证生成代码风格统一、符合业务约束
2. **服务器工具链（flexpilot skill）** —— 让 AI 直接对服务器上的代码文件和微流做上传、下载、执行，形成"改代码 → 上传 → 运行验证"的闭环
3. **项目知识库（wiki/）** —— 40 篇结构化的项目文档（架构、API、规范、FAQ），所有 AI 工具共享

## 特性

- **多 AI 工具复用**：同一套规范与知识库同时服务于 Kimi Code、Codex、Opencode、Qoder，通过同步脚本保持一致
- **微流（Microflow）支持**：`.mf.json` 自定义扩展名标识微流资源，支持下载完整定义、带参数执行、覆盖式上传
- **知识库自动同步 + 脱敏**：`sync-repowiki.js` 从 Qoder repowiki 同步文档到 `wiki/`，内置脱敏映射，防止平台标识符回灌
- **凭证安全**：服务器凭证通过 `flexpilot-accounts.json` 配置，多层 `.gitignore` 保证不会入库；支持项目级 / 用户级多级查找
- **零依赖**：工具脚本仅使用 Python 标准库，同步脚本仅使用 Node.js 标准库

## 仓库结构

```
├── AGENTS.md                  # 所有 AI 工具的入口指引（自动被读取）
├── wiki/                      # 项目知识库（40 篇文档，同步产物 + 自动索引）
├── scripts/
│   ├── sync-skills.js         # skills 规范同步：.opencode/skills → .qoder/skills
│   ├── sync-repowiki.js       # 知识库同步：.qoder/repowiki → wiki/（内置脱敏）
│   └── fix-python-path.ps1    # Windows PATH 修复参考脚本
├── .opencode/skills/          # skills 规范权威来源
│   ├── foundation/            #   基础规范（代码标准、日志、错误处理、版本控制…）
│   ├── architecture/          #   架构规范（业务组件编写约定）
│   └── business/              #   业务规范（公共资源、接口、生产、模具、OEE…）
├── .kimi-code/skills/flexpilot/   # 服务器工具链（Kimi Code 版）
├── .codex/skills/flexpilot/       # 同上（Codex 版）
└── .qoder/                        # Qoder 配置与 repowiki 源
```

## 快速开始

### 前置要求

- Python 3.x（服务器工具链）
- Node.js（同步脚本）

### 1. 配置服务器凭证

复制模板并填写你的环境信息：

```bash
cp .kimi-code/skills/flexpilot/flexpilot-accounts.json.example .kimi-code/flexpilot-accounts.json
```

```json
{
    "currentEnv": "dev",
    "environments": [
        {
            "name": "dev",
            "user": "your-username",
            "password": "your-password",
            "org": "your-org",
            "url": "http://your-platform-host",
            "tokenUri": "http://your-platform-host/auth/login"
        }
    ]
}
```

凭证查找顺序：项目 `.kimi-code/flexpilot-accounts.json` → 项目 `.opencode/flexpilot-accounts.json` → 用户级 `~/.kimi-code/flexpilot-accounts.json`（多项目共享推荐用户级）。

### 2. 使用服务器工具链

本地业务文件放在 `src/` 目录下，路径与服务器资源一一对应：

```bash
# 下载服务器上的代码文件
python .kimi-code/skills/flexpilot/scripts/download.py --env dev --file src/path/to/file.groovy

# 上传本地修改
python .kimi-code/skills/flexpilot/scripts/upload.py --env dev --file src/path/to/file.groovy

# 执行（微流可用 --params 传入参，--debug 查看节点调试信息）
python .kimi-code/skills/flexpilot/scripts/run.py --env dev --file src/path/to/file.mf.json --params '{"flag": 0}'
```

在 Kimi Code 中也可以直接说"下载/上传/执行 xxx 文件"，由 `flexpilot` skill 自动完成。

### 3. 同步规范与知识库

```bash
node scripts/sync-skills.js           # .opencode/skills → .qoder/skills
node scripts/sync-repowiki.js         # .qoder/repowiki → wiki/（自动脱敏 + 生成索引）
```

两者都支持 `--dry-run` 预览。

## 文档

完整知识库见 [wiki/README.md](wiki/README.md)，建议从 [项目概述](wiki/项目概述.md) 开始。

## License

[MIT](LICENSE)
