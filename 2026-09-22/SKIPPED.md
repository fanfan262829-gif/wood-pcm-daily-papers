---
date: 2026-09-22
status: skipped
reason: api-rate-limit
---

# 2026-09-22 — 今日跳过

## 原因

今天的 scholar-scout 三步流水线在 **Step 1（论文抓取）** 阶段就失败了，**不是因为没有符合条件的新论文**，而是两个数据源都返回 `HTTP 429 Too Many Requests`：

1. **OpenAlex**（`api.openalex.org/works`）
   返回：
   ```
   {"error":"Rate limit exceeded","message":"Insufficient budget. This request has no API key,
   so it counts against the free daily budget shared by everyone on your network's IP address,
   and that budget is used up ($0 remaining; resets at midnight UTC)...","retryAfter":40447}
   ```
   `retryAfter` ≈ 40447 秒（约 11.2 小时），即需要等到 UTC 午夜配额重置。

2. **Semantic Scholar**（`api.semanticscholar.org/graph/v1/paper/search`）
   同样返回 `429 TooManyRequestsException`（`Too Many Requests. Please wait and try again or apply for a key for higher rate limits.`）。

两次均直接用 `curl` 复现，排除了 `fetch_and_score.py` 脚本本身的问题——是当前云端执行环境的出口 IP 与其他用户共享，OpenAlex 的免费匿名额度（无 API key 时按网络出口 IP 共享每日预算）已被耗尽，Semantic Scholar 的免费限额同样触顶。

`fetch_and_score.py --date 2026-09-22` 最终输出：`Final: 0 papers (target 10)`（合并 0 篇，因为两个源都没抓到任何数据，而非抓到后被判定不相关）。

## 建议后续处理

- 在共享配置 `_skills/_shared/scholar-config.json` 的 `researcher.semantic_scholar_api_key` 中配置一个 Semantic Scholar API key，可显著提高限额。
- 为 OpenAlex 请求申请/配置专属 API key（`?api_key=...`），避免与云端环境其他用户共享匿名额度。
- 或将本流水线安排在 UTC 午夜之后的时间窗口运行，避开当前网络出口 IP 已耗尽当日额度的时间段。

## 本次未执行的步骤

由于 Step 1 抓取产出为空，后续 `scholar-scout-review`（点评）与 `scholar-scout-notes`（笔记）两步按前置检查规则均无法执行，今日无点评、无笔记产出。
