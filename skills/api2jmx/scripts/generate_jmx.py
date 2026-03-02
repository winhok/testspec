#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 endpoints.json 生成 JMX 测试脚本

用法:
    python generate_jmx.py --input endpoints.json --output test.jmx
    python generate_jmx.py --input endpoints.json --output perf.jmx --threads 50 --ramp 30 --loops 5
"""

import argparse
import json
import logging
import sys
from pathlib import Path

try:
    from .generator import JmxGenerator
except ImportError:
    from generator import JmxGenerator

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="从 endpoints.json 生成 JMX 测试脚本")
    parser.add_argument("--input", required=True, help="endpoints.json 文件路径")
    parser.add_argument("--output", required=True, help="输出 JMX 文件路径")
    parser.add_argument("--name", default=None, help="测试计划名称")
    parser.add_argument("--threads", type=int, default=None, help="线程数")
    parser.add_argument("--ramp", type=int, default=None, help="启动时间（秒）")
    parser.add_argument("--loops", type=int, default=None, help="循环次数")
    args = parser.parse_args()

    # 读取 endpoints.json
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error("文件不存在 - %s", args.input)
        sys.exit(1)

    try:
        endpoints_data = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        logger.error("JSON 格式无效 - %s", e)
        sys.exit(1)

    if not endpoints_data.get("endpoints"):
        logger.error("endpoints 为空")
        sys.exit(1)

    # 生成 JMX
    generator = JmxGenerator()
    generator.generate_from_endpoints(
        endpoints_data,
        test_plan_name=args.name,
        num_threads=args.threads,
        ramp_time=args.ramp,
        loops=args.loops,
    )
    generator.save_jmx(args.output)


if __name__ == "__main__":
    main()
