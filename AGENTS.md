# 给 AI 的工作边界（成大毛茸茸）

本文件只约束这个 fork。CloudBase 官方 Skill 留在站外作参考，不要把上游或 CloudBase 的整包 Skill 复制进仓库。

## 项目是什么

成大毛茸茸是校园猫狗微信小程序。代码 fork 自 `sysucats/zhongdamaopu`（中大猫谱 / 笃行猫谱），许可 MPL-2.0。现行代码按阿里云 EMAS Serverless 编写，照片走腾讯云 COS。2026-11-01 起 EMAS Serverless 不能新建空间，2027-09-30 存量停服。不要按上游部署手册为成大开通 EMAS。COS 不在该公告范围内。函数计算 FC 不是这套 BaaS 的替代。CloudBase 仍是未选定的候选，代码没有接入。

先读：

- `docs/technical-overview.md`
- `docs/architecture-decisions.md`
- `docs/backend-cost-research.md`
- `docs/development-workflow.md`
- `docs/optimization-roadmap.md`

## 允许

- 读 `functionsEMAS/`，把风险写进文档或 Issue。
- 改文档、Issue/PR 模板、`CONTRIBUTING.md`、本文件、以及不触达云端的静态检查。
- 在有调用点证据时，修前端里边界清楚、可用本地检查验证的缺陷。
- 用独立分支和 Pull Request。PR 的目标仓库是 `userAlex110/cdu-furry`。新工作先在本 fork 写 Issue 和验收，再改代码。2026-11-18 的第一份 PR 是先有分支、后补记录的例外，见 `docs/development-workflow.md`。

## 禁止

- 修改 `functionsEMAS/` 下的后端代码，包括顺手格式化。
- 把项目改写成 CloudBase，或新增 `wx.cloud` 正式调用。
- 创建或绑定云环境，购买资源，部署，上传代码，提交微信审核。
- 写入真实 AppID、`appSecret.js`、`private.*.key`、数据库密钥或 COS 密钥。
- 把上游猫狗档案当作成大已经授权的数据，或在新文档、Issue、PR 里粘贴具体坐标。
- 联系上游维护者，或向上游仓库开 Issue / PR。
- 把活动价、试用额度或上游「约 5 元」写成永久价格或已成交账单。引用金额时指向 `docs/backend-cost-research.md`，并保留原文的价格标签。
- 合并 Pull Request。合并要等人审查。
- 创建或绑定 CloudBase、EMAS、COS、CDN 资源。国内开发助手即使已经认证，也没有得到创建环境的授权。不要执行 Skill 里的部署步骤。

## 官方材料怎么用

2026-11-18 读过：

- `https://docs.cloudbase.net/skill.md`：区分国内站和国际站，并引导安装插件、登录、创建环境。本项目两项都还没选定，这些步骤不要执行。
- 微信小程序开发 Skill：页面和 `project.config.json` 按小程序习惯处理；没有明确决定时，不要假设项目使用 CloudBase。
- Spec 工作流：复杂新功能先写需求、设计、任务，等人确认再写代码。本轮是审计和基础规范，没有走产品改造。

CloudBase 国内开发助手可以已经认证。认证只覆盖工具层。仓库里没有环境 ID，也没有 `wx.cloud` 正式初始化。不要用认证状态去创建或绑定环境。

## 验证

改完运行 `node scripts/repo-check.mjs`。需要微信开发者工具、真实 AppID 或管理员扫码才能看的结果，写成待人工，不要写成已通过。
