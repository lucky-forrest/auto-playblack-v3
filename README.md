# auto-playblack-v3 软件代操系统

一个符合B0304标准的Socket客户端与操作回放测试系统，支持双模式运行。

## 项目概述

本项目提供自动化操作执行功能，可以精确地按时间顺序回放操作记录。系统支持通过CSV文件读取操作序列，并在Windows环境下通过autoit库控制鼠标、窗口等自动化操作。

## 功能特性

### 1. CSV回放模式
- ✅ 解析CSV格式的操作记录文件
- ✅ 精确控制操作执行时间（误差±0.1秒）
- ✅ 支持多种操作类型：鼠标移动、点击、键盘按键、窗口控制等
- ✅ 详细的执行结果统计

### 2. Socket实时模式 (待实现)
- 作为Socket客户端连接测试设备
- 接收实时操作指令
- 执行指令并反馈结果
- 支持心跳保活和断线重连

## 安装步骤

### 1. 环境要求

- Python 3.6+
- Windows操作系统
- 已安装的测试软件（根据B0304协议要求）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 基本使用

```bash
# 使用默认CSV文件路径执行回放
python main.py

# 指定自定义CSV文件路径
python main.py --csv-path "path/to/your/operation_log.csv"

# 仅列出操作记录，不执行回放
python main.py --list-operations

# 详细模式执行回放
python main.py --verbose --csv-path "..."
```

### 使用交互式回放

```python
from executor.replay_engine import execute_csv_replay

def progress_callback(current, total, operation):
    print(f"\r进度: [{current}/{total}] {operation.event_type}", end="")

result = execute_csv_replay(callback=progress_callback)
print(f"成功率: {result.get_success_rate():.2f}%")
print(f"总耗时: {result.total_time_elapsed:.3f}秒")
```

## 项目结构

```
socket_client/
├── main.py                  # 主程序入口
├── config/                  # 配置模块
│   ├── __init__.py
│   ├── settings.py          # 系统配置
│   └── constants.py         # 常量定义
├── models/                  # 数据模型
│   ├── __init__.py
│   ├── operation.py        # 操作模型
│   └── replay_result.py     # 回放结果模型
├── parsers/                 # 文件解析
│   ├── __init__.py
│   └── csv_parser.py        # CSV解析器
├── executor/                # 操作执行
│   ├── __init__.py
│   ├── operation_executor.py    # 操作执行器
│   ├── time_controller.py       # 时间控制器
│   └── replay_engine.py         # 回放引擎
└── utils/                   # 工具函数
    ├── __init__.py
    └── exceptions.py       # 自定义异常
```

## 执行模式

### CSV回放模式

1. 准备CSV格式的操作记录文件
2. 使用程序读取并解析文件
3. 按照记录的时间顺序精确回放操作
4. 获取详细的执行结果统计

### 操作类型支持

| 操作类型 | 说明 | 支持状态 |
|---------|------|---------|
| `mouse_move` | 鼠标移动到指定坐标 | ✅ 已实现 |
| `mouse_click` | 鼠标左键点击 | ✅ 已实现 |
| `mouse_scroll` | 鼠标滚轮滚动 | ✅ 已实现 |
| `key_press` | 键盘按键 | ✅ 已实现 |
| `key_release` | 键盘按键释放 | ✅ 已实现 |
| `window_control` | 窗口控制操作 | ✅ 已实现 |

## 配置说明

### Socket配置

```python
# Socket默认配置
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8888
SOCKET_TIMEOUT = 30  # 秒
RECONNECT_DELAY = 5  # 秒
```

### 日志配置

```python
# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "socket_client.log"
```

### CSV回放配置

```python
# CSV回放配置
CSV_DEFAULT_PATH = "path/to/operation_log.csv"
REQUIRED_TIME_PRECISION = 0.1  # 秒
```

## CSV文件格式

CSV文件应包含以下列：

| 列名 | 说明 |
|------|------|
| `timestamp` | 操作时间戳（ISO 8601格式） |
| `event_type` | 操作类型（mouse_move, mouse_click, etc.） |
| `detail` | 操作详细信息 |
| `x` | X坐标（可选） |
| `y` | Y坐标（可选） |
| `window_title` | 窗口标题 |
| `control_text` | 控件文本 |

示例：

```csv
timestamp,event_type,detail,x,y,window_title,control_text
2026-04-02T10:04:11.071105,mouse_move,"Mouse at (725, 689)",725,689,Test Window,
2026-04-02T10:04:14.282875,mouse_click,Mouse left Click,575,288,Test Window,Button1
```

## 错误处理

系统实现了完善的异常处理机制：

- `SocketOperationError`: Socket操作异常基类
- `CSVParseError`: CSV解析错误
- `OperationExecuteError`: 操作执行错误
- `WindowNotFoundError`: 窗口未找到错误
- `TimeCalculationError`: 时间计算错误

所有异常都包含详细的错误信息和上下文数据。

## 日志说明

系统使用Python logging模块记录操作日志：

- 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
- 日志文件：`socket_client.log`
- 日志格式：`时间戳 - 模块名 - 级别 - 消息`

## 性能要求

- **内存占用**：< 100MB
- **启动时间**：< 5秒
- **响应时间**：< 100ms
- **执行精度**：±0.1秒

## 开发注意事项

1. 严格遵循PEP 8代码规范
2. 所有函数必须有docstring
3. 使用类型注解
4. 中文注释和日志
5. 完善的异常处理
6. 详细的日志记录

## 待实现功能

- [ ] Socket实时模式
- [ ] 协议握手和消息序列化
- [ ] 多线程操作回放
- [ ] 自动化测试报告生成
- [ ] Web界面控制面板

## 版本历史

- **v1.0.0** (2026-04-02)
  - ✅ CSV回放模式完全实现
  - ✅ 完整的错误处理机制
  - ✅ 详细的执行结果统计
  - 🔄 Socket实时模式（待开发）

## 贡献指南

欢迎提交问题报告和功能请求！

## 许可证

本项目为内部使用项目。

## 联系方式

如有问题，请联系开发团队。

---

**注意**: 本系统已按照B0304_EQP_Socket标准接口文档进行开发。CSV文件仅作为开发参考，实际生产环境使用Socket实时模式。
