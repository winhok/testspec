---
name: testspec-generate
description: TestSpec 生成测试用例 - 根据测试点（specs/*.md）生成完整测试用例并导出 Excel 或 XMind。当用户要生成用例、执行 testspec-generate Excel 或 testspec-generate XMind 时使用。对应流程中的「生成测试用例」步骤。不依赖外部技能，使用内置脚本完成生成。
---

# testspec-generate：用例生成

## 职责

读取当前变更的 `specs/*.md`（测试点），根据用户指定的格式（Excel 或 XMind）直接生成测试用例文件，输出到当前变更的 `artifacts/` 目录。若存在 `strategy.md` 可参考其测试类型、层级与通过标准；否则使用默认策略（测试类型以功能为主，类型：正向/负向/边界/异常，优先级 P0/P1/P2，通过标准为用例通过）。不依赖 excel-test-case-generator、xmind-test-case-generator 等外部技能，使用本技能内置脚本完成生成。

## 当前变更目录

参见 `.claude/skills/testspec-shared/common.md` 中的「当前变更目录定位规则」。

## 输出格式

- **Excel**：生成 .xlsx 文件，包含用例编号、用例名称、前置条件、测试步骤、预期结果、优先级等标准字段。
- **XMind**：生成 .xmind 思维导图（XMind 8 格式，兼容 XMind 桌面版打开），按功能模块组织，包含正向用例、负向用例、边界值用例、异常用例等分类。

可同时生成两种格式，如 testspec-generate Excel,XMind。

## 执行步骤

1. **确定当前变更目录**（按上规则）。
2. **读取上下文**：读取 `specs/*.md`（必须）；若存在 `strategy.md`、`requirements-analysis.md` 或 `proposal.md` 可一并读取以保持策略与优先级一致，否则按默认策略展开。
3. **从 specs 提取测试用例**：解析每个 spec 文件中的「场景与验收条件」，将其转换为结构化测试用例列表。每个用例包含：
   - 功能/模块（来自 spec 文件名或场景概述）
   - 用例名称
   - 类型：正向 / 负向 / 边界 / 异常
   - 前置条件、步骤、预期结果
   - 优先级：P0 / P1 / P2
4. **生成 testcases.json**：在变更目录或 artifacts/ 下写入临时 `testcases.json`，供脚本读取。格式示例：

   ```json
   [
     {
       "feature": "登录",
       "name": "正常登录-有效账号密码",
       "type": "正向",
       "preconditions": "系统已启动，用户已注册",
       "steps": "1. 打开登录页\n2. 输入正确账号密码\n3. 点击登录",
       "expected_result": "登录成功，跳转首页",
       "priority": "P0"
     }
   ]
   ```

5. **调用生成脚本**：
   - **Excel**：执行
     ```powershell
     python .claude/skills/testspec-generate/scripts/generate_excel.py --input <变更目录>/testcases.json --output <变更目录>/artifacts/<name>_cases.xlsx
     ```
   - **XMind**：执行
     ```powershell
     python .claude/skills/testspec-generate/scripts/generate_xmind.py --input <变更目录>/testcases.json --output <变更目录>/artifacts/<name>_cases.xmind --title "测试用例"
     ```
6. **清理**：可删除临时 testcases.json，或保留供用户审查。
7. **告知用户**：列出生成的文件路径及简要说明。

## 依赖

- **Excel**：需要 `openpyxl`（`pip install openpyxl`）
- **XMind**：无额外依赖，使用 XMind 8 格式（content.xml + manifest/styles/meta）生成，兼容 XMind 桌面版打开

若 Excel 生成失败且提示缺少 openpyxl，请运行 `pip install openpyxl`。

## 产物

- `testspec/changes/<name>/artifacts/<name>_cases.xlsx`（Excel 格式）
- `testspec/changes/<name>/artifacts/<name>_cases.xmind`（XMind 格式）

文件名可根据变更名或用户指定调整。
