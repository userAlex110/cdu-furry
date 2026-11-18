# 架构决策

日期：2026-11-18。状态里的「已接受」表示本 fork 现在按此执行。「待定」表示还不能写代码实现。

## ADR-001 现行实现保持 EMAS + COS

状态：已接受（描述现状，不是最终选型）

`miniprogram/app.js` 初始化 `@alicloud/mpserverless-sdk`，空间地址是 `https://api.next.bspapp.com`。照片在 `use_private_tencent_cos === true` 时走腾讯云：上传用 `getURL` 的 S3 兼容签名，读取用 `getTempCOS` 的 STS，策略只有 `cos:GetObject`。

Laf 不是现行后端。仓库里已经没有 Laf 云函数目录。`pages/debug/debug.js` 的 `wx.cloud.callFunction` 是旧调试入口，对应函数不在 `functionsEMAS/`。

后果：接手人按 EMAS 集合、`unionOp` 动作和 COS 字段理解系统。不要把调试页的 `wx.cloud` 当成主链路。

## ADR-002 新环境不能再开通 EMAS Serverless，选型仍待定

状态：待定。2026-11-18 用公开公告更正了「可以按上游手册新建 EMAS」这一条。

阿里云文档 https://help.aliyun.com/zh/document_detail/2584338.html 的更新时间是 2026-10-26。正文写明：2026-11-01 起停止新建服务空间和新购，续费叠加不得超过 2027-08-31；存量空间服务到 2027-09-30 停服，控制台与后端同时下线。成大这个 fork 没有自己的存量空间。`config.js` 里的空间标识属于上游，不能拿来当成成大的新环境。所以上游 README、外部部署文档和 `pages/debug/deployTip` 里的开通步骤，从这一天起不能再当作施工单。

公告只覆盖 EMAS Serverless：

- 腾讯云 COS 不在下线范围内。现行图片路径已经走 COS。桶可以继续作为存储候选，本阶段仍然不创建、不购买。
- 函数计算 FC 只是 EMAS 云函数所基于的运行时。它不带这套文档库、登录和客户端 SDK，不能写成停服后的整套替代。
- 公告没有给出官方迁移目标。不要把别的阿里云产品写成指定后继。

CloudBase 国内站仍是候选，不是决定。价格、活动价、试用额度和未核验的成交价写在 `docs/backend-cost-research.md`，出处在 `docs/backend-cost-sources.md`。19.9 元/月是活动价。免费体验有截止日期或发布后 15 天的限制，不是永久免费。上游「每月约 5 元」不是报价。

对照代码之后，换后端不是改配置。前端有 50 个文件、136 处直接读库；线上形状是 `unionOp` 加 `timeTrigger` 两个函数，另加仓库外的 `catFace`。`photoProcess` 的时间预算是 60 秒，对不上 CloudBase 免费档「3 秒且不可改」的能力表。细节见成本文档的迁移一节。在新的 ADR 写成已选择之前，不开始迁移。

在那之前：

- 不新增 CloudBase 环境、数据库、存储或云函数，也不绑定已有环境。
- 不把 `functionsEMAS/` 重写成 CloudBase 或 FC。
- 不把前端数据库调用改成 `wx.cloud`。
- 不按 CloudBase Skill 去创建环境。国内开发助手即使已经认证，也只是工具层。认证不等于环境已创建，更不等于本项目授权去创建。

2026-11-18 还读过：

- `https://docs.cloudbase.net/skill.md`：它引导安装插件、登录并创建环境。这些步骤会碰到资源，本项目没有授权执行。
- 微信小程序开发 Skill：没有明确决定时，不要假设项目使用 CloudBase。预览仍要微信开发者工具和可用 AppID。
- Spec 工作流：后端替换要先有需求、设计和任务，并等人确认。这次只把公告和代码量写进文档。

## ADR-003 后端代码目前只读

状态：已接受

`functionsEMAS/` 含权限、密钥读取和删除文件。没有控制台和测试环境时改这些文件，无法证明线上行为。发现的缺陷记在 `docs/optimization-roadmap.md` 和上游已有的 `maintenance/TODO.md`。

允许的验证是阅读和本地静态检查。`scripts/repo-check.mjs` 不导入、不部署云函数。

## ADR-004 身份以平台为准，密钥不进 git

状态：已接受

`unionOp/index.js` 用 `_helper.js` 的平台身份覆盖 `ctx.args.openid`。这是 2026-09-19 那次加固之后的现行代码。新的客户端仍会把 openid 传进参数，服务端不信任它。

密钥边界：

- `miniprogram/appSecret.js` 和 `private.*.key` 必须保持未跟踪。
- `appSecret.demo.js` 只保留占位符。
- COS 与小程序 `MP_SECRET` 存在数据库集合 `app_secret`，不存在仓库。
- 静态检查拒绝私钥正文和 `AKID` 开头的 SecretId 形态。

`getTempCOS` 会把只读临时密钥返回给调用方，这是私有桶读图的现行设计。调用方是否必须登录、地图接口是否必须检查 `mapAccess`，见路线图，本次不改。

## ADR-005 上游数据与成大数据分开

状态：已接受

fork 带入了上游的 AppID、EMAS 空间、系统图片 URL、种子 JSON、Demo 地标和示例坐标。它们可以留在历史代码里，供对照实现。成大不能把它们当成自己已经授权的猫狗档案。

新文档、Issue 和 PR 不粘贴具体经纬度。替换 AppID、空间、地图中心、文案和图片，要等成大自己的资料和产品确认，不在审计提交里改 `config.js` 的业务文案。

`initDatabase/` 不要被导入成尚未确认的生产库。

## ADR-006 许可与作者归属保持 MPL-2.0

状态：已接受

根目录 `LICENSE` 是 Mozilla Public License 2.0。修改过的文件仍受该许可证约束。README 保留上游功能介绍和开发团队。本 fork 在 README 顶部增加成大毛茸茸的说明，避免把两个项目写成同一个部署。

`miniprogram/package.json` 的 `"license": "ISC"` 与仓库许可证不一致。这次没有改它，避免在没有法务确认时单独改一个包的许可证字段。以根目录 `LICENSE` 为准。

## ADR-007 复杂产品改动先写规格

状态：已接受

界面改版、品牌替换、新功能、后端迁移，先有 Issue 或 Spec（需求、设计、任务），等人确认再改。CloudBase 的 Spec 工作流可以当写法参考，不必安装它的 Skill 包。

这次审计没有新增产品功能。已做的两处代码改动都有直接证据：sitemap 指向不存在的页面；`getDate` 计算了参数又丢弃。二者都由 `scripts/repo-check.mjs` 锁住。

## 仍未决定的问题

- EMAS + COS 与 CloudBase 国内站哪一个作为成大的后端。
- 成大自己的 AppID、地图范围、品牌文案和是否保留识猫。
- `policies/*.yaml` 是否就是控制台正在执行的规则。
- 仓库外的 `catFace` 函数由谁提供，成大是否继续使用。
