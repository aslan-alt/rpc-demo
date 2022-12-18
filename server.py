import struct
from io import BytesIO
import socket


# struct的格式请参考：https://docs.python.org/zh-cn/dev/library/struct.html
class InvalidOperation(Exception):
    def __int__(self, message=None):
        self.message = message or 'Invalid operation'


# divide过程消息协议转换工具
class DivideProtocol(object):

    def _read_all(self, size):
        if isinstance(self.connection, BytesIO):
            buff = self.connection.read(size)
            return buff
        else:
            have = 0
            buff = b''
            while have < size:
                chunk = self.connection.recv(size - have)
                buff += chunk
                have += len(chunk)

                if len(chunk) == 0:
                    raise EOFError()
            return buff

    def args_encode(self, num1, num2=1):
        """将原始请求的参数转换成二进制数据"""
        name = 'divide'
        # 处理方法的名字
        # 用于标记divide方法长度为6
        buff = struct.pack('!I', 6)
        # 拼接bytes类型
        buff += name.encode()

        # 处理第一个参数
        # 处理序号
        buff2 = struct.pack('!B', 1)
        # 处理参数值
        buff2 += struct.pack('!i', num1)

        # 处理参数2
        if num2 != 1:
            # 处理序号
            buff2 += struct.pack('!B', 2)
            # 处理参数值
            buff2 += struct.pack('!i', num2)
        # 处理消息长度，边界设定

        buff += struct.pack('!I', len(buff2))
        # 最终消息体
        # 方法长度 ｜ 消息名 ｜ 参数1的序号 ｜ 参数1 ｜ 参数2的序号 ｜ 参数2
        buff += buff2
        return buff

    def args_decode(self, connection):
        args = {}
        param_len_map = {
            1: 4,
            2: 4
        }
        param_fmt_map = {
            1: '!i',
            2: '!i'
        }
        param_name_map = {
            1: 'num1',
            2: 'num2'
        }
        # 已处理字节数
        have = 0
        # 接受消息体，并且解析
        self.connection = connection

        # 读取二进制数据，长度为4个字节整数
        buff = self._read_all(4)
        # 获取消息总长度
        length = struct.unpack('!I', buff)[0]

        # 处理第一个参数,序号为一个字节证书
        buff = self._read_all(1)
        have += 1
        param_seq = struct.unpack('!B', buff)[0]

        # 处理参数值
        param_len = param_len_map[param_seq]
        param_fmt = param_fmt_map[param_seq]
        param_name = param_name_map[param_seq]
        have += param_len
        buff = self._read_all(param_len)
        param = struct.unpack(param_fmt, buff)[0]
        args[param_name] = param

        if have >= length:
            return args
        # 处理第二个参数
        buff = self._read_all(1)
        have += 1
        param_seq = struct.unpack('!B', buff)[0]
        # 处理参数值
        param_len = param_len_map[param_seq]
        param_fmt = param_fmt_map[param_seq]
        param_name = param_name_map[param_seq]

        buff = self._read_all(param_len)
        param = struct.unpack(param_fmt, buff)[0]
        args[param_name] = param

        return args

    def result_encode(self, result):
        # 正常
        if isinstance(result, float):
            # 1个字节的序号 ｜ 4个字节的float结果
            buff = struct.pack('!B', 1)
            buff += struct.pack('!f', result)
            return buff
        # 异常
        else:
            buff = struct.pack('!B', 2)
            buff += struct.pack('!I', len(result.message))
            buff += result.message.encode()
            return buff

    def result_decode(self, connection):
        self.connection = connection
        buff = self._read_all(1)
        result_type = struct.unpack('!B', buff)[0]

        if result_type == 1:
            buff = self._read_all(4)
            return struct.unpack('!f', buff)[0]
        else:
            # 异常
            buff = self._read_all(4)
            length = struct.unpack('!I', buff)[0]
            buff = self._read_all(length)
            message = buff.decode()
            return InvalidOperation(message)


# 解读方法名
class MethodProtocol(object):
    def __init__(self, connection):
        self.connection = connection

    def get_method_name(self):
        # 读取字符串长度
        buff = self._read_all(4)
        length = struct.unpack('!I', buff)[0]
        buff = self._read_all(length)
        return buff.decode()

    def _read_all(self, size):
        if isinstance(self.connection, BytesIO):
            buff = self.connection.read(size)
            return buff
        else:
            have = 0
            buff = b''
            while have < size:
                chunk = self.connection.recv(size - have)
                buff += chunk
                have += len(chunk)

                if len(chunk) == 0:
                    raise EOFError()
            return buff


# 客户端建立网络连接
class Channel(object):
    def __init__(self, host, post):
        self.host = host
        self.post = post

    def get_connection(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.post))
        return sock


class RPCServer(object):
    def __init__(self, host, post):
        self.host = host
        self.post = post
        # 创建socket 的工具对象
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 设置socket 重用地址
        sock.setsockopt(socket.SOL_SOCKET, socket.SOCK_STREAM, 1)
        # 绑定地址
        sock.bind((self.host, self.post))
        self.sock = sock




if __name__ == '__main__':
    # 构造消息体
    proto = DivideProtocol()
    message = proto.args_encode(200, 100)

    conn = BytesIO()
    conn.write(message)
    conn.seek(0)
    # 解析消息数据
    method_proto = MethodProtocol(conn)
    name = method_proto.get_method_name()

    args = proto.args_decode(conn)
    print('args------------')
    print(args)
