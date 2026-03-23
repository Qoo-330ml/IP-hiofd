from __future__ import annotations

import argparse
import json
from datetime import datetime

from .client import HiofdIpClient


def main() -> int:
    parser = argparse.ArgumentParser(description="IP-hiofd Python API/CLI")
    parser.add_argument("--ip", required=True, help="IP 地址，例如 61.175.188.57 或 2001:0db8:85a3:0000:0000:8a2e:0370:7334")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--timeout", type=int, default=90, help="超时秒数，默认 90")
    parser.add_argument("--retries", type=int, default=3, help="重试次数，默认 3")
    parser.add_argument("--retry-delay", type=float, default=1.0, help="重试间隔秒，默认 1.0")
    args = parser.parse_args()

    client = HiofdIpClient()
    result = client.lookup(
        args.ip,
        timeout_sec=args.timeout,
        retries=args.retries,
        retry_delay_sec=args.retry_delay,
    )

    timestamp = datetime.now().strftime("[%H:%M:%S]")

    if args.json:
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    else:
        print(f"{timestamp} [INFO] IP-hiofd IP 地理信息查询 ver 0.3.0")
        print(f"{timestamp} [INFO] IP地址: {result.query_ip}")
        print(f"{timestamp} [INFO] 归属地: {result.location}")
        print(f"{timestamp} [INFO] 运营商: {result.isp}")
        print(f"{timestamp} [INFO] 区: {result.district}")
        print(f"{timestamp} [INFO] 街道: {result.street}")
        if result.latitude and result.longitude:
            print(f"{timestamp} [INFO] 纬度: {result.latitude}")
            print(f"{timestamp} [INFO] 经度: {result.longitude}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
