# -*- coding: UTF-8 -*-
"""
常量定义模块
"""
from enum import Enum


class MessageType(Enum):
    """消息类型枚举"""
    E_StartTest = "E_StartTest"
    E_OperationStart = "E_OperationStart"
    E_OperationDone = "E_OperationDone"
    E_OperationError = "E_OperationError"
    E_Ping = "E_Ping"
    E_ConnectionLost = "E_ConnectionLost"


class OperationType(Enum):
    """操作类型枚举"""
    mouse_move = "mouse_move"
    mouse_click = "mouse_click"
    mouse_scroll = "mouse_scroll"
    key_press = "key_press"
    key_release = "key_release"
    window_control = "window_control"


class WindowControlType(Enum):
    """窗口控制类型枚举"""
    activate = "activate"
    maximize = "maximize"
    minimize = "minimize"
    close = "close"
    restore = "restore"


# 消息类型对应的大写格式（用于协议）
MSG_TYPE_MAP = {
    MessageType.E_StartTest: "E_StartTest",
    MessageType.E_OperationStart: "E_OperationStart",
    MessageType.E_OperationDone: "E_OperationDone",
    MessageType.E_OperationError: "E_OperationError",
    MessageType.E_Ping: "E_Ping",
    MessageType.E_ConnectionLost: "E_ConnectionLost",
}
