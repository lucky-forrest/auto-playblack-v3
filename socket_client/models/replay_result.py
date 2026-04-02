# -*- coding: UTF-8 -*-
"""
回放结果数据模型
"""
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class OperationResult:
    """单次操作执行结果"""

    success: bool
    operation_type: str
    message: str = ""
    error_details: Optional[str] = None

    def __post_init__(self):
        """初始化后的处理"""
        if self.success:
            self.message = f"{self.operation_type} 执行成功"
        else:
            self.message = f"{self.operation_type} 执行失败: {self.error_details}"


@dataclass
class ReplayResult:
    """回放结果对象"""

    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_time_elapsed: float = 0.0
    execution_start_time: Optional[float] = None
    execution_end_time: Optional[float] = None
    results: List[OperationResult] = field(default_factory=list)

    def add_result(self, result: OperationResult):
        """添加操作执行结果

        Args:
            result: 操作执行结果对象
        """
        self.results.append(result)
        self.total_operations += 1
        if result.success:
            self.successful_operations += 1
        else:
            self.failed_operations += 1

    def is_completed(self) -> bool:
        """判断回放是否已完成

        Returns:
            bool: 回放是否完成
        """
        return self.execution_end_time is not None

    def get_success_rate(self) -> float:
        """获取成功率

        Returns:
            float: 成功率，百分比，0.0-100.0
        """
        if self.total_operations == 0:
            return 0.0
        return (self.successful_operations / self.total_operations) * 100

    def to_dict(self):
        """将结果对象转换为字典

        Returns:
            dict: 结果信息的字典表示
        """
        return {
            'total_operations': self.total_operations,
            'successful_operations': self.successful_operations,
            'failed_operations': self.failed_operations,
            'success_rate': self.get_success_rate(),
            'total_time_elapsed': self.total_time_elapsed,
            'results': [
                {
                    'success': r.success,
                    'operation_type': r.operation_type,
                    'message': r.message,
                    'error_details': r.error_details
                }
                for r in self.results
            ]
        }

    def __repr__(self):
        """获取结果对象的字符串表示"""
        return (f"ReplayResult(total={self.total_operations}, "
                f"success={self.successful_operations}, failed={self.failed_operations}, "
                f"success_rate={self.get_success_rate():.2f}%, "
                f"time={self.total_time_elapsed:.3f}秒)")
