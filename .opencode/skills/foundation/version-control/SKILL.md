---
name: version-control
description: CMES项目版本控制规范，包含仓库结构、提交消息格式、目录同步规范、变更记录等。
compatibility: opencode
metadata:
  layer: foundation
  priority: 7
---

# 版本控制规范

> CMES项目的版本控制规范，确保代码变更可追溯、协作有序

## 1. 仓库结构

```
cmes/
├── Domain/              # 领域模型
├── bzc/                # 业务组件
└── skills/             # 开发规范
```

| 上级菜单 | BZC包 | Domain包 |
|---------|-------|----------|
| 基础 | `app.base.bzcomponent.{模块}` | `app.base.domain.{模块}` |
| 接口管理 | `app.interface_manage.bzcomponent.{模块}` | `app.interface_manage.domain.{模块}` |

## 2. 提交规范

### 2.1 提交消息格式
```
<类型>: <模块名> - <简要描述>
```

### 2.2 类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新增功能 | feat: 物理建模 - 新增企业模块BZC |
| fix | 修复缺陷 | fix: 人员管理 - 修复删除校验逻辑 |
| docs | 文档变更 | docs: skills - 新增错误处理规范 |
| refactor | 重构代码 | refactor: 工厂模块 - 优化查询逻辑 |

### 2.3 提交粒度
- **一个功能模块一次提交**：不要把多个模块的变更混在一起
- **Domain 和 BZC 分开提交**：先提交 Domain，再提交 BZC
- **skill 文件独立提交**：规范变更单独提交

## 3. 目录同步规范

- 新增 BZC 目录时，必须在 Domain 下创建对应目录
- 目录结构必须保持一致

## 4. 检查清单

| 序号 | 检查项 | 是否通过 |
|-----|-------|---------|
| 1 | 提交消息符合格式规范 | ☐ |
| 2 | Domain 和 BZC 目录结构同步 | ☐ |
| 3 | Domain 变更先于 BZC 提交 | ☐ |
| 4 | 不同模块的变更分开提交 | ☐ |