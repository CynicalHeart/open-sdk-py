## 云枢开放平台Python版工具使用

> 调用云枢开放平台接口集成工具，支持RSA数据加密，请求业务接口可集成到客户端系统中

### 1. 安装与使用

1. 安装依赖

- python版本要求：>=3.7.12

```python
pip install open-sdk-py
```

### 2. 使用

```python
from open_sdk_py import OpenPlatformClient

# 建立请求云枢客户端
client = OpenPlatformClient.create(
            app_key="企业端key值",
            app_secret="企业端secret值",
            request_url="企业申请能力接口，通过后可在申请详情获取接口地址",
            request_data=data # 请求数据，推荐dict格式或json格式
            headers={} # 【若有】dict类型，包含请求头键值对
        )

# 发送请求
result = client.send()  # type为dict类型
```

也可以采用链式构建客户端
```python
client = OpenPlatformClient.create(
            app_key="企业端key值",
            app_secret="企业端secret值",
            request_url="企业申请能力接口，通过后可在申请详情获取接口地址")
            .set_request_data({}).set_headers({})

result = client.send()
```

### 3. 云枢平台自身错误响应

|错误编码|错误信息（含义）|
|:---:|:---:|
|M0411|`app_key`、`app_secret`和`request_url`是必填参数，不能为空|
|M0429|请求次数过多，请稍后重试|
|M0430|不支持的请求类型|
|M0500|系统繁忙，请稍后重试|
|M0555|参数校验失败|
|M0511|三方服务调用失败|
|M0512|获取接口信息失败|
|M0513|响应信息转换失败|
|M0514|接口请求参数不能为空|
|M0515|接口请求头不能为空|

### 补充

---

云枢开放平台地址：[**https://open.yljr.com**](https://open.yljr.com)

问题反馈联系方式：***wantless_wty@163.com***