from enum import Enum


class OpenPlatformConstants:
    """
    全局编码常量
    """
    SECURE = "secure"
    ALGORITHM = "algorithm"
    SUCCESS_CODE_M0200 = "M0200"
    RESOURCE = "resources"
    RSA = "RSA"
    SM2 = "SM2"
    RSA_FILE_NAME = "RSA-PublicKey.pem"
    SM2_FILE_NAME = "SM2-PublicKey.pem"
    SSL_FILE_NAME = "cacert.pem"
    PRODUCTION_ENVIRONMENT = "https://open.yljr.com"


class AlgorithmType(Enum):
    """
    枚举：算法类型
    """
    RSA = OpenPlatformConstants.RSA
    SM2 = OpenPlatformConstants.SM2

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
