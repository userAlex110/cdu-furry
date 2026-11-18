# 架构决策

日期：2026-11-18。状态里的「已接受」表示本 fork 现在按此执行。「待定」表示还不能写代码实现。

## ADR-001 现行实现保持 EMAS + COS

状态：已接受（描述现状，不是最终选型）

`miniprogram/app.js` 初始化 `@alicloud/mpserverless-sdk`，空间地址是 `https://api.next.bspapp.com`。照片在 `use_private_tencent_cos === true` 时走腾讯云：上传用 `getURL` 的 S3 兼容签名，读取用 `getTempCOS` 的 STS，策略只有 `cos:GetObject`。

Laf 不是现行后端。仓库里已经没有 Laf 云函数目录。`pages/debug/debug.js` 的 `wx.cloud.callFunction` 是旧调试入口，对应函数不在 `functionsEMAS/`。

后果：接手人按 EMAS 集合、`unionOp` 动作和 COS 字段理解系统。不要把调试页的 `wx.cloud` 当成主链路。

## ADR-002 后端选型待定，本阶段不改写成 CloudBase

状态：待定

候选包括继续使用 EMAS + COS，以及改用 CloudBase 国内站。主协调在单独做价格对照。结果还没写回仓库。上游 README 里有一句历史费用描述，本文件不把它当成现行报价，也不写任何新的价格数字。

在决定写进新的 ADR 之前：

- 不新增 CloudBase 环境、数据库、存储或云函数。
- 不把 `functionsEMAS/` 重写成 CloudBase。
- 不把前端数据库调用改成 `wx.cloud`。
- 不安装 CloudBase 插件，不执行登录或 `tcb` 创建环境。

2026-11-18 读过的官方材料：

- `https://docs.cloudbase.net/skill.md` 要求先分清国内站和国际站，再安装插件、登录并创建环境。国内站有免费体验环境的说明。这些步骤会创建资源，本项目没有授权执行。
- 微信小程序开发 Skill 要求按 `project.config.json` 管理小程序，并写明：没有证据时不要假设项目使用 CloudBase。调试、预览和发布依赖微信开发者工具；外部 Agent 还需要工具导出的 Skill 和管理员授权。这些条件这次都不具备。
- Spec 工作流把新功能拆成需求、设计、任务，确认后才实现。后端替换属于这种大功能，不能在审计 PR 里顺手做。

CloudBase 开发助手或 MCP 能被列出来，只表示代理可以读文档。它不等于数据库或存储已经接上。

下次决定选型时要写新的 ADR，至少包括：数据模型怎么迁、权限规则谁执行、文件桶谁保存、密钥放哪、以及价格调研的出处。没有出处就不写金额。

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
