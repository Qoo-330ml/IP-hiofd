# IP-hiofd

通过 `https://tool.hiofd.com/ip/` 的真实页面交互查询 IP 信息。

输出字段：
- 网络服务商
- 位置(IP归属地)
- 区
- 街道

## 目录说明

- `hiofd_browser.js`：底层浏览器自动化脚本（Playwright）
- `ip_hiofd/`：Python 可调用库
- `ip_hiofd_api.py`：Python CLI 封装

## 安装

```bash
cd ~/Fnos/项目/IP-hiofd
npm install
npx playwright install chromium
```

> Python 端仅用标准库（通过 subprocess 调用 node 脚本）。

## Python 作为命令行使用

```bash
python ip_hiofd_api.py 61.175.188.57
python ip_hiofd_api.py 61.175.188.57 --json
```

## Python 作为库调用

```python
from ip_hiofd import HiofdIpClient

client = HiofdIpClient(project_dir='~/Fnos/项目/IP-hiofd')
result = client.lookup('61.175.188.57')
print(result.isp, result.location, result.district, result.street)
```

或快捷函数：

```python
from ip_hiofd.client import lookup_ip

result = lookup_ip('117.152.147.151', project_dir='~/Fnos/项目/IP-hiofd')
print(result)
```

## 备注

该站后端接口对直连请求有风控校验（444），本项目采用“真实页面流程自动化”来保证可用性与结果一致性。
