#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent.resolve()


def run_command(command):
    """运行命令并返回结果"""
    print(f"运行: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
        return False
    print(f"成功: {result.stdout}")
    return True


def run_black():
    """运行black格式化代码"""
    return run_command(["black", "app", "tests"])


def run_isort():
    """运行isort排序导入"""
    return run_command(["isort", "app", "tests"])


def run_flake8():
    """运行flake8检查代码质量"""
    return run_command(["flake8", "app", "tests"])


def main():
    """主函数"""
    # 切换到项目根目录
    os.chdir(ROOT_DIR)
    
    # 运行代码质量检查
    success = True
    success = run_black() and success
    success = run_isort() and success
    success = run_flake8() and success
    
    if not success:
        print("代码质量检查失败")
        sys.exit(1)
    
    print("代码质量检查通过")
    sys.exit(0)


if __name__ == "__main__":
    import os
    main() 