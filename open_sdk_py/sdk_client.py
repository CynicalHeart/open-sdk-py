import json
import os
import time
import requests
import logging
from typing import Any, Dict, Optional

from .encrypt import *

from .result import ResultCode
from .constants import AlgorithmType, OpenPlatformConstants
from .exception import OpException


class OpenPlatformClient:

    def __init__(self,
                 app_key: str,
                 app_secret: str,
                 request_url: str,
                 request_data: Optional[Any] = None,
                 headers: Optional[Dict[str, str]] = None,
                 algorithm_type: AlgorithmType = AlgorithmType.RSA,
                 is_report: bool = False,
                 product_case: Optional[str] = None):
        self.appKey = app_key
        self.appSecret = app_secret
        self.requestUrl = request_url
        self.requestData = request_data
        self.headers = headers or {}
        self.algorithmType = algorithm_type.value
        self.isReport = is_report
        self.productCase = product_case

    @classmethod
    def create(cls, app_key: str, app_secret: str, request_url: str,
               **kwargs) -> 'OpenPlatformClient':
        # 验证必选参数
        if not app_key or not app_secret or not request_url:
            raise OpException.from_result_code(
                ResultCode.CLIENT_CREATED_EXCEPTION)

        return cls(app_key, app_secret, request_url, **kwargs)

    # 链式设置请求数据
    def set_request_data(self, request_data: Any) -> 'OpenPlatformClient':
        self.requestData = request_data
        return self

    # 链式设置请求头
    def set_headers(self, headers: Dict[str, str]) -> 'OpenPlatformClient':
        self.headers.update(headers)
        return self

    # 链式设置算法类型
    def set_algorithm_type(
            self, algorithm_type: AlgorithmType) -> 'OpenPlatformClient':
        self.algorithmType = algorithm_type.value
        return self

    # 链式设置是否报告
    def set_is_report(self, is_report: bool) -> 'OpenPlatformClient':
        self.isReport = is_report
        return self

    # 链式设置产品案例
    def set_product_case(self, product_case: str) -> 'OpenPlatformClient':
        self.productCase = product_case
        return self

    def send(self):
        """SDK发送请求"""

        request_url_index = [
            i for i, char in enumerate(self.requestUrl) if char == '/'
        ]

        if len(request_url_index) >= 3:
            request_url = self.requestUrl[:request_url_index[2]]
        else:
            request_url = self.requestUrl

        if request_url.startswith(
                OpenPlatformConstants.PRODUCTION_ENVIRONMENT):
            request_url += "/api"

        data = {
            "encryptData":
            rsa_encrypt(get_public_key(AlgorithmType.RSA),
                        json.dumps(self.__dict__))
        }

        headers = {
            OpenPlatformConstants.SECURE: self.get_secure(),
            OpenPlatformConstants.ALGORITHM: self.algorithmType,
            "Content-Type": "application/json"
        }
        request_url = f"{request_url}/api-app/sdk/request"
        response = requests.post(request_url,
                                 data=json.dumps(data),
                                 headers=headers,
                                 verify=False)

        log.info(f"请求云链开放平台接口，响应信息为：{response.text}")
        return response.json()

    def get_secure(self):
        data = {
            "appKey": self.appKey,
            "appSecret": self.appSecret,
            "timestamp": int(time.time() * 1000)
        }

        if self.algorithmType == AlgorithmType.RSA.value:
            return rsa_encrypt(get_public_key(AlgorithmType.RSA),
                               json.dumps(data))
        else:
            return sm2_encrypt(get_public_key(AlgorithmType.SM2),
                               json.dumps(data))


def get_public_key(type: AlgorithmType):

    resoucre_path = os.path.join(
        os.path.dirname(__file__), OpenPlatformConstants.RESOURCE,
        OpenPlatformConstants.RSA_FILE_NAME
        if type is AlgorithmType.RSA else OpenPlatformConstants.SM2_FILE_NAME)
    if type is AlgorithmType.SM2:
        return load_sm2_public_key(resoucre_path)
    else:
        return load_rsa_public_key(resoucre_path)


# 配置日志格式
log_format = '%(asctime)s [%(filename)s] %(levelname)s %(name)s [line:%(lineno)d]  ==> %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(level=logging.INFO,
                    format=log_format,
                    datefmt=date_format,
                    handlers=[logging.StreamHandler()])
log = logging.getLogger('Open-SDK')
