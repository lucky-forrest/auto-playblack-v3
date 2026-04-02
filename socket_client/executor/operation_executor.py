# -*- coding: UTF-8 -*-
"""
操作执行器，负责执行各种鼠标和窗口操作
"""
import time
from typing import Optional

import pyautogui
import pygetwindow
from pygetwindow import PyGetWindowException

import socket_client.models.operation as operation_model
import socket_client.utils.exceptions as exception_module
import socket_client.config as config_module

Operation = operation_model.Operation
OperationExecuteError = exception_module.OperationExecuteError
WindowNotFoundError = exception_module.WindowNotFoundError
config = config_module.config
logger = config_module.logger


class OperationExecutor:
    """操作执行器，负责执行各种自动化操作"""

    def __init__(self):
        """初始化操作执行器"""
        self._current_window = None
        # 设置 pyautogui 防护机制
        # 注意：点击无效时，尝试关闭 FAILSAFE 来排除问题
        pyautogui.FAILSAFE = False  # 关闭failsafe，避免意外中断
        pyautogui.PAUSE = 0.1

    def execute_operation(
        self,
        operation: Operation,
        window_title: Optional[str] = None
    ) -> bool:
        """
        执行单次操作

        Args:
            operation: Operation对象
            window_title: 目标窗口标题，如果不为空会尝试激活该窗口

        Returns:
            bool: 操作是否成功

        Raises:
            OperationExecuteError: 操作执行失败时抛出
        """
        try:
            # 如果指定了窗口标题，激活该窗口
            if window_title:
                self._activate_window(window_title)

            # 根据操作类型执行相应的操作
            if operation.event_type == "mouse_move":
                self._mouse_move(operation)
            elif operation.event_type == "mouse_click":
                self._mouse_click(operation)
            elif operation.event_type == "mouse_scroll":
                self._mouse_scroll(operation)
            elif operation.event_type == "key_press":
                self._key_press(operation)
            elif operation.event_type == "key_release":
                self._key_release(operation)
            elif operation.event_type == "window_control":
                self._window_control(operation)
            else:
                raise OperationExecuteError(f"不支持的操作类型: {operation.event_type}")

            logger.debug(f"操作成功: {operation.event_type} at ({operation.x}, {operation.y})")
            return True

        except Exception as e:
            error_msg = f"操作执行失败: {operation.event_type}, 坐标: ({operation.x}, {operation.y}), 错误: {e}"
            logger.error(error_msg)
            raise OperationExecuteError(error_msg, operation.event_type, (operation.x, operation.y))

    def _ensure_window_active(self, window_title: str) -> bool:
        """
        确保窗口是激活状态

        Args:
            window_title: 窗口标题

        Returns:
            bool: 窗口是否成功激活或已经是激活状态
        """
        try:
            # 获取窗口
            windows = pygetwindow.getWindowsWithTitle(window_title)
            if not windows:
                logger.warning(f"找不到窗口: {window_title}")
                return False

            window = windows[0]

            # 检查是否已经激活
            if window.isActive:
                logger.debug(f"窗口 [{window_title}] 已经激活")
                return True

            # 尝试激活窗口
            logger.debug(f"尝试激活窗口: {window_title}")
            window.activate()

            # 等待窗口激活
            import time
            time.sleep(0.3)

            # 再次检查
            window.refresh()
            if window.isActive:
                logger.debug(f"窗口 [{window_title}] 已激活成功")
                return True
            else:
                logger.warning(f"窗口 [{window_title}] 激活后仍未变为激活状态")
                return False

        except Exception as e:
            logger.warning(f"检查/激活窗口失败: {e}")
            return False

    def _mouse_move(self, operation: Operation) -> None:
        """
        移动鼠标到指定坐标

        Args:
            operation: 包含鼠标移动操作的对象
        """
        if operation.x is None or operation.y is None:
            raise OperationExecuteError("鼠标移动缺少坐标信息")

        logger.debug(f"移动鼠标到 ({operation.x}, {operation.y})")
        pyautogui.moveTo(operation.x, operation.y)

    def _mouse_click(self, operation: Operation) -> None:
        """
        在指定坐标执行左键点击

        Args:
            operation: 包含鼠标点击操作的对象
        """
        if operation.x is None or operation.y is None:
            raise OperationExecuteError("鼠标点击缺少坐标信息")

        logger.debug(f"在坐标 ({operation.x}, {operation.y}) 执行左键点击")
        pyautogui.click(x=operation.x, y=operation.y, button='left')

    def _mouse_scroll(self, operation: Operation) -> None:
        """
        鼠标滚动操作

        Args:
            operation: 包含鼠标滚轮操作的对象

        注意: 使用 pyautogui.scroll() 实现
        """
        detail = operation.detail.lower()
        scroll_distance = 10  # 每次滚动的距离

        if "up" in detail or "上" in detail:
            pyautogui.scroll(scroll_distance)
            logger.debug("执行向上滚动")
        elif "down" in detail or "下" in detail:
            pyautogui.scroll(-scroll_distance)
            logger.debug("执行向下滚动")
        else:
            logger.warning(f"未识别的滚动操作: {detail}")

    def _key_press(self, operation: Operation) -> None:
        """
        模拟键盘按下操作

        Args:
            operation: 包含按键操作的对象

        注意: 使用 pyautogui.press() 发送按键
        """
        detail = operation.detail.lower()
        logger.debug(f"按下按键: {detail}")
        try:
            pyautogui.press(detail)
        except Exception as e:
            # 如果特定的按键名称不工作，尝试发送字符串
            raise OperationExecuteError(f"按键发送失败: {e}")

    def _key_release(self, operation: Operation) -> None:
        """
        模拟键盘释放操作

        Args:
            operation: 包含按键操作的对象

        注意: PyAutoGUI 的 press() 会自动处理按下和释放，通常不需要单独的 release
        """
        detail = operation.detail
        logger.debug(f"释放按键: {detail}")

    def _window_control(self, operation: Operation) -> None:
        """
        执行窗口控制操作

        Args:
            operation: 包含窗口控制操作的对象
        """
        if operation.control_text:
            self._control_click(operation.window_title, operation.control_text)
        else:
            raise OperationExecuteError("窗口控制操作缺少控件文本")

    def _activate_window(self, window_title: str) -> None:
        """
        激活指定窗口

        Args:
            window_title: 窗口标题

        Raises:
            WindowNotFoundError: 窗口不存在时抛出
        """
        try:
            windows = pygetwindow.getWindowsWithTitle(window_title)
            if windows:
                window = windows[0]
                window.activate()
                time.sleep(0.1)  # 等待窗口激活
                self._current_window = window
            else:
                raise WindowNotFoundError(f"窗口不存在: {window_title}", window_title)
        except PyGetWindowException as e:
            raise WindowNotFoundError(f"窗口操作失败: {window_title}, 错误: {e}", window_title)
        except Exception as e:
            raise WindowNotFoundError(f"激活窗口失败: {window_title}, 错误: {e}", window_title)

    def _control_click(self, window_title: str, control_text: str) -> None:
        """
        点击指定窗口中的控件

        Args:
            window_title: 窗口标题
            control_text: 控件文本或类名

        注意: 由于 Windows GUI 自动化的复杂性，提供多种尝试策略
        """
        logger.debug(f"点击窗口 [{window_title}] 中的控件: {control_text}")

        # 获取窗口
        windows = pygetwindow.getWindowsWithTitle(window_title)
        if not windows:
            raise WindowNotFoundError(f"窗口不存在: {window_title}", window_title)

        window = windows[0]

        # 尝试策略1：先激活窗口
        try:
            window.activate()
            time.sleep(0.2)
        except Exception as e:
            logger.warning(f"无法激活窗口: {e}")

        # 尝试策略2：使用窗口坐标 + pyautogui 点击
        try:
            window_rect = window.rect
            x = window_rect.x + window_rect.width // 2
            y = window_rect.y + window_rect.height // 2

            # 尝试在窗口中心点击
            pyautogui.click(x=x, y=y, button='left')
            time.sleep(0.2)
            logger.debug(f"在窗口中心 ({x}, {y}) 执行点击")
            return

        except Exception as e:
            logger.warning(f"窗口中心点击失败: {e}")

        # 尝试策略3：使用 Alt + 控件文本 快捷键
        try:
            # 分解控件文本，尝试作为 Alt 快捷键
            key_parts = control_text.split()
            if len(key_parts) == 2:
                # 组合格式: alt + key
                pyautogui.hotkey('alt', key_parts[1])
                time.sleep(0.2)
                logger.debug(f"使用快捷键 Alt + {key_parts[1]} 点击控制")
                return
        except Exception as e:
            logger.warning(f"快捷键方式失败: {e}")

        # 尝试策略4：点击整个窗口区域
        window_rect = window.rect
        try:
            window.activate()
            time.sleep(0.2)
            pyautogui.click(x=window_rect.x, y=window_rect.y, button='left')
            time.sleep(0.2)
            logger.debug(f"点击窗口左上角")
            return
        except Exception as e:
            logger.warning(f"窗口定位点击失败: {e}")

        raise OperationExecuteError(f"无法点击控件 {control_text}，已尝试多种方法失败", control_text, (None, None))

    def stop(self):
        """停止操作执行"""
        logger.info("操作执行器已停止")
