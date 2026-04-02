# -*- coding: UTF-8 -*-
"""
auto-playblack-v3 软件代操系统
Python版本: 3.6+

socket_client包的主初始化文件
"""
__version__ = "1.0.0"
__author__ = "auto-playblack Team"

# 导出主要类
from .executor.replay_engine import OperationReplayEngine, execute_csv_replay
from .models.operation import Operation
from .models.replay_result import ReplayResult

__all__ = [
    'OperationReplayEngine',
    'execute_csv_replay',
    'Operation',
    'ReplayResult',
]
