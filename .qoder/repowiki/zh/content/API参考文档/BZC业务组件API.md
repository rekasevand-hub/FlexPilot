# BZC业务组件API

<cite>
**本文档引用的文件**
- [bzc-base.skill](file://skills/architecture/bzc-base.skill)
- [public-resource-management.skill](file://skills/business/public-resource-management.skill)
- [logging-standard.skill](file://skills/foundation/logging-standard.skill)
- [business-rule-check.skill](file://skills/foundation/business-rule-check.skill)
- [CreateEmpAndUser.groovy](file://bzc/公共资源管理/人员管理/人员信息/CreateEmpAndUser.groovy)
- [QueryUserStatus.groovy](file://bzc/公共资源管理/人员管理/人员信息/QueryUserStatus.groovy)
- [UserArea.groovy](file://bzc/公共资源管理/人员管理/人员信息/UserArea.groovy)
- [PackageProcessRouteSave.groovy](file://bzc/公共资源管理/工艺建模/包装工艺路线/PackageProcessRouteSave.groovy)
- [PackagingStepDel.groovy](file://bzc/公共资源管理/工艺建模/包装工步信息/PackagingStepDel.groovy)
- [Status.json](file://Domain/公共资源管理/Status.json)
- [ApiApplicationInfo.json](file://Domain/接口管理/ApiApplicationInfo.json)
- [InterfaceConfig.json](file://Domain/接口管理/InterfaceConfig.json)
</cite>

## 目录
1. [简介](#简介)
2. [项目结构](#项目结构)
3. [核心组件](#核心组件)
4. [架构总览](#架构总览)
5. [详细组件分析](#详细组件分析)
6. [依赖关系分析](#依赖关系分析)
7. [性能考量](#性能考量)
8. [故障排除指南](#故障排除指南)
9. [结论](#结论)
10. [附录](#附录)

## 简介
本文件为BZC（业务组件）API的详细技术文档，面向开发者与集成方，系统阐述RESTful API的标准实现模式与最佳实践。文档覆盖doGet、doPost、doPut、doDelete四类核心HTTP方法的映射规范、请求参数处理、响应格式标准化、参数传递机制、数据序列化与反序列化流程、错误处理策略与异常类型定义，并提供各业务组件的调用示例与集成指南。

## 项目结构
BZC业务组件遵循“模块化+分层”的组织方式：
- 技能规范层：定义架构、业务、基础能力规范（skills/）
- 业务组件层：具体业务实现（bzc/公共资源管理/...）
- 领域模型层：数据结构与约束（Domain/公共资源管理/...）

```mermaid
graph TB
subgraph "技能规范层"
A1["architecture/bzc-base.skill"]
A2["business/public-resource-management.skill"]
A3["foundation/logging-standard.skill"]
A4["foundation/business-rule-check.skill"]
end
subgraph "业务组件层"
B1["人员信息/CreateEmpAndUser.groovy"]
B2["人员信息/QueryUserStatus.groovy"]
B3["人员信息/UserArea.groovy"]
B4["工艺建模/包装工艺路线/PackageProcessRouteSave.groovy"]
B5["工艺建模/包装工步信息/PackagingStepDel.groovy"]
end
subgraph "领域模型层"
C1["Status.json"]
C2["ApiApplicationInfo.json"]
C3["InterfaceConfig.json"]
end
A1 --> B1
A1 --> B2
A1 --> B3
A1 --> B4
A1 --> B5
A2 --> B1
A2 --> B2
A2 --> B3
A2 --> B4
A2 --> B5
A3 --> B1
A3 --> B2
A3 --> B3
A4 --> B1
A4 --> B2
A4 --> B3
A4 --> B4
A4 --> B5
B1 --> C1
B2 --> C1
B3 --> C1
B4 --> C1
B5 --> C1
B1 --> C2
B2 --> C2
B3 --> C2
B4 --> C3
B5 --> C3
```

**图表来源**
- [bzc-base.skill:1-162](file://skills/architecture/bzc-base.skill#L1-L162)
- [public-resource-management.skill:1-514](file://skills/business/public-resource-management.skill#L1-L514)

**章节来源**
- [bzc-base.skill:1-162](file://skills/architecture/bzc-base.skill#L1-L162)
- [public-resource-management.skill:1-514](file://skills/business/public-resource-management.skill#L1-L514)

## 核心组件
- BaseBZC基类：所有BZC组件的父类，提供统一的生命周期与工具方法。
- SysHelper：请求参数提取（GET参数、POST请求体）、当前用户上下文等。
- SysResult：标准成功响应封装（如OK）。
- SysException：统一异常类型，承载业务异常信息。
- UDE/RPS：统一数据访问与资源操作抽象（RQL批量查询、资源创建/更新/删除）。

关键规范要点：
- 类结构：继承BaseBZC，方法命名规范，main方法作为本地测试入口。
- RESTful映射：doGet/doPost/doPut/doDelete分别对应HTTP GET/POST/PUT/DELETE。
- 参数处理：GET使用SysHelper.getRequestParameters，POST使用SysHelper.getRequestBody。
- 响应格式：业务方法返回业务对象或Map；REST方法返回业务结果或SysResult.OK。
- 删除策略：删除前检查下级引用，存在引用抛出SysException，无引用执行删除。
- 批量删除：通过obj._data判断，遍历调用delete。

**章节来源**
- [bzc-base.skill:10-26](file://skills/architecture/bzc-base.skill#L10-L26)
- [bzc-base.skill:92-122](file://skills/architecture/bzc-base.skill#L92-L122)
- [bzc-base.skill:74-90](file://skills/architecture/bzc-base.skill#L74-L90)
- [business-rule-check.skill:39-46](file://skills/foundation/business-rule-check.skill#L39-L46)

## 架构总览
BZC API采用“控制器（REST方法）—业务方法—领域模型”的分层架构。REST方法负责协议适配与参数解析，业务方法负责业务逻辑与校验，领域模型承载数据结构与约束。

```mermaid
sequenceDiagram
participant Client as "客户端"
participant REST as "BZC REST方法"
participant Helper as "SysHelper"
participant Biz as "业务方法"
participant Model as "领域模型"
participant Result as "SysResult"
Client->>REST : "HTTP请求(GET/POST/PUT/DELETE)"
REST->>Helper : "提取参数(RequestParameters/RequestBody)"
Helper-->>REST : "参数对象(Map)"
REST->>Biz : "调用业务方法"
Biz->>Model : "读写领域模型"
Model-->>Biz : "持久化结果"
Biz-->>REST : "业务结果"
REST-->>Client : "标准响应(JSON)"
```

**图表来源**
- [bzc-base.skill:92-122](file://skills/architecture/bzc-base.skill#L92-L122)
- [QueryUserStatus.groovy:40-45](file://bzc/公共资源管理/人员管理/人员信息/QueryUserStatus.groovy#L40-L45)
- [UserArea.groovy:192-197](file://bzc/公共资源管理/人员管理/人员信息/UserArea.groovy#L192-L197)

## 详细组件分析

### 人员信息模块

#### 组件：CreateEmpAndUser（员工与用户同步）
- 功能：在创建/修改/删除员工时同步创建/修改/删除系统用户，支持密码强度校验、角色合并、默认角色等。
- REST映射：
  - doGet：本地测试入口（main方法）
  - doPost：创建/修改/删除用户（_method参数）
  - doPut：占位返回SysResult.OK
  - doDelete：占位返回SysResult.OK
- 参数处理：
  - GET：无
  - POST：请求体包含_employee、_method、password、repassword、roles、enabled、passwordLifetime、passwordExpirationTime等
- 响应格式：返回username与_method，或SysResult.OK
- 错误处理：SysException，包含“未知的_method”、“找不到雇员资料”、“密码强度不足”等

```mermaid
sequenceDiagram
participant Client as "客户端"
participant REST as "CreateEmpAndUser.doPost"
participant Helper as "SysHelper"
participant Biz as "createEmpAndUser"
participant UserRepo as "用户资源库(RPS)"
participant Emp as "Employee领域模型"
Client->>REST : "POST /CreateEmpAndUser"
REST->>Helper : "getRequestBody()"
Helper-->>REST : "{_method, employee, password, ...}"
REST->>Biz : "createEmpAndUser(params)"
Biz->>Emp : "查询员工信息"
Biz->>UserRepo : "创建/更新/删除用户"
Biz-->>REST : "{username, method}"
REST-->>Client : "JSON响应"
```

**图表来源**
- [CreateEmpAndUser.groovy:91-130](file://bzc/公共资源管理/人员管理/人员信息/CreateEmpAndUser.groovy#L91-L130)
- [CreateEmpAndUser.groovy:140-232](file://bzc/公共资源管理/人员管理/人员信息/CreateEmpAndUser.groovy#L140-L232)

**章节来源**
- [CreateEmpAndUser.groovy:1-590](file://bzc/公共资源管理/人员管理/人员信息/CreateEmpAndUser.groovy#L1-L590)

#### 组件：QueryUserStatus（查询用户状态）
- 功能：查询用户密码有效期、激活状态、停用/启用时间等。
- REST映射：
  - doGet：接收username参数，返回用户状态信息
  - doPost/doPut/doDelete：返回SysResult.OK
- 参数处理：GET参数username必填
- 响应格式：用户状态Map，包含passwordLifetime、passwordExpirationTime、enabled、userStatusTime、userUri等
- 错误处理：SysException，如“登录用户不可为空”

```mermaid
sequenceDiagram
participant Client as "客户端"
participant REST as "QueryUserStatus.doGet"
participant Helper as "SysHelper"
participant Biz as "queryUserStatus"
participant UserRepo as "用户资源库(RPS)"
Client->>REST : "GET /QueryUserStatus?username=..."
REST->>Helper : "getRequestParameters()"
Helper-->>REST : "{username}"
REST->>Biz : "queryUserStatus(params)"
Biz->>UserRepo : "查询用户"
Biz-->>REST : "用户状态Map"
REST-->>Client : "JSON响应"
```

**图表来源**
- [QueryUserStatus.groovy:40-45](file://bzc/公共资源管理/人员管理/人员信息/QueryUserStatus.groovy#L40-L45)
- [QueryUserStatus.groovy:62-109](file://bzc/公共资源管理/人员管理/人员信息/QueryUserStatus.groovy#L62-L109)

**章节来源**
- [QueryUserStatus.groovy:1-144](file://bzc/公共资源管理/人员管理/人员信息/QueryUserStatus.groovy#L1-L144)

#### 组件：UserArea（用户厂区信息）
- 功能：维护用户默认厂区信息，提供下拉选择与保存。
- REST映射：
  - doGet：获取下拉列表数据
  - doPost：保存默认厂区
  - doPut/doDelete：返回SysResult.OK
- 参数处理：
  - doGet：可选employee参数，默认当前登录用户
  - doPost：请求体包含selectedValue（厂区编号）
- 响应格式：下拉列表list（value/name），或保存后的areaNo/value
- 错误处理：SysException，如员工不存在
- 性能优化：使用RQL批量查询避免N+1问题

```mermaid
sequenceDiagram
participant Client as "客户端"
participant REST as "UserArea.doGet"
participant Helper as "SysHelper"
participant Biz as "getData"
participant UDE as "UDE"
participant Area as "Area领域模型"
Client->>REST : "GET /UserArea"
REST->>Helper : "getRequestParameters()"
Helper-->>REST : "{employee?}"
REST->>Biz : "getData(params)"
Biz->>UDE : "execQuery(RQL : areaNo *= {...})"
UDE-->>Biz : "批量查询结果"
Biz->>Area : "匹配并组装下拉列表"
Biz-->>REST : "{list}"
REST-->>Client : "JSON响应"
```

**图表来源**
- [UserArea.groovy:192-197](file://bzc/公共资源管理/人员管理/人员信息/UserArea.groovy#L192-L197)
- [UserArea.groovy:113-183](file://bzc/公共资源管理/人员管理/人员信息/UserArea.groovy#L113-L183)

**章节来源**
- [UserArea.groovy:1-235](file://bzc/公共资源管理/人员管理/人员信息/UserArea.groovy#L1-L235)

### 工艺建模模块

#### 组件：PackageProcessRouteSave（包装工艺路线保存）
- 功能：保存或更新包装工艺路线，带processRouteNo唯一性校验。
- REST映射：
  - doPost：接收请求体，校验唯一性并保存/更新
  - doGet/doPut/doDelete：返回SysResult.OK
- 参数处理：请求体包含processRouteNo、processRouteName、notes、areaNo、_id等
- 响应格式：保存/更新后的PackageProcessRouteInfo对象
- 错误处理：SysException，如“工艺路线编码不能为空”、“该工艺路线编码已存在”

```mermaid
flowchart TD
Start(["进入checkPackageProcessRouteInfoUnique"]) --> CheckId{"是否包含_id?"}
CheckId --> |否| ValidateNew["校验processRouteNo非空"]
ValidateNew --> ExistsNew{"是否存在相同processRouteNo?"}
ExistsNew --> |是| ThrowDup["抛出异常: 编码已存在"]
ExistsNew --> |否| SaveNew["创建新记录并保存"]
CheckId --> |是| LoadOld["根据_id加载旧记录"]
LoadOld --> UpdateOld["更新名称/备注/厂区并保存"]
SaveNew --> ReturnNew["返回新记录"]
UpdateOld --> ReturnOld["返回旧记录"]
ThrowDup --> End(["结束"])
ReturnNew --> End
ReturnOld --> End
```

**图表来源**
- [PackageProcessRouteSave.groovy:39-81](file://bzc/公共资源管理/工艺建模/包装工艺路线/PackageProcessRouteSave.groovy#L39-L81)

**章节来源**
- [PackageProcessRouteSave.groovy:1-82](file://bzc/公共资源管理/工艺建模/包装工艺路线/PackageProcessRouteSave.groovy#L1-L82)

#### 组件：PackagingStepDel（包装工步删除）
- 功能：支持单点/批量删除包装工步，删除前检查下级引用。
- REST映射：
  - doGet：透传请求参数（用于调试）
  - doPost：接收请求体，判断单点/批量并调用delete
  - doPut/doDelete：返回SysResult.OK
- 参数处理：请求体包含workStepNo、workStepName、_data（批量时）
- 响应格式：SysResult.OK
- 错误处理：SysException，如“已在包装工艺路线明细中使用”

```mermaid
flowchart TD
Start(["进入stepNo"]) --> HasData{"_data是否为空?"}
HasData --> |是| CallDelete["调用delete(obj)"]
HasData --> |否| Loop["_data遍历"]
Loop --> CallDeleteBatch["逐个调用delete(it)"]
CallDelete --> CheckRef{"是否存在下级引用?"}
CallDeleteBatch --> CheckRef
CheckRef --> |是| ThrowRef["抛出异常: 存在引用"]
CheckRef --> |否| Remove["删除记录"]
ThrowRef --> End(["结束"])
Remove --> OK["返回SysResult.OK"]
OK --> End
```

**图表来源**
- [PackagingStepDel.groovy:50-79](file://bzc/公共资源管理/工艺建模/包装工步信息/PackagingStepDel.groovy#L50-L79)

**章节来源**
- [PackagingStepDel.groovy:1-79](file://bzc/公共资源管理/工艺建模/包装工步信息/PackagingStepDel.groovy#L1-L79)

## 依赖关系分析

```mermaid
classDiagram
class BaseBZC
class SysHelper {
+getRequestParameters(request)
+getRequestBody(request)
+getCurrentUsername()
}
class SysResult {
+OK
}
class SysException
class UDE
class RPS
class CreateEmpAndUser
class QueryUserStatus
class UserArea
class PackageProcessRouteSave
class PackagingStepDel
BaseBZC <|-- CreateEmpAndUser
BaseBZC <|-- QueryUserStatus
BaseBZC <|-- UserArea
BaseBZC <|-- PackageProcessRouteSave
BaseBZC <|-- PackagingStepDel
CreateEmpAndUser --> SysHelper : "参数提取/用户上下文"
QueryUserStatus --> SysHelper : "参数提取"
UserArea --> SysHelper : "参数提取"
CreateEmpAndUser --> SysResult : "成功返回"
QueryUserStatus --> SysResult : "成功返回"
UserArea --> SysResult : "成功返回"
CreateEmpAndUser --> SysException : "异常抛出"
QueryUserStatus --> SysException : "异常抛出"
UserArea --> SysException : "异常抛出"
CreateEmpAndUser --> UDE : "批量查询"
UserArea --> UDE : "批量查询"
CreateEmpAndUser --> RPS : "用户资源操作"
```

**图表来源**
- [bzc-base.skill:10-26](file://skills/architecture/bzc-base.skill#L10-L26)
- [CreateEmpAndUser.groovy:1-590](file://bzc/公共资源管理/人员管理/人员信息/CreateEmpAndUser.groovy#L1-L590)
- [UserArea.groovy:1-235](file://bzc/公共资源管理/人员管理/人员信息/UserArea.groovy#L1-L235)

**章节来源**
- [bzc-base.skill:1-162](file://skills/architecture/bzc-base.skill#L1-L162)
- [business-rule-check.skill:39-46](file://skills/foundation/business-rule-check.skill#L39-L46)

## 性能考量
- RQL批量查询：使用“*= 左连接”替代循环单条查询，避免N+1问题，显著提升批量读取性能。
- 批量删除：通过obj._data批量遍历，减少网络往返与数据库交互次数。
- 日志记录：建议在关键节点记录入参与返回，避免在大循环中逐条记录，防止日志风暴。

**章节来源**
- [business-rule-check.skill:48-56](file://skills/foundation/business-rule-check.skill#L48-L56)
- [logging-standard.skill:14-23](file://skills/foundation/logging-standard.skill#L14-L23)
- [logging-standard.skill:99-102](file://skills/foundation/logging-standard.skill#L99-L102)

## 故障排除指南
- 参数缺失：GET参数或POST请求体缺失必填字段时，抛出SysException，检查请求URL与Body。
- 唯一性冲突：新增时若唯一字段已存在，抛出SysException，需调整唯一值。
- 关联引用：删除前检查下级引用，存在引用会抛出SysException，需先清理下级数据。
- 异常捕获：所有异常需被捕获并记录日志，避免空catch块与e.printStackTrace()。
- 日志规范：记录方法入口/出口、外部接口调用、异常信息与关键数据变更，避免记录敏感信息与大对象。

**章节来源**
- [business-rule-check.skill:22-46](file://skills/foundation/business-rule-check.skill#L22-L46)
- [logging-standard.skill:43-52](file://skills/foundation/logging-standard.skill#L43-L52)
- [logging-standard.skill:78-86](file://skills/foundation/logging-standard.skill#L78-L86)

## 结论
BZC业务组件API以BaseBZC为核心，遵循统一的REST映射与参数处理规范，结合SysHelper、SysResult、SysException与UDE/RPS等基础设施，实现了高内聚、低耦合的业务组件体系。通过RQL批量查询与严格的删除校验，保障了性能与数据一致性。开发者可基于本文档快速集成与扩展各类业务组件。

## 附录

### API调用示例（示例路径）
- 查询用户状态
  - 方法：GET
  - 路径：/QueryUserStatus
  - 参数：username（必填）
  - 响应：用户状态Map
  - 参考路径：[QueryUserStatus.groovy:40-45](file://bzc/公共资源管理/人员管理/人员信息/QueryUserStatus.groovy#L40-L45)

- 保存默认厂区
  - 方法：POST
  - 路径：/UserArea
  - 请求体：selectedValue（厂区编号）
  - 响应：value或areaNo
  - 参考路径：[UserArea.groovy:206-211](file://bzc/公共资源管理/人员管理/人员信息/UserArea.groovy#L206-L211)

- 保存包装工艺路线
  - 方法：POST
  - 路径：/PackageProcessRouteSave
  - 请求体：processRouteNo、processRouteName、notes、areaNo、_id（可选）
  - 响应：保存/更新后的对象
  - 参考路径：[PackageProcessRouteSave.groovy:29-32](file://bzc/公共资源管理/工艺建模/包装工艺路线/PackageProcessRouteSave.groovy#L29-L32)

- 删除包装工步（单点/批量）
  - 方法：POST
  - 路径：/PackagingStepDel
  - 请求体：workStepNo、workStepName、_data（批量时）
  - 响应：SysResult.OK
  - 参考路径：[PackagingStepDel.groovy:40-43](file://bzc/公共资源管理/工艺建模/包装工步信息/PackagingStepDel.groovy#L40-L43)

### 参数传递机制与序列化
- GET参数：通过SysHelper.getRequestParameters(request)提取，返回Map。
- POST请求体：通过SysHelper.getRequestBody(request)提取，返回Map。
- 响应：业务方法返回业务对象或Map；REST方法返回业务结果或SysResult.OK。

**章节来源**
- [bzc-base.skill:92-122](file://skills/architecture/bzc-base.skill#L92-L122)
- [QueryUserStatus.groovy:40-45](file://bzc/公共资源管理/人员管理/人员信息/QueryUserStatus.groovy#L40-L45)
- [UserArea.groovy:206-211](file://bzc/公共资源管理/人员管理/人员信息/UserArea.groovy#L206-L211)

### 错误处理策略与异常类型
- 异常类型：SysException，统一承载业务异常信息。
- 成功响应：SysResult.OK。
- 建议：所有异常捕获处记录日志，外部接口调用记录请求/响应，避免记录敏感信息与大对象。

**章节来源**
- [bzc-base.skill:140-145](file://skills/architecture/bzc-base.skill#L140-L145)
- [logging-standard.skill:43-61](file://skills/foundation/logging-standard.skill#L43-L61)