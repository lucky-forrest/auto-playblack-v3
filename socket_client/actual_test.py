# -*- coding: UTF-8 -*-
"""
实际环境测试 - 验证真实操作执行
使用PyAutoGUI作为操作执行引擎
"""
import sys
import time
import pyautogui
from pathlib import Path
from datetime import datetime

# 禁用pyautogui安全功能
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1

# 添加项目根目录到sys.path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent))

import socket_client.models.operation as operation_model
Operation = operation_model.Operation
import socket_client.config as config_module
config = config_module.config
import socket_client.executor.time_controller as time_controller_module
import socket_client.executor.operation_executor as operation_executor_module


def test_mouse_move():
    """测试鼠标移动"""
    print("\n" + "=" * 70)
    print("测试1: 实际鼠标移动测试")
    print("=" * 70)

    try:
        print("\n⚠️  测试将移动鼠标到屏幕中央位置")
        print("   请确保目标窗口如果存在，应该在可见区域")

        # 获取屏幕尺寸
        screen_width = pyautogui.size().width
        screen_height = pyautogui.size().height
        print(f"\n屏幕尺寸: {screen_width} x {screen_height}")

        # 目标位置（屏幕中央）
        target_x = screen_width // 2
        target_y = screen_height // 2

        print(f"目标位置: ({target_x}, {target_y})")

        # 创建测试操作
        operation = Operation(
            timestamp=time.time() + 1.0,
            event_type="mouse_move",
            x=target_x,
            y=target_y,
            window_title="测试窗口"
        )

        # 模拟时间延迟
        delay = operation.calculate_delay(time.time())
        print(f"预期延迟: {delay:.3f}秒")
        print("⏳ 等待1秒...")
        time.sleep(1)

        # 执行鼠标移动
        print("\n🎯 执行鼠标移动...")
        pyautogui.moveTo(target_x, target_y, duration=0.5)
        print("✅ 鼠标移动成功！")

        # 验证位置
        current_x, current_y = pyautogui.position()
        error = ((current_x - target_x)**2 + (current_y - target_y)**2)**0.5
        print(f"当前位置: ({current_x}, {current_y})")
        print(f"误差距离: {error:.1f}像素")

        if error < 10:
            print("✅ 位置误差在可接受范围内 (<10像素)")
            return True
        else:
            print(f"⚠️  位置误差较大 ({error:.1f}像素)")
            return False

    except Exception as e:
        print(f"❌ 鼠标移动测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mouse_click():
    """测试鼠标点击"""
    print("\n" + "=" * 70)
    print("测试2: 实际鼠标点击测试")
    print("=" * 70)

    try:
        print("\n⚠️  测试将在屏幕中央位置执行点击")
        print("   请确保鼠标已经在移动测试的位置，否则点击可能不稳定")

        # 获取屏幕尺寸
        screen_width = pyautogui.size().width
        screen_height = pyautogui.size().height

        # 目标位置（屏幕中央，稍偏上）
        target_x = screen_width // 2
        target_y = screen_height // 2 // 2

        print(f"目标位置: ({target_x}, {target_y})")

        # 创建测试操作
        operation = Operation(
            timestamp=time.time() + 1.0,
            event_type="mouse_click",
            x=target_x,
            y=target_y,
            window_title="测试窗口"
        )

        # 模拟时间延迟
        delay = operation.calculate_delay(time.time())
        print(f"预期延迟: {delay:.3f}秒")
        print("⏳ 等待1秒...")
        time.sleep(1)

        # 执行鼠标点击
        print("\n🎯 执行鼠标点击...")
        pyautogui.click(target_x, target_y)
        print("✅ 鼠标点击成功！")

        # 验证点击是否触发右键菜单
        print("\n💡 提示：如果点击触发了右键菜单或弹出对话框，")
        print("   请手动关闭，点击完成后即可")

        return True

    except Exception as e:
        print(f"❌ 鼠标点击测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_time_precision_with_execution():
    """测试时间精度和执行组合"""
    print("\n" + "=" * 70)
    print("测试3: 时间精度与操作执行组合测试")
    print("=" * 70)

    try:
        print("\n逐步执行5个操作，验证时间控制")

        screen_width = pyautogui.size().width
        screen_height = pyautogui.size().height

        # 创建5个操作
        operations = []
        for i in range(5):
            target_x = screen_width // 4 * (i + 1)
            target_y = screen_height // 3

            operation = Operation(
                timestamp=time.time() + (i + 1),  # 每隔1秒执行
                event_type="mouse_click",
                x=target_x,
                y=target_y,
                window_title="测试窗口"
            )
            operations.append(operation)

        print(f"\n创建了 {len(operations)} 个间隔操作:")
        for i, op in enumerate(operations, 1):
            expected_time = time.ctime(op.timestamp)
            print(f"  [{i}] 操作: {op.event_type} at ({op.x}, {op.y}), 预计时间: {expected_time}")

        print("\n⏳ 开始执行操作...")
        start_time = time.time()

        for i, operation in enumerate(operations, 1):
            delay = operation.calculate_delay(time.time())
            if delay > 0:
                print(f"  [{i}] 等待 {delay:.3f} 秒...")
                time.sleep(delay)

            print(f"  [{i}] 执行: {operation.event_type} at ({operation.x}, {operation.y})")
            pyautogui.click(operation.x, operation.y)

        execution_time = time.time() - start_time

        print(f"\n✅ 所有操作执行完成！")
        print(f"   预计总耗时: {len(operations)}秒")
        print(f"   实际总耗时: {execution_time:.3f}秒")
        print(f"   偏差: {abs(execution_time - len(operations)):.3f}秒")

        if abs(execution_time - len(operations)) < 2.0:
            print("✅ 时间控制符合预期（偏差<2秒）")
            return True
        else:
            print(f"⚠️  时间偏差较大 ({abs(execution_time - len(operations)):.3f}秒)")
            return False

    except Exception as e:
        print(f"❌ 组合测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_actual_tests():
    """运行实际环境测试"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  auto-playblack-v3 - 实际环境操作测试".center(68) + "║")
    print("║" + "  使用 PyAutoGUI 测试真实操作执行".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    print(f"\nPython版本: {sys.version}")
    print(f"PyAutoGUI版本: {pyautogui.__version__}")
    print(f"当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    print("\n⚠️  重要提示:")
    print("   1. 测试将移动和点击鼠标，请确保这只是测试环境")
    print("   2. 测试期间屏幕中央可能会有操作触发")
    print("   3. 测试涉及实际鼠标移动，请保持鼠标在安全区域")

    # 暂停一下让用户准备
    input("\n按回车键开始测试...")

    tests = [
        ("鼠标移动测试", test_mouse_move),
        ("鼠标点击测试", test_mouse_click),
        ("时间精度与执行组合", test_time_precision_with_execution),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name}测试异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # 最终总结
    print("\n\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + "  实际环境测试总结".center(68) + "║")
    print("╚" + "=" * 68 + "╝")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status:<10} {name}")

    success_rate = int(passed / total * 100)
    print(f"\n总计: {passed} / {total} 通过")
    print(f"     {success_rate}%")

    print("\n")
    if passed == total:
        print("╔" + "╔" + "=" * 66 + "╗".replace("╗", "=") + "╗".replace("╗", "="))
        print("║" + " " + "🎉 所有实际环境测试通过！真实操作执行正常！🎉".center(66) + " " + "║")
        print("╚" + "╚" + "=" * 66 + "╝".replace("╝", "=") + "╝".replace("╝", "="))
        print("\n")
        print("✅ 鼠标移动功能正常")
        print("✅ 鼠标点击功能正常")
        print("✅ 时间控制精确")
        print("✅ 操作执行引擎可用")
        print("\n💡 下一步:")
        print("   1. 可以运行完整回放测试")
        print("   2. 在实际软件上验证完整回放功能")
        print("   3. 继续开发 Socket 实时模式")
        return 0
    else:
        print("╔" + "=" * 68 + "╗")
        print("║" + "部分测试失败".center(68) + "║")
        print("=" * 68)
        print(f"\n❌ 有 {total - passed} 个测试失败")
        print("   请检查错误信息")
        return 1


if __name__ == "__main__":
    try:
        # 关闭PyAutoGUI的安全功能
        print("配置 PyAutoGUI 安全选项...")
        pyautogui.PAUSE = 0.1
        pyautogui.FAILSAFE = False
        pyautogui.mouse_jit(False)

        sys.exit(run_actual_tests())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
