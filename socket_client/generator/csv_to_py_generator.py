# -*- coding: UTF-8 -*-
"""
CSV文件转Python文件的生成器 - 重构版
"""
import csv
import time
import socket
import json
from typing import List, Dict
from pathlib import Path
from datetime import datetime
import pyautogui
import pygetwindow
from pygetwindow import PyGetWindowException


def format_value(value, key):
    """
    格式化操作中的值，将None转换为适当的形式

    Args:
        value: 原始值
        key: 键名

    Returns:
        格式化后的字符串
    """
    if value is None:
        if key in ['x', 'y']:
            return 'None'
        elif key == 'scroll_delta':
            return '0'
        elif key == 'window_title':
            return '""'
        elif key == 'control_text':
            return '""'
        elif key == 'event_type':
            return '""'
        elif key == 'detail':
            return '""'
        elif key == 'timestamp':
            return '0'
        else:
            return ''
    elif isinstance(value, str):
        # 对字符串值进行转义
        escaped = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\r')
        return f'"{escaped}"'
    else:
        return str(value)


def save_operations_to_dict(csv_path: str) -> List[Dict]:
    """
    将CSV文件中的操作记录转换为字典列表

    Args:
        csv_path: CSV文件路径

    Returns:
        List[Dict]: 操作记录的字典列表
    """
    operations = []

    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 解析时间戳
                timestamp_str = row.get('timestamp', None)
                if not timestamp_str:
                    continue

                # 转换时间格式
                try:
                    timestamp = time.mktime(time.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%f'))
                except (ValueError, OSError):
                    timestamp = time.time()

                # 提取事件类型和坐标信息
                event_type = row.get('event_type', '').strip().lower()

                # 从CSV列中提取x和y坐标（优先使用列值）
                x_str = row.get('x', '')
                y_str = row.get('y', '')
                try:
                    x = int(float(x_str)) if x_str and float(x_str) >= 0 else None
                    y = int(float(y_str)) if y_str and float(y_str) >= 0 else None
                except (ValueError, TypeError):
                    x = None
                    y = None

                # 从detail字段获取详细的操作信息
                detail = row.get('detail', '')
                detail_text = detail

                # 获取窗口标题和控件文本
                window_title = row.get('window_title', '')
                control_text = row.get('control_text', '')

                # 解析滚动偏移量
                scroll_delta = int(row.get('scroll_delta', '')) if row.get('scroll_delta') else 0

                # 创建操作字典
                operation = {
                    'timestamp': timestamp,
                    'event_type': event_type,
                    'detail': detail_text,
                    'x': x,
                    'y': y,
                    'window_title': window_title,
                    'control_text': control_text,
                    'scroll_delta': scroll_delta
                }

                operations.append(operation)

        return operations

    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return []


def generate_replay_script(operations: List[Dict], script_name: str) -> str:
    """
    生成回放脚本的Python代码 - 重构版

    Args:
        operations: 操作记录字典列表
        script_name: 脚本名称

    Returns:
        str: Python代码字符串
    """
    # 生成Python代码
    py_lines = []

    # 添加文件头
    py_lines.append('# -*- coding: UTF-8 -*-')
    py_lines.append('"""')
    py_lines.append(f'操作回放脚本 - {script_name}')
    py_lines.append('由CSV文件自动生成')
    py_lines.append('"""')
    py_lines.append('')
    # 导入库（按顺序：Python标准库 -> 第三方库 -> 本地模块）
    py_lines.append('import time')
    py_lines.append('import socket')
    py_lines.append('import json')
    py_lines.append('from datetime import datetime')
    py_lines.append('import pyautogui')
    py_lines.append('import pygetwindow')
    py_lines.append('from pygetwindow import PyGetWindowException')
    py_lines.append('')
    py_lines.append('from typing import List, Dict')
    py_lines.append('')

    # 构建操作数据列表的字面量
    ops_list = []
    for i, op in enumerate(operations):
        if i > 0:
            ops_list.append(',\n')

        op_dict = []
        keys = ['timestamp', 'event_type', 'detail', 'x', 'y', 'window_title', 'control_text', 'scroll_delta']
        for key in keys:
            value = format_value(op.get(key), key)
            op_dict.append(f'"{key}": {value}')
        ops_list.append(f'{{{", ".join(op_dict)}}}')

    ops_literal = ''.join(ops_list)

    # 添加OPERATIONS_DATA变量
    py_lines.append('# 操作数据列表')
    py_lines.append(f'OPERATIONS_DATA = [{ops_literal}]')
    py_lines.append('')

    # ========== 第一部分：Socket客户端类 ==========
    py_lines.append('# === Socket客户端类 ===')
    py_lines.append('class SocketClient:')
    py_lines.append('    """Socket客户端类，用于与服务器通信"""')
    py_lines.append('')
    py_lines.append('    ENCODING = \'utf-8\'')
    py_lines.append('    MAX_BUFFER_SIZE = 65536')
    py_lines.append('')
    py_lines.append('    def __init__(self, host=\'127.0.0.1\', port=8888):')
    py_lines.append('        """')
    py_lines.append('        初始化Socket客户端')
    py_lines.append('')
    py_lines.append('        Args:')
    py_lines.append('            host: 服务器地址，默认127.0.0.1')
    py_lines.append('            port: 服务器端口，默认8888')
    py_lines.append('        """')
    py_lines.append('        self.host = host')
    py_lines.append('        self.port = port')
    py_lines.append('        self.client_socket = None')
    py_lines.append('        self.connected = False')
    py_lines.append('')
    py_lines.append('        # 自动生成当前时间戳')
    py_lines.append('        self.get_timestamp = lambda: datetime.now().strftime("%Y%m%d%H%M%S.%f")[:-3]')
    py_lines.append('')
    py_lines.append('    def connect(self, timeout=10):')
    py_lines.append('        """')
    py_lines.append('        连接到服务器')
    py_lines.append('')
    py_lines.append('        Args:')
    py_lines.append('            timeout: 连接超时时间（秒）')
    py_lines.append('')
    py_lines.append('        Returns:')
    py_lines.append('            bool: 是否连接成功')
    py_lines.append('        """')
    py_lines.append('        try:')
    py_lines.append('            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)')
    py_lines.append('            self.client_socket.settimeout(timeout)')
    py_lines.append('            self.client_socket.connect((self.host, self.port))')
    py_lines.append('')
    py_lines.append('            self.connected = True')
    py_lines.append('            print(f"[INFO] 成功连接到服务器: {self.host}:{self.port}")')
    py_lines.append('            return True')
    py_lines.append('')
    py_lines.append('        except Exception as e:')
    py_lines.append('            print(f"[ERROR] 连接服务器失败: {str(e)}")')
    py_lines.append('            self.connected = False')
    py_lines.append('            return False')
    py_lines.append('')
    py_lines.append('    def disconnect(self):')
    py_lines.append('        """断开与服务器的连接"""')
    py_lines.append('        if self.client_socket:')
    py_lines.append('            try:')
    py_lines.append('                self.client_socket.close()')
    py_lines.append('                print("[INFO] 已断开与服务器的连接")')
    py_lines.append('            except Exception as e:')
    py_lines.append('                print(f"[ERROR] 断开连接时出错: {str(e)}")')
    py_lines.append('            finally:')
    py_lines.append('                self.client_socket = None')
    py_lines.append('                self.connected = False')
    py_lines.append('')
    py_lines.append('    def _create_message(self, message_name, body=None, machine_name="ReplayClient"):')
    py_lines.append('        """')
    py_lines.append('        创建标准格式的消息')
    py_lines.append('')
    py_lines.append('        Args:')
    py_lines.append('            message_name: 消息名称')
    py_lines.append('            body: 消息体')
    py_lines.append('            machine_name: 机器名称')
    py_lines.append('')
    py_lines.append('        Returns:')
    py_lines.append('            dict: 标准格式的消息对象')
    py_lines.append('        """')
    py_lines.append('        message = {')
    py_lines.append('            "Request": {')
    py_lines.append('                "Header": {')
    py_lines.append('                    "MachineName": machine_name,')
    py_lines.append('                    "TransactionID": str(int(datetime.now().timestamp() * 1000)),')
    py_lines.append('                    "MessageName": message_name,')
    py_lines.append('                    "UserName": "replay",')
    py_lines.append('                    "EventTime": self.get_timestamp()')
    py_lines.append('                },')
    py_lines.append('                "Body": body or {}')
    py_lines.append('            }')
    py_lines.append('        }')
    py_lines.append('        return message')
    py_lines.append('')
    py_lines.append('    def _format_for_send(self, message):')
    py_lines.append('        """')
    py_lines.append('        格式化消息用于发送：纯 JSON，以换行符结束')
    py_lines.append('')
    py_lines.append('        Args:')
    py_lines.append('            message: 要发送的消息对象')
    py_lines.append('')
    py_lines.append('        Returns:')
    py_lines.append('            bytes: 格式化后的字节流')
    py_lines.append('        """')
    py_lines.append('        message_str = json.dumps(message, ensure_ascii=False)')
    py_lines.append('        # 添加换行符表示结束（Unix风格）')
    py_lines.append('        message_str += \'\\n\'')
    py_lines.append('        # 确保所有换行符都是 \'\\n\' 而不是 \'\\r\\n\'')
    py_lines.append('        message_bytes = message_str.encode(self.ENCODING)')
    py_lines.append('        # 替换所有 \\r\\n 为 \\n')
    py_lines.append('        message_bytes = message_bytes.replace(b\'\\r\\n\', b\'\\n\')')
    py_lines.append('        return message_bytes')
    py_lines.append('')
    py_lines.append('    def _parse_received_data(self, full_data):')
    py_lines.append('        """')
    py_lines.append('        解析接收到的数据（纯 JSON，以换行符结束）')
    py_lines.append('')
    py_lines.append('        Args:')
    py_lines.append('            full_data: 接收到的所有数据')
    py_lines.append('        Returns:')
    py_lines.append('            tuple: (message_dict, remaining_data) or (None, full_data) if incomplete')
    py_lines.append('        """')
    py_lines.append('        if b\'\\n\' not in full_data:')
    py_lines.append('            # 未收到换行符，数据不完整')
    py_lines.append('            return None, full_data')
    py_lines.append('')
    py_lines.append('        # 拆分出完整的消息（前面是 JSON，后面是换行符和数据）')
    py_lines.append('        message_str = full_data.split(b\'\\n\', 1)[0]')
    py_lines.append('        remaining_data = full_data[full_data.index(b\'\\n\') + 1:]')
    py_lines.append('')
    py_lines.append('        # 解析消息')
    py_lines.append('        return json.loads(message_str.decode(self.ENCODING)), remaining_data')
    py_lines.append('')
    py_lines.append('    def _send_and_receive(self, message):')
    py_lines.append('        """')
    py_lines.append('        发送消息并接收响应')
    py_lines.append('')
    py_lines.append('        Args:')
    py_lines.append('            message: 要发送的消息对象')
    py_lines.append('        Returns:')
    py_lines.append('            dict: 解析后的响应,失败返回 None')
    py_lines.append('        """')
    py_lines.append('        try:')
    py_lines.append('            if not self.connected:')
    py_lines.append('                print("[ERROR] 未连接到服务器")')
    py_lines.append('                return None')
    py_lines.append('')
    py_lines.append('            # 格式化消息（添加长度前缀）')
    py_lines.append('            formatted_data = self._format_for_send(message)')
    py_lines.append('')
    py_lines.append('            # 获取消息类型')
    py_lines.append('            header = message.get(\'Request\', {}).get(\'Header\', {})')
    py_lines.append('            message_name = header.get(\'MessageName\', \'unknown\')')
    py_lines.append('            print(f"\\n[SEND] 消息名称: {message_name}")')
    py_lines.append('            print(f"[SEND] 请求数据长度: {len(formatted_data)} 字节")')
    py_lines.append('')
    py_lines.append('            # 发送消息')
    py_lines.append('            self.client_socket.sendall(formatted_data)')
    py_lines.append('            print(f"[SEND] 已发送 {len(formatted_data)} 字节")')
    py_lines.append('')
    py_lines.append('            # 接收响应（可能需要多次接收以获取完整数据）')
    py_lines.append('            full_response = b\'\'')
    py_lines.append('            elapsed_time = 0')
    py_lines.append('            start_time = time.time()')
    py_lines.append('')
    py_lines.append('            while elapsed_time < 10:  # 最多等待10秒')
    py_lines.append('                try:')
    py_lines.append('                    chunk = self.client_socket.recv(self.MAX_BUFFER_SIZE)')
    py_lines.append('                    if not chunk:')
    py_lines.append('                        print("[ERROR] 连接已关闭")')
    py_lines.append('                        return None')
    py_lines.append('')
    py_lines.append('                    full_response += chunk')
    py_lines.append('')
    py_lines.append('                    # 尝试解析数据')
    py_lines.append('                    parsed_message, remaining = self._parse_received_data(full_response)')
    py_lines.append('')
    py_lines.append('                    if parsed_message is not None:')
    py_lines.append('                        # 收到完整消息')
    py_lines.append('                        if parsed_message.get(\'Response\'):')
    py_lines.append('                            response_return = parsed_message.get(\'Response\', {}).get(\'Return\', {})')
    py_lines.append('                            if response_return:')
    py_lines.append('                                return_msg = response_return.get(\'ReturnMessage\', \'unknown\')')
    py_lines.append('                            else:')
    py_lines.append('                                return_msg = \'unknown\'')
    py_lines.append('')
    py_lines.append('                            print(f"[RECV] 响应: {return_msg}")')
    py_lines.append('                            return parsed_message')
    py_lines.append('')
    py_lines.append('                        # 没有嵌套 Response，以整个消息作为响应')
    py_lines.append('                        print(f"[RECV] 响应: 收到消息")')
    py_lines.append('                        return parsed_message')
    py_lines.append('')
    py_lines.append('                    # 数据不完整，更新超时')
    py_lines.append('                    full_response = remaining')
    py_lines.append('                    elapsed_time = time.time() - start_time')
    py_lines.append('                    print(f"[DEBUG] 等待更多数据... 已接收 {len(full_response)} 字节")')
    py_lines.append('                    time.sleep(0.1)')
    py_lines.append('')
    py_lines.append('                except socket.timeout:')
    py_lines.append('                    elapsed_time = time.time() - start_time')
    py_lines.append('                    print(f"[DEBUG] 接收超时... 已接收 {len(full_response)} 字节")')
    py_lines.append('                    time.sleep(0.1)')
    py_lines.append('')
    py_lines.append('            print(f"[ERROR] 接收超时或连接关闭，总接收 {len(full_response)} 字节")')
    py_lines.append('            return None')
    py_lines.append('')
    py_lines.append('        except json.JSONDecodeError as e:')
    py_lines.append('            print(f"[ERROR] JSON 解析失败: {str(e)}")')
    py_lines.append('            print(f"[ERROR] 原始数据: {full_response[:200] if full_response else \'None\'}")')
    py_lines.append('            return None')
    py_lines.append('        except Exception as e:')
    py_lines.append('            print(f"[ERROR] 发送/接收消息时出错: {str(e)}")')
    py_lines.append('            import traceback')
    py_lines.append('            traceback.print_exc()')
    py_lines.append('            return None')
    py_lines.append('')
    py_lines.append('    def send_completion_message(self, success_count, total_count):')
    py_lines.append('        """')
    py_lines.append('        回放完成后发送完成消息给服务器')
    py_lines.append('')
    py_lines.append('        Args:')
    py_lines.append('            success_count: 成功执行的操作数量')
    py_lines.append('            total_count: 总操作数量')
    py_lines.append('')
    py_lines.append('        Returns:')
    py_lines.append('            bool: 发送是否成功')
    py_lines.append('        """')
    py_lines.append('        if not self.connected:')
    py_lines.append('            print("[WARN] 未连接到服务器，无法发送完成消息")')
    py_lines.append('            return False')
    py_lines.append('')
    py_lines.append('        try:')
    py_lines.append('            body = {')
    py_lines.append('                "success_count": success_count,')
    py_lines.append('                "total_count": total_count,')
    py_lines.append('                "completion_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")')
    py_lines.append('            }')
    py_lines.append('')
    py_lines.append('            message = self._create_message("reset_data", body=body)')
    py_lines.append('            formatted_data = self._format_for_send(message)')
    py_lines.append('')
    py_lines.append('            header = message.get(\'Request\', {}).get(\'Header\', {})')
    py_lines.append('            message_name = header.get(\'MessageName\', \'unknown\')')
    py_lines.append('            print(f"\\n[SEND] 发送完成消息: {message_name}")')
    py_lines.append('            print(f"[SEND] 成功: {success_count}, 总数: {total_count}")')
    py_lines.append('')
    py_lines.append('            self.client_socket.sendall(formatted_data)')
    py_lines.append('            print("[INFO] 完成消息已发送")')
    py_lines.append('            return True')
    py_lines.append('')
    py_lines.append('        except Exception as e:')
    py_lines.append('            print(f"[ERROR] 发送完成消息失败: {str(e)}")')
    py_lines.append('            return False')
    py_lines.append('')
    py_lines.append('    def _execute_operations_with_socket(self, operations: List[Dict]) -> int:')
    py_lines.append('        """')
    py_lines.append('        带Socket连接执行所有操作，完成后自动通知服务器')
    py_lines.append('')
    py_lines.append('        Args:')
    py_lines.append('            operations: 操作记录字典列表')
    py_lines.append('')
    py_lines.append('        Returns:')
    py_lines.append('            int: 成功执行的操作数量')
    py_lines.append('        """')
    py_lines.append('        # 连接到服务器')
    py_lines.append('        if not self.connect():')
    py_lines.append('            # 连接失败，继续执行回放但不发送完成消息')
    py_lines.append('            return self._execute_operations_without_socket(operations)')
    py_lines.append('')
    py_lines.append('        try:')
    py_lines.append('            success_count = self._execute_operations_without_socket(operations)')
    py_lines.append('')
    py_lines.append('            # 向服务器发送操作完成消息并等待响应')
    py_lines.append('            completion_body = {')
    py_lines.append('                "success_count": success_count,')
    py_lines.append('                "total_count": len(operations),')
    py_lines.append('                "completion_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")')
    py_lines.append('            }')
    py_lines.append('            completion_message = self._create_message("reset_data", body=completion_body)')
    py_lines.append('            response = self._send_and_receive(completion_message)')
    py_lines.append('')
    py_lines.append('            if response is not None:')
    py_lines.append('                print("[INFO] 操作完成消息发送成功，收到服务器响应")')
    py_lines.append('            else:')
    py_lines.append('                print("[WARN] 操作完成消息发送失败或未收到响应")')
    py_lines.append('')
    py_lines.append('            return success_count')
    py_lines.append('')
    py_lines.append('        except Exception as e:')
    py_lines.append('            print(f"[ERROR] 执行过程中出错: {str(e)}")')
    py_lines.append('            import traceback')
    py_lines.append('            traceback.print_exc()')
    py_lines.append('            return -1')
    py_lines.append('        finally:')
    py_lines.append('            self.disconnect()')
    py_lines.append('')
    py_lines.append('    def _execute_operations_without_socket(self, operations: List[Dict]) -> int:')
    py_lines.append('        """')
    py_lines.append('        执行所有操作（不使用Socket连接）')
    py_lines.append('')
    py_lines.append('        Args:')
    py_lines.append('            operations: 操作记录字典列表')
    py_lines.append('')
    py_lines.append('        Returns:')
    py_lines.append('            int: 成功执行的操作数量')
    py_lines.append('        """')
    py_lines.append('        print("=" * 60)')
    py_lines.append('        print(f"开始执行回放，共 {len(operations)} 条操作")')
    py_lines.append('        print("=" * 60)')
    py_lines.append('        print("")')
    py_lines.append('')
    py_lines.append('        success_count = 0')
    py_lines.append('        last_event_type = None')
    py_lines.append('')
    py_lines.append('        for i in range(len(operations)):')
    py_lines.append('            op_data = operations[i]')
    py_lines.append('')
    py_lines.append('            event_type = op_data.get("event_type", "")')
    py_lines.append('            print(f"[{i+1}/{len(operations)}] 操作类型: {event_type}")')
    py_lines.append('')
    py_lines.append('            if event_type == "mouse_move":')
    py_lines.append('                if _execute_mouse_move(op_data):')
    py_lines.append('                    success_count += 1')
    py_lines.append('            elif event_type == "mouse_click":')
    py_lines.append('                if _execute_mouse_click(op_data):')
    py_lines.append('                    success_count += 1')
    py_lines.append('            elif event_type == "mouse_scroll":')
    py_lines.append('                if _execute_mouse_scroll(op_data):')
    py_lines.append('                    success_count += 1')
    py_lines.append('            elif event_type == "key_press":')
    py_lines.append('                if _execute_key_press(op_data):')
    py_lines.append('                    success_count += 1')
    py_lines.append('            else:')
    py_lines.append('                print(f"跳过不支持的或未实现的操作类型: {event_type}")')
    py_lines.append('')
    py_lines.append('            if i < len(operations) - 1 and event_type != last_event_type:')
    py_lines.append('                time.sleep(0.5)')
    py_lines.append('                last_event_type = event_type')
    py_lines.append('            else:')
    py_lines.append('                time.sleep(0.2)')
    py_lines.append('')
    py_lines.append('        print("")')
    py_lines.append('        print("=" * 60)')
    py_lines.append('        print("回放完成！")')
    py_lines.append('        print(f"成功: {success_count} 个操作")')
    py_lines.append('        print("=" * 60)')
    py_lines.append('        return success_count')
    py_lines.append('')
    py_lines.append('')

    # ========== 第二部分：模块级辅助函数 ==========
    py_lines.append('# === 模块级辅助函数 ===')
    py_lines.append('def activate_window(window_title: str) -> bool:')
    py_lines.append('    """')
    py_lines.append('    激活指定窗口')
    py_lines.append('    ')
    py_lines.append('    Args:')
    py_lines.append('        window_title: 窗口标题')
    py_lines.append('    ')
    py_lines.append('    Returns:')
    py_lines.append('        bool: 操作是否成功')
    py_lines.append('    """')
    py_lines.append('    try:')
    py_lines.append('        windows = pygetwindow.getWindowsWithTitle(window_title)')
    py_lines.append('        if not windows:')
    py_lines.append('            print(f"错误：找不到窗口 [{window_title}]")')
    py_lines.append('            return False')
    py_lines.append('        ')
    py_lines.append('        window = windows[0]')
    py_lines.append('        window.activate()')
    py_lines.append('        time.sleep(0.3)')
    py_lines.append('        print(f"窗口 [{window_title}] 已激活")')
    py_lines.append('        return True')
    py_lines.append('    except PyGetWindowException as e:')
    py_lines.append('        print(f"激活窗口失败 [{window_title}]: {e}")')
    py_lines.append('        return False')
    py_lines.append('    except Exception as e:')
    py_lines.append('        print(f"激活窗口出错 [{window_title}]: {e}")')
    py_lines.append('        return False')
    py_lines.append('')

    py_lines.append('def _execute_mouse_move(operation: Dict) -> bool:')
    py_lines.append('    """')
    py_lines.append('    执行鼠标移动操作')
    py_lines.append('    ')
    py_lines.append('    Args:')
    py_lines.append('        operation: 操作字典')
    py_lines.append('    ')
    py_lines.append('    Returns:')
    py_lines.append('        bool: 是否成功')
    py_lines.append('    """')
    py_lines.append('    x = operation.get("x")')
    py_lines.append('    y = operation.get("y")')
    py_lines.append('    if x is None or y is None:')
    py_lines.append('        print(f"跳过: 缺少坐标信息")')
    py_lines.append('        return False')
    py_lines.append('    pyautogui.moveTo(x, y)')
    py_lines.append('    print(f"移动鼠标到 ({x}, {y})")')
    py_lines.append('    return True')
    py_lines.append('')

    py_lines.append('def _execute_mouse_click(operation: Dict) -> bool:')
    py_lines.append('    """')
    py_lines.append('    执行鼠标点击操作（左键）')
    py_lines.append('    ')
    py_lines.append('    Args:')
    py_lines.append('        operation: 操作字典')
    py_lines.append('    ')
    py_lines.append('    Returns:')
    py_lines.append('        bool: 是否成功')
    py_lines.append('    """')
    py_lines.append('    x = operation.get("x")')
    py_lines.append('    y = operation.get("y")')
    py_lines.append('    if x is None or y is None:')
    py_lines.append('        print(f"跳过: 缺少坐标信息")')
    py_lines.append('        return False')
    py_lines.append('    pyautogui.click(x=x, y=y, button="left")')
    py_lines.append('    print(f"点击坐标 ({x}, {y})")')
    py_lines.append('    return True')
    py_lines.append('')

    py_lines.append('def _execute_mouse_scroll(operation: Dict) -> bool:')
    py_lines.append('    """')
    py_lines.append('    执行鼠标滚动操作')
    py_lines.append('    ')
    py_lines.append('    Args:')
    py_lines.append('        operation: 操作字典')
    py_lines.append('    ')
    py_lines.append('    Returns:')
    py_lines.append('        bool: 是否成功')
    py_lines.append('    """')
    py_lines.append('    window_title = operation.get("window_title", "")')
    py_lines.append('    x = operation.get("x")')
    py_lines.append('    y = operation.get("y")')
    py_lines.append('    scroll_delta = int(operation.get("scroll_delta", 0))')
    py_lines.append('')
    py_lines.append('    # 激活窗口（如果需要）')
    py_lines.append('    if window_title:')
    py_lines.append('        if not activate_window(window_title):')
    py_lines.append('            print("警告: 无法激活窗口")')
    py_lines.append('            return False')
    py_lines.append('')
    py_lines.append('    # 移动鼠标（如果需要）')
    py_lines.append('    if x is not None and y is not None:')
    py_lines.append('        pyautogui.moveTo(x, y)')
    py_lines.append('        time.sleep(0.2)')
    py_lines.append('')
    py_lines.append('    # 执行滚动')
    py_lines.append('    pyautogui.scroll(scroll_delta*300)')
    py_lines.append('    print(f"滚动操作")')
    py_lines.append('    return True')
    py_lines.append('')

    py_lines.append('def _execute_key_press(operation: Dict) -> bool:')
    py_lines.append('    """')
    py_lines.append('    执行键盘按键操作')
    py_lines.append('    ')
    py_lines.append('    Args:')
    py_lines.append('        operation: 操作字典')
    py_lines.append('    ')
    py_lines.append('    Returns:')
    py_lines.append('        bool: 是否成功')
    py_lines.append('    """')
    py_lines.append('    window_title = operation.get("window_title", "")')
    py_lines.append('    detail = operation.get("detail", "")')
    py_lines.append('    key = detail.replace("Key: ", "").strip() if detail and "Key: " in detail else ""')
    py_lines.append('    print("按键: " + str(key if key else "(空)"))')
    py_lines.append('')
    py_lines.append('    # 激活窗口（如果需要）')
    py_lines.append('    if window_title:')
    py_lines.append('        if not activate_window(window_title):')
    py_lines.append('            print("警告: 无法激活窗口，可能按键发送失败")')
    py_lines.append('            return False')
    py_lines.append('')
    py_lines.append('    # 普通按键输入')
    py_lines.append('    if key:')
    py_lines.append('        try:')
    py_lines.append('            for char in detail.replace("Key: ", "").strip():')
    py_lines.append('                pyautogui.press(char)')
    py_lines.append('                time.sleep(0.05)  # 按键之间稍微延迟')
    py_lines.append('        except Exception as e:')
    py_lines.append('            print("按键发送错误: %s" % e)')
    py_lines.append('            return False')
    py_lines.append('    return True')
    py_lines.append('')

    # ========== 第二部分：主执行函数 ==========
    py_lines.append('def execute_operations(operations: List[Dict]) -> int:')
    py_lines.append('    """')
    py_lines.append('    执行操作回放（建议使用 SocketClient）')
    py_lines.append('')
    py_lines.append('    Args:')
    py_lines.append('        operations: 操作记录字典列表')
    py_lines.append('')
    py_lines.append('    Returns:')
    py_lines.append('        int: 成功执行的操作数量')
    py_lines.append('    """')
    py_lines.append('    print("[WARN] 建议使用 SocketClient 来执行操作并通知服务器")')
    py_lines.append('    print("[WARN] 使用 SocketClient 会自动连接服务器并在回放完成后发送消息")')
    py_lines.append('')
    py_lines.append('    success_count = 0')
    py_lines.append('    last_event_type = None  # 记录上一次执行的事件类型')
    py_lines.append('')
    py_lines.append('    # 遍历所有操作')
    py_lines.append('    for i in range(len(operations)):')
    py_lines.append('        op_data = operations[i]')
    py_lines.append('')
    py_lines.append('        # 获取操作详情')
    py_lines.append('        event_type = op_data.get("event_type", "")')
    py_lines.append('        print(f"[{i+1}/{len(operations)}] 操作类型: {event_type}")')
    py_lines.append('')
    py_lines.append('        # 根据不同的事件类型调用对应的处理函数')
    py_lines.append('        if event_type == "mouse_move":')
    py_lines.append('            if _execute_mouse_move(op_data):')
    py_lines.append('                success_count += 1')
    py_lines.append('        elif event_type == "mouse_click":')
    py_lines.append('            if _execute_mouse_click(op_data):')
    py_lines.append('                success_count += 1')
    py_lines.append('        elif event_type == "mouse_scroll":')
    py_lines.append('            if _execute_mouse_scroll(op_data):')
    py_lines.append('                success_count += 1')
    py_lines.append('        elif event_type == "key_press":')
    py_lines.append('            if _execute_key_press(op_data):')
    py_lines.append('                success_count += 1')
    py_lines.append('        else:')
    py_lines.append('            print(f"跳过不支持的或未实现的操作类型: {event_type}")')
    py_lines.append('')
    py_lines.append('        # 如果不是最后一个操作，且当前事件类型与上一次不同， sleep 0.5秒')
    py_lines.append('        if i < len(operations) - 1 and event_type != last_event_type:')
    py_lines.append('            time.sleep(0.5)')
    py_lines.append('            last_event_type = event_type')
    py_lines.append('        else:')
    py_lines.append('            time.sleep(0.2)')
    py_lines.append('')
    py_lines.append('    print("")')
    py_lines.append('    print("=" * 60)')
    py_lines.append('    print("回放完成！")')
    py_lines.append('    print(f"成功: {success_count} 个操作")')
    py_lines.append('    print("=" * 60)')
    py_lines.append('    return success_count')
    py_lines.append('')

    # ========== 第三部分：主入口函数 ==========
    py_lines.append('def main():')
    py_lines.append('    """')
    py_lines.append('    主函数，执行操作回放并连接服务器')
    py_lines.append('    """')
    py_lines.append('    print("")')
    py_lines.append('    print("Python 自动化回放脚本启动")')
    py_lines.append('    print("")')
    py_lines.append('')
    py_lines.append('    # 创建Socket客户端')
    py_lines.append('    socket_client = SocketClient()')
    py_lines.append('')
    py_lines.append('    # 使用带Socket连接的方式执行操作')
    py_lines.append('    try:')
    py_lines.append('        success_count = socket_client._execute_operations_with_socket(OPERATIONS_DATA)')
    py_lines.append('')
    py_lines.append('        # 退出码: 成功执行所有操作返回0, 但要考虑是否使用了Socket并发送了完成消息')
    py_lines.append('        if success_count >= 0:')
    py_lines.append('            # 只要能执行回放就算成功，不管是否连接了服务器')
    py_lines.append('            return 0')
    py_lines.append('        else:')
    py_lines.append('            return 1')
    py_lines.append('')
    py_lines.append('    except Exception as e:')
    py_lines.append('        print(f"[ERROR] 主函数执行失败: {e}")')
    py_lines.append('        import traceback')
    py_lines.append('        traceback.print_exc()')
    py_lines.append('        return 1')
    py_lines.append('')
    py_lines.append('if __name__ == "__main__":')
    py_lines.append('    exit_code = main()')
    py_lines.append('    exit(exit_code)')

    # 返回合并后的代码
    return '\n'.join(py_lines)


def generate_py_file(csv_path: str, output_dir: str = None) -> str:
    """
    将CSV文件转换为Python回放脚本并保存

    Args:
        csv_path: CSV文件路径
        output_dir: 输出目录，默认为用户文档目录

    Returns:
        str: 生成的Python文件路径

    Raises:
        FileNotFoundError: CSV文件不存在时抛出
        IOError: 文件保存失败时抛出
    """
    csv_file = Path(csv_path)

    if not csv_file.exists():
        raise FileNotFoundError(f"CSV文件不存在: {csv_path}")

    # 如果没有指定输出目录，则存储在用户 Documents 目录下，使用与CSV文件同名的py文件
    if output_dir is None:
        # 获取用户文档目录
        documents_dir = Path.home() / 'Documents'

        # 创建输出目录（使用CSV文件所在目录）
        output_dir = csv_file.parent

    # 生成的py文件名（与CSV同名，扩展名改为.py）
    py_filename = csv_file.stem + '.py'
    py_file_path = output_dir / py_filename

    # 转换操作数据为字典列表
    operations = save_operations_to_dict(str(csv_file))

    # 生成Python代码内容
    py_content = generate_replay_script(operations, py_filename)

    # 保存Python文件
    with open(py_file_path, 'w', encoding='utf-8') as f:
        f.write(py_content)

    return str(py_file_path)


if __name__ == '__main__':
    import sys
    # 测试代码
    test_csv = 'documents/test_operation_log.csv'
    if len(sys.argv) > 1:
        test_csv = sys.argv[1]

    try:
        py_file = generate_py_file(test_csv)
        print(f"✓ Python回放脚本已生成: {py_file}")
    except Exception as e:
        print(f"✗ 生成失败: {e}")
        sys.exit(1)