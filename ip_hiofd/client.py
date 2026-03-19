from __future__ import annotations

import re
import time
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

    @staticmethod
    def _text(page, selector: str) -> str:
        return (page.text_content(selector) or "").strip()

    def _lookup_once(self, ip: str, timeout_sec: int) -> IpLookupResult:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(
                "https://tool.hiofd.com/ip/",
                wait_until="domcontentloaded",
                timeout=timeout_sec * 1000,
            )

            my_ip = self._text(page, "#myIp")

            # 清空输入框并输入新 IP
            page.click("#queryIp")
            page.fill("#queryIp", "")
            page.fill("#queryIp", ip)
            page.dispatch_event("#queryIp", "input")
            page.dispatch_event("#queryIp", "change")

            # 只触发一次查询，避免竞态
            page.click("#queryBtn")

            # 核心修复：必须等待 resultIpAddress 与查询 IP 完全一致
            page.wait_for_function(
                """
                (expectedIp) => {
                    const el = document.querySelector('#resultIpAddress');
                    const v = (el?.textContent || '').trim();
                    return v === expectedIp;
                }
                """,
                arg=ip,
                timeout=timeout_sec * 1000,
            )

            result = IpLookupResult(
                query_ip=ip,
                result_ip=self._text(page, "#resultIpAddress"),
                isp=self._text(page, "#resultIsp"),
                location=self._text(page, "#resultLocation"),
                district=self._text(page, "#resultDistrict"),
                street=self._text(page, "#resultStreet"),
                my_ip=my_ip,
            )
            browser.close()

        if result.result_ip != ip:
            raise RuntimeError(
                f"查询结果校验失败：输入 {ip}，返回 resultIp={result.result_ip}"
            )

        return result

    def lookup(
        self,
        ip: str,
        timeout_sec: int = 90,
        retries: int = 3,
        retry_delay_sec: float = 1.0,
    ) -> IpLookupResult:
        ip = self._validate_ip(ip)

        retries = max(1, int(retries))
        last_error: Exception | None = None

        for attempt in range(1, retries + 1):
            try:
                return self._lookup_once(ip, timeout_sec=timeout_sec)
            except Exception as e:
                last_error = e
                if attempt < retries:
                    time.sleep(retry_delay_sec)

        raise RuntimeError(
            f"查询失败（已重试 {retries} 次）：{last_error}"
        )


def lookup_ip(ip: str) -> IpLookupResult:
    return HiofdIpClient().lookup(ip)
