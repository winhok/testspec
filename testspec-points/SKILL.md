---
name: testspec-points
description: TestSpec 测试点 - 生成「要测什么」的要点清单（一个文件）。当用户要写测试点、或执行 testspec points 时使用。产出简短测试点列表，供 testspec-generate 再展开为完整测试用例。与测试用例区分：测试点不写完整步骤/预期，只列覆盖要点。
---

# testspec-points：测试点

## 职责

从需求分析结论中**提炼**出简短的测试覆盖要点清单，作为 testspec-generate 的直接输入。

**与 analysis 的关系**：analysis 做深度拆解（等价类、边界值、状态迁移、风险点），points 是 analysis 的"精华版"——把分析结论转化为一条条简短的"要验什么"。如果已有 `requirements-analysis.md`，points 应该从中提炼而非重复分析；如果没有 analysis，points 按默认策略直接从 `proposal.md` 提炼。

**与测试用例的区别**：测试点只说"验什么"（一句话），不写具体步骤、预期结果、优先级——这些由 testspec-generate 展开补全。

## 当前变更目录

参见 `.claude/skills/testspec-shared/common.md` 中的「当前变更目录定位规则」。

## 执行步骤

1. **确定当前变更目录**。
2. **读取上下文**：
   - 优先读 `requirements-analysis.md`（从中提炼）
   - 若不存在，读 `proposal.md`（直接提炼）
3. **生成 specs/testpoints.md**：

### 提炼原则

- 每条测试点**一句话**，格式：`- <要验什么>（类型）`
- 类型标注：正向 / 负向 / 边界 / 异常 / 兼容性，帮助 generate 展开时确定用例类型
- 按功能模块分组
- 确保覆盖 analysis 中识别的所有风险点和边界值
- analysis 中的"待澄清项"在此标注为待确认

### 产出结构

```markdown
# 测试点：<被测对象>

## 概述
<一两句话：测试范围和重点>

## 模块 N：<模块名>

### <子功能>
- <测试要点 1>（正向）
- <测试要点 2>（边界）
- <测试要点 3>（异常）
```

4. **告知用户**：产出路径及下一步可执行 testspec-generate。

## 产物

- `testspec/changes/<name>/specs/testpoints.md`
