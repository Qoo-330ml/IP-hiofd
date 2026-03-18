#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from typing import Any

import requests

API_URL = "https://toola.hiofd.com/router/rest"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://tool.hiofd.com/ip/",
    "Origin": "https://tool.hiofd.com",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}

IP_RE = re.compile(r"^(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$")


@dataclass
class QueryResult:
    ip: str
    isp: str
    location: str
    district: str
    street: str
    raw: dict[str, Any]


def parse_result(raw: dict[str, Any], query_ip: str) -> QueryResult:
    data = raw.get("data") if isinstance(raw.get("data"), dict) else raw
    if not isinstance(data, dict):
        data = raw

    ip = str(data.get("ip") or query_ip)
    isp = str(data.get("isp") or data.get("org") or "").strip()
    country = str(data.get("country") or data.get("country_name") or "").strip()
    province = str(data.get("province") or data.get("region") or "").strip()
    city = str(data.get("city") or "").strip()
    district = str(data.get("district") or "").strip()
    street = str(data.get("street") or "").strip()

    location = " ".join([x for x in [country, province, city] if x])
    if street:
        location = f"{location} {street}".strip()

    return QueryResult(
        ip=ip,
        isp=isp,
        location=location,
        district=district,
        street=street,
        raw=raw,
    )


def query(ip: str, timeout: int = 12, debug: bool = False) -> QueryResult:
    # 页面脚本中 doConvert('/router/rest','IpQuery', {ip}, cb)
    # 该站对非浏览器请求有强校验（当前环境会返回 444）。
    # 这里先提供最接近网页行为的请求格式。
    payload = {
        "method": "IpQuery",
        "input": json.dumps({"ip": ip}, ensure_ascii=False),
        "key": "key11",
        "pwd": "pwd11",
    }

    with requests.Session() as s:
        s.headers.update(HEADERS)
        r = s.post(API_URL, data=payload, timeout=timeout)

        if debug:
            print("[DEBUG] status:", r.status_code)
            print("[DEBUG] headers:", dict(r.headers))
            print("[DEBUG] body:", r.text[:600])

        r.raise_for_status()
        data = r.json()
        return parse_result(data, ip)


def main() -> int:
    p = argparse.ArgumentParser(description="Hiofd IP 查询")
    p.add_argument("ip", help="IPv4 地址")
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()

    ip = args.ip.strip()
    if not IP_RE.match(ip):
        print("错误：请输入合法 IPv4，例如 61.175.188.57")
        return 2

    try:
        result = query(ip, debug=args.debug)
    except Exception as e:  # noqa: BLE001
        print("查询失败:", e)
        return 1

    print(f"IP: {result.ip}")
    print(f"网络服务商: {result.isp or '-'}")
    print(f"位置(IP归属地): {result.location or '-'}")
    print(f"区: {result.district or '-'}")
    print(f"街道: {result.street or '-'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
