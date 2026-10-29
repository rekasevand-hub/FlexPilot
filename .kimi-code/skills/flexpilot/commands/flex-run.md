# Low-code platform 执行命令

在 Low-code platform 服务器上执行 Groovy/JavaScript/Python 文件或微流。

## 使用方法

```bash
python .kimi-code/skills/flexpilot/scripts/run.py --env <环境> --file <文件路径> [--method <方法>] [--params '<JSON>']
```

## 示例

```bash
# 执行文件 (默认方法 main)
python .kimi-code/skills/flexpilot/scripts/run.py --env dev --file src/mold_manage/bzcomponent/BZTest.groovy

# 执行指定方法
python .kimi-code/skills/flexpilot/scripts/run.py --env prod --file src/xxx.groovy --method customMethod

# 传递参数
python .kimi-code/skills/flexpilot/scripts/run.py --env prod --file src/xxx.groovy --params '{"key": "value"}'

# 执行微流（--params 传微流入参，.mf.json）
python .kimi-code/skills/flexpilot/scripts/run.py --env dev --file src/inventory/microflow/production_work_report/production_task_load.mf.json --params '{"flag": 0}'
```

## 参数说明

- `--env`: 环境名（dev/prod）
- `--file`: 文件路径（相对于项目根目录）
- `--method`: 执行的方法（默认: main）
- `--params`: JSON 格式参数
- `--debug`: 启用调试日志；执行微流时同时输出各节点调试信息（`_debug=true&_limit=-1&_step=false`）

## 注意事项

- 外壳传 `--params` 时可能吞掉双引号（如变成 `'{flag: 0}'`），run.py 已做容错解析；
- 执行微流时 `--method` 不生效（微流参数直接通过 `--params` 传入）；
- 执行发送的是**本地文件内容**，执行前如需让服务器上的版本生效，先上传；
- 微流执行会真实落库，测试后注意清理脏数据（详见 references/microflow-pitfalls.md）；
- 本地文件必须为 UTF-8 编码（含中文时），优先用 Kimi Code 内置 Write/Edit 工具生成/修改。

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
