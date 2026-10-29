# Low-code platform 上传命令

上传本地文件到 Low-code platform 服务器。

## 使用方法

```bash
python .opencode/skills/flexpilot/scripts/upload.py --env <环境> --file <文件路径>
```

## 示例

```bash
# 上传单个文件
python .opencode/skills/flexpilot/scripts/upload.py --env dev --file src/mold_manage/bzcomponent/BZTest.groovy

# 上传多个文件 (通过 JSON 配置)
python .opencode/skills/flexpilot/scripts/upload.py --env prod --files-info files.json
```

## 参数说明

- `--env`: 环境名 (dev/prod)
- `--file`: 单个文件路径 (相对于 src/)
- `--files-info`: JSON 文件，包含文件列表
- `--debug`: 启用调试日志