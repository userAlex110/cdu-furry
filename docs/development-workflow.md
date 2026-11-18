# 开发流程

这份文档做两件事：把 Issue、分支、提交、Pull Request、CI、upstream、fork 讲清楚；记下成大毛茸茸这次实际走了哪些步。下面的命令是档案，方便以后照做。现在不需要为了读文档再跑一遍。

上游 README 和旧部署手册里的「开通 EMAS、新建服务空间」不能当作本仓库的下一步。阿里云已于 2026-11-01 停止这项新购，存量停服日是 2027-09-30。腾讯云 COS 不受那份公告影响，但本阶段也不创建桶。函数计算 FC 不能代替整套 EMAS。CloudBase 助手即使已经认证，也还没有环境，不要顺着认证去创建。价格怎么读见 `docs/backend-cost-research.md`。

## 六个词

**upstream（上游）** 是代码原来的仓库。这里是 `https://github.com/sysucats/zhongdamaopu`。上游继续由中大猫谱的维护者演进。成大的需求和缺陷不要开到上游，也不要请上游维护者部署成大的环境。

**fork** 是复制出来、归自己所有的仓库。这里是 `https://github.com/userAlex110/cdu-furry`。成大的 Issue、分支和 PR 都在这个仓库。fork 可以独立提交，也可以以后再决定是否把通用修复送回上游。送回上游不是这次的工作。

**Issue（议题）** 是动工前的一张说明：要解决什么、不做什么、怎样算做完。它把讨论留在仓库里，而不是留在聊天记录里。一个 PR 可以写 `Fixes #12`，合并之后 GitHub 会关掉 12 号议题。写关联不会在打开 PR 时立刻关闭议题。

**branch（分支）** 是一条独立的提交线。`master` 保持可审查的基线。工作放在 `cursor/<描述>-35f0` 这种分支上，完成后通过 PR 进入 `master`。不要把未审查的提交直接推上 `master`。

**commit（提交）** 是分支上的一个快照，附有说明。审查者靠说明理解「为什么改」。一次提交应能单独看懂。

**Pull Request（PR）** 是请别人把分支合并进 `master` 的申请。它展示相对 `master` 的全部差异，可以讨论、要求修改。本项目约定：作者不自己点合并。

**CI** 是 GitHub 在 PR 或指定分支上自动跑的检查。本仓库的检查是 `.github/workflows/repo-check.yml`，命令是 `node scripts/repo-check.mjs`。它只看文件，不登录微信，不连接 EMAS 或 COS。CI 绿灯只说明这些静态条件通过。模拟器、真机、权限和控制台规则要另标「待人工」。

## 一次标准循环

今后按这个顺序。2026-11-18 的第一份 PR 是例外，原因写在下一节。

1. 在本 fork 开 Issue：https://github.com/userAlex110/cdu-furry/issues 。用 `.github/ISSUE_TEMPLATE/` 。写清目标、不做的事和验收条件。成大的需求不要开到上游。
2. 更新本地 `master`，从它拉出新分支。
3. 在分支上改完，运行 `node scripts/repo-check.mjs`。
4. 提交并推送该分支：`git push -u origin <分支名>`。
5. 打开指向 `userAlex110/cdu-furry` 的 `master` 的 PR，正文写上议题编号。
6. 看 CI。失败就在同一分支继续提交，PR 会自动带上新提交。`repo-check` 通过只说明仓库文件符合静态规则，不说明微信开发者工具或真机已经通过。
7. 等审查。由用户决定是否合并。作者不自己点合并。合并只表示提交进入 `master`，不表示已经部署、提审或开通云资源。

```bash
git checkout master
git pull origin master
git checkout -b cursor/short-name-35f0
node scripts/repo-check.mjs
git push -u origin cursor/short-name-35f0
```

`master` 上的直接推送不在这个循环里。

## 这次实际发生的事

基线是 fork 的 `master`，提交 `7ba22e5e947acba14732d97cab699e417f187f7f`，2026-11-14。用 GitHub API 看过上游 `sysucats/zhongdamaopu` 的 `master`，SHA 相同，所以这是一次还没有分叉提交的 fork。

工作分支是 `cursor/baseline-docs-repo-checks-35f0`。没有把提交推到 `master`。

当时本 fork 的 Issues 是关闭的。`gh issue list --repo userAlex110/cdu-furry` 显示仓库禁用了 Issues。`POST /repos/userAlex110/cdu-furry/issues` 返回 HTTP 410，`Issues has been disabled in this repository`。改仓库功能开关返回 HTTP 403。没有向上游开 Issue，也没有改仓库权限。

用户稍后在同一天打开了 Issues。再次核对：`hasIssuesEnabled` 为 true，`gh issue list --state all` 为空。仓库里当时唯一的编号是 PR #1，它不是一条独立议题。

补录一条综合议题时，当前集成身份 `cursor` 调用创建接口返回 HTTP 403，`Resource not accessible by integration`。GraphQL 的 `createIssue` 同样拒绝。因此没有议题 URL，不能把 PR 写成 `Fixes #编号`。下面这段就是本来要写入那条议题的全文，避免再拆成多条。

### 未能建成的综合议题正文

标题：事后补录：基线文档、成本调研与仓库静态检查

目标：让后来的人能从文档读懂现行代码、协作方式和后端约束，并有一条不联网的静态检查。写清 EMAS 停服和公开价格，不开始迁移。

范围里已经做的：四份接手文档、`docs/backend-cost-research.md`、`docs/backend-cost-sources.md`、`CONTRIBUTING.md`、`AGENTS.md`、Issue/PR 模板、`scripts/repo-check.mjs`，以及 sitemap 识猫路径和 `getDate` 入参这两处小修。

范围里不做的：不改 `functionsEMAS/`，不迁移，不创建云环境，不部署，不购买，不绑定真实 AppID，不向上游发议题，不由作者合并。

验收：文档区分成大与上游并保留 MPL-2.0；写明 2026-11-01 停止新购、2027-09-30 停服，COS 不受影响，FC 不是整套替代；`node scripts/repo-check.mjs` 退出码为 0；PR 没有后端差异；本文写明自己是事后补录。用户是否合并由用户决定，不算作者已完成的验收。

测试证据：提交 `2b26bad` 上本地检查通过；`functionsEMAS/` 差异为空；CI 成功，push 运行 `44229867103`，pull_request 运行 `44229873725`。PR https://github.com/userAlex110/cdu-furry/pull/1 在补录时为 open，且未合并。

未验证和待定：微信开发者工具、真机、真实 AppID、管理员扫码、控制台权限、资源包成交价、后端选型。假设月费不是账单。免费档和 19.9 元/月不是永久价格。

## 审查和合并

审查者看三件事。

1. 差异是否落在议题范围内。这次的范围是文档、仓库规范和两处前端小修。
2. `git diff master...HEAD --stat -- functionsEMAS` 应为空。
3. 新文档没有上游坐标，没有真实 Secret，许可证文件还在。

合并用 GitHub 的 Merge 按钮，由用户决定。作者不自己合并，也不要在本地把功能分支合并进 `master` 再强推。合并进入 `master` 不等于部署、提审或开通云资源。CI 绿灯不等于微信真机已经通过。

CI 配置在 `.github/workflows/repo-check.yml`。它在 Pull Request 上跑，也在 `cursor/**` 分支的 push 上跑。`master` 的直接 push 不在触发列表里，因为正常代码从 PR 进来。

## 本轮验证

在工作区执行：

```bash
node scripts/repo-check.mjs
git diff --stat -- functionsEMAS
```

`repo-check` 退出码 0。它打印两条警告：根目录 AppID 仍是上游小程序；`config.js` 仍有上游 EMAS 空间和校园地图中心。警告按设计不导致失败。脚本报告已注册页面 53 个。`functionsEMAS` 的 diff 为空。

没有运行 `npm run build:npm`、`npm run preview`、微信开发者工具、ESLint，也没有运行 `wb_code/` 里的云函数桩测试。

提交 `85f4ff3` 的 GitHub Actions `repo-check` 成功：push 运行 `44229332571`，pull_request 运行 `44229355453`。提交 `2b26bad` 同样成功：push 运行 `44229867103`，pull_request 运行 `44229873725`。以后的新提交以新的 Actions 记录为准。静态检查通过不等于微信真机通过。

## 和上游同步时

以后若要把上游新提交接进来，使用 fetch 后的合并或 rebase，并在 PR 里说明。同步时保留本 fork 的 `docs/`、`AGENTS.md`、`CONTRIBUTING.md` 和 `.github/`。上游 `maintenance/TODO.md` 仍是他们的待办，成大的路线放在 `docs/optimization-roadmap.md`。

通用且上游也需要的修复，可以另开讨论再决定是否向上游提 PR。那是一次新的授权，不是这次审计的一部分。
