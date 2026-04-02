# -*- coding: UTF-8 -*-
"""
自定义异常类定义
"""


class SocketOperationError(Exception):
    """Socket操作执行时发生的异常基类"""

    def __init__(self, message, error_code=None):
        """初始化异常

        Args:
            message: 异常描述信息
            error_code: 错误代码
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self):
        """异常信息字符串"""
        if self.error_code:
            return f"{self.__class__.__name__} [Code: {self.error_code}]: {self.message}"
        return f"{self.__class__.__name__}: {self.message}"


class CSVParseError(SocketOperationError):
    """CSV文件解析错误的异常"""

    def __init__(self, message, line_number=None):
        """初始化CSV解析异常

        Args:
            message: 异常描述信息
            line_number: 出错的行号
        """
        super().__init__(message)
        self.line_number = line_number


class OperationExecuteError(SocketOperationError):
    """操作执行失败的异常"""

    def __init__(self, message, operation_type=None, coordinates=None):
        """初始化操作执行异常

        Args:
            message: 异常描述信息
            operation_type: 操作类型
            coordinates: 坐标信息
        """
        super().__init__(message)
        self.operation_type = operation_type
        self.coordinates = coordinates


class TimeCalculationError(SocketOperationError):
    """时间计算错误的异常"""

    def __init__(self, message, delay=None):
        """初始化时间计算异常

        Args:
            message: 异常描述信息
            delay: 计算得出但无效的延迟时间
        """
        super().__init__(message)
        self.delay = delay


class WindowNotFoundError(SocketOperationError):
    """窗口未找到的异常"""

    def __init__(self, message, window_title=None):
        """初始化窗口未找到异常

        Args:
            message: 异常描述信息
            window_title: 窗口标题
        """
        super().__init__(message)
        self.window_title = window_title


class ConnectionError(SocketOperationError):
    """连接错误的异常"""

    def __init__(self, message, error_code=None):
        """初始化连接异常

        Args:
            message: 异常描述信息
            error_code: 错误代码
        """
        super().__init__(message)
        self.error_code = error_code
