from __future__ import annotations

import hashlib
import random
import re
import time
from dataclasses import dataclass

import requests


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
    """Hiofd IP 查询客户端（纯 requests 实现，无需浏览器）。"""

    API_URL = "https://toola.hiofd.com/router/rest"
    SERVICE_ID = "IpQuery"
    KEY = "key11"
    PWD = "pwd11"

    # 由前端混淆逻辑还原得到
    _P = "3kp"
    _TAIL = "135"
    _ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"

    def __init__(self, user_agent: str | None = None):
        self.user_agent = user_agent or (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
        )

    @staticmethod
    def _validate_ip(ip: str) -> str:
        ip = ip.strip()
        if not IPV4_RE.match(ip):
            raise ValueError(f"非法 IPv4: {ip}")
        return ip

    @classmethod
    def _g(cls, n: int) -> str:
        return "".join(random.choice(cls._ALPHABET) for _ in range(n))

    @classmethod
    def _build_security_fields(cls) -> tuple[str, str, str, str]:
        # D: 随机 7 位后插入 P 中字符（与站点逻辑一致）
        arr = list(cls._g(7))
        for ch in cls._P:
            idx = random.randrange(0, len(arr) + 1)
            arr.insert(idx, ch)
        d = "".join(arr)

        # K: 每个字符在 D 中首次出现的位置拼接
        k_pos = "".join(str(d.index(ch)) for ch in cls._P)

        t_rand = cls._g(22)
        k = d + t_rand

        # t = J + timestamp(ms) + K + "135"
        j = str(random.randrange(0, 10))
        ts = str(int(time.time() * 1000))
        t = j + ts + k_pos + cls._TAIL

        # r: 32位随机串
        r = cls._g(32)

        # x = md5(t + serviceId + t + r + k) + 8位随机串
        v = t + cls.SERVICE_ID + t + r + k
        x = hashlib.md5(v.encode("utf-8")).hexdigest() + cls._g(8)

        return k, t, x, r

    def _lookup_once(self, ip: str, timeout_sec: int) -> IpLookupResult:
        k, t, x, r = self._build_security_fields()

        payload = {
            "body": {"input": {"ip": ip}},
            "serviceId": self.SERVICE_ID,
            "key": self.KEY,
            "pwd": self.PWD,
            "k": k,
            "t": t,
            "x": x,
            "r": r,
        }

        # URL 上的 r 参数当前不参与校验，但保持与真实请求风格一致
        url = f"{self.API_URL}?method={self.SERVICE_ID}&r={int(time.time() * 1000)}"
        headers = {
            "content-type": "application/json; charset=UTF-8",
            "referer": "https://tool.hiofd.com/ip/",
            "user-agent": self.user_agent,
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=timeout_sec)
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")

        data = resp.json()
        if data.get("resultCode") != 0:
            raise RuntimeError(
                f"查询失败 resultCode={data.get('resultCode')}, resultMessage={data.get('resultMessage')}"
            )

        result_ip = str(data.get("ip") or "")
        if result_ip and result_ip != ip:
            raise RuntimeError(f"查询结果校验失败：输入 {ip}，返回 resultIp={result_ip}")

        country = str(data.get("country") or "").strip()
        province = str(data.get("province") or "").strip()
        city = str(data.get("city") or "").strip()
        location = " · ".join([x for x in [country, province, city] if x])

        return IpLookupResult(
            query_ip=ip,
            result_ip=result_ip,
            isp=str(data.get("isp") or ""),
            location=location,
            district=str(data.get("district") or ""),
            street=str(data.get("street") or ""),
            my_ip="",
        )

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

        raise RuntimeError(f"查询失败（已重试 {retries} 次）：{last_error}")


def lookup_ip(ip: str) -> IpLookupResult:
    return HiofdIpClient().lookup(ip)
