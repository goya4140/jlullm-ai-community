# JLULLM AI 社区

一起理解 AI，一起把想法做出来。

- **社区主页**：https://goya4140.github.io/jlullm-ai-community/
- **日报归档**：https://goya4140.github.io/jlullm-ai-community/daily/
- **整理工作台**：https://goya4140.github.io/jlullm-ai-community/workbench/
- **参与交流**：https://github.com/goya4140/jlullm-ai-community/discussions

这是社区展示与知识积累的共同入口。首版包括社区介绍、可搜索与筛选的日报归档、文章页，以及聊天记录和录音转写两套日报模板。首篇为 2026-10-20 整理的具身智能与 AI 硬件交流特刊。

## 贡献一期日报

1. 在工作台选择「聊天记录」或「录音转写」，粘贴文字材料，生成整理提示词。
2. 把提示词交给你常用的 AI，取得 JSON 初稿。
3. 将初稿导回工作台，预览并核对正文、摘录、时间、公开链接与编辑评论。
4. 填写审核署名，导出已审核 JSON，放进 `content/digests/`。
5. 运行构建与检查，将内容文件和 `docs/` 的变更一起提交到 `main`。GitHub Pages 会自动发布。

工作台不调用模型 API、不自动转写音频、不直接向 GitHub 写入数据；材料不会上传或保存到服务器。所有原始材料应放在本地 `.private/` 或仓库外，切勿加入 Git。日报必须由编辑核对后发布。

完整步骤与字段说明见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 本地运行

只需 Python 3.9+；构建无需第三方依赖。

```sh
python3 scripts/build.py
python3 -m unittest discover -s tests -v
python3 scripts/check_site.py
python3 -m http.server 8000 --directory docs
```

然后打开 http://localhost:8000/ 。`docs/` 是可直接托管的静态网站；也可在本地打开首页，工作台无需联网即可生成提示词与预览 JSON（剪贴板自动复制取决于浏览器权限）。

新建一期草稿：

```sh
python3 scripts/new_digest.py --type chat --date 2026-10-21 --slug agent-tools --title 'Agent 工具与实践讨论'
# 录音使用 --type recording
```

## 项目结构

```text
content/site.json            社区名称、介绍、仓库地址
content/digests/*.json       唯一的日报内容源
scripts/build.py            校验并生成首页、目录、文章页、工作台
scripts/new_digest.py       从模板创建草稿
scripts/check_site.py       静态链接、锚点和公开内容检查
web/assets/                 样式与前端交互
templates/                 聊天/录音 JSON、提示词、字段 schema
docs/                      生成的网站，由 GitHub Pages 托管
 tests/                     发布门槛、草稿排除和文本转义检查
```

## 发布与维护

Pages 使用 `main` 分支的 `/docs` 目录。维护者修改内容后运行构建并提交即可；无需付费服务、模型密钥或独立后端。站点基础元数据位于 `content/site.json`；首页文案与页面布局位于 `scripts/build.py`，视觉与交互位于 `web/assets/`。不要只改生成后的 `docs/`。

日报按**整理日期**归档，活动日期不明时留空。原始录音分享地址和私人聊天不随首期公开，文章中的时间仅用于持有原录音的成员回听。文章保留不同观点，AI 锐评明确标为编辑评论。

## 设计参考

日报的信息组织参考 [AgentHub 日报](https://hqhq1025.github.io/agent_hub/daily/2026-10-19/group-1/)，本站的界面、内容模型与维护工具独立实现。
