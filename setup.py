from setuptools import setup, find_packages

setup(
    name='open-sdk-py',
    version='2.1.1',
    description='云枢开放服务平台集成SDK工具（Python版）',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='CynicalHeart',
    author_email='wutianyu@yljr.com',
    packages=find_packages(),
    license='MIT',
    install_requires=['requests', 'cryptography', 'gmssl', 'certifi'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_data={
        'open_sdk_py': ['resources/*'],
    },
    python_requires='>=3.7',
)
