# -*- coding: UTF-8 -*-
"""
CSV文件解析器
"""
import csv
import time
import json
from typing import List, Optional
from pathlib import Path

import socket_client.models.operation as operation_model
import socket_client.utils.exceptions as exception_module
import socket_client.config as config_module

Operation = operation_model.Operation
CSVParseError = exception_module.CSVParseError
config = config_module.config
logger = config_module.logger


class CSVParser:
    """CSV文件解析器，用于解析操作记录文件"""

    def __init__(self, csv_path: Optional[str] = None, project_root: str = None):
        """初始化CSV解析器

        Args:
            csv_path: CSV文件路径，默认使用配置中的路径
            project_root: 项目根目录，用于处理相对导入
        """
        self.csv_path = csv_path or config.csv_path
        self.project_root = project_root

        # 如果指定了项目根目录，更新path以支持绝对导入
        if self.project_root:
            import sys
            if str(self.project_root) not in sys.path:
                sys.path.insert(0, str(self.project_root))

        self.operations: List[Operation] = []

    def parse(self) -> List[Operation]:
        """解析CSV文件，返回操作列表

        Returns:
            Operation对象列表

        Raises:
            CSVParseError: CSV解析失败时抛出
        """
        try:
            self.operations = []
            path = Path(self.csv_path)

            if not path.exists():
                raise CSVParseError(f"CSV文件不存在: {self.csv_path}")

            with open(path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)

                # 验证文件是否有数据
                total_rows = 0
                for row in reader:
                    total_rows += 1
                    operation = self._parse_row(row)
                    if operation is not None:
                        self.operations.append(operation)

            logger.info(f"CSV文件解析成功: {self.csv_path}，共解析 {len(self.operations)} 条操作")
            return self.operations

        except csv.Error as e:
            raise CSVParseError(f"CSV格式错误: {e}")
        except Exception as e:
            raise CSVParseError(f"CSV解析过程发生错误: {e}")

    def parse_json(self) -> List[Operation]:
        """解析JSON格式的操作记录文件

        Returns:
            Operation对象列表

        Raises:
            CSVParseError: JSON解析失败时抛出
        """
        try:
            self.operations = []

            with open(self.csv_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise CSVParseError("JSON文件格式错误：根节点应为对象")

            events = data.get('events', [])
            if not isinstance(events, list):
                raise CSVParseError("JSON文件格式错误：缺少events数组")

            for idx, event in enumerate(events):
                try:
                    import datetime
                    timestamp = datetime.datetime.fromisoformat(event['time']).timestamp()

                    operation = Operation(
                        timestamp=timestamp,
                        event_type=event['type'],
                        detail=event.get('detail', ''),
                        x=event.get('x'),
                        y=event.get('y'),
                        window_title=event.get('window_title', ''),
                        control_text=event.get('control_text', ''),
                        delay=0.0  # 延迟由 TimeController 计算
                    )
                    self.operations.append(operation)
                except KeyError as e:
                    logger.warning(f"跳过第{idx+1}条记录（缺少字段 {e}）")
                    continue

            logger.info(f"JSON文件解析成功: {self.csv_path}，共解析 {len(self.operations)} 条操作")
            return self.operations

        except json.JSONDecodeError as e:
            raise CSVParseError(f"JSON格式错误: {e}")
        except Exception as e:
            raise CSVParseError(f"JSON解析过程发生错误: {e}")

    def _parse_row(self, row: dict) -> Optional[Operation]:
        """解析CSV单行数据

        Args:
            row: CSV行数据字典

        Returns:
            Operation对象，解析失败返回None
        """
        try:
            # 解析时间戳
            timestamp_str = row.get('timestamp', '')
            if not timestamp_str:
                logger.warning(f"跳过空记录，第1列timestamp为空")
                return None

            # 转换时间格式
            try:
                import datetime
                # 尝试解析ISO 8601格式时间戳
                timestamp = datetime.datetime.fromisoformat(timestamp_str).timestamp()
            except ValueError:
                # 如果失败，使用记录时间
                timestamp = time.time()

            # 提取事件类型和坐标信息
            event_type = row.get('event_type', '').strip().lower()

            # 从detail字段提取坐标信息
            detail = row.get('detail', '')
            x = None
            y = None

            # 解析detail字段中的坐标
            detail_lower = detail.lower()
            if 'mouse at (' in detail_lower:
                try:
                    # 格式: "Mouse at (725, 689)"
                    content_after_bracket = detail_lower.split('(')[1]
                    coords = content_after_bracket.split(')')[0]
                    x_str, y_str = coords.split(',')
                    x = int(x_str.strip())
                    y = int(y_str.strip())
                except (ValueError, IndexError):
                    logger.warning(f"解析detail字段坐标失败: {detail}")

            # 获取窗口标题和控件文本
            window_title = row.get('window_title', '')
            control_text = row.get('control_text', '')

            # 确保坐标值是整数
            param_x = row.get('x', x) if row.get('x') else x
            param_y = row.get('y', y) if row.get('y') else y

            # 将坐标类型转换为整数（如果存在且有效）
            final_x = int(param_x) if param_x is not None else None
            final_y = int(param_y) if param_y is not None else None

            operation = Operation(
                timestamp=timestamp,
                event_type=event_type,
                detail=detail,
                x=final_x,
                y=final_y,
                window_title=window_title,
                control_text=control_text,
                delay=0.0  # 延迟由 TimeController 在执行时计算
            )

            return operation

        except Exception as e:
            logger.error(f"解析行数据失败: {e}, 数据: {row}")
            return None

    def get_operations_count(self) -> int:
        """获取操作数量

        Returns:
            int: 操作数量
        """
        return len(self.operations)

    def get_first_operation(self) -> Optional[Operation]:
        """获取第一条操作

        Returns:
            Operation对象，无数据返回None
        """
        return self.operations[0] if self.operations else None

    def get_last_operation(self) -> Optional[Operation]:
        """获取最后一条操作

        Returns:
            Operation对象，无数据返回None
        """
        return self.operations[-1] if self.operations else None

    def clear(self):
        """清空解析的操作列表"""
        self.operations.clear()


def parse_operation_log(
    csv_path: Optional[str] = None,
    project_root: str = None
) -> List[Operation]:
    """
    解析操作日志文件的便捷函数

    Args:
        csv_path: CSV文件路径，默认使用配置中的路径
        project_root: 项目根目录

    Returns:
        Operation对象列表

    Raises:
        CSVParseError: 解析失败时抛出
    """
    parser = CSVParser(csv_path, project_root)

    # 先尝试解析JSON，失败则尝试CSV
    try:
        return parser.parse_json()
    except Exception as json_err:
        logger.debug(f"JSON解析失败: {json_err}，尝试CSV解析")
        try:
            return parser.parse()
        except Exception as csv_err:
            raise CSVParseError(
                f"JSON和CSV解析均失败。JSON错误: {json_err}, CSV错误: {csv_err}"
            )
