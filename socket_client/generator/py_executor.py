# -*- coding: UTF-8 -*-
"""
生成的Python文件执行器，用于回放操作
"""
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


def execute_generated_py_file(py_file_path: str, pause_after_completion: bool = True) -> bool:
    """
    执行生成的Python回放脚本

    Args:
        py_file_path: Python回放脚本路径
        pause_after_completion: 完成后是否暂停等待用户确认

    Returns:
        bool: 执行是否成功
    """
    try:
        print(f"\n正在执行回放脚本: {py_file_path}\n")

        # 构建Python命令
        # 使用subprocess运行Python文件
        process = subprocess.Popen(
            [sys.executable, py_file_path],
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
            creationflags=subprocess.CREATE_NO_WINDOW  # Windows下不显示控制台窗口
        )

        # 等待进程完成
        return_code = process.wait()

        # 检查退出码
        if return_code == 0:
            print("\n✓ 回放脚本执行成功")
            return True
        else:
            print(f"\n✗ 回放脚本执行失败，退出码: {return_code}")
            return False

    except FileNotFoundError:
        print(f"错误：找不到Python解释器：{sys.executable}")
        return False
    except Exception as e:
        print(f"执行回放脚本时发生错误: {e}")
        return False


def execute_generated_py_with_output(py_file_path: str, output_file: Optional[str] = None) -> dict:
    """
    执行生成的Python回放脚本并捕获输出

    Args:
        py_file_path: Python回放脚本路径
        output_file: 输出日志文件路径（可选）

    Returns:
        dict: 执行结果字典，包含退出码、输出等
    """
    result = {
        'exit_code': None,
        'success': False,
        'stdout': '',
        'stderr': '',
        'output': ''
    }

    try:
        # 使用subprocess执行
        if output_file:
            # 重定向输出到文件
            with open(output_file, 'w', encoding='utf-8') as f_out, \
                 open(output_file, 'a', encoding='utf-8') as f_err:
                process = subprocess.Popen(
                    [sys.executable, py_file_path],
                    stdout=f_out,
                    stderr=f_err,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                process.wait()
                result['exit_code'] = process.returncode

        else:
            # 直接从stdout捕获输出
            process = subprocess.Popen(
                [sys.executable, py_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            stdout, _ = process.communicate()
            result['exit_code'] = process.returncode
            result['stdout'] = stdout
            result['output'] = stdout

        result['success'] = result['exit_code'] == 0

    except Exception as e:
        result['error'] = str(e)
        result['success'] = False

    return result
