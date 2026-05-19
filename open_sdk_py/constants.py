from enum import Enum


class OpenPlatformConstants:
    SECURE = "secure"
    ALGORITHM = "algorithm"
    SUCCESS_CODE_M0200 = "M0200"
    RESOURCE = "resources"
    RSA_FILE_NAME = "RSA-PublicKey.pem"
    PRODUCTION_ENVIRONMENT = "https://open.yljr.com"


class AlgorithmType(Enum):
    RSA = "RSA"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
