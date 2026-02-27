# TestSpec 公共约定

## 当前变更目录定位规则

所有 testspec-* skill 共享以下规则来确定「当前变更目录」：

1. 若用户指定了变更名 → `testspec/changes/<name>/`
2. 若未指定，检查 `testspec/changes/` 下有几个**非 archive** 子目录：
   - 仅 1 个 → 自动使用该目录
   - 多个 → 列出选项，询问用户
   - 0 个 → 提示用户先执行 testspec-new 创建变更

## 流程概览

```
testspec-new → testspec-analysis → testspec-points → testspec-generate
  创建变更       需求深度分析         提炼测试要点       生成测试用例
```

每个步骤的产物是下一步骤的输入。跳步执行时（如直接从 new 到 points），中间产物按默认策略生成。

## 目录结构

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
