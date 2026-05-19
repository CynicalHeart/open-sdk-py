import json
import os
import time
import certifi
import logging
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .encrypt import load_rsa_public_key, rsa_encrypt
from .result import ResultCode
from .constants import AlgorithmType, OpenPlatformConstants
from .exception import OpException


_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


class OpenPlatformClient:
    def __init__(
        self,
        app_key: str,
        app_secret: str,
        request_url: str,
        request_data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        algorithm_type: AlgorithmType = AlgorithmType.RSA,
        is_report: bool = False,
        product_case: Optional[str] = None,
    ):
        self.appKey = app_key
        self.appSecret = app_secret
        self.requestUrl = request_url
        self.requestData = request_data
        self.headers = headers or {}
        self.algorithmType = algorithm_type.value
        self.isReport = is_report
        self.productCase = product_case

        self._session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    @classmethod
    def create(
        cls, app_key: str, app_secret: str, request_url: str, **kwargs
    ) -> "OpenPlatformClient":
        if not app_key or not app_secret or not request_url:
            raise OpException.from_result_code(ResultCode.CLIENT_CREATED_EXCEPTION)

        return cls(app_key, app_secret, request_url, **kwargs)

    def set_request_data(self, request_data: Any) -> "OpenPlatformClient":
        self.requestData = request_data
        return self

    def set_headers(self, headers: Dict[str, str]) -> "OpenPlatformClient":
        self.headers.update(headers)
        return self

    def set_algorithm_type(self, algorithm_type: AlgorithmType) -> "OpenPlatformClient":
        self.algorithmType = algorithm_type.value
        return self

    def set_is_report(self, is_report: bool) -> "OpenPlatformClient":
        self.isReport = is_report
        return self

    def set_product_case(self, product_case: str) -> "OpenPlatformClient":
        self.productCase = product_case
        return self

    def send(self):
        request_url = self._build_request_url()

        body = self._build_request_body()

        http_headers = dict(_DEFAULT_HEADERS)
        http_headers.update(
            {
                OpenPlatformConstants.SECURE: self.get_secure(),
                OpenPlatformConstants.ALGORITHM: self.algorithmType,
                "Content-Type": "application/json",
            }
        )

        data = {"encryptData": rsa_encrypt(_get_rsa_public_key(), json.dumps(body))}

        try:
            response = self._session.post(
                request_url,
                data=json.dumps(data),
                headers=http_headers,
                verify=certifi.where(),
                timeout=(10, 30),
            )
        except requests.Timeout as e:
            raise OpException("REQUEST_TIMEOUT", f"请求超时: {e}") from e
        except requests.ConnectionError as e:
            raise OpException("CONNECTION_ERROR", f"连接失败: {e}") from e
        except requests.RequestException as e:
            raise OpException("REQUEST_ERROR", f"请求异常: {e}") from e

        log.info(f"请求云链开放平台接口，响应信息为：{response.text}")

        if not (200 <= response.status_code < 300):
            raise OpException(
                f"HTTP_{response.status_code}",
                f"请求失败: {response.text[:200]}",
            )

        try:
            return response.json()
        except json.JSONDecodeError as e:
            raise OpException(
                "PARSE_ERROR",
                f"响应非JSON格式: {response.text[:200]}",
            ) from e

    def _build_request_url(self) -> str:
        request_url_index = [i for i, char in enumerate(self.requestUrl) if char == "/"]

        if len(request_url_index) >= 3:
            request_url = self.requestUrl[: request_url_index[2]]
        else:
            request_url = self.requestUrl

        if request_url.startswith(OpenPlatformConstants.PRODUCTION_ENVIRONMENT):
            request_url += "/api"

        return f"{request_url}/api-app/sdk/request"

    def _build_request_body(self) -> Dict[str, Any]:
        return {
            "appKey": self.appKey,
            "appSecret": self.appSecret,
            "requestUrl": self.requestUrl,
            "requestData": self.requestData,
            "headers": self.headers,
            "algorithmType": self.algorithmType,
            "isReport": self.isReport,
            "productCase": self.productCase,
        }

    def get_secure(self):
        data = {
            "appKey": self.appKey,
            "appSecret": self.appSecret,
            "timestamp": int(time.time() * 1000),
        }
        return rsa_encrypt(_get_rsa_public_key(), json.dumps(data))


def _get_rsa_public_key():
    resource_path = os.path.join(
        os.path.dirname(__file__),
        OpenPlatformConstants.RESOURCE,
        OpenPlatformConstants.RSA_FILE_NAME,
    )
    return load_rsa_public_key(resource_path)


log_format = "%(asctime)s [%(filename)s] %(levelname)s %(name)s [line:%(lineno)d]  ==> %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    datefmt=date_format,
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger("Open-SDK")
