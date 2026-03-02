import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


def _venv_python() -> str:
    return sys.executable


def _xmind_script() -> str:
    pkg_root = Path(__file__).resolve().parents[1]
    return str(pkg_root / "scripts" / "generate_xmind.py")


class TestSmokeTestCase(unittest.TestCase):
    def test_smoke_testcase_appears_first(self):
        """冒烟用例应该在 XMind 中排在第一位"""
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            input_path = td_path / "testcases.json"
            output_path = td_path / "out.xmind"

            testcases = [
                {
                    "id": "需求A_202602280001",
                    "title": "登录_凭据验证_正确凭据登录成功",
                    "feature": "登录",
                    "type": "冒烟",
                    "priority": "P1",
                    "steps": "1、输入正确的账号密码\\n2、点击登录",
                    "expected_result": "1、登录成功",
                },
                {
                    "id": "需求A_202602280002",
                    "title": "登录_凭据验证_错误凭据登录失败",
                    "feature": "登录",
                    "type": "负向",
                    "priority": "P2",
                    "steps": "1、输入错误的账号密码\\n2、点击登录",
                    "expected_result": "1、提示登录失败",
                },
            ]
            input_path.write_text(json.dumps(testcases, ensure_ascii=False), encoding="utf-8")

            subprocess.check_call(
                [
                    _venv_python(),
                    _xmind_script(),
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                    "--title",
                    "测试用例",
                ],
                timeout=30,
            )

            with zipfile.ZipFile(output_path, "r") as zf:
                content = zf.read("content.xml").decode("utf-8")

            # 验证冒烟用例存在
            self.assertIn("冒烟用例", content)
            # 验证负向用例存在
            self.assertIn("负向用例", content)
            # 验证冒烟用例在负向用例之前（通过检查索引位置）
            smoke_pos = content.find("冒烟用例")
            negative_pos = content.find("负向用例")
            self.assertLess(smoke_pos, negative_pos, "冒烟用例应该在负向用例之前")


if __name__ == "__main__":
    unittest.main()
