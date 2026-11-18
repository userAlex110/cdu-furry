# 后端选型来源

研究日期：2026-11-18。只读公开页面和本仓库 `7ba22e5` 的源码。未登录控制台，未创建账号或环境，未购买，未部署，未调用业务云接口。

核算脚本：`docs/backend-metered-cost.py`。它不联网。2026-11-18 在本机运行后写出 `docs/backend-metered-cost-results.json`。`full_bill` 保持 `null`。未知项不按 0 加总。

未合并的架构记录仍在 https://github.com/userAlex110/cdu-furry/pull/1 。本文件不复制那份正文。

## 本轮为改写结论重新打开的页面

| 主题 | URL | 页面上的时间 | 本轮采用 |
| --- | --- | --- | --- |
| uniCloud 价格 | https://doc.dcloud.net.cn/uniCloud/price.html | 上次更新 2026/10/9 10:30:17 | 支付宝云纯按量单价、200 元可退保证金、独立预存余额、免费空间与 4.5 元基础版、HTTP 180 秒、定时 3 小时、数据库表述互相冲突的两段、纯按量表格 |
| uniCloud HTTP | https://doc.dcloud.net.cn/uniCloud/http.html | 本轮读取日未显示单独修订日期 | 非 uni-app 可通过 HTTP URL 访问；支付宝云最多 3 个自定义域名；备案在阿里云接入 |
| uniCloud 云函数 | https://doc.dcloud.net.cn/uniCloud/cf-functions.html | 本轮读取日未显示单独修订日期 | 10MB 包体、支付宝云可云端安装 npm、默认内存 512MB、`node-canvas` 不可用、相对路径限制 |
| 函数计算 FC 计费 | https://help.aliyun.com/zh/functioncompute/billing-overview-of-fc | 本轮读取时折扣列写到 2026-08-27 | 活跃小时不足 0.01 元按 0.01 元；阶梯 1 为 0.00011 元/CU。与 EMAS 下线不是同一产品 |
| EMAS 下线 | https://help.aliyun.com/zh/document_detail/2584338.html | 更新 2026-10-26 03:48:42 | 停止新空间和新购；2027-09-30 停服；公告写仅涉及该产品 |

## 同日研究里核对过、本轮沿用 URL 的页面

这些页的摘录用于华为、火山、百度、Tablestore、COS、Laf 和 Cloudflare 的【未知】或对照价。本轮改写没有再逐页打开它们。缺价处保持未知。

| 主题 | URL |
| --- | --- |
| 腾讯云 SCF 计费 | https://cloud.tencent.com/document/product/583/12281 |
| 腾讯云函数 URL | https://cloud.tencent.com/document/product/583/96099 |
| COS 广州示例 | https://cloud.tencent.com/document/product/436/50201 |
| Tablestore 计费项 | https://help.aliyun.com/zh/tablestore/table-store-service/product-overview/billable-items-and-billing-methods/ |
| Tablestore 局部事务 | https://help.aliyun.com/zh/tablestore/table-store-service/local-transactions |
| 百度 BTS 计费 | https://cloud.baidu.com/doc/BTS/s/Ljwvydvu9 |
| 百度 BTS 价格表 | https://cloud.baidu.com/product-price/bts.html |
| 百度 CFC 价格 | https://cloud.baidu.com/product-price/cfc.html |
| 华为 FunctionGraph 价格 | https://support.huaweicloud.com/price-functiongraph/functiongraph_00_0001.html |
| 华为函数 URL API | https://support.huaweicloud.com/api-functiongraph/functiongraph_06_1706.html |
| 火山函数按量 | https://docs.volcengine.com/docs/vefaas/pay-as-you-go-27?lang=zh |
| 火山 API 网关计费 | https://docs.volcengine.com/docs/apig/billingoverview-13?lang=zh |
| uniCloud 阿里云空间公告 | https://ask.dcloud.net.cn/article/id-42719 |
| Sealos 计费 | https://sealos.cn/docs/billing |
| Cloudflare Workers 价格 | https://developers.cloudflare.com/workers/platform/pricing/ |
| 微信网络要求 | https://developers.weixin.qq.com/miniprogram/dev/framework/ability/network.html |

支付宝一手文档 https://opendoc.alipay.com/cloud/0dztak?pathHash=f4979147 在同日研究中返回空正文，不当成独立报价。BOS 动态价格页没有取到完整数字，不用 2020 年案例价。

## 本仓库源码

| 项 | 路径 |
| --- | --- |
| 客户端数据库调用 | `miniprogram/` 下 50 个 js、136 处 `mpServerless.db`（2026-11-18 对当前分支计数） |
| 首用户写成管理员 | `functionsEMAS/unionOp/userOp.js` |
| 平台身份 | `functionsEMAS/unionOp/index.js`、`functionsEMAS/unionOp/_helper.js` |
| 地图接口 | `functionsEMAS/unionOp/getCatLocations.js` |
| 定时与图片依赖 | `functionsEMAS/timeTrigger/index.js`、`functionsEMAS/timeTrigger/photoProcess.js`、`functionsEMAS/timeTrigger/package.json` |
| 文本检查 | `functionsEMAS/unionOp/commentCheck.js` |

## 核算时怎样避免重复和漏项

- uniCloud 路径只使用 DCloud 的 CDN 与回源单价。同一批用户图片不再加 COS 直出。
- CDN 流量和回源流量是两个科目。回源只计入未命中和压缩拉取，不把已计 CDN 的字节再乘一次直出单价。
- SCF 或 CFC 加 BTS 加 COS 时，BTS 返回的公网下行和 COS 图片直出都保留。它们是两家账单。看图字节在 COS 行，不在函数出网里再加一遍。
- 压缩函数从 COS 拉原图时，COS 出口和函数公网入口若分属两家，两行都保留，并在结果里单独命名，避免看成同一科目加了两次。
- 日志、审核附加、域名分摊、隐藏保底不在 JSON 里填 0。`unknown_extras` 和 `full_bill` 为 `null`。
- 200 元保证金不进入月费公式。

## 文档验证限制

`master` 没有 `scripts/repo-check.mjs`，本 PR 不复制那套检查。本轮验证是：重新阅读上表前五行官方页，并离线跑通核算脚本。这不是微信开发者工具、真机、控制台或账单验收。
