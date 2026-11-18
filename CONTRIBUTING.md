# 参与成大毛茸茸

这个 fork 用来学习一条完整的协作链：Issue、分支、实现、测试、Pull Request、审查、合并。合并由审查者来做，提交代码的人不要合并自己的 PR。

概念和本仓库这次实际走过的步骤写在 `docs/development-workflow.md`。架构边界写在 `docs/architecture-decisions.md`。给 AI 的限制写在 `AGENTS.md`。

## 开始之前

- 目标仓库是 `userAlex110/cdu-furry`。上游是 `sysucats/zhongdamaopu`。成大的议题和 PR 都留在 fork。
- 许可是 MPL-2.0。保留根目录 `LICENSE` 和上游作者说明。
- 后端目录 `functionsEMAS/` 目前只读。发现缺陷就记下来。不要按上游手册新建 EMAS 空间：2026-11-01 起已停止新购，存量停服日是 2027-09-30。COS 不在该公告里，本阶段也不创建桶。
- 不要提交 `miniprogram/appSecret.js`、`private.*.key`，不要把真实密钥写进 `appSecret.demo.js`。
- 新文档使用 ASCII 路径，正文用中文。不要转载上游校园的具体坐标。

## 建议顺序

1. 在本 fork 开 Issue，写清要做什么、不做什么、怎样验收。入口是 https://github.com/userAlex110/cdu-furry/issues 。
2. 从最新的 `master` 拉分支。分支只包含这一件工作。
3. 在分支上改代码并提交。提交说明写给人看，说明改了什么、为什么。
4. 运行 `node scripts/repo-check.mjs`。它不访问云端，通过也不表示真机已经可用。
5. 推送分支，打开指向 `master` 的 Pull Request，并在正文写上 Issue 编号。
6. 等审查。由用户决定是否合并。作者不点 Merge。合并只把提交带进 `master`，不表示部署、提审或开通云资源。

2026-11-18 的第一份工作是例外：当时 Issues 关闭，分支和 PR 先出现。用户打开 Issues 之后，自动化身份创建补录议题被拒绝（HTTP 403）。细节在 `docs/development-workflow.md`。不要为了补这个权限去改仓库设置。

## 本地检查

```bash
node scripts/repo-check.mjs
```

等价的 npm 脚本是 `npm run check`。它不需要安装依赖。

`npm run build:npm` 和 `npm run preview` 会调用微信的 `miniprogram-ci`。预览还需要上传密钥。这两条命令会接触微信的编译服务，不属于本仓库的默认检查。

## 审查时多看一眼

- PR 是否只含约定范围内的改动。
- `functionsEMAS/` 是否被动过。
- 是否出现新的密钥、真实 AppID 绑定，或上游坐标。
- 文档是否把上游项目和成大毛茸茸分开写。
- 不能在本地验证的部分有没有标明待人工。

上游原有的审查清单仍在 `maintenance/PR_REVIEW_CHECKLIST.md`，那是中大猫谱的维护习惯。两边冲突时，以本文件和 `AGENTS.md` 为准。
