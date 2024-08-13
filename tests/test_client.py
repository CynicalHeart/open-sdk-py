import unittest
import sys
import os

# 将项目根目录添加到sys.path
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from open_sdk_py import OpenPlatformClient


class PlatfromClientTest(unittest.TestCase):

    def test_sdk_send(self):

        client = OpenPlatformClient.create(
            app_key="企业端key值",
            app_secret="企业端secret值",
            request_url='企业申请能力接口，通过后可在申请详情获取接口地址',
            request_data='{}',  # json化
            headers={})

        # 发送请求
        result = client.send()
        print(f"content is {result}")


if __name__ == '__main__':
    unittest.main()
