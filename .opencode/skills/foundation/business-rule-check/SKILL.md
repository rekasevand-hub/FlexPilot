---
name: business-rule-check
description: 生成代码前必须执行的业务规则检查规范，包含非空校验、唯一性校验、关联关系校验、联合唯一校验等检查清单和代码示例。
compatibility: opencode
metadata:
  layer: foundation
  priority: 2
---

# 业务规则检查

> 生成代码前必须执行的业务规则检查，确保业务逻辑完整准确

## 1. 检查时机

- **生成代码前**：必须先检查业务规则是否明确定义
- **如有疑问**：必须向用户确认后才能继续生成代码

## 2. 检查清单

| 序号 | 检查项 | 说明 |
|-----|-------|------|
| 1 | Domain 是否已提供 | 业务需求发布后，必须先有 Domain 定义 |
| 2 | 字段非空校验 | nullable=false 的字段必须生成非空校验代码 |
| 3 | 字段唯一性校验 | unique=true 的字段必须生成唯一性校验代码 |
| 4 | 关联关系校验 | 删除操作必须检查下级是否被引用 |
| 5 | 业务特殊规则 | 如有特殊业务逻辑，需确认后生成 |

## 3. 校验逻辑生成规则

### 3.1 非空校验
```groovy
if (Util.isStringBlank(obj.fieldName)) {
    throw new SysException("字段名称不能为空！");
}
```

### 3.2 唯一性校验
```groovy
def existing = EntityName.find(["fieldName": obj.fieldName]);
if (existing) {
    throw new SysException("该编码已存在，不可重复！");
}
```

### 3.3 关联关系校验
```groovy
List<SubEntity> list = SubEntity.findAll([parentNo: obj.parentNo]);
if (list.size() > 0) {
    throw new SysException("删除失败，该记录已被下级使用");
}
```

### 3.4 联合唯一性校验
```groovy
def params = ["field1": obj.field1, "field2": obj.field2];
def existing = EntityName.findAll(params);
if (existing.size() > 0) {
    throw new SysException("该组合已存在，不可重复！");
}
```

## 4. 模块专属业务规则

### 4.1 无需上料物料 (NoFeedMaterial)

**业务规则**：物料编码 + 厂区编码 联合唯一

**校验逻辑要求**：
- 同一厂区下物料编码不能重复
- 不同厂区下同一物料编码可以重复

**正确示例（RQL批量查询）**：
```groovy
def nfmRql = "select * from NoFeedMaterial where material *= {? 'material'} and areaNo = {? 'areaNo'}";
def materialCodes = materialData.collect { it.material };
def nfmList = ude.execQuery(nfmRql, ["material": materialCodes, "areaNo": areaNow], true);
if (nfmList && nfmList.size() > 0) {
    def existMaterials = nfmList.material.join(",");
    throw new SysException("当前厂区【" + areaNow + "】，物料编码：【" + existMaterials + "】已存在，请勿重复添加");
}
```

**常见错误**：
- ❌ 遗漏厂区条件，导致跨厂区重复
- ❌ 使用 SQL 拼接而非 RQL 参数化查询
- ❌ 单条循环查询（N+1问题）

## 5. Domain 字段属性对应关系

| Domain属性 | 校验类型 | 代码生成 |
|-----------|---------|---------|
| nullable: false | 非空校验 | 必须生成 |
| unique: true | 唯一性校验 | 必须生成 |
| unique: composite | 联合唯一性校验 | 必须生成 |
| parentId 关联 | 关联关系校验 | 删除时必须检查 |

## 6. 疑问反馈格式

生成代码前如有问题，按以下格式向用户确认：

```
## 业务规则确认 - {模块名称}

| 序号 | 字段/规则 | Domain定义 | 疑问内容 |
|-----|---------|-----------|---------|
| 1 | xxxNo | nullable: false | 是否需要非空校验？ |
| 2 | xxxNo | unique: true | 是否需要唯一性校验？ |
```

## 7. 使用说明

1. **每次生成 BZC 前**：必须先执行本检查清单
2. **发现 Domain 问题**：立即向用户反馈，不要跳过
3. **确认后记录**：将确认结果记录到 dev-questions skill
4. **更新模块规范**：将业务规则更新到对应模块的 skill 中
5. **生成代码时必须遵守**：
   - error-handling skill - 异常抛出和捕获规范
   - logging-standard skill - 日志记录规范
   - global-code-standard skill - 注释和目录规范

## 8. 检查清单

| 序号 | 检查项 | 是否通过 |
|-----|-------|---------|
| 1 | Domain 已提供且字段完整 | ☐ |
| 2 | nullable=false 的字段已生成非空校验 | ☐ |
| 3 | unique=true 的字段已生成唯一性校验 | ☐ |
| 4 | unique=composite 的字段已生成联合唯一校验 | ☐ |
| 5 | 删除操作已检查下级引用 | ☐ |
| 6 | 业务特殊规则已确认并生成 | ☐ |
| 7 | 异常使用 SysException，消息包含操作+主体+原因 | ☐ |
| 8 | 没有空 catch 块和 e.printStackTrace() | ☐ |
| 9 | 成功返回使用 SysResult.OK | ☐ |
| 10 | 异常捕获处有日志记录 | ☐ |