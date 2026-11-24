# 任务：从零构建一个功能完整、界面美观的英语学习网站（纯静态，无 AI、无外部 API）

你在一个空目录里工作。用 Vue 3 + Vite + vue-router（hash 路由）构建，`npm run build` 必须成功，产物是可直接部署到 GitHub Pages 的静态站点。所有数据都是站内本地数据（JS/JSON 文件），所有音频都是本地 MP3 文件。**禁止**调用任何外部 API、禁止 AI 功能、禁止使用浏览器 speechSynthesis（TTS 在手机上不可靠，这是硬红线，代码里不许出现 speechSynthesis）。

工作方式：分阶段做，每完成一阶段在终端用中文简述做了什么。阶段：1) 脚手架+设计系统+数据层 2) 单词模块 3) 听力模块 4) 阅读模块 5) 写作模块 6) 语法/表达/仪表盘/全局功能 7) 音频生成 8) 构建修复与自检报告。最后写 BUILD_REPORT.md 记录：功能清单、数据量统计、音频文件数与总大小、构建结果、已知限制。

## 设计要求（美观大方是硬指标）
- 风格参考 BBC Learning English / Duolingo 的清晰感，但做原创设计：主色深青绿 (#0F766E 系) + 暖橙点缀 (#F59E0B 系)，浅色背景，卡片圆角 16px，柔和阴影，字体系统字体栈 + 英文优先 'Segoe UI'/Inter 回退。
- 支持深色模式切换（localStorage 记忆），CSS 变量实现。
- PC 端：顶部导航 + 内容最大宽 1200px 居中；手机端：底部 Tab 栏（首页/单词/听力/阅读/我的），断点 768px。所有页面在 375px 宽不溢出、不横滚。
- 首页仪表盘：问候语、连续学习天数（streak，localStorage 按日期计算）、今日学习进度环或条、各模块入口卡片、每日一句（按日期轮换 30 句）、继续学习（上次位置）、本周学习统计（CSS 柱状图即可）。

## 模块一：单词学习（数据量是硬指标）
- 4 个词库，每个 **至少 60 个真实单词**（共 ≥240）：CET-4 核心、CET-6 进阶、IELTS 学术、日常高频。每个单词字段：word、phonetic（英式音标）、pos（词性）、cn（中文释义）、example（英文例句）、exampleCn、level。数据写成独立 JS 数据文件，不许用 lorem、不许重复充数、不许编造音标（用常见词，音标要准）。
- 功能：词库列表与进度；学习模式（卡片翻转、认识/不认识标记、掌握度 0-3 存 localStorage）；闪卡模式；四选一测验（英→中、中→英随机，10 题一组，即时反馈+解析，错题自动进错题本）；拼写练习（听读音/看释义拼单词）；错题本（可重练、可移除）；单词搜索（全库模糊搜）；每个单词有发音按钮（播本地 MP3，见音频部分）。

## 模块二：听力训练（难度从低到高）
- 4 个难度：A2 初级、B1 中级、B2 中高级、C1 高级，每级 **3 篇**，共 12 篇。每篇字段：title、level、topic、transcript（A2 约 80-120 词，B1 120-170，B2 170-230，C1 230-300，内容原创：日常对话、校园、旅行、职场、科技、环境等）、questions（每篇 4 道四选一，含 answer 与 explanation 中文解析）、dictation（从原文选 5 句做听写填空，挖去关键词）。
- 功能：音频播放器（播放/暂停、进度条拖动、0.75/1/1.25/1.5 倍速、当前句高亮可选做）；原文可隐藏/显示（先听后看）；理解测验即时判分；听写模式逐空判对错并给答案；完成状态与得分存 localStorage，列表页显示。

## 模块三：阅读训练
- **至少 8 篇**分级阅读（A2×2、B1×2、B2×2、C1×2），每篇 250-450 词，原创文章（文化、科技、健康、环境、人物故事等），字段：title、level、topic、wordCount、minutes（预计时长）、paragraphs、glossary（文中 6-10 个生词：word+phonetic+cn）、questions（每篇 5 道：主旨/细节/推断/词义，含 answer+explanation）。
- 功能：阅读页（段落排版舒适、生词点击弹出释义卡）、答题判分、生词一键加入单词错题本/收藏、阅读完成记录与用时计时。

## 模块四：写作模板（不做 AI 批改）
- 模板库 **至少 12 个**，分三类：CET-4/6（议论文观点类、问题解决类、图表作文、书信、通知/倡议书）、IELTS Task 1（折线图、柱状图、饼图、表格、流程图）、IELTS Task 2（同意与否、讨论双方、利弊类）。每个模板字段：name、exam、type、structure（段落框架，分段说明）、outline、sentenceFrames（每段可套用句型，含填空位 ____）、sampleEssay（完整范文，词数达标：四六级 150-200 词，雅思 200-280 词）、usefulPhrases（高级表达 8-10 个，含中文）、checklist（自查清单）。
- 写作练习：选题目（至少给 10 个练习题，关联模板）→ 写作区（实时词数统计、目标词数进度、计时器、套用句型一键插入）→ 交卷后对照 checklist 自评 → 草稿自动存 localStorage，可在「我的作文」里查看/删除。明确标注「自评模式，无 AI 批改」。

## 模块五：语法与表达（加分模块，做实）
- 语法小课 **至少 8 课**：时态总览、现在完成时、被动语态、定语从句、虚拟语气、非谓语动词、倒装、主谓一致。每课：中文讲解要点、例句 4-6 条（英+中）、易错点、随堂 5 题小测（判分+解析）。
- 常用表达：**至少 40 个**地道词块/短语，按场景分组（日常寒暄、课堂学习、旅行、职场、表达观点），每个含 example 与中文，带发音 MP3。

## 音频生成（Piper 本地神经 TTS，美音）
环境已备好，直接用：
- piper 可执行：`/home/hatch/workspace/tools/tts-venv/bin/piper`
- 模型：`/home/hatch/workspace/tools/piper-voices/en_US-lessac-medium.onnx`
- 用法：`echo "text" | piper -m <model> -f out.mp3`（输出 wav 时改后缀 .wav 再用 ffmpeg 转 mp3，或直接 -f out.wav 后批量转码；优先生成 mp3：piper 输出 wav，用 ffmpeg -y -i in.wav -codec:a libmp3lame -q:a 4 out.mp3）
需要生成的音频：
1. 全部单词的单词读音（≥240 个）→ `public/audio/words/<word>.mp3`（文件名小写、空格/斜杠做安全处理，并建 word→file 映射）
2. 12 篇听力全文（按整篇生成一个 MP3）→ `public/audio/listening/<id>.mp3`
3. 40 个常用表达各一个 MP3 → `public/audio/phrases/<id>.mp3`
写一个可重复运行的脚本 `scripts/gen_audio.py`（从数据文件读文本生成，已存在则跳过），实际运行它生成全部音频，并在报告里统计文件数。生成失败的文件要在报告里列出，不许假装成功。听力整篇生成若太慢，可按句生成后用 ffmpeg 拼接，二选一，能跑通为准。

## 全局与工程要求
- 进度中心（「我的」页）：总学习数据（已学单词数、听力完成数、阅读完成数、作文草稿数、连续天数）、各模块进度条、错题本入口、数据导出/清除按钮。
- 全站搜索入口（搜单词/文章/模板标题）。
- 路由至少包括：/（首页）、/words、/words/:deck、/words/quiz、/words/spelling、/words/wrong、/listening、/listening/:id、/reading、/reading/:id、/writing、/writing/template/:id、/writing/practice、/grammar、/grammar/:id、/phrases、/me。底部 Tab 与顶部导航都要能到达主模块。
- vite base 设为 './'，路由用 createWebHashHistory，确保 GitHub Pages 子路径下资源与路由都正常。
- 不引入大型 UI 库；图标用内联 SVG 或 emoji 少量点缀（以 SVG 为主）。
- README.md 写清：功能、本地运行、构建部署、数据与音频说明。
- 完成后运行 `npm run build` 并修复所有报错；抽查 dist 里 audio 文件数与数据量，写入 BUILD_REPORT.md。
