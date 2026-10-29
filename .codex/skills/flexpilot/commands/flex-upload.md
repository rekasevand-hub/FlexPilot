# Low-code platform 上传命令

上传本地文件到 Low-code platform 服务器。

## 使用方法

```bash
python .codex/skills/flexpilot/scripts/upload.py --env <环境> --file <文件路径>
```

## 示例

```bash
# 上传单个文件
python .codex/skills/flexpilot/scripts/upload.py --env dev --file src/mold_manage/bzcomponent/BZTest.groovy

# 上传多个文件 (通过 JSON 配置)
python .codex/skills/flexpilot/scripts/upload.py --env prod --files-info files.json
```

```bash
# 上传微流定义（.mf.json）
python .codex/skills/flexpilot/scripts/upload.py --env dev --file src/inventory/microflow/production_work_report/production_task_load.mf.json --force
```

## 参数说明

- `--env`: 环境名 (dev/prod)
- `--file`: 单个文件路径 (相对于 src/)
- `--files-info`: JSON 文件，包含文件列表
- `--debug`: 启用调试日志

## 编码注意事项（重要）

上传前先自检本地文件编码：脚本按 UTF-8 读取，如果含中文的本地文件是 GBK 或中文已变成 `?`，上传后服务器上也是乱码。

```powershell
# 统计非 ASCII 字符数；含中文但结果是 0，说明中文已变成 ?，先修复再上传
$c = [System.IO.File]::ReadAllText('src/xxx/Test.groovy', [System.Text.UTF8Encoding]::new($false))
($c.ToCharArray() | Where-Object { [int]$_ -gt 127 }).Count
```

写文件时推荐用 `apply_patch` 工具；新建含中文文件可用 `write_utf8.ps1`（用法见 SKILL.md「编码注意事项」），不要用 `@'...'@ | python -` 管道（PowerShell 管道默认按 GBK 传中文，会变成 `?`）。