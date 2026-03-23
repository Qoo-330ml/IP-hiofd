# IP-hiofd

通过 `https://toola.hiofd.com/router/rest` 直连查询 IP 信息。

输出字段：
- IP地址
- 网络服务商
- 位置(IP归属地)
- 区
- 街道
- 纬度
- 经度

## 安装

### 作为 Python 包安装

```bash
pip install ip-hiofd
```

### 开发环境安装

```bash
git clone https://github.com/Qoo-330ml/IP-hiofd
cd IP-hiofd
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Python 命令行

```bash
ip-hiofd --ip=61.175.188.57
ip-hiofd --ip=61.175.188.57 --json
ip-hiofd --ip=61.175.188.57 --timeout 30 --retries 5 --retry-delay 1.5
ip-hiofd --ip=2408:8440:7a80:1df:d0db:53ff:fe1b:410e
```

## Python 作为库调用

```python
from ip_hiofd import HiofdIpClient

client = HiofdIpClient()
result = client.lookup('61.175.188.57')
print(result.isp, result.location, result.district, result.street)
print(result.latitude, result.longitude)
```

或快捷函数：

```python
from ip_hiofd.client import lookup_ip

result = lookup_ip('117.152.147.151')
print(result)
```

## 目录说明

- `ip_hiofd/`：Python 包
- `ip_hiofd/client.py`：纯 requests 实现
- `ip_hiofd_api.py`：兼容旧用法的 Python CLI 封装

## 说明

- 请求参数 `k/t/x/r` 由本地算法生成并直连查询。
- 支持 IPv4 和 IPv6 地址查询。
