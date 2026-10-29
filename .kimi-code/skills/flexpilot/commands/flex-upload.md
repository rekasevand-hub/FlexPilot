# Low-code platform 上传命令

上传本地文件到 Low-code platform 服务器。

## 使用方法

```bash
python .kimi-code/skills/flexpilot/scripts/upload.py --env <环境> --file <文件路径>
```

## 示例

```bash
# 上传单个文件
python .kimi-code/skills/flexpilot/scripts/upload.py --env dev --file src/mold_manage/bzcomponent/BZTest.groovy

# 跳过确认直接上传
python .kimi-code/skills/flexpilot/scripts/upload.py --env dev --file src/mold_manage/bzcomponent/BZTest.groovy --force

# 上传多个文件 (通过 JSON 配置)
python .kimi-code/skills/flexpilot/scripts/upload.py --env prod --files-info files.json

# 上传微流定义（.mf.json）
python .kimi-code/skills/flexpilot/scripts/upload.py --env dev --file src/inventory/microflow/production_work_report/production_task_load.mf.json --force
```

`--files-info` 的 JSON 格式：

```json
{
    "files": [
        { "path": "src/mold_manage/bzcomponent/BZTest.groovy" },
        { "path": "src/inventory/microflow/production_work_report/production_task_load.mf.json" }
    ]
}
```

## 参数说明

- `--env`: 环境名（对应 flexpilot-accounts.json 中的 environments name，如 dev/prod）
- `--file`: 单个文件路径（相对于项目根目录）
- `--files-info`: JSON 文件，包含文件列表
- `--force`: 跳过确认直接上传
- `--debug`: 启用调试日志
- `--proxy` / `--port`: 代理设置（可选）

## 编码注意事项（重要）

上传前先自检本地文件编码：脚本按 UTF-8 读取，如果含中文的本地文件是 GBK 或中文已变成 `?`，上传后服务器上也是乱码。

```bash
# 统计非 ASCII 字符数；含中文但结果是 0，说明中文已变成 ?，先修复再上传
python -c "print(sum(ord(c) > 127 for c in open('src/xxx/Test.groovy', encoding='utf-8').read()))"
```

写文件时优先用 Kimi Code 内置的 Write/Edit 工具（始终 UTF-8）；在 PowerShell 中生成含中文文件可用 `scripts/write_utf8.ps1`；不要用 `@'...'@ | python -` 管道（PowerShell 管道默认按 GBK 传中文，会变成 `?`）。
