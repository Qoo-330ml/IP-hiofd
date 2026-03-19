# IP-hiofd

通过 `https://tool.hiofd.com/ip/` 的真实页面交互查询 IP 信息。

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

> 运行前请安装 Python Playwright 浏览器依赖（无需 Node.js）。

### 开发环境安装

```bash
git clone https://github.com/Qoo-330ml/IP-hiofd
cd IP-hiofd
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## Python 命令行

```bash
ip-hiofd 61.175.188.57
ip-hiofd 61.175.188.57 --json
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
- `ip_hiofd/client.py`：纯 Python Playwright 浏览器自动化实现
- `ip_hiofd_api.py`：兼容旧用法的 Python CLI 封装

## 备注

该站后端接口对直连请求有风控校验（444），本项目采用“真实页面流程自动化”来保证可用性与结果一致性。
