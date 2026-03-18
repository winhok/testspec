---
name: testspec-points
description: TestSpec 测试点（流程第 3 步）- 从需求分析中提炼「要测什么」的简短要点清单，产出 specs/testpoints.md。当用户要「写测试点」「提取测试要点」「列出要验证的内容」或执行 testspec-points / testspec points 时使用。也适用于用户说「这个功能要测哪些点」「帮我列测试清单」的场景。与测试用例区分：测试点只列验证目标（What），不写操作步骤（How）。产出供 testspec-generate 展开为完整测试用例。
---

# testspec-points：测试点

## 职责

从需求分析结论中**提炼**出简短的测试覆盖要点清单，作为 testspec-generate 的直接输入。

**与 analysis 的关系**：analysis 做深度拆解（等价类、边界值、状态迁移、风险点），points 是 analysis 的"精华版"——把分析结论转化为一条条简短的"要验什么"。如果已有 `requirements-analysis.md`，points 应该从中提炼而非重复分析；如果没有 analysis，points 按默认策略直接从 `proposal.md` 提炼。

---

## 核心定义

### 测试点（Test Point）

- 代表一个**可独立验证的业务或功能验证目标**
- 关注系统行为、业务规则或质量属性
- 不描述"如何测试"，仅描述"验证什么"

### 测试点 ≠ 测试用例 ≠ 校验点

- **测试点**：验证目标（What）
- **测试用例**：操作步骤（How）
- **校验点**：字段 / 状态 / 断言（Check）

## 测试点分类

每个测试点必须归属以下一种类型：

- **功能验证**（Functional）
- **边界验证**（Boundary）
- **异常验证**（Exception）
- **集成验证**（Integration）
- **非功能性验证**（Non-Functional）

## TP_ID 生成规则

格式：`TP_<MODULE>_<FEATURE>_<SEQ>`

- MODULE：2-5 位大写缩写（来自文档顶部「命名字典」）
- FEATURE：2-10 位大写缩写（来自文档顶部「命名字典」）
- 缩写不得临时发明；同一模块/功能点必须长期稳定复用同一缩写
- SEQ 范围按类别：
  - 001–099：Functional
  - 100–199：Boundary
  - 200–299：Exception
  - 300–399：Integration
  - 400–499：Non-Functional

## 优先级规则

每个测试点必须标注优先级：

- **P1**：核心业务链路、权限、安全、资金、数据安全
- **P2**：常规业务功能、重要边界和异常
- **P3**：低频功能、边缘场景、体验类验证

## 粒度控制

- 一个测试点只验证一个业务意图
- 不以字段为单位拆分测试点
- 不以接口参数为单位拆分测试点
- 出现"且 / 并且 / 同时"时，评估是否拆分为多个测试点
- 测试点应长期稳定，不随实现细节变化

## 命名契约（points ↔ generate，必须遵守）

详见 `../testspec-shared/naming-contract.md`。生成 testpoints.md 后必须按其中的自检清单逐项验证。

---

## 禁止事项（严格）

- 不包含操作步骤（点击、输入、跳转等）
- 不包含具体测试数据
- 不包含接口字段名或表结构
- 不描述实现方式（Redis、MQ、数据库等）
- 不生成测试用例形式内容

---

## 当前变更目录

参见 `../testspec-shared/common.md` 中的「当前变更目录定位规则」。

## 执行步骤

1. **确定当前变更目录**。
2. **读取上下文**：
   - 优先读 `requirements-analysis.md`（从中提炼）
   - 若不存在，读 `proposal.md`（直接提炼）
3. **生成 specs/testpoints.md**：

### 写入策略（重要）

为确保大文件写入成功，按以下优先级执行：

1. **首选方案**：使用 Write 工具直接写入完整内容
2. **兜底方案**：如果 Write 失败，使用 Bash heredoc 写入：
   ```bash
   mkdir -p specs
   cat > "specs/testpoints.md" << 'EOF'
   <完整 Markdown 内容>
   EOF
   ```
3. **验证写入**：使用 Read 工具读取文件前 10 行，确认内容正确

### 提炼原则

- 按模块/功能点组织，并按类别分区（Functional / Boundary / Exception / Integration / Non-Functional）
- 每条测试点必须包含：TP_ID、测试点名称、验证要点、优先级（P1/P2/P3）、关联需求
- 确保覆盖 analysis 中识别的风险点和边界值
- 不确定项标注"需与产品确认"，优先级设为 P3，不补充假设性业务规则

### 输出质量要求

- 测试点必须完整覆盖需求
- 测试点之间不得重复
- 每个测试点必须可独立验证
- 测试点应可直接用于后续测试用例设计

### 默认行为

- 未特别说明时，按"最小充分覆盖"原则生成测试点
- 不主动扩展需求之外的业务场景
- 不推断实现细节

### 产出结构

```markdown
# 测试点：<被测对象>

## 概述
<一两句话说明本次测试覆盖范围与重点>

## 命名字典

### 模块字典
| 模块名称 | MODULE |
|---|---|
| <模块名称> | <2-5 位大写缩写> |

### 功能点字典
| 模块名称 | 功能点名称 | FEATURE |
|---|---|---|
| <模块名称> | <功能点名称> | <2-10 位大写缩写> |

### [模块名称]模块

#### [功能点名称]功能

##### 功能验证点 (Functional)

- TP_<MODULE>_<FEATURE>_001: <测试点名称（格式：{模块}_{功能点}_{验证意图}）>
  - 验证要点: <验证什么（What），不写步骤/数据>
  - 优先级: P1/P2/P3
  - 关联需求: <需求编号/段落>

##### 边界验证点 (Boundary)

##### 异常验证点 (Exception)

##### 集成验证点 (Integration)

##### 非功能性验证点 (Non-Functional)
```

4. **告知用户**：产出路径及下一步可执行 testspec-generate。

## 产物

- `testspec/changes/<name>/specs/testpoints.md`
