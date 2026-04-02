# -*- coding: UTF-8 -*-
"""
操作回放引擎,整合所有模块实现完整的回放流程
"""
import time
from typing import Optional, List, Callable

import socket_client.models.operation as operation_model
import socket_client.models.replay_result as replay_result_model
import socket_client.parsers.csv_parser as csv_parser_module
import socket_client.utils.exceptions as exception_module
import socket_client.config as config_module

Operation = operation_model.Operation
ReplayResult = replay_result_model.ReplayResult
OperationResult = replay_result_model.OperationResult
parse_operation_log = csv_parser_module.parse_operation_log
OperationExecuteError = exception_module.OperationExecuteError
config = config_module.config
logger = config_module.logger
from .operation_executor import OperationExecutor
from .time_controller import TimeController


class OperationReplayEngine:
    """操作回放引擎，负责整个CSV回放流程"""

    def __init__(self, csv_path: Optional[str] = None, logger_instance=None):
        """
        初始化回放引擎

        Args:
            csv_path: CSV文件路径，默认使用配置中的路径
            logger_instance: 日志记录器实例，None则使用配置中的日志
        """
        self.csv_path = csv_path
        self.logger = logger_instance or logger

        # 创建解析器和执行器
        self.parser = parse_operation_log(csv_path)
        self.executor = OperationExecutor()
        self.time_controller = TimeController()

        # 回放状态
        self._is_running = False
        self._current_callback: Optional[Callable] = None
        self._operations: List[Operation] = []

    def load_operations(self) -> List[Operation]:
        """
        加载并解析操作记录

        Returns:
            Operation对象列表

        Raises:
            OperationExecuteError: 加载失败时抛出
        """
        try:
            self.logger.info(f"开始加载操作记录: {self.csv_path}")
            operations = self.parser  # parse_operation_log返回的是列表

            if not operations:
                raise OperationExecuteError("操作记录为空，没有可执行的操作")

            self.logger.info(f"加载完成，共 {len(operations)} 条操作记录")
            self._operations = operations
            return operations

        except Exception as e:
            self.logger.error(f"加载操作记录失败: {e}")
            raise OperationExecuteError(f"加载操作记录失败: {e}")

    def start_replay(self, callback: Optional[Callable] = None) -> ReplayResult:
        """
        开始回放操作

        Args:
            callback: 回调函数，用于报告进度（operation_index, total_operations, operation）

        Returns:
            ReplayResult: 回放结果对象

        Raises:
            OperationExecuteError: 回放失败时抛出
        """
        self._is_running = True
        self._current_callback = callback

        # 重置时间控制器
        self.time_controller.reset()

        # 创建结果对象
        result = ReplayResult(
            execution_start_time=time.time()
        )

        try:
            self.logger.info("=" * 60)
            self.logger.info("操作回放开始")
            self.logger.info(f"操作记录文件: {self.csv_path}")
            self.logger.info("=" * 60)

            # 加载操作记录
            operations = self.load_operations()
            result.total_operations = len(operations)

            self.logger.info(f"开始执行 {result.total_operations} 条操作...")

            # 执行每条操作
            for i, operation in enumerate(operations):
                if not self._is_running:
                    self.logger.warning("回放已被停止，终止执行")
                    break

                try:
                    # 计算并等待时间延迟
                    self.time_controller.execute_with_delay(
                        operation.timestamp,
                        operation.event_type
                    )

                    # 执行具体操作
                    success = self.executor.execute_operation(
                        operation,
                        operation.window_title
                    )

                    # 创建结果对象
                    op_result = OperationResult(
                        success=success,
                        operation_type=operation.event_type
                    )

                    # 记录结果
                    result.add_result(op_result)

                    # 执行回调
                    if self._current_callback:
                        self._current_callback(i + 1, result.total_operations, operation)

                    self.logger.debug(f"[{i + 1}/{result.total_operations}] {op_result.message}")

                except OperationExecuteError as e:
                    error_result = OperationResult(
                        success=False,
                        operation_type=operation.event_type,
                        message=str(e),
                        error_details=f"操作类型: {e.operation_type}, 坐标: {e.coordinates}"
                    )

                    result.add_result(error_result)
                    self.logger.error(f"[{i + 1}/{result.total_operations}] 操作失败: {e.message}")

            # 回放完成
            result.execution_end_time = time.time()
            result.total_time_elapsed = result.execution_end_time - result.execution_start_time

            self._log_replay_result(result)

            return result

        except Exception as e:
            self.logger.error(f"回放过程中发生错误: {e}", exc_info=True)
            raise OperationExecuteError(f"回放过程中发生错误: {e}")

        finally:
            # 停止执行器
            self.executor.stop()
            self._is_running = False
            self._current_callback = None

    def stop(self) -> None:
        """停止当前回放"""
        self._is_running = False
        self.logger.info("回放已停止")

    def _log_replay_result(self, result: ReplayResult):
        """
        记录回放结果到日志

        Args:
            result: 回放结果对象
        """
        self.logger.info("=" * 60)
        self.logger.info("操作回放完成")
        self.logger.info("=" * 60)
        self.logger.info(f"总操作数: {result.total_operations}")
        self.logger.info(f"成功数: {result.successful_operations}")
        self.logger.info(f"失败数: {result.failed_operations}")
        self.logger.info(f"成功率: {result.get_success_rate():.2f}%")
        self.logger.info(f"总耗时: {result.total_time_elapsed:.3f}秒")
        self.logger.info(f"平均每条操作: {(result.total_time_elapsed / result.total_operations):.3f}秒")

        if result.failed_operations > 0:
            self.logger.warning("=" * 60)
            self.logger.warning("失败的操作详情:")
            self.logger.warning("=" * 60)
            for r in result.results:
                if not r.success:
                    self.logger.warning(f"- {r.operation_type}: {r.message}")

    def get_operation_by_index(self, index: int) -> Optional[Operation]:
        """
        根据索引获取操作

        Args:
            index: 操作索引（从0开始）

        Returns:
            Operation对象，不存在返回None
        """
        operations = self.parser
        if 0 <= index < len(operations):
            return operations[index]
        return None

    def get_operations_count(self) -> int:
        """获取操作数量"""
        return len(self.parser)


def execute_csv_replay(
    csv_path: Optional[str] = None,
    callback: Optional[Callable] = None
) -> ReplayResult:
    """
    执行CSV回放的便捷函数

    Args:
        csv_path: CSV文件路径
        callback: 进度回调函数

    Returns:
        ReplayResult: 回放结果对象
    """
    engine = OperationReplayEngine(csv_path)
    return engine.start_replay(callback)
