from __future__ import annotations

import re
from dataclasses import dataclass

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
    """Hiofd IP 查询客户端（纯 Python Playwright 实现）。"""

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
            page.goto(
                "https://tool.hiofd.com/ip/",
                wait_until="domcontentloaded",
                timeout=timeout_sec * 1000,
            )

            my_ip = (page.text_content("#myIp") or "").strip()

            page.click("#queryIp")
            page.fill("#queryIp", ip)
            page.dispatch_event("#queryIp", "input")
            page.dispatch_event("#queryIp", "change")

            page.click("#queryBtn")
            page.press("#queryIp", "Enter")

            page.wait_for_function(
                """
                () => {
                    const v = (document.querySelector('#resultIpAddress')?.textContent || '').trim();
                    return v && v !== '正在查询...' && v !== '-';
                }
                """,
                timeout=timeout_sec * 1000,
            )
            page.wait_for_timeout(1500)

            def get_text(selector: str) -> str:
                return (page.text_content(selector) or "").strip()

            result = IpLookupResult(
                query_ip=ip,
                result_ip=get_text("#resultIpAddress"),
                isp=get_text("#resultIsp"),
                location=get_text("#resultLocation"),
                district=get_text("#resultDistrict"),
                street=get_text("#resultStreet"),
                my_ip=my_ip,
            )
            browser.close()

        if result.result_ip and result.result_ip != ip:
            raise RuntimeError(
                f"查询结果校验失败：输入 {ip}，返回 resultIp={result.result_ip}，请重试"
            )

        return result


def lookup_ip(ip: str) -> IpLookupResult:
    return HiofdIpClient().lookup(ip)
