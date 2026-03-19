from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Optional

from playwright.sync_api import sync_playwright


IPV4_RE = re.compile(
    r"^(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$"
)


@dataclass
class IpLookupResult:
    query_ip: str
    result_ip: str
    isp: str
    location: str
    district: str
    street: str
    my_ip: str = ""


class HiofdIpClient:
    def __init__(self):
        pass

    @staticmethod
    def _validate_ip(ip: str) -> str:
        ip = ip.strip()
        if not IPV4_RE.match(ip):
            raise ValueError(f"非法 IPv4: {ip}")
        return ip

    def lookup(self, ip: str, timeout_sec: int = 90) -> IpLookupResult:
        ip = self._validate_ip(ip)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('https://tool.hiofd.com/ip/', wait_until='domcontentloaded', timeout=timeout_sec * 1000)

            my_ip = page.text_content('#myIp') or ''

            page.click('#queryIp')
            page.fill('#queryIp', ip)
            page.dispatch_event('#queryIp', 'input')
            page.dispatch_event('#queryIp', 'change')

            page.click('#queryBtn')
            page.press('#queryIp', 'Enter')

            page.wait_for_function('''
                () => {
                    const v = (document.querySelector('#resultIpAddress')?.textContent || '').trim();
                    return v && v !== '正在查询...' && v !== '-';
                }
            ''', timeout=timeout_sec * 1000)

            page.wait_for_timeout(1500)

            def get_text(selector):
                return (page.text_content(selector) or '').strip()

            result = {
                'queryIp': ip,
                'myIp': my_ip,
                'resultIp': get_text('#resultIpAddress'),
                'isp': get_text('#resultIsp'),
                'location': get_text('#resultLocation'),
                'district': get_text('#resultDistrict'),
                'street': get_text('#resultStreet'),
            }

            browser.close()

        if result['resultIp'] and result['resultIp'] != ip:
            raise RuntimeError(
                f"查询结果校验失败：输入 {ip}，返回 resultIp={result['resultIp']}，请重试"
            )

        return IpLookupResult(
            query_ip=str(result.get('queryIp') or ip),
            result_ip=str(result.get('resultIp') or ''),
            isp=str(result.get('isp') or ''),
            location=str(result.get('location') or ''),
            district=str(result.get('district') or ''),
            street=str(result.get('street') or ''),
            my_ip=str(result.get('myIp') or ''),
        )


def lookup_ip(ip: str) -> IpLookupResult:
    return HiofdIpClient().lookup(ip)


if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Hiofd IP 查询客户端")
    parser.add_argument("ip", help="IPv4 地址，例如 61.175.188.57")
    parser.add_argument("--timeout", type=int, default=90, help="超时秒数，默认 90")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    
    args = parser.parse_args()
    
    try:
        result = lookup_ip(args.ip)
        
        if args.json:
            print(json.dumps({
                "query_ip": result.query_ip,
                "result_ip": result.result_ip,
                "isp": result.isp,
                "location": result.location,
                "district": result.district,
                "street": result.street,
                "my_ip": result.my_ip
            }, ensure_ascii=False, indent=2))
        else:
            print(f"查询IP: {result.query_ip}")
            print(f"我的IP: {result.my_ip}")
            print(f"结果IP: {result.result_ip}")
            print(f"网络服务商: {result.isp}")
            print(f"位置: {result.location}")
            print(f"区: {result.district}")
            print(f"街道: {result.street}")
            
    except Exception as e:
        print(f"查询失败: {e}")
        exit(1)