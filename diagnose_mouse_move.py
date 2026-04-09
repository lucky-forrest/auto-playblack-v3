# -*- coding: UTF-8 -*-
"""
诊断 mouse_move 问题
"""
import time
from socket_client.executor.operation_executor import OperationExecutor

executor = OperationExecutor()

print("=" * 60)
print("mouse_move 诊断测试")
print("=" * 60)
print()

# 测试1: 直接调用 _mouse_move
print("【测试1】直接调用 _mouse_move 方法")
print("目标坐标: (500, 300)")
print("(请不要移动鼠标，start 后会自动执行)")
time.sleep(2)

op1 = executor.models.Operation(
    timestamp=time.time(),
    event_type='mouse_move',
    detail='Move mouse to test',
    x=500,
    y=300
)

# 直接调用，绕过 execute_operation
try:
    executor._mouse_move(op1)
    print("✅ _mouse_move 执行成功")
except Exception as e:
    print(f"❌ _mouse_move 执行失败: {e}")

print()

# 测试2: 通过 execute_operation 调用
print("【测试2】通过 execute_operation 调用 (带 window_title)")
target_window = input("请输入要激活的窗口标题（直接回车跳过）: ").strip()
op2 = executor.models.Operation(
    timestamp=time.time(),
    event_type='mouse_move',
    detail='Move mouse via execute',
    x=500,
    y=500
)

try:
    executor.execute_operation(op2, window_title=target_window if target_window else None)
    print("✅ execute_operation 执行成功")
except Exception as e:
    print(f"❌ execute_operation 执行失败: {e}")

print()
print("=" * 60)
print("诊断完成")
print("=" * 60)
