import struct
from io import BytesIO

# struct的格式请参考：https://docs.python.org/zh-cn/dev/library/struct.html


# divide过程消息协议转换工具
class DivideProtocol(object):

    def _read_all(self,size):
        if isinstance(self.connection,BytesIO):
            buff = self.connection.read(size)
            return buff
        else:
            have = 0
            buff = b''
            while have < size:
                chunk = self.connection.recv(size-have)
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
        print('param_seq---------------111111')
        print(param_seq)
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
        print('param_seq---------------22222')
        print(param_seq)
        # 处理参数值
        param_len = param_len_map[param_seq]
        param_fmt = param_fmt_map[param_seq]
        param_name = param_name_map[param_seq]

        buff = self._read_all(param_len)
        param = struct.unpack(param_fmt, buff)[0]
        args[param_name] = param

        return args

# 解读方法名
class MethodProtocol(object):
    def __init__(self,connection):
        self.connection = connection
    def get_method_name(self):
        # 读取字符串长度
        buff = self._read_all(4)
        length = struct.unpack('!I',buff)[0]
        buff = self._read_all(length)
        return buff.decode()

    def _read_all(self,size):
        if isinstance(self.connection,BytesIO):
            buff = self.connection.read(size)
            return buff
        else:
            have = 0
            buff = b''
            while have < size:
                chunk = self.connection.recv(size-have)
                buff += chunk
                have += len(chunk)

                if len(chunk) == 0:
                    raise EOFError()
            return buff

if __name__ == '__main__':
    # 构造消息体
    proto = DivideProtocol()
    message = proto.args_encode(200,100)

    conn = BytesIO()
    conn.write(message)
    conn.seek(0)
    # 解析消息数据
    method_proto = MethodProtocol(conn)
    name = method_proto.get_method_name()

    args = proto.args_decode(conn)
    print('args------------')
    print(args)

