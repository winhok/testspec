import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


def _venv_python() -> str:
    return sys.executable


def _jmx_script() -> str:
    pkg_root = Path(__file__).resolve().parents[1]
    return str(pkg_root / "scripts" / "generate_jmx.py")


def _write_endpoints(td_path: Path, data: dict) -> Path:
    p = td_path / "endpoints.json"
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return p


def _parse_jmx(path: Path) -> ET.Element:
    return ET.parse(str(path)).getroot()


class TestGenerateJmx(unittest.TestCase):

    def test_basic_get_endpoint(self):
        """最小 GET 端点生成有效 JMX。"""
        data = {
            "base_url": "https://api.example.com",
            "endpoints": [
                {"path": "/api/users", "method": "GET", "summary": "List users"}
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            input_path = _write_endpoints(td_path, data)
            output_path = td_path / "out.jmx"

            subprocess.check_call(
                [_venv_python(), _jmx_script(), "--input", str(input_path), "--output", str(output_path)],
                timeout=30,
            )

            root = _parse_jmx(output_path)
            self.assertEqual(root.tag, "jmeterTestPlan")
            # 应有一个 ThreadGroup
            thread_groups = root.findall(".//ThreadGroup")
            self.assertEqual(len(thread_groups), 1)
            self.assertIn("GET", thread_groups[0].get("testname", ""))
            # 应有 HTTPSamplerProxy
            samplers = root.findall(".//HTTPSamplerProxy")
            self.assertEqual(len(samplers), 1)

    def test_post_with_body_and_assertions(self):
        """POST + requestBody + 显式 assertions 正确生成。"""
        data = {
            "base_url": "https://api.example.com",
            "endpoints": [
                {
                    "path": "/api/users",
                    "method": "POST",
                    "summary": "Create user",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "example": {"name": "John"}
                            }
                        }
                    },
                    "assertions": [
                        {"type": "status_code", "status_code": "201"},
                        {"type": "json_path", "json_path": "$.id", "expected_value": None},
                        {"type": "response_contains", "contains": "John"},
                    ],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            input_path = _write_endpoints(td_path, data)
            output_path = td_path / "out.jmx"

            subprocess.check_call(
                [_venv_python(), _jmx_script(), "--input", str(input_path), "--output", str(output_path)],
                timeout=30,
            )

            root = _parse_jmx(output_path)
            # 应有 ResponseAssertion（status_code + response_contains = 2 个）
            response_assertions = root.findall(".//ResponseAssertion")
            self.assertEqual(len(response_assertions), 2)
            # 应有 JSONPathAssertion
            json_assertions = root.findall(".//JSONPathAssertion")
            self.assertEqual(len(json_assertions), 1)

    def test_thread_overrides_from_cli(self):
        """CLI 参数覆盖 JSON 中的配置。"""
        data = {
            "base_url": "https://api.example.com",
            "test_plan_name": "JSON Plan",
            "num_threads": 1,
            "ramp_time": 1,
            "loops": 1,
            "endpoints": [
                {"path": "/api/health", "method": "GET", "summary": "Health"}
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            input_path = _write_endpoints(td_path, data)
            output_path = td_path / "out.jmx"

            subprocess.check_call(
                [
                    _venv_python(), _jmx_script(),
                    "--input", str(input_path),
                    "--output", str(output_path),
                    "--name", "CLI Plan",
                    "--threads", "50",
                    "--ramp", "30",
                    "--loops", "5",
                ],
                timeout=30,
            )

            root = _parse_jmx(output_path)
            # 测试计划名称应为 CLI 参数
            test_plan = root.find(".//TestPlan")
            self.assertEqual(test_plan.get("testname"), "CLI Plan")
            # 线程数应为 50
            tg = root.find(".//ThreadGroup")
            num_threads_el = tg.find("stringProp[@name='ThreadGroup.num_threads']")
            self.assertEqual(num_threads_el.text, "50")
            ramp_el = tg.find("stringProp[@name='ThreadGroup.ramp_time']")
            self.assertEqual(ramp_el.text, "30")

    def test_auto_assertions_from_response_example(self):
        """无显式 assertions 时自动从 response example 生成 JSONPath 断言。"""
        data = {
            "base_url": "https://api.example.com",
            "endpoints": [
                {
                    "path": "/api/users/1",
                    "method": "GET",
                    "summary": "Get user",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "example": {"id": 1, "name": "John", "email": "john@test.com"}
                                }
                            },
                        }
                    },
                }
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            input_path = _write_endpoints(td_path, data)
            output_path = td_path / "out.jmx"

            subprocess.check_call(
                [_venv_python(), _jmx_script(), "--input", str(input_path), "--output", str(output_path)],
                timeout=30,
            )

            root = _parse_jmx(output_path)
            # 应有 status_code=200 断言
            response_assertions = root.findall(".//ResponseAssertion")
            self.assertGreaterEqual(len(response_assertions), 1)
            # 应有 3 个 JSONPath 断言（id, name, email）
            json_assertions = root.findall(".//JSONPathAssertion")
            self.assertEqual(len(json_assertions), 3)

    def test_get_with_query_parameters(self):
        """GET + query 参数正确生成 HTTPArgument。"""
        data = {
            "base_url": "https://api.example.com",
            "endpoints": [
                {
                    "path": "/api/users",
                    "method": "GET",
                    "summary": "List users",
                    "parameters": [
                        {"name": "page", "in": "query", "default": "1"},
                        {"name": "size", "in": "query", "default": "10"},
                    ],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            input_path = _write_endpoints(td_path, data)
            output_path = td_path / "out.jmx"

            subprocess.check_call(
                [_venv_python(), _jmx_script(), "--input", str(input_path), "--output", str(output_path)],
                timeout=30,
            )

            root = _parse_jmx(output_path)
            # 应有 HTTPArgument 元素
            args = root.findall(".//elementProp[@elementType='HTTPArgument']")
            self.assertEqual(len(args), 2)
            arg_names = [a.find("stringProp[@name='Argument.name']").text for a in args]
            self.assertIn("page", arg_names)
            self.assertIn("size", arg_names)
            # 验证默认值
            for arg in args:
                name = arg.find("stringProp[@name='Argument.name']").text
                value = arg.find("stringProp[@name='Argument.value']").text
                if name == "page":
                    self.assertEqual(value, "1")
                elif name == "size":
                    self.assertEqual(value, "10")

    def test_multiple_endpoints_batch(self):
        """多接口各生成独立线程组。"""
        data = {
            "base_url": "https://api.example.com",
            "endpoints": [
                {"path": "/api/users", "method": "GET", "summary": "List users"},
                {"path": "/api/users", "method": "POST", "summary": "Create user"},
                {"path": "/api/users/1", "method": "DELETE", "summary": "Delete user"},
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            input_path = _write_endpoints(td_path, data)
            output_path = td_path / "out.jmx"

            subprocess.check_call(
                [_venv_python(), _jmx_script(), "--input", str(input_path), "--output", str(output_path)],
                timeout=30,
            )

            root = _parse_jmx(output_path)
            thread_groups = root.findall(".//ThreadGroup")
            self.assertEqual(len(thread_groups), 3)
            samplers = root.findall(".//HTTPSamplerProxy")
            self.assertEqual(len(samplers), 3)

    def test_invalid_json_exits_with_error(self):
        """非法 JSON 报错退出。"""
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            input_path = td_path / "endpoints.json"
            output_path = td_path / "out.jmx"
            input_path.write_text("{invalid json", encoding="utf-8")

            result = subprocess.run(
                [_venv_python(), _jmx_script(), "--input", str(input_path), "--output", str(output_path)],
                capture_output=True, text=True, timeout=30,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("JSON 格式无效", result.stderr)

    def test_empty_endpoints_exits_with_error(self):
        """空 endpoints 报错退出。"""
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            input_path = _write_endpoints(td_path, {"base_url": "https://api.example.com", "endpoints": []})
            output_path = td_path / "out.jmx"

            result = subprocess.run(
                [_venv_python(), _jmx_script(), "--input", str(input_path), "--output", str(output_path)],
                capture_output=True, text=True, timeout=30,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("endpoints 为空", result.stderr)

    def test_missing_file_exits_with_error(self):
        """文件不存在报错退出。"""
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            output_path = td_path / "out.jmx"

            result = subprocess.run(
                [_venv_python(), _jmx_script(), "--input", "/nonexistent/endpoints.json", "--output", str(output_path)],
                capture_output=True, text=True, timeout=30,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("文件不存在", result.stderr)


if __name__ == "__main__":
    unittest.main()
