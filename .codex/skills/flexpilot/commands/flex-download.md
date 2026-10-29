# Low-code platform 下载命令

从 Low-code platform 服务器下载文件到本地。

## 使用方法

```bash
python .codex/skills/flexpilot/scripts/download.py --env <环境> --file <文件路径>
```

## 示例

```bash
# 下载单个文件
python .codex/skills/flexpilot/scripts/download.py --env dev --file src/mold_manage/bzcomponent/BZTest.groovy


# 下载多个文件 (通过 JSON 配置)
python .codex/skills/flexpilot/scripts/download.py --env prod --files-info files.json
```

```bash
# 下载微流定义（.mf.json）
python .codex/skills/flexpilot/scripts/download.py --env dev --file src/inventory/microflow/production_work_report/production_task_load.mf.json
```

## 参数说明

- `--env`: 环境名 (dev/prod)
- `--file`: 单个文件路径 (相对于 src/)
- `--files-info`: JSON 文件，包含文件列表
- `--debug`: 启用调试日志

## 编码注意事项

- 下载的本地文件按 UTF-8 无 BOM 写入，编码本身无需处理；但若随后修改并上传，仍要按 flex-upload.md「编码注意事项」自检。
