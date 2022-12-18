from services import InvalidOperation
from services import RPCServer


class Handlers:
    @staticmethod
    def divide(num1, num2=1):
        if num2 == 0:
            raise InvalidOperation()
        return num1 / num2


# 开启服务器
if __name__ == '__main__':
    _server = RPCServer('127.0.0.1', 8000, Handlers)
    _server.start()
