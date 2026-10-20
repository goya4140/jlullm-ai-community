# 持续维护与日报贡献

本站使用 JSON 作为内容源，由 Python 构建器生成静态 HTML。通过仓库中的模板与脚本维护日报。

## 一、从材料到初稿

- **聊天记录**：保留消息时间和上下文；相同主题可跨消息合并。默认用匿名代号，不猜真实身份。
- **录音**：先通过常用录音工具转写，再保留发言人和时间标记。不要只凭 AI 纪要写正文；重要数字、术语和引文应回听核对。
- 将原始材料留在仓库外或 `.private/`（已忽略）。公开仓库只存已确定可以公开的内容。
- 使用 `templates/chat-prompt.md`、`templates/recording-prompt.md`。

## 二、JSON 结构

模板为 `templates/chat.json` 与 `templates/recording.json`。机器可读字段规范见 `templates/digest.schema.json`。

| 字段 | 用途 |
| --- | --- |
| `id` | URL 标识，推荐 `YYYY-MM-DD-english-slug`，只能用小写字母、数字、连字符；发布后不要随意修改 |
| `title` / `subtitle` | 标题与一段简短导读 |
| `date` | 整理日期，YYYY-MM-DD；用于排序和归档 |
| `event_date` | 原讨论日期，不明确填 `null` |
| `source_type` | `chat` 或 `recording` |
| `duration` | 录音时长；不明确留空 |
| `status` | `draft` 为草稿；`published` 才会进入网站 |
| `reviewed_by` | 审核署名；发布时不可为空 |
| `tags` | 用于展示和搜索的主题标签 |
| `summary` | 本期概述 |
| `source_note` | 来源说明、转写局限、活动日期等 |
| `sources` | 确定可以公开的来源，数组元素为 `{ "title": "名称", "url": "https://..." }`；不公开则 `[]` |
| `topics` | 按主题组织的讨论，结构见下 |
| `followups` | `{ "kind": "现场提议/明确行动/编辑建议/待核实", "text": "具体内容" }` |

每个 topic 使用唯一 `id`（如 `topic-1`），包含 `category`、`title`、`time_range`、`paragraphs`、`editor_note`、`quotes` 与 `links`。

- `paragraphs` 是非空文字数组，建议 2–4 段，把问题、回应、分歧和结论串起来。
- `quotes` 为 `{ "speaker": "发言人1", "time": "32:25", "text": "原文摘录" }`。只能使用真实摘录，不能替模型总结加引号。聊天时间可保留日期。
- `editor_note` 可留空；有内容时会显示为「AI 锐评 / 编辑评论」，不冒充与会者结论。
- `links` 为公开资料链接，格式同 `sources`；只允许 http(s)，不接受脚本或本地地址。

## 三、审核与发布

使用模板生成 JSON 初稿后，核对来源、公开范围和观点归属。修改任何正文后，都要重新在本地预览并审核。

新建草稿：

```sh
python3 scripts/new_digest.py --type recording --date 2026-10-21 --slug research-chat --title '本次交流标题'
```

默认生成草稿，不会出现在网站。补全正文后，由编辑把 `status` 设为 `published`，填写 `reviewed_by`。

```sh
python3 scripts/build.py
python3 -m unittest discover -s tests -v
python3 scripts/check_site.py
```

浏览器本地检查后，提交 `content/` 和构建后的 `docs/`，建议通过 PR 让另一位成员阅读。合并到 `main` 后，Pages 自动部署 `/docs`。在仓库 Actions 中可以查看 `pages build and deployment` 是否成功。

```sh
git add content/digests docs
git commit -m "Add community digest for YYYY-MM-DD"
git push
```

若需撤下一篇，把它改成 `draft`，重新构建并提交。已公开内容可能被缓存或保存在 Git 历史中，因此发布前核对比事后删除更可靠。

## 四、社区维护

- 内容勘误：Issue 写明文章地址、段落、问题与可核对依据。
- 新议题：在 Discussions 发起，介绍具体问题、已有尝试和希望得到的帮助。
- UI 与功能修改：提交 PR，说明用户能看到的变化与验证方式。
- 不要虚构社区成员数、活动、项目、合作方或官方身份。没有明确群入口时，使用 GitHub Discussions。
- 目前不会自动抓取群聊、自动读录音链接或定时生成日报；新增自动采集与模型调用时，需另行设计授权、数据来源与维护成本。
