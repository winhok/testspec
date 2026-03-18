---
name: testspec-new
description: TestSpec 新建测试工作（流程第 1 步）- 创建测试变更目录并编写 proposal.md，关联需求文档。当用户要「新建测试」「开始测试」「创建测试变更」「建一个测试项目」或执行 testspec-new / testspec new 时使用。也适用于用户说「我要测 XXX 功能」「帮我准备测试」「有个新需求要测」的场景——如果尚无 testspec/changes/ 目录，这是流程的起点。产出 testspec/changes/<name>/ 目录结构及 proposal.md。
---

# testspec-new：新建测试工作（需求文档）

## 职责

新建一次 TestSpec 测试工作：创建变更目录并编写测试提案初稿，在 proposal 中**关联或引用需求文档**（PRD、用户故事、接口说明等），对应流程中的「需求文档」步骤。

## 确定变更名

- 从用户输入中提取被测对象（功能名、模块名、版本号等）。
- 将名称规范为短名：英文或拼音，空格与特殊字符替换为 `-`（如「用户登录」→ `user-login`，`release 2.0` → `release-2.0`）。

## 执行步骤

1. **确保根目录存在**：若项目下没有 `testspec/changes/`，直接创建（`mkdir -p testspec/changes`）。
2. **创建变更目录**：`testspec/changes/<name>/`，以及子目录 `specs/`、`artifacts/`。
3. **编写 proposal.md**：在变更目录下创建 `proposal.md`。

   模板见 `../testspec-shared/artifact-templates.md` 中的「proposal.md」小节，核心字段：
   - 被测对象（功能/模块/版本）
   - **关联需求文档**：路径或链接（PRD、用户故事、接口文档等）
   - 测试目标与原因
   - 可选：关联的 OpenSpec

4. **告知用户**：变更目录路径及下一步可执行 testspec-analysis 或 testspec-points。

## 产物

- `testspec/changes/<name>/proposal.md`
- `testspec/changes/<name>/specs/`（空目录）
- `testspec/changes/<name>/artifacts/`（空目录）
