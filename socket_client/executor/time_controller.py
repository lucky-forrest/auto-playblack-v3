# -*- coding: UTF-8 -*-
"""
时间控制器，负责计算和等待时间
"""
import time
from typing import Optional

import socket_client.utils.exceptions as exception_module
import socket_client.config as config_module

TimeCalculationError = exception_module.TimeCalculationError
config = config_module.config
logger = config_module.logger


class TimeController:
    """时间控制器，负责精确控制操作的时间延迟"""

    def __init__(self, precision: float = None):
        """
        初始化时间控制器

        Args:
            precision: 时间精度要求，默认使用配置中的值
        """
        self.precision = precision or config.time_precision
        self._last_operation_timestamp: Optional[float] = None

    def calculate_delay(self, operation_timestamp: float) -> float:
        """
        计算操作延迟时间（操作之间的间隔）

        Args:
            operation_timestamp: 当前操作的时间戳

        Returns:
            float: 延迟时间（秒），表示距离上一个操作的时间间隔

        Raises:
            TimeCalculationError: 如果第一个操作或时间间隔为负数时抛出
        """
        # 如果没有上一个执行时间，说明这是第一个操作
        if self._last_operation_timestamp is None:
            delay = 0.0
        else:
            # 计算两个操作时间戳之间的差值
            delay = operation_timestamp - self._last_operation_timestamp

            if delay < 0:
                logger.warning(
                    f"时间戳递减：当前 {operation_timestamp:.3f}，上一次 {self._last_operation_timestamp:.3f}，"
                    f"延迟 {delay:.3f} 秒，取值为0"
                )
                delay = 0.0

        # 四舍五入到指定精度（转换为整数位数）
        precision_int = int(self.precision * 10) if self.precision <= 3 else int(self.precision)
        return round(delay, precision_int)

    def wait_for_delay(self, delay: float) -> None:
        """
        等待指定的延迟时间

        Args:
            delay: 要等待的延迟时间（秒）

        Raises:
            TimeCalculationError: 等待超时时抛出
        """
        if delay <= 0:
            logger.debug("延迟时间为0或负数，跳过等待")
            return

        logger.debug(f"等待 {delay:.3f} 秒")
        try:
            # 使用time.sleep实现精确的延迟等待
            time.sleep(delay)
        except Exception as e:
            logger.error(f"等待过程发生错误: {e}")
            raise TimeCalculationError(f"等待过程发生错误: {e}", delay)

    def record_operation_timestamp(self, operation_timestamp: float):
        """
        记录已执行的操作时间戳

        Args:
            operation_timestamp: 本次操作的时间戳

        Note:
            这用于计算连续操作之间的时间间隔
        """
        self._last_operation_timestamp = operation_timestamp

    def get_last_operation_timestamp(self) -> Optional[float]:
        """
        获取上次记录的操作时间戳

        Returns:
            float: 上次操作时间戳，无记录返回None
        """
        return self._last_operation_timestamp

    def execute_with_delay(
        self,
        operation_timestamp: float,
        operation_type: str
    ) -> float:
        """
        计算并执行时间延迟

        Args:
            operation_timestamp: 操作的时间戳（时间戳类型，不是时间字符串）
            operation_type: 操作类型，用于日志记录

        Returns:
            float: 实际执行的延迟时间

        Raises:
            TimeCalculationError: 时间计算错误时抛出
        """
        # 计算延迟时间
        delay = self.calculate_delay(operation_timestamp)

        if delay > 0:
            # 执行等待
            self.wait_for_delay(delay)
            logger.debug(f"操作 [{operation_type}] 等待完成，实际延迟: {delay:.3f}秒")
        else:
            logger.debug(f"操作 [{operation_type}] 立即执行（延迟: {delay:.3f}秒）")

        # 记录操作时间戳，用于计算下一个操作的时间间隔
        self.record_operation_timestamp(operation_timestamp)

        # 添加调试日志：显示两个操作的时间戳差值
        last_ts = self.get_last_operation_timestamp()
        if last_ts is not None:
            logger.debug(f"操作间隔: 上次 {last_ts:.6f} → 当前 {operation_timestamp:.6f}, 差值 {delay:.6f}秒")

        return delay

    def reset(self) -> None:
        """重置执行时间记录"""
        self._last_operation_timestamp = None
