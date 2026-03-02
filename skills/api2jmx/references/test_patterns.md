# 测试模式说明

## 概述

本文档说明生成 JMX 测试脚本时使用的测试模式，包括正向用例、负向用例、边界值用例和异常用例的生成规则。

## 测试用例类型

### 1. 正向用例（Positive Test Cases）

正向用例验证 API 在正常条件下的行为。

**生成规则：**
- 使用所有必需参数
- 使用有效的参数值
- 期望响应状态码为 200（或文档中定义的成功状态码）
- 验证响应体结构（如果定义了响应 schema）

**示例：**
- GET /api/users?page=1&size=10
- POST /api/users (body: 有效的用户数据)
- PUT /api/users/1 (body: 有效的更新数据)

### 2. 负向用例（Negative Test Cases）

负向用例验证 API 在错误条件下的行为。

**生成规则：**
- 缺失必需参数
- 使用无效的参数值
- 使用错误的数据类型
- 期望响应状态码为 4xx 或 5xx

**常见场景：**
- 缺失必需参数：GET /api/users (缺少 page 参数)
- 无效参数值：GET /api/users?page=-1
- 类型错误：GET /api/users?page=abc
- 无效请求体：POST /api/users (body: 缺少必需字段)

### 3. 边界值用例（Boundary Test Cases）

边界值用例验证 API 在边界条件下的行为。

**生成规则：**
- 最小值：使用参数的最小允许值
- 最大值：使用参数的最大允许值
- 最小值-1：使用小于最小值的值（期望错误）
- 最大值+1：使用大于最大值的值（期望错误）
- 空值：使用空字符串或 null

**示例：**
- 字符串长度边界：name 字段 minLength=1, maxLength=100
  - 正常：name="a" (1字符), name="a"*100 (100字符)
  - 边界：name="" (空字符串), name="a"*101 (超长)
- 数值边界：age 字段 minimum=18, maximum=100
  - 正常：age=18, age=100
  - 边界：age=17, age=101

### 4. 异常用例（Exception Test Cases）

异常用例验证 API 在异常条件下的行为。

**生成规则：**
- SQL 注入尝试
- XSS 攻击尝试
- 特殊字符和 Unicode 字符
- 超长字符串
- 格式错误的数据

**示例：**
- SQL 注入：name="1' OR '1'='1"
- XSS 攻击：name="<script>alert('XSS')</script>"
- 特殊字符：name="测试@#$%^&*()"
- 超长字符串：name="a"*10000

## 参数化模式

### 1. 变量参数化

使用 JMeter 变量来参数化请求。

**实现方式：**
- 在测试计划中定义用户变量
- 在请求中使用 `${variable_name}` 引用变量

**示例：**
```xml
<TestPlan>
  <elementProp name="TestPlan.arguments">
    <collectionProp name="Arguments.arguments">
      <elementProp name="base_url" elementType="Argument">
        <stringProp name="Argument.name">base_url</stringProp>
        <stringProp name="Argument.value">https://api.example.com</stringProp>
      </elementProp>
    </collectionProp>
  </elementProp>
</TestPlan>
```

### 2. CSV 数据驱动

使用 CSV 文件进行数据驱动测试。

**实现方式：**
- 创建 CSV 文件，包含测试数据
- 使用 CSVDataSet 配置读取 CSV 文件
- 在请求中使用 `${variable_name}` 引用 CSV 列

**CSV 文件示例：**
```csv
username,password,expected_status
user1,pass1,200
user2,pass2,200
invalid,invalid,401
```

**配置示例：**
```xml
<CSVDataSet guiclass="TestBeanGUI" testclass="CSVDataSet" 
           testname="CSV Data Set Config" enabled="true">
  <stringProp name="filename">test_data.csv</stringProp>
  <stringProp name="variableNames">username,password,expected_status</stringProp>
  <boolProp name="ignoreFirstLine">true</boolProp>
  <boolProp name="recycle">true</boolProp>
</CSVDataSet>
```

## 性能测试配置

### 1. 线程组配置

**关键参数：**
- `num_threads`: 并发用户数
- `ramp_time`: 启动时间（所有用户启动所需时间）
- `loops`: 循环次数（-1 表示永远）

**示例配置：**
- 轻量级测试：10 线程，10 秒启动，1 次循环
- 中等负载：50 线程，30 秒启动，5 次循环
- 压力测试：100 线程，60 秒启动，-1 次循环（持续运行）

### 2. 定时器（Timers）

在请求之间添加延迟，模拟真实用户行为。

**常见定时器：**
- `ConstantTimer`: 固定延迟
- `RandomTimer`: 随机延迟
- `UniformRandomTimer`: 均匀随机延迟

## 断言模式

### 1. 响应状态码断言

验证 HTTP 响应状态码。

**模式：**
- 等于：期望状态码为 200
- 包含：期望状态码在 [200, 201, 204] 中
- 不匹配：期望状态码不是 500

### 2. 响应体断言

验证响应体内容。

**模式：**
- 包含：响应体包含特定字符串
- 匹配：响应体匹配正则表达式
- JSON 路径：使用 JSONPath 验证 JSON 响应

### 3. 响应时间断言

验证响应时间。

**模式：**
- 小于：响应时间 < 1000ms
- 大于：响应时间 > 100ms

## 监听器配置

### 1. 查看结果树（ViewResultsTree）

显示每个请求的详细结果。

**用途：**
- 调试测试脚本
- 查看请求和响应详情
- 验证断言结果

**注意：** 生产环境应禁用，影响性能。

### 2. 聚合报告（SummaryReport）

显示测试结果的汇总统计。

**包含信息：**
- 请求总数
- 平均响应时间
- 最小/最大响应时间
- 错误率
- 吞吐量

### 3. 图形结果（GraphVisualizer）

以图形方式显示响应时间趋势。

**用途：**
- 可视化性能趋势
- 识别性能瓶颈
- 分析响应时间分布

## 最佳实践

1. **测试数据准备**
   - 使用独立的测试数据
   - 避免使用生产数据
   - 准备足够的数据覆盖各种场景

2. **断言设计**
   - 验证关键业务逻辑
   - 不要过度断言
   - 使用有意义的断言消息

3. **性能测试**
   - 逐步增加负载
   - 监控系统资源
   - 分析瓶颈点

4. **结果分析**
   - 关注错误率
   - 分析响应时间分布
   - 识别性能问题

5. **维护性**
   - 使用变量提高可维护性
   - 添加注释说明
   - 定期更新测试脚本
