#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通过真实浏览器自动化访问 https://tool.hiofd.com/ip/：
- 把 IP 填入 #queryIp
- 点击 #queryBtn
- 读取页面展示字段：
  - 网络服务商 (#resultIsp)
  - 位置(IP归属地) (#resultLocation)
  - 区 (#resultDistrict)
  - 街道 (#resultStreet)
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass

from playwright.sync_api import sync_playwright

IP_RE = re.compile(
    r"^(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$"
)


@dataclass
class QueryResult:
    ip: str
    isp: str
    location: str
    district: str
    street: str


def text_or_dash(v: str | None) -> str:
    v = (v or "").strip()
    return v if v else "-"


def query_ip(ip: str, headless: bool = True, timeout_ms: int = 20000) -> QueryResult:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        page.goto("https://tool.hiofd.com/ip/", wait_until="domcontentloaded", timeout=timeout_ms)

        page.fill("#queryIp", ip)
        page.click("#queryBtn")

        # 等待查询结果区域刷新（优先等 ISP 字段变化）
        page.wait_for_selector("#resultIsp", timeout=timeout_ms)
        page.wait_for_timeout(1200)

        isp = text_or_dash(page.text_content("#resultIsp"))
        location = text_or_dash(page.text_content("#resultLocation"))
        district = text_or_dash(page.text_content("#resultDistrict"))
        street = text_or_dash(page.text_content("#resultStreet"))

        browser.close()

    return QueryResult(ip=ip, isp=isp, location=location, district=district, street=street)


def main() -> int:
    parser = argparse.ArgumentParser(description="Hiofd IP 查询（浏览器自动化版）")
    parser.add_argument("ip", help="IPv4，例如 61.175.188.57")
    parser.add_argument("--headed", action="store_true", help="显示浏览器窗口（默认无头）")
    parser.add_argument("--timeout", type=int, default=20000, help="超时毫秒，默认 20000")
    args = parser.parse_args()

    ip = args.ip.strip()
    if not IP_RE.match(ip):
        print("错误：请输入合法 IPv4，例如 61.175.188.57")
        return 2

    try:
        result = query_ip(ip, headless=not args.headed, timeout_ms=args.timeout)
    except Exception as e:  # noqa: BLE001
        print(f"查询失败: {e}")
        return 1

    print(f"IP: {result.ip}")
    print(f"网络服务商: {result.isp}")
    print(f"位置(IP归属地): {result.location}")
    print(f"区: {result.district}")
    print(f"街道: {result.street}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
