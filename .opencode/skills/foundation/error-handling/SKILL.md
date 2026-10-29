---
name: error-handling
description: CMES项目错误处理规范，统一异常抛出和捕获方式，包含SysException使用规范、异常消息格式、返回值规范等。
compatibility: opencode
metadata:
  layer: foundation
  priority: 5
---

# 错误处理规范

> 所有CMES项目代码均需遵守此规范，统一错误处理方式，提升代码健壮性和可维护性

## 1. 异常类型

### 1.1 平台提供的异常类

| 异常类 | 用途 | 使用场景 |
|-------|------|---------|
| `SysException` | 业务异常 | 业务规则校验失败、数据不合法等 |
| 系统运行时异常 | 系统级异常 | 空指针、类型转换等 |

### 1.2 使用原则
- **业务校验失败** → 抛出 `SysException`
- **系统级错误** → 不主动捕获，由平台统一处理
- **禁止** 吞掉异常（catch 空块）
- **禁止** 使用 `e.printStackTrace()`

## 2. 异常抛出规范

### 2.1 格式要求
```groovy
throw new SysException("删除失败，" + obj.enterpriseName + "已在工厂信息使用");
```

### 2.2 错误消息规范

| 规则 | 说明 | 示例 |
|------|------|------|
| 包含操作 | 说明哪个操作失败 | "删除失败，" |
| 包含主体 | 说明哪个对象出错 | obj.enterpriseName |
| 包含原因 | 说明失败原因 | "已在工厂使用" |
| 面向用户 | 消息要用户可理解 | 不暴露技术细节 |

### 2.3 常见场景消息模板

```groovy
throw new SysException("字段名称不能为空！");
throw new SysException("该编码已存在，不可重复！");
throw new SysException("删除失败，" + obj.name + "已被使用");
```

## 3. 异常捕获规范

### 3.1 需要捕获的场景
- 外部接口调用（HTTP 请求、RPC 调用）
- 文件操作
- 数据库批量操作（部分失败需处理时）

### 3.2 捕获模板
```groovy
try {
    def result = externalService.call(params);
} catch (Exception e) {
    console.log("接口调用失败: " + e.getMessage());
    throw new SysException("接口调用失败，请稍后重试");
}
```

### 3.3 禁止的写法
```groovy
// ❌ 禁止：空 catch 块
try { ... } catch (Exception e) { }
// ❌ 禁止：只打印堆栈
try { ... } catch (Exception e) { e.printStackTrace() }
```

## 4. 返回值规范

### 4.1 简单操作成功返回
```groovy
return SysResult.OK;
```

### 4.2 带业务数据的返回
```groovy
return ["createCount": createCount, "updateCount": updateCount];
return ['ResultFlag': resultCode, 'ResultMsg': message, 'RetData': RetData];
```

### 4.3 禁止的返回值用法
```groovy
// ❌ 禁止：返回 SysResult.OK 后用 result.error 判断
def result = execute(list, empAll);
if (result.error == "SUCCESS") { ... }  // 永远为 false
```

## 5. 检查清单

| 序号 | 检查项 | 是否通过 |
|-----|-------|---------|
| 1 | 所有业务校验失败都使用 SysException | ☐ |
| 2 | 异常消息包含操作+主体+原因 | ☐ |
| 3 | 没有空 catch 块 | ☐ |
| 4 | 没有使用 e.printStackTrace() | ☐ |
| 5 | 外部调用有异常捕获和处理 | ☐ |
| 6 | 简单成功返回使用 SysResult.OK | ☐ |
| 7 | 需要业务数据时返回 Map 而非 SysResult.OK | ☐ |