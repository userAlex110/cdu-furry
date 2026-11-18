# 开发流程

这份文档做两件事：把 Issue、分支、提交、Pull Request、CI、upstream、fork 讲清楚；记下成大毛茸茸这次实际走了哪些步。下面的命令是档案，方便以后照做。现在不需要为了读文档再跑一遍。

## 六个词

**upstream（上游）** 是代码原来的仓库。这里是 `https://github.com/sysucats/zhongdamaopu`。上游继续由中大猫谱的维护者演进。成大的需求和缺陷不要开到上游，也不要请上游维护者部署成大的环境。

**fork** 是复制出来、归自己所有的仓库。这里是 `https://github.com/userAlex110/cdu-furry`。成大的 Issue、分支和 PR 都在这个仓库。fork 可以独立提交，也可以以后再决定是否把通用修复送回上游。送回上游不是这次的工作。

**Issue（议题）** 是动工前的一张说明：要解决什么、不做什么、怎样算做完。它把讨论留在仓库里，而不是留在聊天记录里。一个 PR 可以写 `Fixes #12`，合并之后 GitHub 会关掉 12 号议题。写关联不会在打开 PR 时立刻关闭议题。

**branch（分支）** 是一条独立的提交线。`master` 保持可审查的基线。工作放在 `cursor/<描述>-35f0` 这种分支上，完成后通过 PR 进入 `master`。不要把未审查的提交直接推上 `master`。

**commit（提交）** 是分支上的一个快照，附有说明。审查者靠说明理解「为什么改」。一次提交应能单独看懂。

**Pull Request（PR）** 是请别人把分支合并进 `master` 的申请。它展示相对 `master` 的全部差异，可以讨论、要求修改。本项目约定：作者不自己点合并。

**CI** 是 GitHub 在 PR 或指定分支上自动跑的检查。本仓库的检查是 `.github/workflows/repo-check.yml`，命令是 `node scripts/repo-check.mjs`。它只看文件，不登录微信，不连接 EMAS 或 COS。CI 绿灯只说明这些静态条件通过。模拟器、真机、权限和控制台规则要另标「待人工」。

## 一次标准循环

1. 在 fork 上开 Issue，用 `.github/ISSUE_TEMPLATE/` 里的模板。
2. 更新本地 `master`，从它拉出新分支。
3. 在分支上改完，运行 `node scripts/repo-check.mjs`。
4. 提交并推送该分支：`git push -u origin <分支名>`。
5. 打开指向 `userAlex110/cdu-furry` 的 `master` 的 PR，正文写上议题编号。
6. 看 CI。失败就在同一分支继续提交，PR 会自动带上新提交。
7. 审查者阅读差异。通过之后由审查者合并。合并前作者不合并。

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

计划中的两张议题没有建成。`gh issue list --repo userAlex110/cdu-furry` 返回 “the repository has disabled issues”。随后 `POST /repos/userAlex110/cdu-furry/issues` 返回 HTTP 410，`Issues has been disabled in this repository`。`gh repo edit userAlex110/cdu-furry --enable-issues` 返回 HTTP 403，当前集成令牌不能改仓库功能开关。按约定没有向上游开 Issue。

待人工：仓库管理员打开 `https://github.com/userAlex110/cdu-furry/settings`，在 General → Features 勾选 Issues。打开之后可以把下面两段原文建成议题，再在 PR 里补上 `Fixes #编号`。模板已经放进仓库，打开功能后新建议题会看到它们。

### 拟议题 A：基线审计与接手文档

标题：基线审计：写清现行 EMAS 架构，供新的 AI 和初学者接手

要完成：

- 按当前代码写技术总览、开发流程、优化路线和架构决策。
- 区分成大毛茸茸和上游中大猫谱，保留 MPL-2.0 与作者归属。
- 写明前端调用链、集合、权限、配置和隐私边界。
- 标出 Laf 已经退出、EMAS + COS 仍是现行实现、CloudBase 尚未接入。
- 不编造价格。价格调研未完成就保持待整合。

验收：新的 AI 只读 `docs/`、`AGENTS.md` 和 `CONTRIBUTING.md`，就能知道什么能改、后端在哪、哪些验证必须等人。

### 拟议题 B：非后端基础质量

标题：仓库规范与本地静态检查，并修两处有证据的前端缺陷

要完成：

- Issue 模板、PR 模板、`CONTRIBUTING.md`、`AGENTS.md`。
- 让 `docs/` 可以被 git 跟踪。
- 增加不联网的 `scripts/repo-check.mjs` 和 GitHub Actions。
- 修正 `sitemap.json` 里已经不存在的识猫路径。
- 修正 `getDate` 忽略参数的实现。现有调用都不传参，所以页面上看得到的时间不变。

明确不做：改 `functionsEMAS/`、换后端、改品牌文案、大改界面、升级依赖、绑定真实 AppID。

验收：`node scripts/repo-check.mjs` 退出码为 0；PR 差异里没有 `functionsEMAS/`。

## 审查和合并

审查者看三件事。

1. 差异是否落在议题范围内。这次的范围是文档、仓库规范和两处前端小修。
2. `git diff master...HEAD --stat -- functionsEMAS` 应为空。
3. 新文档没有上游坐标，没有真实 Secret，许可证文件还在。

合并用 GitHub 的 Merge 按钮，由审查者操作。不要在本地把功能分支合并进 `master` 再强推。

CI 配置在 `.github/workflows/repo-check.yml`。它在 Pull Request 上跑，也在 `cursor/**` 分支的 push 上跑。`master` 的直接 push 不在触发列表里，因为正常代码从 PR 进来。

## 本轮验证

在工作区执行：

```bash
node scripts/repo-check.mjs
git diff --stat -- functionsEMAS
```

`repo-check` 退出码 0。它打印两条警告：根目录 AppID 仍是上游小程序；`config.js` 仍有上游 EMAS 空间和校园地图中心。警告按设计不导致失败。脚本报告已注册页面 53 个。`functionsEMAS` 的 diff 为空。

没有运行 `npm run build:npm`、`npm run preview`、微信开发者工具、ESLint，也没有运行 `wb_code/` 里的云函数桩测试。

提交 `85f4ff3` 推上 `cursor/baseline-docs-repo-checks-35f0` 之后，GitHub Actions 的 `repo-check` 两次都成功：push 运行 `44229332571`，pull_request 运行 `44229355453`。以后的新提交以新的 Actions 记录为准。

## 和上游同步时

以后若要把上游新提交接进来，使用 fetch 后的合并或 rebase，并在 PR 里说明。同步时保留本 fork 的 `docs/`、`AGENTS.md`、`CONTRIBUTING.md` 和 `.github/`。上游 `maintenance/TODO.md` 仍是他们的待办，成大的路线放在 `docs/optimization-roadmap.md`。

通用且上游也需要的修复，可以另开讨论再决定是否向上游提 PR。那是一次新的授权，不是这次审计的一部分。
