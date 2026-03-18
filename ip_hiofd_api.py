#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json

from ip_hiofd import HiofdIpClient


def main() -> int:
    parser = argparse.ArgumentParser(description="IP-hiofd Python API/CLI")
    parser.add_argument("ip", help="IPv4 地址，例如 61.175.188.57")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    client = HiofdIpClient()
    result = client.lookup(args.ip)

    if args.json:
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    else:
        print(f"查询IP: {result.query_ip}")
        print(f"结果IP: {result.result_ip}")
        print(f"网络服务商: {result.isp}")
        print(f"位置(IP归属地): {result.location}")
        print(f"区: {result.district}")
        print(f"街道: {result.street}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
