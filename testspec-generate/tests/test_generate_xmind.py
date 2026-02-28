import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


def _venv_python() -> str:
    repo_root = Path(__file__).resolve().parents[2]
    return str(repo_root / ".venv" / "bin" / "python")


def _xmind_script() -> str:
    pkg_root = Path(__file__).resolve().parents[1]
    return str(pkg_root / "scripts" / "generate_xmind.py")


class TestGenerateXMind(unittest.TestCase):
    def test_xmind_uses_title_when_name_missing(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            input_path = td_path / "testcases.json"
            output_path = td_path / "out.xmind"

            testcases = [
                {
                    "id": "需求A_202602280001",
                    "title": "登录_凭据验证_正确凭据登录成功",
                    "feature": "登录",
                    "type": "正向",
                    "priority": "P0",
                    "steps": "1、...",
                    "expected_result": "1、...",
                }
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
                ]
            )

            with zipfile.ZipFile(output_path, "r") as zf:
                content = zf.read("content.xml").decode("utf-8")

            self.assertIn("登录_凭据验证_正确凭据登录成功", content)
            self.assertIn("P0操作步骤：", content)
            self.assertIn("期望结果：", content)


if __name__ == "__main__":
    unittest.main()
