---
name: quality-batch-issue
description: 产品质量批量问题记录业务规范，包含BatchQualityIssue批量质量预警检测的目录结构、实体定义、业务规则、调用时序等。
compatibility: opencode
metadata:
  layer: business
  priority: 4
---

# 产品质量批量问题记录

> 产品质量批量问题记录业务模块规范

## 1. 目录结构

### BZC业务组件
```
bzc/生产管理/单据记录/产品质量批量问题记录/
└── BatchQualityIssue.groovy
```

### Domain实体
```
Domain/生产管理/单据记录/产品质量批量问题记录/
├── BatchQualityIssueLog.json
├── BatchQualityIssueLogDetails.json
└── BatchQualityIssueLogDetailsLog.json
```

## 2. 实体列表

| 实体 | 说明 |
|-----|------|
| BatchQualityIssueLog | 批量质量预警主表 |
| BatchQualityIssueLogDetails | 预警明细表 |
| BatchQualityIssueLogDetailsLog | 预警日志表（后台表） |

## 3. 业务规则

| 规则 | 说明 |
|-----|------|
| 触发条件-monitorNum | monitorNum > 0 时才进行预警判断，为0则跳过 |
| 触发条件-monitorHours | monitorHours > 0 时才进行预警判断，为0则跳过 |
| 触发条件-下线时间 | productionOfflineTime != null 才计算时间窗口 |
| 防重-日志表 | try-catch 捕获保存异常，已存在则跳过后续逻辑 |
| 防重-明细表 | 创建前查询 container 是否已存在，存在则跳过主表创建 |
| 时间窗口 | 以下线时间为基准，前后各 monitorHours 小时 |
| 消息接收人 | 从"软光缆管理人员"员工组获取 |
| 排除产线 | isBackLine = true 的产线不计入统计 |
| flag标记 | 未触发=false，已触发=true |

## 4. 调用时序

1. 质检完成 → 调用 batchQualityIssue
2. 判断 monitorNum > 0，否则跳过
3. 判断 monitorHours > 0，否则跳过
4. 保存日志记录（flag=false），防重
5. 查询产品族配置
6. 判断 productionOfflineTime != null，否则跳过
7. 计算时间窗口：下线时间前后各 monitorHours 小时
8. 查询前时间窗口内记录数
9. ≥ monitorNum 则触发预警
10. 查询后时间窗口内记录数
11. ≥ monitorNum 则触发预警
12. 触发预警时：创建主表 → 创建明细 → 更新flag → 发消息

## 5. 相关模块

| 模块 | 说明 |
|-----|------|
| ProcessProdFamily | 提供 monitorHours、monitorNum 配置 |
| ProcessProdFamilyDetails | 关联预警通知用户 |
| EmployeeDetails | 查询"软光缆管理人员"员工组获取接收人 |
| ProductionLine | 判断 isBackLine 排除返修线 |