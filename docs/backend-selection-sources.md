# 后端选型：来源与核对记录

- 日期：2026-11-18
- 代码提交：fork `master` `7ba22e5e947acba14732d97cab699e417f187f7f`
- 方法：阅读本仓库源码，并打开下表中的公开官方页面。未登录云控制台，未访问阿里云服务器，未创建、购买或部署资源，未执行云调用。
- 前一份成本与架构记录在未合并的 PR 里，不在本分支：https://github.com/userAlex110/cdu-furry/blob/fc2d723561298ad639635058a9352f8e7ce50e98/docs/backend-cost-research.md 与同提交的 `docs/backend-cost-sources.md`、`docs/technical-overview.md`。本文件不复制那些正文。PR 地址是 https://github.com/userAlex110/cdu-furry/pull/1 。

## 本轮打开的官方页面

| 主题 | URL | 页面上可见的时间 | 本轮采用的内容 | 标签 |
| --- | --- | --- | --- | --- |
| 腾讯云国内 CloudBase 套餐 | https://cloud.tencent.com/document/product/876/140498 | 最近更新 2026-11-10 11:25:59 | 免费体验版 3,000 点、超时 3 秒且不可改、内存 256MB 且不可改；个人版刊例 39.9 元/月、活动价 19.9 元/月连续包月、40,000 点、超时最大 900 秒、内存可改；标准版 199 元/月、330,000 点，回档从标准版写 14 天；发布后免费环境第 15 天到期；续期政策注明微信体验版不适用 | 事实，限该页 |
| 云函数配置默认值 | https://docs.cloudbase.net/cloud-function/function-configuration/config | 本轮读取日 2026-11-18；页内未显示单独的修订日期 | 普通云函数默认 3 秒，可选 1–900 秒；内存默认 256MB，可选 64–3072MB | 事实，限该页。默认值不是套餐上限 |
| 微信云开发计费 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloud/billing/Billing_Instructions.html | 最后编辑 2026-10-26 | 1000 点=1 元；基础套餐 19.9 元/月（原价 39 元）、40,000 点，可加购可按量；免费环境配额与基础套餐一致、有未列明的功能限制、发布后第 15 天到期、活动至 2026-12-31；库、函数、云存储 CDN 与回源的资源点单价 | 事实，限该页。该页没有超时秒数 |
| EMAS Serverless 下线 | https://help.aliyun.com/zh/document_detail/2584338.html | 更新时间 2026-10-26 03:48:42 | 2026-11-01 起停止新空间和新购；续费叠加不超过 2027-08-31；2027-09-30 停服。页面写本次仅涉及该产品 | 事实 |
| LeanCloud 停服 | https://docs.leancloud.cn/sdk/announcements/sunset-announcement/ | 文内日期 2026-01-12 与 2027-01-12 | 停止新注册和新应用；一年后停服并销毁或匿名化数据 | 事实 |
| uniCloud 阿里云空间 | https://ask.dcloud.net.cn/article/id-42719 | 发布 2026-09-17，更新 2026-11-17 14:05 | 阿里云空间与 EMAS 同步停新购、2027-09-30 停服；公告写可新建支付宝云或腾讯云 uniCloud 空间，并写 uniCloud 腾讯云套餐起步价 99 元/月、定时任务最长 900 秒 | 事实，限 uniCloud。不换算成微信云开发个人版价格 |

## 本轮在源码里核对的位置

| 项 | 仓库路径 | 标签 |
| --- | --- | --- |
| 客户端数据库调用面 | `miniprogram/` 下 50 个 js、136 处 `mpServerless.db`；8 个 js、38 处 `function.invoke` | 事实，2026-11-18 对 `7ba22e5` 计数 |
| 函数入口规模 | `functionsEMAS/unionOp/` 37 个 js；`functionsEMAS/timeTrigger/` 6 个 js；`functionsEMAS/temp/` 7 个 js | 事实 |
| 定时与照片预算 | `functionsEMAS/timeTrigger/index.js`，`functionsEMAS/timeTrigger/photoProcess.js` 的 `TOTAL_BUDGET_MS`，`functionsEMAS/timeTrigger/Readme.md` | 事实。60 秒是代码预算，不是必须购买的套餐档 |
| 首个用户写成管理员 | `functionsEMAS/unionOp/userOp.js` 的 `get` 分支 | 事实，且明确不是新后端的推荐设计 |
| 平台身份覆盖客户端 | `functionsEMAS/unionOp/index.js`，`functionsEMAS/unionOp/_helper.js` | 事实 |
| 地图接口只检查登录 | `functionsEMAS/unionOp/getCatLocations.js` | 事实 |
| 文本内容安全 | `functionsEMAS/unionOp/commentCheck.js` | 事实。覆盖范围未扩展成产品结论 |
| Laf 已不是运行目录 | `README.md`、`miniprogram/pages/info/devTeam/devTeam.js`、`miniprogram/pages/info/info.js` 仍有 Laf 字样；仓库没有 Laf 云函数目录 | 事实。公有云是否仍可新购为未知 |

## 未写成事实的说法

| 说法 | 处理 |
| --- | --- |
| Laf 或 Sealos 公有云已经停购 | 本轮没有官方停购公告。标为未知 |
| Cloudflare 不可用，或不支持银联 | 维护者已接通 Cloudflare。国内访问和支付方式都未核验，标为未知 |
| Supabase 不支持银联所以淘汰 | 支付方式未核验。只记录微信身份集成和国内访问尚未测量 |
| 微信基础套餐已经具备 900 秒 | 900 秒出现在腾讯云 140498 的个人版及更高档。微信计费页没有这句话。标为待验证 |
| 免费体验版 3 秒等于全部 CloudBase | 不采用。PR #1 对免费体验版的警告保留 |
| 第一个访问者自动成为 `manager: 99` 是推荐设计 | 不采用。新后端要求显式、可审计的管理员引导 |
| 只剩一个技术门槛，或必须升到 199 元档才能处理长任务 | 不采用。鉴权、数据库规则、图片和定时任务都还要验收；长任务可以拆分 |
| 研究者列出的首版功能范围等于用户同意删功能 | 不采用 |
| 国际站个人版超时 3 秒 | 本轮没有用国际站判断国内套餐 |
| 服务器规格、地域、续费 | 未知。Issue #3 只确认有服务器和域名 |
| COS 资源包成交价、真实图片体积、CDN 命中率 | 未知。费用表使用可复算假设 |

## 文档验证限制

`master` 上没有 `scripts/repo-check.mjs`，也没有 `.github/workflows/`。本 PR 不复制那套检查，避免把未合并的 PR #1 带进来。因此没有静态脚本或 CI 证明这两份文档。验证限于：文件进入版本库、公式可按正文重算、上表页面在 2026-11-18 打开过、源码路径能在 `7ba22e5` 找到。这不等于微信真机、控制台或服务器已经核验。
