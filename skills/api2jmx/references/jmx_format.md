# JMX 格式说明

## 概述

JMX（JMeter eXtensible Markup Language）是 Apache JMeter 测试计划的 XML 格式文件。本文档说明 JMX 文件的基本结构和主要元素。

## JMX 文件结构

### 基本结构

```xml
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6">
  <hashTree>
    <TestPlan>
      <!-- 测试计划配置 -->
    </TestPlan>
    <hashTree>
      <!-- 测试计划内容 -->
    </hashTree>
  </hashTree>
</jmeterTestPlan>
```

## 主要元素

### 1. TestPlan（测试计划）

测试计划的根元素，包含全局配置。

**主要属性：**
- `testname`: 测试计划名称
- `enabled`: 是否启用

**主要配置：**
- `TestPlan.functional_mode`: 功能模式（通常为 false）
- `TestPlan.serialize_threadgroups`: 序列化线程组（通常为 false）
- `TestPlan.arguments`: 用户定义变量

### 2. ThreadGroup（线程组）

定义并发用户和循环行为。

**主要属性：**
- `testname`: 线程组名称
- `enabled`: 是否启用

**主要配置：**
- `ThreadGroup.num_threads`: 线程数（并发用户数）
- `ThreadGroup.ramp_time`: 启动时间（秒）
- `ThreadGroup.scheduler`: 是否启用调度器
- `LoopController.loops`: 循环次数（-1 表示永远）

### 3. HTTPSamplerProxy（HTTP 请求）

HTTP 请求采样器。

**主要属性：**
- `testname`: 请求名称
- `enabled`: 是否启用

**主要配置：**
- `HTTPSampler.domain`: 域名
- `HTTPSampler.port`: 端口
- `HTTPSampler.protocol`: 协议（http/https）
- `HTTPSampler.path`: 路径
- `HTTPSampler.method`: HTTP 方法（GET、POST、PUT、DELETE 等）
- `HTTPSampler.follow_redirects`: 是否跟随重定向
- `HTTPSampler.use_keepalive`: 是否使用 Keep-Alive
- `HTTPSampler.postBodyRaw`: 是否使用原始请求体

### 4. ResponseAssertion（响应断言）

响应断言，用于验证响应内容。

**主要配置：**
- `Assertion.test_field`: 测试字段
  - `Assertion.response_code`: 响应代码
  - `Assertion.response_message`: 响应消息
  - `Assertion.response_headers`: 响应头
  - `Assertion.response_data`: 响应数据
- `Assertion.test_type`: 测试类型
  - `1`: 包含
  - `2`: 等于
  - `8`: 匹配（正则表达式）
  - `16`: 不匹配
- `Asserion.test_strings`: 测试字符串列表

### 5. JSONPathAssertion（JSON 路径断言）

JSON 路径断言，用于验证 JSON 响应。

**主要配置：**
- `JSON_PATH`: JSON 路径表达式
- `EXPECTED_VALUE`: 期望值
- `JSONVALIDATION`: 是否验证 JSON
- `EXPECT_NULL`: 是否期望 null
- `INVERT`: 是否反转
- `ISREGEX`: 是否使用正则表达式

### 6. HeaderManager（请求头管理器）

管理 HTTP 请求头。

**主要配置：**
- `HeaderManager.headers`: 请求头集合
  - `Header.name`: 请求头名称
  - `Header.value`: 请求头值

### 7. CSVDataSet（CSV 数据集配置）

CSV 数据驱动配置。

**主要配置：**
- `filename`: CSV 文件路径
- `variableNames`: 变量名（逗号分隔）
- `delimiter`: 分隔符
- `ignoreFirstLine`: 是否忽略第一行
- `recycle`: 是否循环使用
- `stopThread`: 是否在文件结束时停止线程

### 8. 监听器（Listeners）

用于查看和报告测试结果。

**常见监听器：**
- `ViewResultsTree`: 查看结果树（详细结果）
- `SummaryReport`: 聚合报告（汇总统计）
- `GraphVisualizer`: 图形结果（响应时间图）
- `StatVisualizer`: 统计报告（详细统计）

## 元素层次结构

```
TestPlan
└── hashTree
    └── ThreadGroup
        └── hashTree
            ├── HTTPSamplerProxy
            ├── HeaderManager
            ├── ResponseAssertion
            ├── JSONPathAssertion
            ├── CSVDataSet
            └── Listeners
```

## 命名空间和属性

JMX 文件使用特定的属性来标识元素类型：

- `guiclass`: GUI 类名
- `testclass`: 测试类名
- `testname`: 元素名称
- `enabled`: 是否启用

## 示例

### 简单的 HTTP GET 请求

```xml
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" 
                 testname="GET /api/users" enabled="true">
  <stringProp name="HTTPSampler.domain">api.example.com</stringProp>
  <stringProp name="HTTPSampler.port">443</stringProp>
  <stringProp name="HTTPSampler.protocol">https</stringProp>
  <stringProp name="HTTPSampler.path">/api/users</stringProp>
  <stringProp name="HTTPSampler.method">GET</stringProp>
</HTTPSamplerProxy>
```

### 响应断言

```xml
<ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" 
                  testname="Status Code 200" enabled="true">
  <collectionProp name="Asserion.test_strings">
    <stringProp name="49586">200</stringProp>
  </collectionProp>
  <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
  <intProp name="Assertion.test_type">2</intProp>
</ResponseAssertion>
```

## 注意事项

1. **XML 格式**：JMX 文件必须是有效的 XML 格式
2. **编码**：建议使用 UTF-8 编码
3. **元素顺序**：某些元素的顺序可能影响执行结果
4. **hashTree**：每个主要元素后通常需要一个 `hashTree` 元素来包含子元素
5. **版本兼容性**：不同版本的 JMeter 可能对 JMX 格式有不同要求

## 参考资源

- [Apache JMeter 官方文档](https://jmeter.apache.org/usermanual/)
- [JMeter 测试计划结构](https://jmeter.apache.org/usermanual/test_plan.html)
