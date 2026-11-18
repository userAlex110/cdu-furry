# 后端成本调研的来源

研究日：2026-11-18，时区 Asia/Shanghai。单价表的访问窗口约 11:07–11:14。写入本仓库时又打开了一次下线公告，正文与该窗口的摘录一致。

方法：只读公开网页。没有登录阿里云或腾讯云控制台，没有创建环境，没有购买，没有部署。CloudBase 国内开发助手在后续步骤里处于已认证状态，本文件不把「已认证」写成「已有环境」。

第三方博客和上游 README 里的「每月约 5 元」没有进入单价表。COS 资源包的下单页成交价没有打开，表中标为未核验。

## 本轮复查的公告

页面：https://help.aliyun.com/zh/document_detail/2584338.html

页面自带更新时间：2026-10-26 03:48:42。

写入文档时读到的正文：

> 于 2026 年 11 月 1 日起，不再支持创建新的服务空间，停止新购，同时续费时长叠加不允许超过 2027年 8月 31日；
>
> 我们将为存量服务空间继续提供服务，直到 2027 年 9 月 30 日，正式停服，届时，控制台与后端服务将同步下线，不再提供服务。
>
> 本次调整仅涉及该产品。EMAS 将进一步加大对 HTTPDNS 和移动推送的投入……

同一公告的另一入口 https://help.aliyun.com/zh/document_detail/3062704.html 在调研窗口里正文一致。公告只点名 EMAS Serverless。腾讯云 COS 不在这次下线范围内。公告也没有把函数计算 FC 写成整套后继。

## 单价与规则页面

下列「页面时间」是页面上能看到的更新或编辑时间。没有单独时间戳的页面，只记调研日访问过。

| 主题 | URL | 页面时间 |
| --- | --- | --- |
| EMAS 计费概述 | https://help.aliyun.com/zh/document_detail/435823.html | 2026-04-21 03:31:24 |
| EMAS 计费概述另一入口 | https://help.aliyun.com/zh/document_detail/435829.html | 调研日访问，抓取正文无单独时间 |
| EMAS 云函数结算与低消 | https://help.aliyun.com/zh/document_detail/435831.html | 调研日访问 |
| EMAS 云函数低消变更 | https://help.aliyun.com/zh/document_detail/3014648.html | 公告日 2026-01-16，生效 2026-03-16 |
| EMAS 包年包月配额 | https://help.aliyun.com/zh/document_detail/435837.html | 调研日访问 |
| EMAS 欠费 | https://help.aliyun.com/zh/document_detail/435835.html | 调研日访问 |
| EMAS 系统限制 | https://help.aliyun.com/zh/document_detail/606199.html | 调研日访问 |
| EMAS 数据库备份 | https://help.aliyun.com/zh/document_detail/435860.html | 调研日访问 |
| EMAS Serverless 是什么 | https://help.aliyun.com/zh/document_detail/436030.html | 调研日访问 |
| CloudBase 云数据库环境计费 | https://cloud.tencent.com/document/product/876/140498 | 2026-11-10 11:25:59 |
| CloudBase 计费概述（另一环境口径，套餐价同行） | https://cloud.tencent.com/document/product/876/127357 | 2026-11-10 11:25:51 |
| CloudBase 套餐停服 | https://cloud.tencent.com/document/product/876/136006 | 2026-10-28 18:06:02 |
| CloudBase 欠费（页面标明面向旧配额制） | https://cloud.tencent.com/document/product/876/39729 | 2026-08-17 |
| 旧资源套餐停止续费 | https://cloud.tencent.com/announce/detail/2440 | 涉及 2026-09-09 与 2026-11-09 |
| CloudBase 定价页 | https://tcb.cloud.tencent.com/pricing | 无独立更新日期 |
| 微信资源点计费 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloud/billing/Billing_Instructions.html | 最后编辑 2026-10-26 |
| 微信固定配额旧说明 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloud/billing/price.html | 最后编辑 2026-10-23 |
| 微信云开发与腾讯云账号 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloud/basis/concepts/account | 最后编辑 2026-08-24 |
| COS 存储容量费用 | https://cloud.tencent.com/document/product/436/53482 | 2026-10-12 |
| COS 流量费用 | https://cloud.tencent.com/document/product/436/53863 | 2026-08-26 |
| COS 免费额度 | https://cloud.tencent.com/document/product/436/6240 | 调研日访问 |
| COS 欠费 | https://cloud.tencent.com/document/product/436/10044 | 2025-03-11 |
| CDN 基础服务计费 | https://cloud.tencent.com/document/product/228/75562 | 2026-11-17 |
| 小程序备案问答 | https://developers.weixin.qq.com/miniprogram/product/record/record_faq.html | 最后编辑 2026-09-11 |
| CloudBase Setup Skill | https://docs.cloudbase.net/skill.md | 只用于区分工具和平台，没有执行其中的登录和创建步骤 |

流量文档要求具体价格以腾讯云定价中心实时公示为准。本轮没有登录定价中心。广州存储 0.118 元/GB/月、外网下行 0.5 元/GB、CDN 回源 0.15 元/GB 来自上述官方文档中的刊例或示例，地域差价没有逐个打开。

## 关键摘录

云函数小时低消（435831 / 3014648）：自 2026-03-16 00:00（UTC+8）起，某函数在某一小时内只要产生资源消耗（GBs > 0），该小时资源使用量费用不低于 0.01 元。未运行的函数不计这一笔。

微信免费体验（Billing_Instructions，最后编辑 2026-10-26）：未发布阶段无需续费；发布后到期时间改为上线后第 15 天；活动截止 2026-12-31；免费环境配额与基础套餐一致，不支持额外加购。

腾讯云控制台免费体验（140498，2026-11-10）：2026-01-16 起每个账号可用一次性兑换码创建一个免费体验环境，每月 3,000 点。续期政策只适用于控制台创建的体验版，微信体验版不适用。发布后同样改为上线后第 15 天。

微信与腾讯云（account，2026-08-24）：开通微信云开发会在腾讯云侧创建对应云账号。

## 代码核对

迁移量一节对照的是本仓库，不是公告页面。统计日与文档提交同一天：`miniprogram/` 里 `mpServerless.db` 出现在 50 个文件、共 136 处；`function.invoke` 出现在 8 个文件。`functionsEMAS/unionOp` 有 37 个 js，`timeTrigger` 有 6 个 js，`temp/` 有 7 个 js。`photoProcess.js` 的 `TOTAL_BUDGET_MS` 为 60000。`timeTrigger/index.js` 注释写定时器约 5 分钟一次。这些数字描述代码形状，不表示已经部署或计费。
