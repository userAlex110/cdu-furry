# 技术总览

这份文档给下一任开发者和下一任 AI 接手用。结论都来自 2026-11-18 对 `userAlex110/cdu-furry` 工作区的直接阅读，基线提交是 `7ba22e5`（与上游 `sysucats/zhongdamaopu` 的 `master` 相同）。下文描述的是仓库里的现行代码。后端选型还没定。

**新环境不要按上游手册去开通 EMAS。** 阿里云 2026-10-26 的公告写明：2026-11-01 起 EMAS Serverless 停止新购和新空间，存量服务到 2027-09-30 停服。成大没有自己的存量空间。腾讯云 COS 不受这份公告影响。函数计算 FC 也不是这套数据库加登录的替代。部署手册、README 里的开通段落和 `pages/debug/deployTip` 只能当历史说明。价格和代码迁移量见 `docs/backend-cost-research.md`。

## 仓库身份

| 项 | 值 |
| --- | --- |
| 本项目 | 成大毛茸茸，校园猫狗微信小程序 |
| 本仓库 | `https://github.com/userAlex110/cdu-furry` |
| 上游 | `https://github.com/sysucats/zhongdamaopu`（中大猫谱 / 笃行猫谱） |
| 默认分支 | `master` |
| 许可 | MPL-2.0，正文在根目录 `LICENSE` |
| 版本号 | `miniprogram/config.js` 的 `app_version` 为 `v1.20.4` |

上游 README、开发团队名单和 `maintenance/` 里的清单属于中大猫谱的历史。成大的约定在 `CONTRIBUTING.md`、`AGENTS.md` 和本目录。

上游的猫狗档案、地图点位、AppID、EMAS 空间和对象存储不是成大已经授权的数据。本文只写字段名和文件路径，不抄坐标，也不抄空间 ID。

## 目录

| 路径 | 角色 |
| --- | --- |
| `miniprogram/` | 微信小程序前端。根目录 `project.config.json` 的 `miniprogramRoot` 指向这里 |
| `functionsEMAS/` | 现行后端。`unionOp` 是客户端调用入口，`timeTrigger` 是定时任务，`temp/` 是一次性脚本 |
| `policies/` | 两份数据库权限 YAML。仓库里没有加载它们的代码，是否已经配到控制台要人工核对 |
| `initDatabase/`、`initStorage/` | 上游种子数据和系统图片。不要当成成大的正式档案导入 |
| `wb_code/` | 已跟踪的本地脚本（构建 npm、预览、几份云函数桩测试）。`.gitignore` 忽略该目录的新文件，所以新脚本不要放这里 |
| `maintenance/` | 上游的审查清单、发版笔记、待办。里面的后端问题这次只引用，不修改代码 |
| `readme/` | 上游 README 用的校园小程序二维码图片 |
| `scripts/repo-check.mjs` | 本 fork 新增的本地静态检查 |
| `docs/` | 本 fork 的接手文档。成本见 `backend-cost-research.md`，出处见 `backend-cost-sources.md` |

`miniprogram/app.json` 注册了 53 个页面，页面四件套（js/json/wxml/wxss）都在。页面脚本一共 59 个，多出来的是被页面引用的辅助脚本，例如 `lock.js`、`desc.js`。

## 现行运行时

现行链路是：微信小程序 → 阿里云 EMAS Serverless（`@alicloud/mpserverless-sdk`）→ 文档数据库；图片上传和读取走腾讯云 COS。

Laf 已经退出运行路径。`git log` 里有 `62401b0 chore: 清除 Laf 托管遗留`，仓库中没有 `functionsLaf/` 或 Laf 云函数目录。还留着的字样是历史说明：根 README 提到 Laf 不再维护、`devTeam.js` 的更新日志、`info.js` 里一条旧文档提示。`pages/debug/debug.js` 仍调用 `wx.cloud.callFunction`（`deleteRawPhoto`、`imProcess`）。这是调试页上的旧接口，这两个函数不在 `functionsEMAS/` 里，主流程不走它。

CloudBase 没有接入。前端初始化的是 EMAS SDK，不是 `wx.cloud.init`。国内开发助手可以已经认证，仓库里仍然没有 CloudBase 环境。官方 Skill 只作参考，见 `docs/architecture-decisions.md`。

这套 EMAS 代码解释的是「现在程序怎么写的」。它不能被部署成成大的新空间：2026-11-01 之后官方已停止新建服务空间。COS 的上传和读取代码可以继续阅读，公告没有下线 COS。真正要换后端时要改的调用面，写在成本文档里，不在这一轮动手。

有两个云函数名会被客户端调用：

- `unionOp`：`functionsEMAS/unionOp/index.js`，用参数 `unionAction` 分发。
- `catFace`：`miniprogram/utils/cloudApi.js` 的 `catFace()` 会 `invoke('catFace')`。源码不在本仓库。识猫页依赖它，也依赖数据库设置里的 `secretKey`。

`timeTrigger` 设计成 EMAS 定时触发，大约 5 分钟一次。客户端业务页面不直接调用它。

## 前端怎么启动

`miniprogram/app.js` 用 `config.js` 里的 `app_id`、`space_id`、`space_secret`、`space_endpoint` 创建 `MPServerless`。`space_secret` 来自被 git 忽略的 `miniprogram/appSecret.js`；文件不存在时 secret 为空字符串。`appSecret.demo.js` 只放占位符 `ABCDABCDABCDABCD==`。

SDK 加载或 `init()` 失败时进入离线 Demo：`utils/demo.js` 提供假数据和假的数据库接口。没有安装 npm 包、没有 secret、或空间连不上，都会落到这条路径。Demo 里的校区名、地标和示例坐标来自上游校园，只能当界面样品，不能当作成大的档案，也不能抄进公开材料。

非 Demo 启动时调用 `utils/common.js` 的 `ensureCos()`，向 `unionOp` / `getTempCOS` 要只读临时密钥，再交给 `miniprogram/packages/tencentcloud/cos.js`。

`config.js` 里 `use_private_tencent_cos` 为 `true`。上传因此不走 EMAS 文件服务，而走 `getURL`：服务端用 MinIO SDK 按 `app_secret` 里的 `OSS_*` 字段签发 POST 策略，客户端再 `wx.uploadFile`。同一组字段在压缩任务里被腾讯云 COS SDK 当作 SecretId/SecretKey。也就是说，现行存储是 COS，上传签名走 S3 兼容接口，读取签名走腾讯云 STS。`OSS_` 前缀是旧命名，不代表现在还在用独立的 MinIO 集群。这个判断来自代码调用的 SDK，没有连上真实桶核对。

## 功能清单

底栏在 `miniprogram/custom-tab-bar/tab.js`，由 `setting.tabBarCtrl` 控制完整版或精简版。

| 底栏 | 页面 | 用户能做什么 |
| --- | --- | --- |
| 猫谱 | `pages/genealogy/genealogy` | 按校区、花色、领养状态浏览猫，搜索名字或编号 |
| 喵友圈 | `pages/followFeed/followFeed` | 看关注的猫的新照片和新便利贴 |
| 猫抓板 | `pages/news/news` | 看公告和科普 |
| 榜单 | `pages/leaderboard/leaderboard` | 拍照榜、徽章榜、成就榜 |
| 关于 | `pages/info/info` | 统计、反馈、个人资料、管理入口 |
| 喵地图 | `pages/map/map` | 看已批准用户可见的猫位置。页面入口会先检查 `mapAccess` |

主要分包：

- 猫详情、相册、评分、关系图、徽章详情、便利贴、反馈、上传照片、地图权限申请。
- 识猫和徽章：`pages/packageA`。
- 管理：照片审核、评论审核、反馈回复、猫档案、医疗和疫苗、领养审核、公告、管理员、页面设置、徽章定义、成就编辑、图片处理。
- 领养申请、个人成就、足迹、关注、我的反馈、我的领养。
- `pages/debug`：部署自检和旧调试按钮。
- `pages/tools`：邀请特邀用户、调整用户角色。

组件包括猫信息、便利贴、足迹、海报、弹层、徽章 3D、医疗记录、关系、搜猫。`maintenance/TODO.md` 记录弹层有多套实现，这次没有合并。

管理等级写在 `pages/manage/managers/managers.js`：0 非管理员，1 审核照片和便利贴，2 改猫、校区、关系、徽章，3 发公告，99 超级管理（成员、页面设置、图片处理）。特邀用户是 `user.role == 1`，用来放宽 `setting.accessCtrl` 里的功能开关。第一个注册用户在 `userOp` 的 `get` 分支被写成 `manager: 99`。

## 调用链

读数据有两条路，写数据主要走云函数。

1. 页面直接调用 `app.mpServerless.db.collection(...).find/count`。猫列表、详情、照片、评论、公告、设置都有这种读法。能不能读到，取决于 EMAS 控制台里该集合的规则，不取决于 `curdOp.js`。
2. 页面调用 `utils/cloudApi.js`，或直接 `function.invoke('unionOp', { unionAction })`。`unionOp/index.js` 用平台身份覆盖客户端传来的 `openid`，再交给具体 handler。

上传照片的主链：

1. `pages/genealogy/addPhoto/addPhoto.js` 选图、选位置。
2. `common.js` `uploadFile()` → `unionOp` `getURL` → 客户端把文件 POST 到桶。
3. `curdOp` `add` / `photo` 写入 `photo`。服务端把 `verified` 设为 false，并只留下白名单字段（猫 id、文件、拍摄者、拍摄日期、经纬度）。
4. 管理员在审核页通过 `managePhoto` 改 `verified`。
5. `timeTrigger` 里的 `photoProcess` 给已审核照片做压缩图和水印。`countPhoto` 回写猫的照片计数。

识猫：

1. 识猫页从全局设置读取 `secretKey`（设置集合对登录用户可读，密钥会下发到客户端）。
2. 用 `hex_sha256(照片 base64 + 时间戳 + secretKey)` 做签名。
3. `api.catFace()` 调用仓库外的 `catFace` 云函数。超时被临时调到 30 秒。

喵地图：

1. `map.js` 先跑 `checkCanUseMap()`。非 Demo 时要求 `user.mapAccess.status === 'approved'`。
2. 通过后调用 `unionOp` / `getCatLocations`。该函数只检查登录，不再检查地图权限。
3. 校区中心来自 `setting` 的 `campusCenters`。`setting` 在 `policies/miniprogram.yaml` 里对登录用户可读。因此地图开关目前是页面层的。服务端和设置集合没有同一道门。这是待修风险，这次不改后端。

身份：

1. 客户端 `user.getInfo({ authProvider: 'wechat_openapi' })`，openid 在 `oAuthUserId`。
2. `functionsEMAS/unionOp/_helper.js` 的 `getCallerOpenid` 再向平台要一次。失败就当未登录。
3. 客户端如果传入另一个 openid，`index.js` 会记一条 `[SECURITY] identity mismatch`，然后用平台身份覆盖。

`index.js` 拒绝客户端直接调用 `getAccessToken`、`deleteFiles`、`deleteCosFiles`。它们只能被别的 handler `require`。

## unionOp 动作

| unionAction | 文件 | 作用 |
| --- | --- | --- |
| `curdOp` | `curdOp.js` | 按管理员等级做增删改，以及少数读 |
| `userOp` | `userOp.js` | 获取或创建用户、改自己的资料、99 级改角色 |
| `updateCat` | `updateCat.js` | 新建或更新猫。编号生成不是原子操作 |
| `managePhoto` | `managePhoto.js` | 审核、移动、删除照片 |
| `commentCheck` | `commentCheck.js` | 用小程序 access_token 调微信内容安全接口 |
| `sendMsgV2` | `sendMsgV2.js` | 订阅消息 |
| `getMpCode` | `getMpCode.js` | 生成猫的小程序码 |
| `getAllSci` | `getAllSci.js` | 科普列表 |
| `getBadge` / `giveBadge` / `genBadgeCode` | 对应文件 | 猫徽章、发放、兑换码 |
| `updateCatRating` / `getCatStats` / `getUserStats` | 对应文件 | 评分和统计 |
| `updateFollowCats` | `updateFollowCats.js` | 关注或取消关注 |
| `vaccineOp` / `initVaccineTypes` / `medicalOp` | 对应文件 | 疫苗和医疗记录 |
| `adoptionOp` | `adoptionOp.js` | 领养申请和审核 |
| `catRelationOp` / `manageRelationRules` | 对应文件 | 猫之间的关系和规则 |
| `getCatLocations` / `getCatTrajectory` | 对应文件 | 地图点和轨迹 |
| `getURL` / `getTempCOS` | 对应文件 | 上传签名、只读临时密钥 |
| `isManager` | `isManager.js` | 查询 `user.manager` 是否达到等级 |
| `achievement` / `manageAchievementCatalog` / `getAchievementRank` | 对应文件 | 用户成就，和猫徽章不是同一套数据 |
| `getAccessToken` / `deleteFiles` / `deleteCosFiles` | 对应文件 | 仅服务端内部 |

`timeTrigger` 每次并行跑 `countPhoto`、`getTempCOS`、`photoProcess`。北京时间当天第一次再跑 `getBadgeRank` 和 `getPhotoRank`，用 `setting.rankDailyGate` 防重复。部署自检参数 `deploy_test: true` 时期望返回字符串 `v1.6`。

## 数据集合

代码里出现的集合：

`achievement`、`achievement_def`、`achievement_material`、`adoption`、`app_secret`、`badge`、`badge_code`、`badge_def`、`badge_rank`、`cat`、`comment`、`feedback`、`inter`、`medical`、`news`、`photo`、`photo_rank`、`rating`、`reward`、`science`、`setting`、`user`、`vaccine`。

`policies/miniprogram.yaml` 覆盖了其中大部分，规则大体是：登录用户可读，客户端不可直接写；`feedback` 和 `rating` 允许本人新增。`badge_code` 客户端不可读。`policies/catface.yaml` 只放开 `photo` 的读和计数，像是识猫函数使用的另一套规则。

YAML 没有写到、但代码在用的集合：`adoption`、`app_secret`、`medical`、`vaccine`。仓库不能证明控制台的默认规则是拒绝。`app_secret` 里放着 COS 密钥、小程序 AppSecret、access_token 缓存和导入口令。上线前必须在控制台确认客户端读不到它。这次只记录。

`curdOp.js` 另有一套等级表。等级 0 表示登录用户可做；1、2、3、99 表示 `user.manager` 要达到该数。表里没有的集合会返回 `unk req.`。这套表只在请求走进 `curdOp` 时生效。页面直接 `db.collection().find()` 不经过它。

`app_secret` 字段名（值只应存在数据库里）：`OSS_ENDPOINT`、`OSS_PORT`、`OSS_BUCKET`、`OSS_SECRET_ID`、`OSS_SECRET_KEY`、`MP_APPID`、`MP_SECRET`、`IMPORT_KEY`（仅临时迁移脚本）、`cache.tempCOSToken`、`cache.accessToken`。

`getTempCOS` 向腾讯云申请的 STS 策略只允许 `cos:GetObject`，时长 7200 秒，数据库缓存按 3600 秒判断。定时触发带 `triggerName` 时会跳过缓存。这是 `maintenance/TODO.md` 已记录的费用浪费，后端未改。

## 配置与隐私

| 位置 | 内容 | 接手时要怎么看 |
| --- | --- | --- |
| `miniprogram/config.js` `app_id` | 上游小程序 AppID `wx5bd705b2bc91c73b` | 成大预览或上传前换成自己的。现在不要用它做上传 |
| 根 `project.config.json` `appid` | 同一个上游 AppID | `wb_code/preview.mjs` 读的是这一份 |
| `miniprogram/project.config.json` `appid` | 另一个 AppID `wxda17b675d1cf6f46`，基础库 `3.10.1` | 与根配置不一致。开发者工具以根配置为准 |
| 根 `project.config.json` `libVersion` | `2.24.7` | 与内层基础库不一致 |
| `space_id`、`space_endpoint` | 上游 EMAS 空间和 `https://api.next.bspapp.com` | 接成大自己的空间前不要拿它做真实写入 |
| `space_secret` | 本地 `appSecret.js`，仓库只有 demo 占位 | 不要提交 |
| `map_center`、`demo.js` 坐标、`setting` 里的校区中心 | 上游校园方位 | 文档和讨论里不写数字。成大地图要换自己的中心 |
| `science_imgs` 等 URL | 上游 COS 桶上的系统图 | 成大要换自己的图片地址 |
| `text` | 仍是「笃行猫谱」和上游社团文案 | 改名、改联系方式需要产品确认，这次没改界面文案 |
| `initDatabase/setting.json` | 5 条设置：`pages`、`filter`、`friendLink`、`subscribeMsg`、`relation` | 识猫 `secretKey` 在种子数据里是 `changeToYourKey` |
| `initDatabase/science.json` | 11 行科普种子 | 上游内容 |
| 编译条件 | 根 `project.config.json` 的 condition 带有上游猫档案 id | 不要当成成大数据 |
| `requiredPrivateInfos` | `getFuzzyLocation`、`chooseLocation` | 隐私协议已打开：`__usePrivacyCheck__: true` |
| `embeddedAppIdList` | 两个外部小程序 id | 是否保留等产品确认 |

隐私边界：照片可以带经纬度；地图函数会把每只猫最新坐标返回给任何已登录调用者；设置集合若按 YAML 对登录用户可读，校区中心也会被读到。页面上的「申请通过才能看地图」没有在 `getCatLocations` 里再验一次。成大在公开任何地图之前，要先定权限，并避免把真实点位写进仓库。

## 构建、预览和测试

当前能在本地做的：

```bash
node scripts/repo-check.mjs
```

它检查页面是否齐全、sitemap 是否指向真实页面、`getDate` 是否尊重传入时间、密钥文件是否被跟踪、MPL 许可证是否还在。它不联网。

仓库里还有这些入口，这次没有执行：

| 命令或方式 | 实际做什么 | 这次为什么没跑 |
| --- | --- | --- |
| 微信开发者工具打开仓库根目录 | 编译并模拟器预览 | 需要开发者工具、登录，以及可用的 AppID |
| `npm run build:npm` | `miniprogram-ci` 构建小程序 npm | 会拉依赖并调用微信工具链，不是这轮的检查 |
| `npm run preview` | 用上传密钥做 CI 预览并生成二维码 | 需要真实 AppID 和私钥，属于上传 |
| `miniprogram` 的 `npm test` | 固定打印错误并退出 1 | 上游留的占位，没有测试用例 |
| `miniprogram/.eslintrc.js` | airbnb-base | 现有代码大量不符合。把它设成失败门禁会变成无关的大改 |
| `wb_code/testPhotoProcess.cjs` 等 | 云函数桩测试 | 测的是后端行为；这轮不改后端，也没把它们接进新检查 |

`wb_code/` 被 `.gitignore` 忽略，已跟踪的 7 个脚本仍然在。新的检查放在 `scripts/`，避免被忽略。

## 本轮读过的关键文件

前端：`app.js`、`app.json`、`sitemap.json`、`config.js`、`appSecret.demo.js`、`project.config.json`（根和 miniprogram）、`utils/cloudApi.js`、`utils/user.js`、`utils/common.js`、`utils/demo.js`、`custom-tab-bar/tab.js`、`pages/map/map.js`、`pages/packageA/pages/recognize/recognize.js`、`pages/debug/debug.js`、`pages/manage/managers/managers.js`。

后端（只读）：`functionsEMAS/unionOp/index.js`、`_helper.js`、`curdOp.js`、`isManager.js`、`userOp.js`、`getTempCOS.js`、`getURL.js`、`getCatLocations.js`、`commentCheck.js`、`timeTrigger/index.js`，以及两个 `package.json`。集合名用脚本从 `collection('...')` 调用里汇总。

其他：`README.md`、`LICENSE`、`.gitignore`、`package.json`、`policies/*.yaml`、`maintenance/TODO.md`、`maintenance/PR_REVIEW_CHECKLIST.md` 开头、`wb_code/preview.mjs`、`wb_code/buildNpm.mjs`、`initDatabase/setting.json` 的文档 id 和字段名。

官方参考：`https://docs.cloudbase.net/skill.md`，以及 CloudBase 文档里的微信小程序开发 Skill 和 Spec 工作流说明。没有按那些页面安装插件或创建环境。
