// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

// 成大毛茸茸仓库静态检查。
// 只读本地文件和 git 索引，不安装依赖，不访问微信、EMAS、COS 或 CloudBase。

import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const errors = [];
const warnings = [];

function fail(message) {
  errors.push(message);
}

function warn(message) {
  warnings.push(message);
}

function read(rel) {
  return fs.readFileSync(path.join(root, rel), 'utf8');
}

function exists(rel) {
  return fs.existsSync(path.join(root, rel));
}

function git(args) {
  return execFileSync('git', args, { cwd: root, encoding: 'utf8' });
}

const requiredDocs = [
  'docs/technical-overview.md',
  'docs/development-workflow.md',
  'docs/optimization-roadmap.md',
  'docs/architecture-decisions.md',
  'docs/backend-cost-research.md',
  'docs/backend-cost-sources.md',
  'CONTRIBUTING.md',
  'AGENTS.md',
  '.github/PULL_REQUEST_TEMPLATE.md',
  '.github/ISSUE_TEMPLATE/bug_report.md',
  '.github/ISSUE_TEMPLATE/task.md',
  '.github/workflows/repo-check.yml',
  'LICENSE',
];

for (const rel of requiredDocs) {
  if (!exists(rel)) fail(`缺少 ${rel}`);
}

if (exists('LICENSE') && !read('LICENSE').includes('Mozilla Public License Version 2.0')) {
  fail('LICENSE 不再是 MPL-2.0');
}

const gitignore = exists('.gitignore') ? read('.gitignore') : '';
if (!gitignore.includes('miniprogram/appSecret.js')) {
  fail('.gitignore 需要忽略 miniprogram/appSecret.js');
}
if (!gitignore.includes('private.*.key')) {
  fail('.gitignore 需要忽略 private.*.key');
}
if (/^docs\/\s*$/m.test(gitignore)) {
  fail('.gitignore 把整个 docs/ 排除了，项目文档无法入库');
}

for (const rel of ['docs/technical-overview.md', 'AGENTS.md']) {
  try {
    git(['check-ignore', '-q', rel]);
    fail(`${rel} 被 gitignore 排除`);
  } catch (error) {
    if (error.status !== 1) fail(`无法检查 ${rel} 是否被忽略：${error.message}`);
  }
}

const tracked = git(['ls-files', '-z']).split('\0').filter(Boolean);
const forbiddenName = tracked.filter((file) => (
  file === 'miniprogram/appSecret.js'
  || /(^|\/)private\..+\.key$/.test(file)
  || file.endsWith('.pem')
));
for (const file of forbiddenName) fail(`密钥文件被跟踪：${file}`);

const textExt = new Set(['.js', '.mjs', '.cjs', '.json', '.md', '.yml', '.yaml', '.py', '.txt', '.wxml', '.wxss']);
const secretPatterns = [
  { name: '私钥正文', re: /-----BEGIN [A-Z ]*PRIVATE KEY-----/ },
  { name: '腾讯云 SecretId 形态', re: /AKID[0-9A-Za-z]{16,}/ },
];

for (const file of tracked) {
  if (file.endsWith('package-lock.json') || file.startsWith('miniprogram/packages/')) continue;
  const ext = path.extname(file);
  if (!textExt.has(ext)) continue;
  let text;
  try {
    text = read(file);
  } catch {
    continue;
  }
  for (const pattern of secretPatterns) {
    if (pattern.re.test(text)) fail(`${file} 含有${pattern.name}`);
  }
}

const demoSecret = 'ABCDABCDABCDABCD==';
if (!exists('miniprogram/appSecret.demo.js') || !read('miniprogram/appSecret.demo.js').includes(demoSecret)) {
  fail('miniprogram/appSecret.demo.js 应保留占位 Secret，不能改成真实密钥');
}
for (const file of tracked) {
  if (!file.endsWith('.js') && !file.endsWith('.mjs')) continue;
  const text = read(file);
  const match = text.match(/space_secret\s*:\s*["']([^"']+)["']/);
  if (match && match[1] !== demoSecret) {
    fail(`${file} 写入了 space_secret 字面量`);
  }
}

const appJson = JSON.parse(read('miniprogram/app.json'));
const pages = [...appJson.pages];
for (const pack of appJson.subPackages || []) {
  for (const page of pack.pages) pages.push(`${pack.root}/${page}`);
}
const pageSet = new Set(pages);
for (const page of pages) {
  for (const ext of ['.js', '.json', '.wxml', '.wxss']) {
    const rel = path.join('miniprogram', `${page}${ext}`);
    if (!exists(rel)) fail(`已注册页面缺少文件 ${rel}`);
  }
}

const sitemap = JSON.parse(read('miniprogram/sitemap.json'));
for (const rule of sitemap.rules || []) {
  if (!rule.page || rule.page === '*') continue;
  if (!pageSet.has(rule.page)) {
    fail(`sitemap.json 的页面不在 app.json 中：${rule.page}`);
  }
}

const cloudApi = read('miniprogram/utils/cloudApi.js');
const dateMatch = cloudApi.match(/function getDate\(date\) \{([\s\S]*?)\n\}/);
if (!dateMatch) {
  fail('miniprogram/utils/cloudApi.js 找不到 getDate');
} else {
  const getDate = new Function('date', dateMatch[1]);
  const input = new Date('2020-01-02T03:04:05.000Z');
  const copied = getDate(input);
  if (!(copied instanceof Date) || copied.getTime() !== input.getTime()) {
    fail('getDate(date) 必须返回传入的时间');
  }
  const now = getDate();
  if (!(now instanceof Date) || Math.abs(now.getTime() - Date.now()) > 2000) {
    fail('getDate() 必须返回当前时间');
  }
}

if (exists('project.config.json') && read('project.config.json').includes('wx5bd705b2bc91c73b')) {
  warn('根目录 project.config.json 仍是上游小程序 AppID。预览或上传前要换成成大自己的 AppID。本检查不因此失败。');
}
if (exists('miniprogram/config.js') && read('miniprogram/config.js').includes('space_id:')) {
  warn('miniprogram/config.js 仍有上游 EMAS space_id 与校园地图中心。连接自己的后端前要替换，文档里不要转载坐标。');
}

if (warnings.length) {
  console.log('警告（不导致失败）：');
  for (const message of warnings) console.log(`- ${message}`);
}

if (errors.length) {
  console.error(`repo-check 失败，${errors.length} 项：`);
  for (const message of errors) console.error(`- ${message}`);
  process.exit(1);
}

console.log(`repo-check 通过。已注册页面 ${pages.length} 个，跟踪文件 ${tracked.length} 个。`);
