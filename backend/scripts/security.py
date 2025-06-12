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


def run_bandit():
    """运行bandit检查安全漏洞"""
    return run_command(["bandit", "-r", "app", "-x", "tests"])


def run_safety():
    """运行safety检查依赖安全"""
    return run_command(["safety", "check", "--full-report"])


def main():
    """主函数"""
    # 切换到项目根目录
    import os
    os.chdir(ROOT_DIR)
    
    # 运行安全检查
    success = True
    success = run_bandit() and success
    success = run_safety() and success
    
    if not success:
        print("安全检查失败")
        sys.exit(1)
    
    print("安全检查通过")
    sys.exit(0)


if __name__ == "__main__":
    main() 