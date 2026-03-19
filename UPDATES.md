# IP-hiofd 项目更新说明

## v0.2.0（纯 requests 版本）

### 重大变更
- 去除 Playwright/Chromium 依赖，改为纯 `requests` 直连 `toola.hiofd.com/router/rest`。
- 本地生成请求校验字段：`k / t / x / r`。
- 保留原有结果结构与 CLI 参数（`--timeout --retries --retry-delay`）。

### 依赖变化
- 移除：`playwright`
- 新增：`requests>=2.31.0`

### 兼容性
- 对外 API 入口保持不变：`HiofdIpClient().lookup(ip)` 与 `lookup_ip(ip)`。
- 输出字段保持不变：`query_ip/result_ip/isp/location/district/street`。

### 风险提示
- 当前算法基于目标站现行前端逻辑逆向得到；若站点调整风控参数生成规则，需同步更新。
- 建议在生产环境保留可回退方案（例如浏览器自动化分支）。

## v0.1.2（稳定性修复）

### 修复点
- 修复偶发 `query_ip` 与 `result_ip` 不一致的问题（页面旧结果脏读）。
- 查询触发改为单次点击，避免 click + Enter 双触发竞态。
- 等待条件升级为：`#resultIpAddress` 必须与输入 IP 完全一致。
- 内置重试机制（默认 3 次，间隔 1 秒）。

### CLI 新增参数
- `--timeout`（默认 90）
- `--retries`（默认 3）
- `--retry-delay`（默认 1.0）
