# -*- coding: UTF-8 -*-
"""
操作数据模型
"""
import time
from typing import Optional


class Operation:
    """操作对象，包含操作类型和坐标信息"""

    def __init__(
        self,
        timestamp: float,
        event_type: str,
        detail: str = "",
        x: Optional[int] = None,
        y: Optional[int] = None,
        window_title: str = "",
        control_text: str = "",
        delay: float = 0.0
    ):
        """初始化操作对象

        Args:
            timestamp: 操作时间戳（Unix时间戳，秒）
            event_type: 事件类型（mouse_move/mouse_click等）
            detail: 操作详细信息
            x: X坐标
            y: Y坐标
            window_title: 窗口标题
            control_text: 控件文本
            delay: 延迟时间（秒）
        """
        self.timestamp = timestamp
        self.event_type = event_type
        self.detail = detail
        self.x = x
        self.y = y
        self.window_title = window_title
        self.control_text = control_text
        self.delay = delay

    def to_dict(self):
        """将操作对象转换为字典

        Returns:
            dict: 操作信息的字典表示
        """
        return {
            'timestamp': self.timestamp,
            'event_type': self.event_type,
            'detail': self.detail,
            'x': self.x,
            'y': self.y,
            'window_title': self.window_title,
            'control_text': self.control_text,
            'delay': self.delay
        }

    def from_dict(self, data: dict):
        """从字典创建操作对象

        Args:
            data: 包含操作信息的字典
        """
        self.timestamp = data.get('timestamp')
        self.event_type = data.get('event_type')
        self.detail = data.get('detail', '')
        self.x = data.get('x')
        self.y = data.get('y')
        self.window_title = data.get('window_title', '')
        self.control_text = data.get('control_text', '')
        self.delay = data.get('delay', 0.0)

    def should_wait(self) -> bool:
        """判断是否需要等待操作延迟

        Returns:
            bool: 是否需要等待
        """
        return self.delay > 0

    @staticmethod
    def calculate_delay(operation_timestamp: float) -> float:
        """
        计算操作延迟时间（当前时间距离操作录制时刻的延迟）

        注意：这不是计算连续操作之间的间隔，而是计算如果现在执行的操作距离
        录制时刻需要等待多久。这个方法正在被 TimeController.calculate_delay
        替代，后者用于计算操作之间的时间间隔。

        Args:
            operation_timestamp: 操作录制的时间戳

        Returns:
            float: 延迟时间，最小为0秒
        """
        import time
        current_time = time.time()
        delay = operation_timestamp - current_time
        return max(0.0, delay)

    def __repr__(self):
        """获取操作对象的字符串表示"""
        return (f"Operation(timestamp={self.timestamp:.3f}, "
                f"type={self.event_type}, x={self.x}, y={self.y})")
