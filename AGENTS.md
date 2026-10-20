# JLULLM AI 社区维护约定

- 使用 Python 标准库构建，优先保持静态站；无理由不引入框架或模型后端。
- 内容源在 `content/digests/*.json`，不要仅编辑生成的 `docs/`。
- 新内容默认 `draft`；只有核对公开范围、来源和引文并填写 `reviewed_by` 后，才能设为 `published`。
- 用户授权发布整理版不等于授权公开原始录音、聊天全文或私密分享链接。原始材料保留本地 `.private/` 或仓库外。
- 不从自动转写中的含糊术语猜测人名、模型名、容量单位。保留观点归属，不把预测改写成事实。
- 不虚构人数、活跃榜、活动、合作方、群入口或功能状态。
- 每次修改运行 `python3 scripts/build.py`、`python3 -m unittest discover -s tests -v` 和 `python3 scripts/check_site.py`。
- 布局或交互修改需在浏览器检查相应页面和移动布局，保持 `/jlullm-ai-community/` 子路径下的链接可用。
- 发布源为 `main:/docs`；将内容源与生成文件一起提交。
