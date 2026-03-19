# IP-hiofd

通过 `https://toola.hiofd.com/router/rest` 直连查询 IP 信息（纯 requests 版本，不依赖浏览器）。

输出字段：
- 网络服务商
- 位置(IP归属地)
- 区
- 街道

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
ip-hiofd 61.175.188.57
ip-hiofd 61.175.188.57 --json
ip-hiofd 61.175.188.57 --timeout 30 --retries 5 --retry-delay 1.5
```

## Python 作为库调用

```python
from ip_hiofd import HiofdIpClient

client = HiofdIpClient()
result = client.lookup('61.175.188.57')
print(result.isp, result.location, result.district, result.street)
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

- 本版本已去除 Playwright/Chromium 依赖。
- 请求参数 `k/t/x/r` 由本地算法生成并直连查询。
- 若目标站风控策略调整，建议升级版本或临时回退浏览器自动化方案。
