# 微流（Microflow）编辑避坑指南

改动 `.mf.json` 前必读。以下规则来自生产报工、成品入库申请、自动投料等微流改造实战，违反会导致重复创建或 StackOverflowError。

## 结构与引用

- 子流程定义内嵌在**主微流 JSON** 的 `objectExt.<uuid>` 里，顶层节点用 `uri: "/@/microflow/<uuid>"` 引用它。改子流程 = 改 `objectExt` 里的定义，上传主微流即生效。
- 节点、连线、端口都在 `content.layers[].models`；端口 `links` 数组与连线模型 `source/target` 必须双向一致，删连线要同步清理端口 `links` 里的引用。

## 引擎触发规则（最关键）

- **一个节点有几条入链，就会被执行几次**（每条入链独立触发）。给创建节点（method-c）加第二条入链 = 重复创建。
- **pass-all 连线传递整个 `_data`，含引擎内部状态 `fi`/`ti`**。内部状态传给下游 gateway 会自引用递归 → StackOverflowError（表现为 debug 里 gateway 的 `input` 出现 `fi`/`ti` 无限嵌套）。
- **子流程 `output.items` 不要引用 method-c 创建节点**：创建节点返回 `error`/`message` + 内部 `fi`/`ti`，会污染输出。输出应引用干净的查询/直通节点，或让 `output.items` 留空。
- **创建类节点放旁路**：主数据流保持原连线，把创建子流程做成无出链的 side branch，与参考微流 `bar_code_scan_submit` 的 `isSingleOrder_true` 结构一致。

## 引擎触发规则（成品入库申请 014 补充）

- **跨级"传字段"直连 = 第二条执行入链，下游子流被重复执行**：查询节点（如 `查询所有申请明细`）的 `o_workCenter` 直连到多层之后子流节点（如 `开始处理完工检验数据`）的 `i_workCenter` 输入端口（`pass-single`，看似只传数据），引擎仍把它当作第二条入链 → 子流被执行 2 次。典型症状：FQC 先创建 50，第二次执行查到已存在记录后累加成 100（debug 里同一 uri 出现 2 次）。
- **修复方式**：删掉跨级直连，字段走主链路透传——gateway 的 `pass-all` 边把整个 `_data`（含 workCenter/mfgOrderCode/process）带给子流，子流 input schema 用 `styles=''`（pass-all `_data` 同名绑定）即可收到字段。删除连线时必须同步清理目标端口 `links` 数组里的引用。
- **验证**：改完上传后，debug 重跑并统计 `开始处理完工检验数据` uri 调用次数应为 1，FQC `inspectionQty` 不再翻倍。

## 端口绑定

- `flow-io`：从子流程/流输入按同名取值。
- 无样式字段端口：从连线带过来的 `_data` 按同名取值。
- `port-assignment`：显式表达式（如 `${_data.unit}`、`${sys.today()}`）。
- **端口级 link 绑定的是源端口字段值，经常取不到**（如 `Material.o_unit → MID.i_unit` 会得 null）。
- 创建节点入链应指向 `i__data` 数据端口（`port-extra` Map, pass-all），字段值靠 `flow-io`/`asFlowIO` 或 `_data.xxx` 绑定（参考 `scan_submit` 里 StockDataFreeze 的写法）。

## 端口绑定补充（自动投料实战新增）

- **表达式引擎不支持 `?.` 安全导航**：`${ti._id?.toString()}` 直接报 EVAL_ERROR（`Encountered '.' at line 1, column 10`）。转字符串需求不要写 `?.toString()`，直接取字段 `${ti._id}`（参考里 stockDataId 就是 Long 类型）。
- **`ti.xxx` 在输出端口表达式里 = 节点输入数据**（含 port-extra 输入字段），不是创建后的记录。例：`load_available_stock` 的 `o_usedQty = ${ti._usedQty}` 取的是它自己的输入 `_usedQty`；`MID.o_stockDataId = ${ti._stockDataId}` 取 MID 输入里的 `_stockDataId`。
- **port-extra 字段命名规则**：输入端口 `i__xxx` 进到节点输入数据后字段名是 `_xxx`（下划线前缀）；输出端口 `o_xxx` 输出字段名是 `xxx`。搬运上游字段用：加输入端口 `i__stockDataId`（`port-extra port-assignment`，`${_data._id}`）→ 输入数据得到 `_stockDataId`；加输出端口 `o_stockDataId`（`port-extra port-assignment`，`${ti._stockDataId}`）→ 输出数据得到 `stockDataId`。
- **method-c 创建节点的输入载荷只包含声明过的输入端口字段**：即使 pass-all `_data` 里有 `_id`，没声明输入端口也会丢，`ti._id` 取到 null。要从上游带额外字段（如库存ID）到创建节点，必须显式加 port-extra 输入端口。
- **字段取值优先级**：`flow-io`/`asFlowIO` = 子流程输入按同名取；无样式字段端口 = pass-all `_data` 按同名取；`port-assignment` = 显式表达式；端口级 link = 源端口字段值（经常取不到）。创建节点入链指向 `i__data`（port-extra Map, pass-all）。
- **StockDataFreeze 冻结写法**：`i_fromDomain='MaterialInputDetails'`（port-assignment 字面量）、`i_keyId=${_data._id}`（创建节点 MID 的 _id）、`i_stockDataId` 必须指向 CommonStockData._id（null 会报"库存ID不可为空！"）、`i_qty` 用 `_data.qty`（= 冻结数量）、`i_location/i_lotNo/i_material/...` 无样式按 `_data` 同名取。
- **冻结落库效果**：创建 StockDataFreeze 同时生成 StockDataFreezeRecord（operationType=C），CommonStockData.frozenQty 增加；删除 StockDataFreeze 会生成 op=D 记录并回滚 frozenQty。
- **清理顺序**：先删 StockDataFreezeRecord 再删 StockDataFreeze，否则删 freeze 会再生成一批 op=D 记录（孤儿数据）。
- **Groovy 诊断脚本**：同一方法作用域里 `def qs` 不能重复声明（MultipleCompilationErrorsException），用不同变量名。
- **查询类 node 的 flow-io 端口**：`i_material`/`i_materialVersion`/`i__usedQty` 要用 `flow-io`（asFlowIO 绑子流程入参名，如 `usedQty`），否则引擎把前一条链的输出当输入，缺失 material/version。

## 调试与验证

- 执行加 `--debug`（即 `_debug=true&_limit=-1&_step=false`），返回 `debug.invokes` 完整调用树；对比改动前后同一 URI 的调用次数（是否重复创建）、gateway 输入是否干净。
- StackOverflowError 的 debug 响应可能是深度递归 JSON，`json.load` 会 RecursionError，直接用文本搜索 `StackOverflow` 定位。
- 微流执行会真实落库（投入明细/报工明细/出库单等），测试后写临时 Groovy 诊断脚本清理，避免脏数据。
