#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 文档解析器
支持 OpenAPI/Swagger（YAML/JSON）和 Markdown 格式
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import yaml
except ImportError:
    yaml = None


# ---------------------------------------------------------------------------
# OpenAPI / Swagger
# ---------------------------------------------------------------------------

class OpenApiParser:
    """解析 OpenAPI/Swagger 文档"""

    def __init__(self):
        self.spec: Optional[Dict[str, Any]] = None
        self.version: Optional[str] = None

    def parse(self, file_path: str) -> Dict[str, Any]:
        """解析 OpenAPI/Swagger 文档"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix in ['.yaml', '.yml']:
                if yaml is None:
                    raise ImportError("解析 YAML 格式需要安装 pyyaml: pip install pyyaml")
                self.spec = yaml.safe_load(f)
            else:
                self.spec = json.load(f)

        # 检测版本
        if 'openapi' in self.spec:
            self.version = 'openapi3'
        elif 'swagger' in self.spec:
            self.version = 'swagger2'
        else:
            raise ValueError("无法识别 OpenAPI/Swagger 版本")

        return self.spec

    def parse_from_string(self, content: str, input_format: str = 'yaml') -> Dict[str, Any]:
        """从字符串解析 OpenAPI/Swagger 文档"""
        if input_format.lower() == 'yaml':
            if yaml is None:
                raise ImportError("解析 YAML 格式需要安装 pyyaml: pip install pyyaml")
            self.spec = yaml.safe_load(content)
        else:
            self.spec = json.loads(content)

        # 检测版本
        if 'openapi' in self.spec:
            self.version = 'openapi3'
        elif 'swagger' in self.spec:
            self.version = 'swagger2'
        else:
            raise ValueError("无法识别 OpenAPI/Swagger 版本")

        return self.spec

    def get_endpoints(self) -> List[Dict[str, Any]]:
        """提取所有 API 端点信息"""
        if not self.spec:
            raise ValueError("请先解析 OpenAPI 文档")

        endpoints = []
        paths = self.spec.get('paths', {})

        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method not in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    continue

                endpoint = {
                    'path': path,
                    'method': method.upper(),
                    'operationId': operation.get('operationId', ''),
                    'summary': operation.get('summary', ''),
                    'description': operation.get('description', ''),
                    'parameters': operation.get('parameters', []),
                    'responses': operation.get('responses', {}),
                    'tags': operation.get('tags', [])
                }

                # OpenAPI 3.0 使用 requestBody 字段
                if self.version == 'openapi3':
                    endpoint['requestBody'] = operation.get('requestBody')
                # Swagger 2.0 使用 parameters 中 in=body 的参数
                elif self.version == 'swagger2':
                    body_params = [p for p in operation.get('parameters', []) if p.get('in') == 'body']
                    if body_params:
                        body_param = body_params[0]
                        endpoint['requestBody'] = {
                            'content': {
                                'application/json': {
                                    'schema': body_param.get('schema', {})
                                }
                            }
                        }
                    else:
                        endpoint['requestBody'] = None

                endpoints.append(endpoint)

        return endpoints

    def get_parameter_details(self, parameter: Dict[str, Any]) -> Dict[str, Any]:
        """提取参数详细信息"""
        details = {
            'name': parameter.get('name', ''),
            'in': parameter.get('in', 'query'),
            'required': parameter.get('required', False),
            'description': parameter.get('description', ''),
            'schema': parameter.get('schema', {}) if self.version == 'openapi3' else parameter,
            'type': None,
            'format': None,
            'enum': None,
            'default': None
        }

        if self.version == 'openapi3':
            schema = details['schema']
            details['type'] = schema.get('type')
            details['format'] = schema.get('format')
            details['enum'] = schema.get('enum')
            details['default'] = schema.get('default')
        elif self.version == 'swagger2':
            details['type'] = parameter.get('type')
            details['format'] = parameter.get('format')
            details['enum'] = parameter.get('enum')
            details['default'] = parameter.get('default')

        return details

    def get_base_url(self) -> str:
        """获取基础 URL"""
        if not self.spec:
            return ''

        if self.version == 'openapi3':
            servers = self.spec.get('servers', [])
            if servers:
                return servers[0].get('url', '')
        elif self.version == 'swagger2':
            schemes = self.spec.get('schemes', ['http'])
            host = self.spec.get('host', '')
            base_path = self.spec.get('basePath', '')
            return f"{schemes[0]}://{host}{base_path}"

        return ''


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------

class MarkdownParser:
    """解析 Markdown 格式的 API 文档"""

    def __init__(self):
        self.content: str = ''
        self.endpoints: List[Dict[str, Any]] = []

    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """解析 Markdown API 文档"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            self.content = f.read()

        return self._extract_endpoints()

    def parse_from_string(self, content: str) -> List[Dict[str, Any]]:
        """从字符串解析 Markdown API 文档"""
        self.content = content
        return self._extract_endpoints()

    def _extract_endpoints(self) -> List[Dict[str, Any]]:
        """提取所有 API 端点"""
        # 定义匹配模式：(pattern, flags, group_mapping)
        # group_mapping: {'name': group_idx, 'path': group_idx, 'method': group_idx}
        patterns = [
            # 格式1: ## 接口名称\n**接口地址**:`/api/xxx`\n**请求方式**:`GET`
            (
                r'##\s+(.+?)\n.*?\*\*接口地址\*\*[：:]\s*`([^`]+)`.*?\*\*请求方式\*\*[：:]\s*`([^`]+)`',
                re.DOTALL | re.IGNORECASE,
                {'name': 1, 'path': 2, 'method': 3},
            ),
            # 格式2: ### GET /api/xxx
            (
                r'###\s+(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+([^\s\n]+)',
                re.IGNORECASE,
                {'method': 1, 'path': 2},
            ),
            # 格式3: ## API 名称\n**URL**: `/api/xxx`\n**Method**: `GET`
            (
                r'##\s+(.+?)\n.*?\*\*URL\*\*[：:]\s*`([^`]+)`.*?\*\*Method\*\*[：:]\s*`([^`]+)`',
                re.DOTALL | re.IGNORECASE,
                {'name': 1, 'path': 2, 'method': 3},
            ),
            # 格式4: ### 接口名称\n**接口URL**\n> /api/xxx\n**请求方式**\n> POST
            (
                r'###\s+(.+?)\n.*?\*\*接口URL\*\*.*?>\s*([^\n]+).*?\*\*请求方式\*\*.*?>\s*([^\n]+)',
                re.DOTALL | re.IGNORECASE,
                {'name': 1, 'path': 2, 'method': 3},
            ),
        ]

        for pattern, flags, mapping in patterns:
            endpoints = []
            for match in re.finditer(pattern, self.content, flags):
                section = self._extract_section(match.start(), match.end())
                name_group = mapping.get('name')
                path_str = match.group(mapping['path']).strip()
                method_str = match.group(mapping['method']).strip().upper()
                name_str = match.group(name_group).strip() if name_group else f"{method_str} {path_str}"
                endpoint = {
                    'name': name_str,
                    'path': path_str,
                    'method': method_str,
                    'summary': name_str,
                    'description': self._extract_description(section),
                    'parameters': self._extract_parameters(section),
                    'requestBody': self._extract_request_body(section),
                    'responses': self._extract_responses(section),
                    'tags': []
                }
                endpoints.append(endpoint)
            if endpoints:
                return endpoints

        return []

    def _extract_section(self, start: int, end: int) -> str:
        """提取接口章节内容"""
        next_section = re.search(r'\n##', self.content[end:])
        if next_section:
            return self.content[start:end + next_section.start()]
        return self.content[start:]

    def _extract_description(self, section: str) -> str:
        """提取接口描述"""
        desc_pattern = r'(?:接口描述|描述|Description)[：:]\s*(.+?)(?:\n\*\*|\n###|\n##|$)'
        match = re.search(desc_pattern, section, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return ''

    @staticmethod
    def _col_value(names: list, col_map: Dict[str, int], cols: List[str], default: str = '') -> str:
        """通过列名映射获取值，兼容不同表头格式。"""
        for name in names:
            if name in col_map and col_map[name] < len(cols):
                val = cols[col_map[name]]
                return val if val != '-' else ''
        return default

    @staticmethod
    def _parse_required(value: str) -> bool:
        """解析是否必填字段。"""
        normalized = value.strip().lower()
        return normalized in ('是', 'true', 'yes')

    def _parse_parameter_row(self, cols: List[str], col_map: Dict[str, int],
                              header_row: str, use_header_names: bool,
                              param_in: str) -> Optional[Dict[str, Any]]:
        """解析参数表中的一行数据。"""
        if not cols or not cols[0] or cols[0] == '暂无参数':
            return None

        if use_header_names:
            param_name = self._col_value(['参数名称', '参数名', 'name', '名称'], col_map, cols, cols[0] if cols else '')
            if not param_name:
                param_name = cols[0] if cols else ''
            param_default = self._col_value(['示例值', '默认值', 'default', 'example'], col_map, cols)
            param_type = self._col_value(['参数类型', '类型', 'type'], col_map, cols, 'string')
            param_required_str = self._col_value(['是否必填', '必填', 'required'], col_map, cols)
            param_required = self._parse_required(param_required_str)
            param_desc = self._col_value(['参数说明', '说明', '描述', 'description'], col_map, cols)
        elif len(cols) >= 5:
            if '示例值' in header_row or '参数类型' in header_row:
                param_name = cols[0]
                param_default = cols[1] if cols[1] != '-' else ''
                param_type = cols[2] if len(cols) > 2 else 'string'
                param_required = self._parse_required(str(cols[3])) if len(cols) > 3 else False
                param_desc = cols[4] if len(cols) > 4 else ''
            else:
                param_name = cols[0]
                param_default = ''
                param_desc = cols[1] if len(cols) > 1 else ''
                param_required = self._parse_required(str(cols[3])) if len(cols) > 3 else False
                param_type = cols[4] if len(cols) > 4 else 'string'
        else:
            param_name = cols[0]
            param_type = cols[1] if len(cols) > 1 else 'string'
            param_required = False
            param_desc = ''
            param_default = ''

        if '(' in param_type:
            param_type = param_type.split('(')[0]

        return {
            'name': param_name,
            'description': param_desc,
            'in': param_in,
            'required': param_required,
            'type': param_type,
            'schema': {'type': param_type},
            'default': param_default
        }

    def _extract_parameters(self, section: str) -> List[Dict[str, Any]]:
        """提取请求参数"""
        parameters: List[Dict[str, Any]] = []

        param_types = [
            ('请求Header参数', 'header'),
            ('请求Body参数', 'body'),
            ('请求参数', 'query')
        ]

        for param_type_name, param_in in param_types:
            title_pattern = rf'\*\*{param_type_name}\*\*[：:]?\s*\n'
            title_match = re.search(title_pattern, section, re.IGNORECASE)
            if not title_match:
                continue

            start_pos = title_match.end()
            remaining_section = section[start_pos:]
            table_pattern = r'(\|[^\n]+\n\|[^\n]+\n)((?:\|[^\n]+\n?)+)'
            table_match = re.search(table_pattern, remaining_section, re.IGNORECASE)
            if not table_match:
                continue

            # 解析表头建立列名到索引的映射
            header_row = table_match.group(1).split('\n')[0]
            header_cols = [col.strip() for col in header_row.split('|')[1:-1]]
            col_map = {name: idx for idx, name in enumerate(header_cols)}

            # 检测是否有已知列名命中，若无则回退到位置索引
            known_names = {'参数名称', '参数名', 'name', '名称', '示例值', '默认值',
                           'default', 'example', '参数类型', '类型', 'type',
                           '是否必填', '必填', 'required', '参数说明', '说明',
                           '描述', 'description'}
            use_header_names = bool(known_names & set(header_cols))

            data_rows = table_match.group(2).strip().split('\n')
            for row in data_rows:
                if not row.strip() or not row.startswith('|'):
                    continue
                cols = [col.strip() for col in row.split('|')[1:-1]]
                param = self._parse_parameter_row(cols, col_map, header_row, use_header_names, param_in)
                if param:
                    parameters.append(param)

        return parameters

    def _extract_request_body(self, section: str) -> Optional[Dict[str, Any]]:
        """提取请求体"""
        json_pattern = r'```(?:json|javascript)\s*\n(.*?)\n```'
        match = re.search(json_pattern, section, re.DOTALL | re.IGNORECASE)
        if match:
            try:
                body_content = json.loads(match.group(1))
                return {
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'example': body_content
                            }
                        }
                    }
                }
            except (json.JSONDecodeError, ValueError):
                pass
        return None

    def _extract_responses(self, section: str) -> Dict[str, Any]:
        """提取响应信息"""
        responses = {}

        response_table_pattern = r'\*\*响应状态\*\*[：:]?\s*\n\|[^\n]+\n\|[^\n]+\n((?:\|[^\n]+\n?)+)'
        match = re.search(response_table_pattern, section, re.IGNORECASE | re.DOTALL)

        if match:
            rows = match.group(1).strip().split('\n')
            for row in rows:
                if not row.strip() or not row.startswith('|'):
                    continue
                cols = [col.strip() for col in row.split('|')[1:-1]]
                if len(cols) >= 1:
                    status_code = cols[0]
                    responses[status_code] = {
                        'description': cols[1] if len(cols) > 1 else '',
                        'content': {}
                    }

        if not responses:
            json_pattern = r'```(?:json|javascript)\s*\n(.*?)\n```'
            matches = re.finditer(json_pattern, section, re.DOTALL | re.IGNORECASE)
            for i, match in enumerate(matches):
                if i == 0:
                    continue
                responses['200'] = {
                    'description': 'Success',
                    'content': {
                        'application/json': {
                            'example': match.group(1)
                        }
                    }
                }
                break

        if not responses:
            responses['200'] = {
                'description': 'Success'
            }

        return responses

    def get_base_url(self) -> str:
        """获取基础 URL（从文档中提取）"""
        base_url_pattern = r'(?:base[_\s]?url|baseUrl|服务器地址)[：:]\s*`?([^`\n]+)`?'
        match = re.search(base_url_pattern, self.content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return 'http://localhost:8080'
