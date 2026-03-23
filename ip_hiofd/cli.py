from __future__ import annotations

import argparse
import json
from datetime import datetime

from .client import HiofdIpClient


def main() -> int:
    parser = argparse.ArgumentParser(description="IP-hiofd Python API/CLI")
    parser.add_argument("--ip", type=str, dest="ip", action="store", help="ip address")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--timeout", type=int, default=90, help="超时秒数，默认 90")
    parser.add_argument("--retries", type=int, default=3, help="重试次数，默认 3")
    parser.add_argument("--retry-delay", type=float, default=1.0, help="重试间隔秒，默认 1.0")
    args = parser.parse_args()

    if not args.ip:
        parser.print_help()
        return 1

    client = HiofdIpClient()
    result = client.lookup(
        args.ip,
        timeout_sec=args.timeout,
        retries=args.retries,
        retry_delay_sec=args.retry_delay,
    )

    if args.json:
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    else:
        print(f"IP-hiofd IP 地理信息查询 ver 0.3.1")
        print(f"IP地址: {result.query_ip}")
        print(f"归属地: {result.location}")
        print(f"运营商: {result.isp}")
        print(f"区: {result.district}")
        print(f"街道: {result.street}")
        if result.latitude and result.longitude:
            print(f"纬度: {result.latitude}")
            print(f"经度: {result.longitude}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
