---
name: flexpilot
description: Low-code platform 文件操作工具，支持上传、下载、执行 Low-code platform（cmes/lowcode）服务器上的代码文件与微流（microflow）
whenToUse: 用户提到 Low-code platform、cmes、lowcode 并要求操作文件，或说"上传"、"下载"、"执行"、"运行测试"、"同步文件"、"run"、"upload"、"download"、"sync"时；用户要求修改/编辑/新增微流（.mf.json）时也适用（先读 references/microflow-pitfalls.md）
---

# Low-code platform Skill

Low-code platform 文件操作工具，支持 **上传**、**下载**、**执行** 三种操作。脚本位于 `${KIMI_SKILL_DIR}/scripts/`，全部按 UTF-8 读写，零第三方依赖（仅用 Python 标准库）。

## 目录结构

```
.kimi-code/skills/flexpilot/
├── scripts/
│   ├── upload.py      # 上传文件
│   ├── download.py    # 下载文件
│   ├── run.py         # 执行文件（微流走运行时地址）
│   └── write_utf8.ps1 # UTF-8（无 BOM）写文件助手（PowerShell 场景备用）
├── utils/
│   ├── utils.py         # 认证、HTTP、URL 构造、文件类型映射
│   └── path_mapping.py  # 远程路径 <-> 本地中文目录映射
├── commands/                  # 各命令详细说明
├── references/                # 微流编辑避坑等深度参考
├── flexpilot-accounts.json.example  # 账号配置模板
└── SKILL.md           # 本文件
```

## 快速开始

### 1. 配置账户

脚本按以下顺序查找凭证文件（命中即用，模板见 skill 目录下的 `flexpilot-accounts.json.example`）：

1. 项目根目录 `.kimi-code/flexpilot-accounts.json`（向上逐级查找）
2. 项目根目录 `.opencode/flexpilot-accounts.json`（兼容旧配置，与 `.codex` 版 skill 共用）
3. 用户级 `~/.kimi-code/flexpilot-accounts.json`（所有项目共享，其他项目无需再配）

配置格式：

```json
{
    "currentEnv": "dev",
    "environments": [
        {
            "name": "dev",
            "user": "your-username",
            "password": "your-password",
            "org": "your-org",
            "url": "http://lowcode-dev.example.com",
            "tokenUri": "http://lowcode-dev.example.com/auth/login"
        },
        {
            "name": "prod",
            "user": "your-username",
            "password": "your-password",
            "org": "your-org",
            "url": "https://lowcode.example.com",
            "tokenUri": "https://lowcode.example.com/auth/login"
        }
    ]
}
```

### 2. 上传文件

```bash
python "${KIMI_SKILL_DIR}/scripts/upload.py" --env dev --file src/path/to/file.groovy
```

### 3. 下载文件

```bash
python "${KIMI_SKILL_DIR}/scripts/download.py" --env dev --file src/path/to/file.groovy
```

### 4. 执行文件

```bash
python "${KIMI_SKILL_DIR}/scripts/run.py" --env dev --file src/path/to/file.groovy
```

各命令的完整参数说明见 `commands/flex-upload.md`、`commands/flex-download.md`、`commands/flex-run.md`。

## 文件路径规范

- 本地文件放在 `src/` 目录下，路径相对于项目根目录
- 示例：`src/mold_manage/bzcomponent/BZTest.groovy` 对应服务器路径 `/repository/mold_manage/bzcomponent/BZTest`
- `utils/path_mapping.py` 内置了部分模块到本地中文目录的映射（如 `mold_manage/bzcomponent` ↔ `bzc/模具管理`），走映射目录的文件会自动换算路径

## 支持的文件类型

| 类型 | 扩展名 |
|------|--------|
| Groovy | `.groovy` |
| JavaScript | `.js` |
| Python | `.py`（仅执行） |
| HTML | `.html` |
| JSON | `.json` |
| SQL | `.sql` |
| Microflow | `.mf.json` |

## 微流（Microflow）

微流资源用自定义扩展名 `.mf.json` 标识，内容仍是标准 JSON（整个微流资源定义），既能被工具明确识别为微流，又不影响 JSON 解析。

```bash
# 下载微流定义
python "${KIMI_SKILL_DIR}/scripts/download.py" --env dev --file src/inventory/microflow/production_work_report/production_task_load.mf.json

# 执行微流（--params 传微流入参）
python "${KIMI_SKILL_DIR}/scripts/run.py" --env dev --file src/inventory/microflow/production_work_report/production_task_load.mf.json --params '{"flag": 0}'

# 上传微流定义
python "${KIMI_SKILL_DIR}/scripts/upload.py" --env dev --file src/inventory/microflow/production_work_report/production_task_load.mf.json --force
```

说明：
- 本地 `src/inventory/microflow/.../xxx.mf.json` 对应服务器资源 `/repository/inventory/microflow/.../xxx`。
- 下载保存完整资源定义 JSON（含 `content`、`objectExt`、`input`、`output`、`startNode` 等）。
- 上传仅用本地定义字段覆盖服务器最新定义，服务器管理的元数据（如 `modificationTime`）不会被覆盖。
- 外壳吞双引号时（如 `'{flag: 0}'`），run.py 已做容错解析；`--debug` 输出微流各节点调试信息。

**修改/新增微流前必读** `${KIMI_SKILL_DIR}/references/microflow-pitfalls.md` —— 引擎触发规则、端口绑定、调试方法的实战避坑总结，违反会导致重复创建或 StackOverflowError。

## 注意事项

1. **上传前**：确保远程文件已存在（需先在 Low-code platform 平台创建）
2. **执行前**：先上传本地修改到服务器
3. **下载前**：无需准备，`src/` 目录结构会自动创建

## 编码注意事项（重要）

上传/下载/执行脚本全部按 UTF-8 读写，**问题通常出在"怎么生成含中文的本地文件"这一步**。

- **首选**：用 Kimi Code 内置的 Write/Edit 工具创建和修改文件 —— 始终按 UTF-8 写入，不会出错。
- **避免**：在 PowerShell 里用管道把含中文的内容喂给脚本（如 `@'...'@ | python -`），PowerShell 管道默认按控制台代码页（GBK）编码，中文会变 `?`，上传后服务器上也是乱码。
- 若必须在 PowerShell 生成含中文文件，用 `scripts/write_utf8.ps1`（.NET 写 UTF-8 无 BOM）。

**上传前自检**（Git Bash 中统计非 ASCII 字符数；文件含中文但结果为 0，说明中文已变成 `?`）：

```bash
python -c "print(sum(ord(c) > 127 for c in open('src/xxx/Test.groovy', encoding='utf-8').read()))"
```

## 错误处理

- 认证失败：检查 `flexpilot-accounts.json` 凭证与 `tokenUri`（查找顺序见「快速开始」）
- 文件不存在：确保远程文件已创建（上传场景）
- 执行错误：查看输出的 Console Output / debug.error 字段
