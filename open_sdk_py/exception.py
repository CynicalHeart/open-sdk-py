from .result import ResultCode


class OpException(Exception):
    """自定义异常类"""

    def __init__(self, status: str = None, msg: str = None):
        super().__init__(msg)
        self.status = status
        self.msg = msg

    def __eq__(self, other):
        if not isinstance(other, OpException):
            return False
        return self.status == other.status and self.msg == other.msg

    def __hash__(self):
        return hash((self.status, self.msg))

    def __str__(self):
        return f"OpException(status={self.status}, msg={self.msg})"

    @classmethod
    def from_result_code(cls, result_code):
        return cls(result_code.status, result_code.msg)


if __name__ == "__main__":
    # 创建异常实例
    exception = OpException.from_result_code(ResultCode.FAILED)
    print(exception)
