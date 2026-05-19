import json
import unittest
from unittest.mock import patch, MagicMock

import requests

from open_sdk_py import OpenPlatformClient, AlgorithmType
from open_sdk_py.exception import OpException
from open_sdk_py.result import ResultCode


class PlatformClientTest(unittest.TestCase):

    def setUp(self):
        self.valid_app_key = "test_app_key"
        self.valid_app_secret = "test_app_secret"
        self.valid_request_url = "https://open.yljr.com/api/test"

    # ---- 创建客户端测试 ----

    def test_create_missing_params(self):
        with self.assertRaises(OpException) as ctx:
            OpenPlatformClient.create("", "", "") 
        self.assertEqual(ctx.exception.status,
                         ResultCode.CLIENT_CREATED_EXCEPTION.status)

    def test_create_missing_app_key(self):
        with self.assertRaises(OpException) as ctx:
            OpenPlatformClient.create("", self.valid_app_secret,
                                      self.valid_request_url)
        self.assertEqual(ctx.exception.status,
                         ResultCode.CLIENT_CREATED_EXCEPTION.status)

    def test_create_success(self):
        client = OpenPlatformClient.create(
            self.valid_app_key,
            self.valid_app_secret,
            self.valid_request_url,
        )
        self.assertEqual(client.appKey, self.valid_app_key)
        self.assertEqual(client.appSecret, self.valid_app_secret)
        self.assertEqual(client.requestUrl, self.valid_request_url)

    def test_create_with_algorithm_type(self):
        client = OpenPlatformClient.create(
            self.valid_app_key,
            self.valid_app_secret,
            self.valid_request_url,
            algorithm_type=AlgorithmType.RSA,
        )
        self.assertEqual(client.algorithmType, AlgorithmType.RSA.value)

    # ---- 链式调用测试 ----

    def test_chain_setters(self):
        client = OpenPlatformClient.create(
            self.valid_app_key,
            self.valid_app_secret,
            self.valid_request_url,
        )
        client.set_request_data({"key": "value"}) \
              .set_headers({"X-Custom": "custom"}) \
              .set_algorithm_type(AlgorithmType.RSA) \
              .set_is_report(True) \
              .set_product_case("case-001")

        self.assertEqual(client.requestData, {"key": "value"})
        self.assertEqual(client.headers, {"X-Custom": "custom"})
        self.assertEqual(client.algorithmType, AlgorithmType.RSA.value)
        self.assertTrue(client.isReport)
        self.assertEqual(client.productCase, "case-001")

    # ---- send 请求测试 ----

    def _build_mock_response(self, status_code, body, content_type,
                             json_ok=True):
        mock = MagicMock(spec=requests.Response)
        mock.status_code = status_code
        mock.text = body
        mock.headers = {"Content-Type": content_type}
        if json_ok:
            mock.json.return_value = json.loads(body)
        else:
            mock.json.side_effect = json.JSONDecodeError(
                "Expecting value", body, 0)
        return mock

    def _create_client(self):
        return OpenPlatformClient(
            app_key=self.valid_app_key,
            app_secret=self.valid_app_secret,
            request_url=self.valid_request_url,
        )

    @patch("open_sdk_py.sdk_client.requests.Session.post")
    def test_send_success(self, mock_post):
        response_body = '{"status": "M0200", "msg": "操作成功", "data": {}}'
        mock_post.return_value = self._build_mock_response(
            200, response_body, "application/json")

        client = self._create_client()
        result = client.send()

        self.assertEqual(result["status"], "M0200")
        mock_post.assert_called_once()

    @patch("open_sdk_py.sdk_client.requests.Session.post")
    def test_send_waf_blocked(self, mock_post):
        waf_body = ("<html><head><title>403 Forbidden</title></head>"
                    "<body><center><h1>403 Forbidden</h1></center>"
                    "<hr><center>WAF</center></body></html>")
        mock_post.return_value = self._build_mock_response(
            403, waf_body, "text/html", json_ok=False)

        client = self._create_client()
        with self.assertRaises(OpException) as ctx:
            client.send()
        self.assertEqual(ctx.exception.status, "HTTP_403")

    @patch("open_sdk_py.sdk_client.requests.Session.post")
    def test_send_waf_blocked_no_content_type(self, mock_post):
        waf_body = "<html><body>WAF Block</body></html>"
        mock_resp = MagicMock(spec=requests.Response)
        mock_resp.status_code = 403
        mock_resp.text = waf_body
        mock_resp.headers = {"Content-Type": "text/plain"}

        mock_post.return_value = mock_resp

        client = self._create_client()
        with self.assertRaises(OpException) as ctx:
            client.send()
        self.assertEqual(ctx.exception.status, "HTTP_403")

    @patch("open_sdk_py.sdk_client.requests.Session.post")
    def test_send_http_error(self, mock_post):
        mock_post.return_value = self._build_mock_response(
            500, '{"status": "M0500", "msg": "系统繁忙"}',
            "application/json")

        client = self._create_client()
        with self.assertRaises(OpException) as ctx:
            client.send()
        self.assertEqual(ctx.exception.status, "HTTP_500")

    @patch("open_sdk_py.sdk_client.requests.Session.post")
    def test_send_parse_error(self, mock_post):
        mock_post.return_value = self._build_mock_response(
            200, "not valid json", "application/json", json_ok=False)

        client = self._create_client()
        with self.assertRaises(OpException) as ctx:
            client.send()
        self.assertEqual(ctx.exception.status, "PARSE_ERROR")

    @patch("open_sdk_py.sdk_client.requests.Session.post")
    def test_send_timeout(self, mock_post):
        mock_post.side_effect = requests.Timeout("Connection timed out")

        client = self._create_client()
        with self.assertRaises(OpException) as ctx:
            client.send()
        self.assertEqual(ctx.exception.status, "REQUEST_TIMEOUT")

    @patch("open_sdk_py.sdk_client.requests.Session.post")
    def test_send_connection_error(self, mock_post):
        mock_post.side_effect = requests.ConnectionError("Connection refused")

        client = self._create_client()
        with self.assertRaises(OpException) as ctx:
            client.send()
        self.assertEqual(ctx.exception.status, "CONNECTION_ERROR")

    @patch("open_sdk_py.sdk_client.requests.Session.post")
    def test_send_headers_include_browser_ua(self, mock_post):
        response_body = '{"status": "M0200", "msg": "ok"}'
        mock_post.return_value = self._build_mock_response(
            200, response_body, "application/json")

        client = self._create_client()
        client.send()

        call_kwargs = mock_post.call_args.kwargs
        self.assertIn("User-Agent", call_kwargs["headers"])
        self.assertIn("Chrome", call_kwargs["headers"]["User-Agent"])


if __name__ == "__main__":
    unittest.main()
