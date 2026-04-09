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
        delay: float = 0.0,
        element_type: Optional[str] = None,
        element_content: Optional[str] = None,
        window_handle: Optional[str] = None,
        window_class_name: Optional[str] = None,
        window_process_id: Optional[int] = None,
        window_process_name: Optional[str] = None,
        window_visible: Optional[bool] = None,
        window_enabled: Optional[bool] = None,
        window_active: Optional[bool] = None,
        control_handle: Optional[str] = None,
        control_class_name: Optional[str] = None,
        rect: Optional[str] = None,
        relative_coordinates: Optional[str] = None,
        application_name: Optional[str] = None,
        scroll_delta: Optional[int] = None,
        drag_delta_x: Optional[int] = None,
        drag_delta_y: Optional[int] = None
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
            element_type: 元素类型
            element_content: 元素内容
            window_handle: 窗口句柄
            window_class_name: 窗口类名
            window_process_id: 窗口进程ID
            window_process_name: 窗口进程名
            window_visible: 窗口是否可见
            window_enabled: 窗口是否启用
            window_active: 窗口是否激活
            control_handle: 控件句柄
            control_class_name: 控件类名
            rect: 窗口/控件位置和大小
            relative_coordinates: 相对坐标
            application_name: 应用程序名称
            scroll_delta: 滚动距离
            drag_delta_x: 拖拽X距离
            drag_delta_y: 拖拽Y距离
        """
        self.timestamp = timestamp
        self.event_type = event_type
        self.detail = detail
        self.x = x
        self.y = y
        self.window_title = window_title
        self.control_text = control_text
        self.delay = delay

        # 通用属性
        self.element_type = element_type
        self.element_content = element_content
        self.window_handle = window_handle
        self.window_class_name = window_class_name
        self.window_process_id = window_process_id
        self.window_process_name = window_process_name
        self.window_visible = window_visible
        self.window_enabled = window_enabled
        self.window_active = window_active
        self.control_handle = control_handle
        self.control_class_name = control_class_name
        self.rect = rect
        self.relative_coordinates = relative_coordinates
        self.application_name = application_name

        # 滚动和拖拽相关属性
        self.scroll_delta = scroll_delta
        self.drag_delta_x = drag_delta_x
        self.drag_delta_y = drag_delta_y

    def to_dict(self):
        """将操作对象转换为字典

        Returns:
            dict: 操作信息的字典表示
        """
        data = {
            'timestamp': self.timestamp,
            'event_type': self.event_type,
            'detail': self.detail,
            'x': self.x,
            'y': self.y,
            'window_title': self.window_title,
            'control_text': self.control_text,
            'delay': self.delay
        }

        # 添加可选字段
        if self.element_type is not None:
            data['element_type'] = self.element_type
        if self.element_content is not None:
            data['element_content'] = self.element_content
        if self.scroll_delta is not None:
            data['scroll_delta'] = self.scroll_delta
        if self.drag_delta_x is not None:
            data['drag_delta_x'] = self.drag_delta_x
        if self.drag_delta_y is not None:
            data['drag_delta_y'] = self.drag_delta_y

        return data

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
