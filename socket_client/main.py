# -*- coding: UTF-8 -*-
"""
操作回放测试系统 - 主程序入口
Python版本: 3.6+
"""
import sys
import argparse
import time
from pathlib import Path

# 添加项目根目录到sys.path（在最开始）
import sys
from pathlib import Path
current_dir = Path(__file__).parent  # socket_client/ 目录
project_root = current_dir.parent     # 项目根目录

# 确保项目根目录在sys.path的最前面
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 现在可以导入所有模块了
import socket_client.executor.replay_engine as replay_engine
import socket_client.models.operation as operation_model
import socket_client.models.replay_result as replay_result_model
import socket_client.config as config_module
import socket_client.config.constants as constants
import socket_client.utils.exceptions as exceptions

import socket_client.executor.replay_engine as replay_engine
import socket_client.models.operation as operation_model
import socket_client.models.replay_result as replay_result_model
import socket_client.config as config_module
import socket_client.config.constants as constants
import socket_client.utils.exceptions as exceptions

OperationReplayEngine = replay_engine.OperationReplayEngine
execute_csv_replay = replay_engine.execute_csv_replay
ReplayResult = replay_result_model.ReplayResult
Operation = operation_model.Operation
config = config_module.config
logger = config_module.logger
MessageType = constants.MessageType
OperationExecuteError = exceptions.OperationExecuteError


def print_progress(current: int, total: int, operation: Operation):
    """
    打印回放进度的回调函数

    Args:
        current: 当前执行的序号
        total: 总数
        operation: 当前操作对象
    """
    progress = (current / total) * 100
    print(f"\r进度: [{current}/{total}] ({progress:.1f}%) | 操作: {operation.event_type} | "
          f"坐标: ({operation.x}, {operation.y}) | "
          f"窗口: {operation.window_title[:30]}...", end="", flush=True)


def print_summary(result: ReplayResult):
    """
    打印回放结果的摘要信息

    Args:
        result: 回放结果对象
    """
    print("\n\n" + "=" * 60)
    print("回放完成！以下为结果摘要:")
    print("=" * 60)
    print(f"总操作数: {result.total_operations}")
    print(f"成功数: {result.successful_operations}")
    print(f"失败数: {result.failed_operations}")
    print(f"成功率: {result.get_success_rate():.2f}%")
    print(f"总耗时: {result.total_time_elapsed:.3f}秒")
    print(f"平均每条: {(result.total_time_elapsed / result.total_operations):.3f}秒")

    if result.failed_operations > 0:
        print("\n失败的操作详情:")
        print("-" * 60)
        for r in result.results:
            if not r.success:
                print(f"- {r.operation_type}: {r.message}")

    print("=" * 60)


def main():
    """
    主函数，处理命令行参数并执行相应的功能
    """
    parser = argparse.ArgumentParser(
        description="auto-playblack-v3 软件代操系统 - CSV回放功能",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 使用默认CSV文件路径执行回放
  python main.py

  # 指定自定义CSV文件路径
  python main.py --csv-path "path/to/your/operation_log.csv"

  # 仅显示操作列表（不执行回放）
  python main.py --list-operations

  # 详细模式执行回放
  python main.py --verbose --csv-path "..."
        """
    )

    # 命令行参数
    parser.add_argument(
        '--csv-path',
        type=str,
        default=None,
        help='CSV文件路径，默认使用配置中的路径'
    )

    parser.add_argument(
        '--list-operations',
        action='store_true',
        help='仅列出操作记录，不执行回放'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细日志信息'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='auto-playblack-v3 1.0.0'
    )

    args = parser.parse_args()

    # 设置日志级别
    if args.verbose:
        config.log_level = "DEBUG"

    # 打印启动信息
    print("=" * 60)
    print("auto-playblack-v3 软件代操系统 - CSV回放模式")
    print("=" * 60)
    print(f"Python版本: {'.'.join(map(str, sys.version_info[:2]))}")
    print(f"CSV文件路径: {args.csv_path or config.csv_path}")
    print("=" * 60)

    try:
        # 如果指定了--list-operations，仅列出操作
        if args.list_operations:
            list_operations(args.csv_path)
            return

        # 执行回放
        result = execute_csv_replay(
            csv_path=args.csv_path,
            callback=print_progress
        )

        # 打印结果摘要
        print_summary(result)

        # 返回退出码
        sys.exit(0 if result.failed_operations == 0 else 1)

    except OperationExecuteError as e:
        logger.error(f"操作回放失败: {e}")
        print(f"\n错误: {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("用户中断了回放")
        print("\n回放已用户中断")
        sys.exit(130)

    except Exception as e:
        logger.error(f"发生未预期的错误: {e}", exc_info=True)
        print(f"\n发生未预期的错误: {e}")
        sys.exit(1)


def list_operations(csv_path: str = None):
    """
    列出操作记录的详细信息

    Args:
        csv_path: CSV文件路径
    """
    csv_path = csv_path or config.csv_path
    print(f"\n正在读取操作记录: {csv_path}\n")
    print("=" * 100)

    try:
        engine = OperationReplayEngine(csv_path)

        # 解析操作记录
        operations = engine.load_operations()

        if not operations:
            print("未找到任何操作记录")
            return

        # 列出所有操作
        for i, op in enumerate(operations, 1):
            print(f"\n[{i}/{len(operations)}] 操作 #{i}")
            print(f"  时间戳:     {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(op.timestamp))} "
                  f"(±{op.delay:.3f}秒)")
            print(f"  操作类型:   {op.event_type}")
            print(f"  详细信息:   {op.detail}")
            print(f"  坐标:       X={op.x}, Y={op.y}")
            print(f"  窗口标题:   {op.window_title}")
            print(f"  控件文本:   {op.control_text}")

        print("\n" + "=" * 100)

    except Exception as e:
        print(f"错误: 无法读取操作记录 - {e}")


if __name__ == "__main__":
    main()
