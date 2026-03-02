# TestKit

一套 Agent Skills 测试工具集，用于在 AI 辅助下完成软件测试工作。兼容 Claude Code、Cursor、Trae 等支持 SKILL.md 的 AI 编码助手。

## 包含的 Skills

### testspec - 测试用例设计

从需求分析到测试用例生成的完整流程。

```
testspec-new → testspec-analysis → testspec-points → testspec-generate
  创建变更       需求深度分析         提炼测试要点       生成测试用例
```

| Skill | 说明 |
|-------|------|
| testspec-new | 新建测试工作，创建变更目录和测试提案（proposal.md） |
| testspec-analysis | 需求深度分析，识别测试风险和边界，产出 requirements-analysis.md |
| testspec-points | 从分析结论中提炼测试点清单（specs/testpoints.md） |
| testspec-generate | 根据测试点生成完整测试用例，导出 Excel（.xlsx）或 XMind（.xmind） |

### api2jmx - API 文档转 JMX 测试脚本

根据 API 接口文档（OpenAPI/Swagger 或 Markdown 格式）自动生成 Apache JMeter 的 JMX 测试脚本。

- 支持 OpenAPI 3.0 / Swagger 2.0（YAML/JSON）
- 支持 Markdown 格式的 API 文档（多种常见格式）
- 生成包含 HTTP 请求、参数、断言的完整测试计划

## 安装

### Claude Code（推荐）

```
/plugin install testkit
```

安装后重启 Claude Code 加载新 skills。

### Cursor

通过 Settings UI：

1. 打开 Settings（`Cmd+Shift+J` / `Ctrl+Shift+J`）
2. 进入 Rules → Add Rule → Remote Rule (GitHub)
3. 输入：`https://github.com/winhok/testkit.git`

### Trae

1. 打开 Settings → Rules & Skills
2. 导入本仓库中 `skills/` 下各目录的 `SKILL.md` 文件

### 手动安装（通用）

```bash
# Claude Code
git clone git@github.com:winhok/testkit.git .claude/skills/testkit

# Cursor
git clone git@github.com:winhok/testkit.git .cursor/skills/testkit

# Trae
git clone git@github.com:winhok/testkit.git .trae/skills/testkit
```

### Python 依赖

```bash
# testspec 生成 Excel 格式用例
pip install openpyxl

# api2jmx 解析 YAML 格式 OpenAPI 文档
pip install pyyaml
```

## 使用

### testspec

```
testspec-new 用户登录
testspec-analysis
testspec-points
testspec-generate Excel
testspec-generate XMind
```

### api2jmx

```
api2jmx openapi.yaml
api2jmx api_doc.md
```

## License

MIT
