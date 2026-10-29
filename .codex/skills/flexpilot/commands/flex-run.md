# Low-code platform 执行命令

在 Low-code platform 服务器上执行 Groovy/JavaScript/Python 文件。

## 使用方法

```bash
python .codex/skills/flexpilot/scripts/run.py --env <环境> --file <文件路径> [--method <方法>] [--params '<JSON>']
```

## 示例

```bash
# 执行文件 (默认方法 main)
python .codex/skills/flexpilot/scripts/run.py --env dev --file src/mold_manage/bzcomponent/BZTest.groovy

# 执行指定方法
python .codex/skills/flexpilot/scripts/run.py --env prod --file src/xxx.groovy --method customMethod

# 传递参数
python .codex/skills/flexpilot/scripts/run.py --env prod --file src/xxx.groovy --params '{"key": "value"}'

# 执行微流（--params 传微流入参，.mf.json）
python .codex/skills/flexpilot/scripts/run.py --env dev --file src/inventory/microflow/production_work_report/production_task_load.mf.json --params '{"flag": 0}'
```

## 参数说明

- `--env`: 环境名 (dev/prod)
- `--file`: 文件路径 (相对于 src/)
- `--method`: 执行的方法 (默认: main)
- `--params`: JSON 格式参数
- `--debug`: 启用调试日志

## 注意事项
- PowerShell 等外壳传 `--params` 时可能吞掉双引号（如变成 `'{flag: 0}'`），run.py 已做容错解析；
- 执行微流时 `--method` 不生效（微流参数直接通过 `--params` 传入）；加 `--debug` 可输出微流各节点调试信息。

- 本地文件必须为 UTF-8 编码（含中文时）；不要用 `@'...'@ | python -` 管道把中文代码写入文件（PowerShell 管道默认按 GBK 传中文会变 `?`），用 `apply_patch` 或 `write_utf8.ps1` 生成/修改文件。

## 输出说明

- **Console Output**: 服务端打印的日志
- **Return**: 执行结果 (JSON)
- **Status Code**: HTTP 状态码

## 支持的文件类型

| 扩展名 | 类型 |
|--------|------|
| `.groovy` | groovy |
| `.js` | javascript |
| `.py` | python |
| `.mf.json` | microflow |