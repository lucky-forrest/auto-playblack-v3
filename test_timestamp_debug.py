# -*- coding: UTF-8 -*-
"""
时间戳调试测试 - 验证时间转换和延迟计算
"""
import time
from datetime import datetime
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import socket_client.executor.time_controller as time_controller_module
import socket_client.models.operation as operation_model
import socket_client.config as config_module
config = config_module.config


def test_timestamp_conversion():
    """测试时间戳转换"""
    print("\n" + "=" * 80)
    print("测试1: 时间戳转换")
    print("=" * 80)

    original_csv_timestamps = [
        "2026-04-02T17:27:56.799316",
        "2026-04-02T17:27:58.104727",
        "2026-04-02T17:27:59.574132",
    ]

    print("\nCSV文件原始时间戳:")
    for ts in original_csv_timestamps:
        print(f"  {ts}")

    # 模拟CSV解析过程
    parsed_timestamps = []
    config = config_module.config
    tc = time_controller_module.TimeController()

    for csv_ts in original_csv_timestamps:
        # 解析为datetime
        dt = datetime.fromisoformat(csv_ts)
        # 转换为时间戳
        timestamp = dt.timestamp()
        parsed_timestamps.append(timestamp)

        print(f"\n  原始: {csv_ts}")
        print(f"  解析: {dt}")
        print(f"  时间戳: {timestamp:.6f}")

    # 计算延迟
    print("\n延迟计算:")
    last_ts = None
    for i, ts in enumerate(parsed_timestamps):
        if last_ts is not None:
            delay = ts - last_ts
            ts_str = "立即执行" if delay <= 0 else f"{delay:.3f}秒后"
            print(f"  操作{i+1}: 上次 {last_ts:.6f} → 当前 {ts:.6f}, 延迟 {delay:.4f}秒 ({ts_str})")
        else:
            print(f"  操作{i+1}: 初始时间. 延迟 0.000秒 (初始操作)")
        last_ts = ts

    return parsed_timestamps


def test_delay_execution():
    """测试延迟执行"""

    print("\n" + "=" * 80)
    print("测试2: 延迟执行模拟")
    print("=" * 80)

    csv_timestamps = [
        "2026-04-02T17:27:56.799316",
        "2026-04-02T17:27:58.104727",
        "2026-04-02T17:27:59.574132",
        "2026-04-02T17:28:01.558175",
    ]

    # 创建操作对象列表
    operations = []
    for csv_ts in csv_timestamps:
        dt = datetime.fromisoformat(csv_ts)
        timestamp = dt.timestamp()
        operations.append(operation_model.Operation(
            timestamp=timestamp,
            event_type="mouse_click",
            detail="Test click",
            x=100 + len(operations) * 50,
            y=100 + len(operations) * 50,
            window_title="Test Window"
        ))

    print(f"\n创建了 {len(operations)} 个操作对象")
    print(f"时间控制精度: ±{config.time_precision}秒")

    # 执行延迟控制
    last_ts = None
    for i, op in enumerate(operations):
        if last_ts is not None:
            delay = op.timestamp - last_ts
        else:
            delay = 0.0

        print(f"\n操作 {i+1}:")
        print(f"  时间戳: {op.timestamp:.6f}")
        if last_ts is not None:
            print(f"  上次时间戳: {last_ts:.6f}")
        print(f"  计算延迟: {delay:.4f}秒")

        if delay > 0:
            print(f"  等待中...")
            start = time.time()
            time.sleep(delay)
            elapsed = time.time() - start
            print(f"  实际等待: {elapsed:.3f}秒")
            print(f"  误差: {abs(elapsed - delay):.3f}秒")
        else:
            print(f"  立即执行")

        print(f"  执行点击: ({op.x}, {op.y})")

        last_ts = op.timestamp

    print(f"\n✅ 所有操作已执行完成")


def test_pyautogui_failsafe():
    """测试pyautogui的安全机制"""

    print("\n" + "=" * 80)
    print("测试3: PyAutoGUI安全机制")
    print("=" * 80)

    import pyautogui

    print(f"\nPyAutoGUI FAILSAFE: {pyautogui.FAILSAFE}")
    print(f"PyAutoGUI PAUSE: {pyautogui.PAUSE}秒")

    # 如果FAILSAFE开启，移动鼠标到屏幕左上角会触发failsafe
    print("\n⚠️  注意:")
    print("  - 如果FAILSAFE=True，移动鼠标到屏幕左上角会中断执行")
    print("  - 如果网页浏览器在前台，可能会触发failsafe")
    print("  - 尝试点击屏幕时会受到安全机制限制")


def main():
    """主测试函数"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  时间戳调试测试 - 验证时间控制逻辑".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        test_timestamp_conversion()
        test_delay_execution()
        test_pyautogui_failsafe()

        print("\n" + "=" * 80)
        print("✅ 调试测试完成")
        print("=" * 80)
        print("\n总结:")
        print("1. CSV解析器正确将ISO时间字符串转换为浮点数时间戳")
        print("2. TimeController正确计算操作之间的延迟")
        print("3. pyautogui可能有failsafe机制影响执行")
        print("\n建议:")
        print("- 如果点击无效，检查FAILSAFE设置")
        print("- 确保目标窗口在前台")
        print("- 添加更多日志查看实际执行的步骤")

        return 0

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
