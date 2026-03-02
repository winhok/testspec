# 自然语言输入模式 — AI 解析规则

## 概述

本文档定义了 AI 如何将用户粘贴的原始 API 数据（curl 命令、HTTP 请求/响应、Postman 导出）解析为标准 `endpoints.json` 格式，以供 `generate_jmx.py` 生成 JMX 测试脚本。

## 支持的输入格式

### 1. curl 命令

**识别特征**：以 `curl` 开头

**提取规则**：

| 元素 | 提取方式 |
|------|---------|
| method | `-X` / `--request` 参数；无则默认 GET（有 `-d` 时为 POST） |
| URL | 第一个非选项参数；拆分为 base_url（scheme+host+port）、path、query |
| headers | `-H` / `--header` 参数（可多个） |
| requestBody | `-d` / `--data` / `--data-raw` / `--data-binary` 参数内容 |

**示例输入**：
```bash
curl -X POST 'https://api.example.com/api/users?source=web' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer token123' \
  -d '{"name": "John", "email": "john@test.com"}'
```

**解析结果**：
```json
{
  "base_url": "https://api.example.com",
  "endpoints": [{
    "path": "/api/users",
    "method": "POST",
    "summary": "POST /api/users",
    "parameters": [
      {"name": "source", "in": "query", "default": "web"},
      {"name": "Authorization", "in": "header", "default": "Bearer token123"}
    ],
    "requestBody": {
      "content": {
        "application/json": {
          "example": {"name": "John", "email": "john@test.com"}
        }
      }
    }
  }]
}
```

### 2. Raw HTTP 请求/响应

**识别特征**：包含 `HTTP/1.1` 或 `HTTP/2`

**提取规则**：

| 元素 | 提取方式 |
|------|---------|
| method + path | 请求行第一行（如 `POST /api/users HTTP/1.1`） |
| base_url | `Host` 头（加上协议推断） |
| headers | 请求头各行（`Key: Value` 格式） |
| requestBody | 请求空行之后的内容 |
| assertions.status_code | 响应状态行（如 `HTTP/1.1 201 Created`） |
| response example | 响应体（空行之后的 JSON） |

**示例输入**：
```
POST /api/users HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer token123

{"name": "John", "email": "john@test.com"}

HTTP/1.1 201 Created
Content-Type: application/json

{"id": 42, "name": "John", "email": "john@test.com"}
```

### 3. Postman Collection v2.1

**识别特征**：JSON 格式，包含 `info` 和 `item` 字段

**提取规则**：

| 元素 | 提取方式 |
|------|---------|
| endpoints | `item[].request` 逐个提取 |
| method | `request.method` |
| path | `request.url.path` 拼接为 `/path/segments` |
| base_url | `request.url.host` 拼接 + protocol |
| query | `request.url.query` 数组 |
| headers | `request.header` 数组 |
| requestBody | `request.body.raw`（JSON 解析后放入 example） |
| response example | `response[].body`（取第一个成功响应） |

## endpoints.json Schema

```json
{
  "base_url": "string (required) — API 基础 URL，如 https://api.example.com",
  "test_plan_name": "string (optional) — 测试计划名称，默认 'API Test Plan'",
  "num_threads": "integer (optional) — 线程数，默认 1",
  "ramp_time": "integer (optional) — 启动时间（秒），默认 1",
  "loops": "integer (optional) — 循环次数，默认 1",
  "endpoints": [
    {
      "path": "string (required) — 接口路径，如 /api/users",
      "method": "string (required) — HTTP 方法，如 GET/POST/PUT/DELETE",
      "summary": "string (optional) — 接口简要描述",
      "parameters": [
        {
          "name": "string — 参数名",
          "in": "string — 位置: path | query | header",
          "default": "string — 默认值"
        }
      ],
      "requestBody": {
        "content": {
          "application/json": {
            "example": "object — 请求体示例"
          }
        }
      },
      "responses": {
        "<status_code>": {
          "description": "string",
          "content": {
            "application/json": {
              "example": "object — 响应体示例"
            }
          }
        }
      },
      "assertions": [
        {"type": "status_code", "status_code": "string — 期望状态码"},
        {"type": "json_path", "json_path": "string — JSONPath 表达式", "expected_value": "any | null"},
        {"type": "response_contains", "contains": "string — 期望包含的字符串"}
      ]
    }
  ]
}
```

## 断言生成策略

### 显式模式（endpoints 中包含 `assertions` 字段）

按用户定义的 assertions 数组原样生成：

- `status_code` → JMeter ResponseAssertion（response_code 字段，EQUALS 匹配）
- `json_path` → JMeter JSONPathAssertion（存在性或值匹配）
- `response_contains` → JMeter ResponseAssertion（response_data 字段，CONTAINS 匹配）

### 自动模式（无 `assertions` 字段）

1. 默认添加 status_code=200 断言
2. 从 `responses.200.content.application/json.example` 的顶层 key 生成 JSONPath 存在性断言（上限 10 个）

## AI 解析注意事项

1. **多 curl 命令**：用户可能粘贴多条 curl，每条生成一个 endpoint
2. **不完整信息**：缺少 Host/base_url 时，询问用户或使用 `http://localhost:8080`
3. **敏感信息**：保留 Authorization 头等认证信息作为参数默认值，但在 summary 中不暴露 token 内容
4. **Content-Type 推断**：有 JSON body 时自动推断 `application/json`
5. **query 参数**：从 URL 的 `?key=value` 部分提取为 parameters（in=query）
