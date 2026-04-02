# Python开发规范文档

## 项目规范

### 项目名称
auto-playblack-v3 软件代操系统

### 适用范围
本规范适用于auto-playblack-v3项目的所有Python代码开发工作。

---

## 1. 代码风格规范

### 1.1 文件编码
- 所有文件必须使用 **UTF-8** 编码
- 文件首行添加：`# -*- coding: UTF-8 -*-`
- 示例：
```python
# -*- coding: UTF-8 -*-
"""
操作回放测试系统
模块：operation_executor
"""
import time
```

### 1.2 缩进
- 使用 **4个空格** 作为缩进（不使用Tab）
- 禁止混合使用空格和Tab
- 示例：
```python
def function_example():
    if condition:
        # 正确的缩进
        print("Hello")
    else:
        print("World")
```

### 1.3 行长度
- 单行最大长度：**100个字符**
- 需要换行时，在运算符后换行，保持对齐
- 示例：
```python
# 错误示例
result = function_name(param1, param2, param3)

# 正确示例
result = (function_name(param1, param2,
                        param3))
```

### 1.4 导入语句
- 所有导入语句放在文件顶部
- 按分组排序：标准库 → 第三方库 → 本地模块
- 每组之间用空行分隔
- 不使用通配符导入（`from module import *`）
- 示例：
```python
# -*- coding: UTF-8 -*-
import os
import sys
import time
import csv

import autoit
from core import daemonInfo

from .models import Operation
from .utils.exceptions import OperationError
```

### 1.5 命名规范

| 类型 | 规范 | 示例 | 说明 |
|-----|------|------|------|
| 模块名 | `lowercase_with_underscores.py` | `csv_parser.py` | 简短、小写 |
| 类名 | `PascalCase` | `OperationExecutor` | 驼峰命名 |
| 函数名 | `snake_case()` | `execute_operation()` | 下划线分隔 |
| 变量名 | `snake_case` | `window_handle` | 下划线分隔 |
| 常量 | `UPPER_CASE` | `DEFAULT_TIMEOUT` | 全大写下划线 |
| 私有成员 | `_leading_underscore` | `_internal_method()` | 模块私有 |
| 保护成员 | `leading_underscore` | `_internal_var` | 类私有 |

### 1.6 注释规范
- 类和函数必须包含docstring
- 复杂逻辑必须有行内注释
- 注释使用中文
- 示例：
```python
def execute_operation(operation):
    """
    执行单次操作

    Args:
        operation: Operation对象，包含操作类型和坐标信息

    Returns:
        bool: 操作是否成功
    """
    # 计算时间差并等待
    delay = operation.timestamp - time.time()
    if delay > 0:
        time.sleep(delay)

    # 执行操作
    try:
        autoit.mouse_click("left", operation.x, operation.y)
        return True
    except Exception as e:
        logger.error(f"操作执行失败: {e}")
        return False
```

---

## 2. 类设计规范

### 2.1 类结构
- 类应包含：`__init__()`, 文档字符串，私有方法，公有方法
- 使用保护成员表示内部状态（`_private`）
- 使用强封装，避免暴露过多属性
- 示例：
```python
class TimeController:
    """时间控制器，负责计算和等待时间"""

    def __init__(self, start_time=None):
        """
        初始化时间控制器

        Args:
            start_time: 初始时间戳，默认为当前时间
        """
        self._start_time = start_time or time.time()
        self._last_executed_time = None
```

### 2.2 方法定义

| 类型 | 规范 |
|-----|------|
| 公有方法 | 小写字母开头，可带下划线 |
| 私有方法 | 单下划线开头 `_method_name()` |
| 静态方法 | 使用装饰器 `@staticmethod` |
| 类方法 | 使用装饰器 `@classmethod` |

---

## 3. 异常处理规范

### 3.1 异常定义
- 创建自定义异常类继承自`Exception`
- 复杂异常应提供详细的错误信息
- 示例：
```python
class OperationError(Exception):
    """操作执行时发生的异常基类"""
    pass

class WindowNotFoundError(OperationError):
    """窗口未找到的异常"""
    pass

class TimeCalculationError(OperationError):
    """时间计算错误的异常"""
    pass
```

### 3.2 异常捕获
- 不要捕获所有异常（`except Exception`）
- 明确捕获需要的异常类型
- 使用`try-except-finally`处理资源释放
- 异常处理应该在代码块外部有两层内层
- 示例：
```python
def safe_execute(func):
    """安全执行的装饰器"""
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except WindowNotFoundError as e:
            logger.error(f"窗口操作失败: {e}")
            raise
        except Exception as e:
            logger.error(f"未知错误: {e}", exc_info=True)
            raise
    return wrapper
```

### 3.3 日志规范
- 使用`logging`模块记录日志
- 日志级别：DEBUG < INFO < WARNING < ERROR < CRITICAL
- 添加日志前缀，便于追踪
- 示例：
```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.debug("函数开始执行")
    logger.info("操作成功")
    logger.warning("注意：窗口状态变化")
    logger.error("操作失败", exc_info=True)
    logger.critical("关键错误，系统可能无法恢复")
```

---

## 4. 文件组织规范

### 4.1 目录结构
```
operation_replay/
├── __init__.py              # 包初始化
├── main.py                  # 主程序入口
├── config.py                # 配置管理
├── models/                  # 数据模型
│   ├── __init__.py
│   ├── operation.py
│   └── session.py
├── parsers/                 # 文件解析
│   ├── __init__.py
│   ├── base_parser.py
│   └── csv_parser.py
├── executor/                # 操作执行
│   ├── __init__.py
│   ├── operation_executor.py
│   ├── window_manager.py
│   └── time_controller.py
└── utils/                   # 工具函数
    ├── __init__.py
    ├── logger.py
    └── exceptions.py
```

### 4.2 包初始化文件
每个包目录必须包含`__init__.py`：
```python
# models/__init__.py
from .operation import Operation
from .session import OperationSession

__all__ = ['Operation', 'OperationSession']
```

---

## 5. 函数设计规范

### 5.1 函数签名
- 第一行必须是文档字符串
- 文档字符串格式：`""""""`
- 参数和返回值使用`Args:`和`Returns:`说明
- 示例：
```python
def execute_operation(operation):
    """
    执行单次操作

    Args:
        operation: Operation对象
        包含以下属性：
            timestamp (float): 操作时间戳
            event_type (str): 事件类型 (mouse_move/mouse_click)
            x (int): X坐标
            y (int): Y坐标
            window_title (str): 窗口标题

    Returns:
        bool: 操作是否成功

    Raises:
        OperationError: 操作执行失败时抛出
    """
```

### 5.2 函数复杂度
- 单函数最大行数：100行
- 单函数最大圈复杂度：10
- 避免过长函数，应拆分为更小的子函数
- 嵌套层数不超过3层

---

## 6. 数据处理规范

### 6.1 类型安全
- 使用类型注解（Type Hints）
- 不要过度注释类型，类型不明确时才需要注释
- 示例：
```python
from typing import List, Optional
import time

def parse_csv_file(filename: str) -> List[Operation]:
    """
    解析CSV文件

    Args:
        filename: CSV文件路径

    Returns:
        Operation对象列表

    Raises:
        FileNotFoundError: 文件不存在时抛出
        csv.Error: CSV格式错误时抛出
    """
    operations: List[Operation] = []
```

### 6.2 空值处理
- 使用`Optional`表示可能为None的类型
- 检查None值后再访问属性
- 示例：
```python
from typing import Optional

def process_operation(operation: Optional[Operation]) -> bool:
    """
    处理操作，支持None输入

    Args:
        operation: 操作对象，可能为None

    Returns:
        bool: 处理是否成功
    """
    if operation is None:
        logger.warning("操作对象为None")
        return False

    if operation.x is None or operation.y is None:
        logger.error("操作缺少坐标信息")
        return False

    # ...
```

---

## 7. 字符串处理规范

### 7.1 字符编码
- 所有字符串处理使用UTF-8
- 中文注释和日志
- 示例：
```python
# 正确
message = "窗口标题"
logger.info("操作成功完成")

# 错误
message = b"window title"  # 不要使用bytes混合处理
```

### 7.2 格式化字符串
- 使用f-string进行字符串格式化
- 保持格式化字符串简洁明了
- 示例：
```python
# 正确
logger.info(f"操作坐标: ({x}, {y}), 延迟: {delay:.3f}秒")

# 错误
logger.info("操作坐标: (%s, %s), 延迟: %f秒" % (x, y, delay))
```

---

## 8. 资源管理规范

### 8.1 文件操作
- 使用`with`语句管理文件资源
- 文件关闭自动处理
- 示例：
```python
# 正确
with open(filename, 'r', encoding='utf-8') as f:
    data = f.read()

# 错误
f = open(filename, 'r')
try:
    data = f.read()
finally:
    f.close()
```

### 8.2 网络和外部资源
- 设置合理的超时时间
- 使用上下文管理器
- 异常处理和资源释放

```python
import socket
from contextlib import closing

def safe_connect(host: str, port: int):
    """安全连接"""
    try:
        with closing(socket.socket(socket.AF_INET,
                                  socket.SOCK_STREAM)) as s:
            s.settimeout(5)
            s.connect((host, port))
            return s
    except Exception as e:
        logger.error(f"连接失败: {e}")
        raise
```

---

## 9. 测试规范

### 9.1 测试文件命名
- 测试文件命名：`test_*.py`
- 测试函数命名：`test_*`
- 测试类命名：`Test*`

### 9.2 测试结构
- 使用pytest框架
- 测试前置准备和清理
- 使用断言验证结果
- 示例：
```python
import pytest
from models.operation import Operation

def test_operation_model():
    """测试操作模型"""
    op = Operation(
        timestamp=123456.789,
        event_type='mouse_click',
        detail='Left click',
        x=100,
        y=200,
        window_title='Test Window'
    )

    assert op.event_type == 'mouse_click'
    assert op.x == 100
    assert op.y == 200
```

### 9.3 测试覆盖
- 覆盖主要功能逻辑
- 覆盖异常处理路径
- 覆盖边界条件

---

## 10. 接口设计规范

### 10.1 公共接口
- 保持接口简单清晰
- 避免方法过重
- 提供合理的默认参数
- 示例：
```python
def execute_replay(session: OperationSession,
                   auto_confirm: bool = False,
                   logger: Optional[logging.Logger] = None):
    """
    执行操作回放

    Args:
        session: 操作会话数据
        auto_confirm: 是否自动确认弹窗，默认为False
        logger: 日志记录器，默认为None

    Returns:
        ReplayResult: 回放结果对象

    Example:
        >>> session = parse_csv("test.csv")
        >>> result = execute_replay(session)
        >>> print(result.success)
    """
```

### 10.2 版本兼容
- 使用语义化版本控制
- 向后兼容性考虑
- 废弃接口标记（`@deprecated`）

---

## 11. 分支策略

### 11.1 分支命名
- `main`: 主分支，稳定版本
- `dev`: 开发分支
- `feature/*`: 功能开发分支
- `bugfix/*`: 修复分支

### 11.2 提交信息规范
使用Git提交时遵循以下格式：
```
<type>(<scope>): <subject>

<body>

<footer>
```

类型(type):
- `feat`: 新功能
- `fix`: 关键bug修复
- `doc`: 文档更新
- `style`: 代码风格调整
- `test`: 测试相关
- `refactor`: 重构

示例：
```
feat(operation): 添加多线程操作回放支持

- 实现ThreadPoolExecutor用于并发操作
- 支持超时控制和取消机制
- 添加性能监控指标

Closes #123
```

---

## 12. 文档要求

### 12.1 README
- 必须包含项目介绍
- 包含安装步骤
- 包含使用示例
- 包含常见问题

### 12.2 API文档
- 使用Sphinx或类似工具自动生成
- 类和方法必须有docstring
- 包含参数、返回值、异常说明

---

## 13. 文档化工作流程

根据CLAUDE.md全局设置：

1. **始终用中文回复**
   - 代码注释：中文
   - 文档字符串：中文
   - 日志信息：中文
   - 项目文档：中文

2. **完成代码更改后必须进行检查**
   - 检查代码是否完整实现需求
   - 检查代码风格是否符合规范
   - 检查是否有遗漏的功能点
   - 反问自己："我真的完成了吗？"

---

## 14. 开发工具

### 14.1 推荐工具
- **代码编辑器**: VS Code, PyCharm
- **代码检查**: pylint, flake8, black
- **类型检查**: mypy
- **测试框架**: pytest
- **文档生成**: Sphinx

### 14.2 代码格式化
使用black进行代码格式化：
```bash
# 安装black
pip install black

# 格式化代码
black operation_replay/
```

---

## 15. 环境配置

### 15.1 Python版本
- 基础版本：Python 3.6+
- 目标环境：Python 3.8+

### 15.2 依赖管理
使用requirements.txt：
```
autoit==1.1.0
```

依赖安装命令：
```bash
pip install -r requirements.txt
```

### 15.3 虚拟环境
项目应使用虚拟环境：
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

---

## 16. 版本控制

### 16.1 Git仓库
- 主分支：main
- 开发分支：dev
- 功能分支：feature/*

### 16.2 代码审查
- 功能合并到dev分支前需代码审查
- 关键模块需至少1人review
- 审查标准：功能实现、代码质量、文档完整性

---

## 17. 发布流程

### 17.1 版本号规范
遵循语义化版本：`MAJOR.MINOR.PATCH`
- `MAJOR`: 不兼容的API修改
- `MINOR`: 向后兼容的功能增加
- `PATCH`: 向后兼容的bug修复

### 17.2 发布步骤
1. 创建git tag: `git tag v1.0.0`
2. 打包发布: `python setup.py sdist bdist_wheel`
3. 上传PyPI: `twine upload dist/*`
4. 更新CHANGELOG

---

## 18. 维护规范

### 18.1 代码维护
- 避免过度优化
- 保持代码简洁
- 及时更新依赖版本

### 18.2 问题修复
- Bug修复后更新版本号
- 记录修复过程
- 添加修复说明

---

## 19. 参考标准

- **Python官方文档**: https://docs.python.org/3/
- **PEP 8**: Python代码风格指南
- **PEP 257**: Python文档字符串约定
- **PEP 484**: 类型提示

---

## 20. 质量检查清单

在提交代码前，请检查：

- [ ] 代码符合PEP 8规范
- [ ] 所有函数都有docstring
- [ ] 异常处理完整
- [ ] 日志记录完整
- [ ] 单元测试通过
- [ ] 代码注释清晰（中文）
- [ ] 文档完整
- [ ] 无TODO或FIXME标记
- [ ] TypeScript支持（如适用）
- [ ] 整体检查是否完整实现需求

---

**规范维护**
- 负责人：开发团队
- 更新周期：每季度
- 反馈渠道：通过issue或pull request反馈
