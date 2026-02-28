# TestSpec

一套 Agent Skills，用于在 AI 辅助下完成软件测试设计：从需求分析到测试用例生成。兼容 Claude Code、Cursor、Trae 等支持 SKILL.md 的 AI 编码助手。

## 流程

```
testspec-new → testspec-analysis → testspec-points → testspec-generate
  创建变更       需求深度分析         提炼测试要点       生成测试用例
```

每个步骤的产物是下一步骤的输入，也可跳步执行。

## Skills 一览

| Skill | 说明 |
|-------|------|
| testspec-new | 新建测试工作，创建变更目录和测试提案（proposal.md） |
| testspec-analysis | 需求深度分析，识别测试风险和边界，产出 requirements-analysis.md |
| testspec-points | 从分析结论中提炼测试点清单（specs/testpoints.md） |
| testspec-generate | 根据测试点生成完整测试用例，导出 Excel（.xlsx）或 XMind（.xmind） |

## 产物目录结构

```
testspec/changes/<name>/
├── proposal.md                # 测试提案（testspec-new）
├── requirements-analysis.md   # 需求分析（testspec-analysis）
├── specs/
│   └── testpoints.md          # 测试点（testspec-points）
└── artifacts/
    ├── <name>_cases.xlsx      # 测试用例 Excel（testspec-generate）
    └── <name>_cases.xmind     # 测试用例 XMind（testspec-generate）
```

## 安装

### Claude Code（推荐）

```
/plugin marketplace add winhok/testspec
/plugin install testspec
```

安装后重启 Claude Code 加载新 skills。

### Cursor

通过 Settings UI：

1. 打开 Settings（`Cmd+Shift+J` / `Ctrl+Shift+J`）
2. 进入 Rules → Add Rule → Remote Rule (GitHub)
3. 输入：`https://github.com/winhok/testspec.git`

### Trae

1. 打开 Settings → Rules & Skills
2. 导入本仓库中 `skills/` 下各目录的 `SKILL.md` 文件

### 手动安装（通用）

```bash
# Claude Code
git clone git@github.com:winhok/testspec.git .claude/skills/testspec

# Cursor
git clone git@github.com:winhok/testspec.git .cursor/skills/testspec

# Trae
git clone git@github.com:winhok/testspec.git .trae/skills/testspec
```

### Python 依赖

生成 Excel 格式用例时需要 `openpyxl`：

```bash
pip install openpyxl
```

## 使用

在 AI 编码助手中直接调用对应的 skill 名称即可，例如：

```
testspec-new 用户登录
testspec-analysis
testspec-points
testspec-generate Excel
testspec-generate XMind
```

## License

MIT

