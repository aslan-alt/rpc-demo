import struct


class InvalidOperation(Exception):
    def __int__(self,message=None):
        self.message = message or 'Invalid operation'


def divide(num1, num2):
    if num2 == 0:
        raise InvalidOperation()
    return num1 / num2


try:
    val = divide(200, 100)
except InvalidOperation as e:
    print(e.message)
else:
    print(val)

# python 将其他类型转换为bytes 第一个参数 格式 数据
print(struct.pack('!I',6))