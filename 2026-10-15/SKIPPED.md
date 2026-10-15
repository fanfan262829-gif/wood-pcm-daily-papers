---
date: 2026-10-15
tags: [daily-papers, skipped]
---

# 2026-10-15 — 今日跳过（基础设施故障）

## 原因

两个数据源在本次运行期间均持续返回 HTTP 429（请求过多），判定为基础设施故障，而非"候选池中无合适论文"：

- **OpenAlex**：请求返回 `429`，响应头 `retry-after` 约为 49321 秒（约 13.7 小时），且在约 2 分钟内多次重试，倒计时持续按真实时间递减（49321 → 49207 → 49181 → 49156 → 49130），说明是云端环境共享代理 IP 的**每日配额已耗尽**，短时间内重试无法恢复。
- **Semantic Scholar**：无 `retry-after` 响应头，但在 8 组不同关键词查询（覆盖用户研究方向的全部核心词：`wood-based composite`、`phase change material`、`balsa wood`、`anisotropic thermal conductivity`、`interfacial thermal resistance` 等）上，每组均重试 5 次（指数退避 10s × 1~5），耗时数分钟，**全部 40+ 次请求均返回 429**，期间偶有一次探测性请求（`query=wood`）返回 200，证明接口本身可达，但在本次抓取窗口内持续受限，判断为该数据源的限流窗口尚未解除。

## 已执行的操作

1. 按 `scholar-scout-fetch` 流程尝试调用 `fetch_and_score.py` 的内部函数（`fetch_openalex_recent`、`fetch_openalex_high_cited`、`fetch_s2_papers`），覆盖 OpenAlex Recent + OpenAlex High-Cited + Semantic Scholar 三路数据源。
2. 对 OpenAlex 尝试 2 次（按其 `retry-after` 判断单次运行内不可能恢复，不做无意义的长时间等待）。
3. 对 Semantic Scholar 用 8 组不同关键词分别重试 5 次，总计 40+ 次请求，全部失败。
4. 候选池最终为 **0 篇**，无法进行后续"扩大候选池 50-100+ → 跨天查重 → 选优"流程。

## 结论

本次跳过不代表当天无高质量论文可推荐，而是两个数据源在抓取窗口期均不可访问（OpenAlex 配额耗尽 + Semantic Scholar 持续限流）。建议下次运行时正常重试；若 OpenAlex 的配额问题持续出现，可能需要检查云端环境共享代理 IP 的调用频率，或为 `researcher.email` 申请 OpenAlex/S2 的专属 API Key 以获得更高配额。
