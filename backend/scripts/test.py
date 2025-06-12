#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent.resolve()


def run_tests(coverage=False):
    """运行测试"""
    command = ["pytest"]
    
    if coverage:
        command.extend([
            "--cov=app",
            "--cov-report=term",
            "--cov-report=html",
        ])
    
    print(f"运行: {' '.join(command)}")
    result = subprocess.run(command, cwd=ROOT_DIR)
    return result.returncode == 0


def main():
    """主函数"""
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description="运行测试")
    parser.add_argument("--coverage", action="store_true", help="生成覆盖率报告")
    args = parser.parse_args()
    
    # 运行测试
    success = run_tests(coverage=args.coverage)
    
    if not success:
        print("测试失败")
        sys.exit(1)
    
    print("测试通过")
    sys.exit(0)


if __name__ == "__main__":
    main() 