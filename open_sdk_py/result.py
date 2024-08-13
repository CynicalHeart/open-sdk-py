from enum import Enum
from typing import Generic, Optional, TypeVar

T = TypeVar('T')


class BaseResult(Generic[T]):

    def __init__(self, status: str, msg: str, data: Optional[T] = None):
        self._status = status
        self._msg = msg
        self._data = data

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, status: str):
        self._status = status

    @property
    def msg(self) -> str:
        return self._msg

    @msg.setter
    def msg(self, msg: str):
        self._msg = msg

    @property
    def data(self) -> Optional[T]:
        return self._data

    def set_data(self, data: T) -> 'BaseResult':
        self._data = data
        return self

    @classmethod
    def create(cls, status: str, msg: str) -> 'BaseResult':
        return cls(status, msg)

    @classmethod
    def success(cls) -> 'BaseResult':
        return cls.create(ResultCode.SUCCESS.status, ResultCode.SUCCESS.msg)

    @classmethod
    def success_with_data(cls, data: T) -> 'BaseResult':
        return cls.success().set_data(data)

    @classmethod
    def fail(cls) -> 'BaseResult':
        return cls.create(ResultCode.FAILED.status, ResultCode.FAILED.msg)

    @classmethod
    def fail_with_data(cls, data: T) -> 'BaseResult':
        return cls.fail().set_data(data)

    @classmethod
    def fail_with_code(cls, code: str, msg: str) -> 'BaseResult':
        return cls.create(code, msg)

    def __str__(self) -> str:
        return f"status: {self._status}, msg: {self._msg}, data: {self._data}"


class ResultCode(Enum):
    """
    响应结果枚举
    """

    SUCCESS = ("M0200", "操作成功")
    TOO_MANY_REQUESTS = ("M0429", "请求次数过多，请稍后重试")
    UNSUPPORTED_REQUEST_TYPE = ("M0430", "不支持的请求类型")
    FAILED = ("M0500", "系统繁忙，请稍后重试")
    VALIDATE_FAILED = ("M0555", "参数校验失败")
    CALL_FAILED = ("M0511", "三方服务调用失败")
    GET_INTERFACE_INFO_FAILED = ("M0512", "获取接口信息失败")
    RESPONSE_CONVERSION_ERROR = ("M0513", "响应信息转换失败")
    REQUEST_PARAM_NOT_NULL = ("M0514", "接口请求参数不能为空")
    REQUEST_HEADER_NOT_NULL = ("M0515", "接口请求头不能为空")
    CLIENT_CREATED_EXCEPTION = (
        "M0411", "app_key, app_secret 和 request_url 是必填参数，不能为空。")

    def __init__(self, status: str, msg: str):
        self._status = status
        self._msg = msg

    @property
    def status(self) -> str:
        return self._status

    @property
    def msg(self) -> str:
        return self._msg


if __name__ == "__main__":
    result = BaseResult.create("M0200", "操作成功")
    print(result)
