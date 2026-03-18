from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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
    """Hiofd IP 查询客户端（基于真实浏览器自动化脚本）。

    通过调用同目录下的 `hiofd_browser.js`，获取页面查询结果。
    """

    def __init__(self, project_dir: str | Path | None = None, node_bin: str = "node"):
        base = Path(project_dir) if project_dir else Path(__file__).resolve().parents[1]
        self.project_dir = base
        self.node_bin = node_bin
        self.script_path = self.project_dir / "hiofd_browser.js"
        if not self.script_path.exists():
            raise FileNotFoundError(f"未找到脚本: {self.script_path}")

    @staticmethod
    def _validate_ip(ip: str) -> str:
        ip = ip.strip()
        if not IPV4_RE.match(ip):
            raise ValueError(f"非法 IPv4: {ip}")
        return ip

    def lookup(self, ip: str, timeout_sec: int = 90) -> IpLookupResult:
        ip = self._validate_ip(ip)

        proc = subprocess.run(
            [self.node_bin, str(self.script_path), ip],
            cwd=str(self.project_dir),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )

        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()
            stdout = (proc.stdout or "").strip()
            raise RuntimeError(f"查询失败(returncode={proc.returncode}): {stderr or stdout}")

        out = (proc.stdout or "").strip()
        if not out:
            raise RuntimeError("查询失败：无输出")

        try:
            data = json.loads(out)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"查询失败：输出不是 JSON: {out[:300]}") from e

        result = IpLookupResult(
            query_ip=str(data.get("queryIp") or ip),
            result_ip=str(data.get("resultIp") or ""),
            isp=str(data.get("isp") or ""),
            location=str(data.get("location") or ""),
            district=str(data.get("district") or ""),
            street=str(data.get("street") or ""),
            my_ip=str(data.get("myIp") or ""),
        )

        if result.result_ip and result.result_ip != ip:
            raise RuntimeError(
                f"查询结果校验失败：输入 {ip}，返回 resultIp={result.result_ip}，请重试"
            )

        return result


def lookup_ip(ip: str, project_dir: Optional[str | Path] = None) -> IpLookupResult:
    return HiofdIpClient(project_dir=project_dir).lookup(ip)
