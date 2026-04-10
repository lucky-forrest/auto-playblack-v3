# -*- coding: UTF-8 -*-
"""
配置管理模块，提供全局配置和日志配置
"""
import logging
import sys
from pathlib import Path

# 添加项目根目录到sys.path
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# 现在可以导入项目包
from models.operation import Operation
from utils.exceptions import OperationExecuteError


# 默认配置
class Config:
    """全局配置类"""

    def __init__(self):
        """初始化配置"""
        # CSV文件路径
        self.csv_path = "documents/录制会话_20260402_100410/录制会话_20260410_120525_operation_log.csv"

        # 时间控制精度（秒）
        self.time_precision = 0.1

        # 日志级别
        self.log_level = "INFO"

    def __getattr__(self, name):
        """动态属性（向后兼容）"""
        if name == "csv_path":
            return self._csv_path
        elif name == "time_precision":
            return self._time_precision
        elif name == "log_level":
            return self._log_level
        else:
            raise AttributeError(f"'Config' 对象没有属性 '{name}'")

    def __setattr__(self, name, value):
        """设置属性"""
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            if name == "csv_path":
                self._csv_path = value
            elif name == "time_precision":
                self._time_precision = value
            elif name == "log_level":
                self._log_level = value


# 全局配置实例
config = Config()


def setup_logging(level: str = "INFO", log_file: str = None):
    """
    设置日志系统

    Args:
        level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        log_file: 日志文件路径，None则不写入文件
    """
    global logger

    # 标准化日志级别名称
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }

    level_upper = level.upper()
    log_level = level_map.get(level_lower := level.lower(), logging.INFO)

    # 创建logger
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    # 清理已有的handlers
    logger.handlers.clear()

    # 日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # 创建formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # 控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件handler（可选）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.info(f"日志系统初始化完成，级别: {level}")


# 初始化日志
setup_logging()
