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

        注意: 滚动操作需要鼠标先移动到目标位置才能正确滚动目标窗口的内容
        """
        # print(f"执行鼠标滚动操作，坐标: ({operation.x}, {operation.y}), detail: {operation.detail}, scroll_delta: {operation.scroll_delta}")

        # 关键步骤：先激活窗口，确保滚动的是正确的窗口
        if operation.window_title:
            try:
                logger.debug(f"滚动前激活窗口: {operation.window_title}")
                windows = pygetwindow.getWindowsWithTitle(operation.window_title)
                if windows:
                    window = windows[0]
                    window.activate()
                    time.sleep(0.2)  # 等待窗口激活
                    self._current_window = window
                    logger.debug(f"窗口 [{operation.window_title}] 已激活")
                else:
                    logger.warning(f"未找到窗口: {operation.window_title}")
            except PyGetWindowException as e:
                logger.warning(f"无法激活窗口 [{operation.window_title}]: {e}")

        # 再移动鼠标到目标坐标
        if operation.x is not None and operation.y is not None:
            logger.debug(f"滚动前移动鼠标到: ({operation.x}, {operation.y})")
            pyautogui.moveTo(operation.x, operation.y)
            time.sleep(0.1)  # 短暂延迟，确保鼠标已经到达目标位置

        detail = operation.detail.lower()

        # 优先使用CSV记录的scroll_delta值，否则从detail解析
        if operation.scroll_delta is not None and operation.scroll_delta != 0:
            # 使用CSV记录的滚动距离
            scroll_distance = int(operation.scroll_delta)*50
        else:
            # 从detail字段解析滚动方向
            scroll_distance = 50  # 默认每次滚动的距离

            if "up" in detail or "上" in detail:
                scroll_distance = abs(scroll_distance)
                logger.debug("执行向上滚动")
            elif "down" in detail or "下" in detail:
                scroll_distance = -abs(scroll_distance)
                logger.debug("执行向下滚动")
            else:
                logger.warning(f"未识别的滚动方向，无法确定滚动方向: {detail}")
                # 默认向下滚动
                scroll_distance = 50
                logger.debug("默认执行向下滚动")

        # 执行滚动操作
        logger.debug(f"执行滚动操作: {scroll_distance} 格")
        print(f"执行滚动操作: {scroll_distance} 格")
        pyautogui.scroll(scroll_distance)
        time.sleep(0.1)  # 滚动后短暂延迟，确保事件被处理

    def _key_press(self, operation: Operation) -> None:
        """
        模拟键盘按下操作

        Args:
            operation: 包含按键操作的对象

        注意: 别名 Key: a、Key: shift 等格式
        - 修饰键单独发送（shift, ctrl, alt, win等）
        - 字母/数字键支持组合输入（shift + a = A）
        """
        detail = operation.detail.lower()
        logger.debug(f"按下按键: {detail}")

        # 从detail字段提取实际的按键名称
        # CSV中的格式通常是 "Key: a"、"Key: shift"、"Key: backspace" 等
        key_name = detail.replace("key: ", "").strip()

        # 修饰键列表 - 这些键单独发送，用于与其他键组合
        modifier_keys = {'shift', 'ctrl', 'control', 'alt', 'windows', 'win', 'command', 'apple'}

        # 处理特殊按键名称的映射
        # pyautogui.press() 支持: enter, tab, esc, space, up, down, left, right, backspace, home, end, pgup, pgdn, del, ins
        # pyautogui.hotkey() 支持: shift, ctrl, alt, win 等修饰键组合
        special_keys = {'enter', 'tab', 'esc', 'space', 'up', 'down', 'left', 'right',
                       'backspace', 'home', 'end', 'pgup', 'pgdn', 'del', 'ins',
                       'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10',
                       'f11', 'f12', 'caps lock', 'num lock', 'scroll lock'}

        if key_name in modifier_keys:
            # 修饰键 - 虽然也可以用 press() 发送，但为了兼容组合键，我们也用 press()
            try:
                pyautogui.press(key_name)
                logger.debug(f"发送修饰键: {key_name}")
            except Exception as e:
                raise OperationExecuteError(f"修饰键发送失败 (key_name={key_name}): {e}")
        elif key_name in special_keys:
            # 特殊按键 - 使用 press()
            try:
                pyautogui.press(key_name)
                logger.debug(f"成功按下特殊按键: {key_name}")
            except Exception as e:
                logger.error(f"特殊按键发送失败 (key_name={key_name}): {e}")
                # 作为备用方案，尝试使用 write()
                try:
                    pyautogui.write(key_name.lower(), interval=0.02)
                    logger.debug(f"使用write发送特殊按键: {key_name}")
                except Exception as e2:
                    raise OperationExecuteError(f"特殊按键发送失败 (key_name={key_name}): {e2}")
        else:
            # 普通字母/数字键 - 逐个发送
            try:
                # 使用单独的press()逐个发送按键，确保在任何应用中都能工作
                # 比write()更可靠，因为它不依赖输入焦点
                for char in key_name.lower():
                    pyautogui.press(char)
                logger.debug(f"成功输入按键: {key_name}")
                # 在发送单个字符后添加小延迟，确保被接收
                time.sleep(0.05)
            except Exception as e:
                logger.error(f"按键输入失败 (key_name={key_name}, detail={detail}): {e}")
                # 如果单独发送失败，尝试使用write()作为备用
                try:
                    pyautogui.write(key_name.lower(), interval=0.02)
                    logger.debug(f"使用write发送按键: {key_name}")
                except Exception as e2:
                    # 最后尝试使用hotkey
                    modifier = []
                    if 'shift' in detail.lower():
                        modifier.append('shift')
                    try:
                        pyautogui.hotkey(*modifier, key_name.lower())
                        logger.debug(f"使用hotkey组合键输入: {('+'.join(modifier) if modifier else '')} + {key_name}")
                    except Exception as e3:
                        raise OperationExecuteError(f"按键发送失败 (key_name={key_name}): {e3}")

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
