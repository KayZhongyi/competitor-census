<p align="center">
  <img src="assets/hero.svg" alt="Competitor Census — 从公开信号到可追溯策略" width="100%" />
</p>

# Competitor Census｜竞品公开信息普查

**把任意友商分散在公开渠道中的信息，变成一份可追溯、可复用的竞品情报档案。**

Competitor Census 是面向全球市场的 Agent Skill 与开源工具包。输入公司和市场，它可以帮助你找到真正活跃的公开渠道，建立结构化证据库，处理多语言内容，从完整语料中形成分类，量化内容表现与客户诉求，并生成每条关键结论都能回到数据行和原始链接的报告。

> 先普查，后深挖；先证据，后结论。

## 它能实现什么

| 能力 | 结果 |
|---|---|
| **平台普查** | 先找到并核验友商真正活跃的公开渠道，再决定深挖哪些平台 |
| **范围内全量采集** | 统一保留发布日期、正文、播放量、点赞、评论、分享、账号字段和原始链接 |
| **多语言处理** | 原文与工作译文分开保存，不同语言进入同一套结构化数据 |
| **自下而上归类** | Agent 通读完整语料后再形成类别，不用预设关键词硬套标签 |
| **专业分析** | 对比内容供给与平均/中位传播效果，统计客户诉求、回复方式和机会缺口 |
| **可追溯交付** | 输出 CSV 证据库、分类体系、校验结果和带证据链接的 HTML 报告 |

证据结构与分析层不绑定具体平台，因此同一流程可以跨公司、跨语言、跨地区，并接入经过批准的采集工具。

## 60 秒看到结果

无需 API Key、浏览器登录或第三方依赖：

```bash
git clone https://github.com/KayZhongyi/competitor-census.git
cd competitor-census
python3 scripts/run_demo.py
```

打开 `demo/output/report.html`，或查看[在线虚构案例](https://kayzhongyi.github.io/competitor-census/)。

<p align="center">
  <img src="assets/demo-preview.svg" alt="可追溯竞品报告虚构示例" width="100%" />
</p>

## 运行真实公开渠道普查

仓库自带 YouTube 公开元数据连接器，不下载视频文件。建议先用少量记录核验账号和字段：

```bash
python3 -m pip install -U "yt-dlp[default]"
python3 scripts/collect_youtube.py \
  --company "OpenAI" \
  --channel "https://www.youtube.com/@OpenAI" \
  --tabs videos \
  --max-items-per-tab 10
```

运行后，`runs/openai/` 会同时得到证据库、基础报告、运行记录和可直接交给 Agent 的分析任务。

<p align="center">
  <img src="assets/youtube-live-demo.gif" alt="从 YouTube 公开元数据到证据库与报告" width="100%" />
</p>

核验无误后，对所选标签页中可检索的公开内容执行尽可能完整的普查：

```bash
python3 scripts/collect_youtube.py \
  --company "目标公司" \
  --channel "https://www.youtube.com/@TargetHandle" \
  --tabs videos,shorts,streams \
  --max-items-per-tab 0
```

## 用任意 Agent 完成分析

每次采集都会生成模型无关的 `analysis/analysis_task.md`。让你常用的文件型 Agent 按任务完成分析，再运行校验：

```text
使用 $competitor-census 执行 runs/openai/analysis/analysis_task.md。
通读完整语料，形成分类体系，并完成每一条分析结果。
```

```bash
python3 scripts/apply_analysis.py --bundle runs/openai
```

```text
content.csv（原始证据，不改写）
  → Agent 通读完整语料
  → taxonomy.json + analysis_results.csv
  → 确定性校验
  → analyzed_content.csv + analysis_report.html
```

校验器会检查源文件指纹、ID 完整性、译文覆盖率、分类定义、置信度和代表性证据，全部通过后才生成分析数据和报告。

## 安装为 Agent Skill

Codex：

```bash
git clone https://github.com/KayZhongyi/competitor-census.git ~/.codex/skills/competitor-census
```

Claude Code：

```bash
git clone https://github.com/KayZhongyi/competitor-census.git ~/.claude/skills/competitor-census
```

调用示例：

```text
使用 $competitor-census 调研 [国家/地区] 的 [公司] 公开渠道。
先建立证据库，再生成可追溯的策略报告。
```

Skill 由 Markdown 流程和 Python 标准库脚本组成，其他具备终端和浏览器能力的 Agent 也可以执行。

## 最终交付什么

| 交付物 | 用途 |
|---|---|
| `platform_census.csv` | 账号核验、活跃度与深挖决策 |
| `content.csv` | 公开内容、发布日期和互动指标等源级证据 |
| `comments.csv` | 采集到的用户对话和官方回复关系 |
| `run_manifest.json` | 调研范围、截止时间、工具、覆盖与运行记录 |
| `analysis/taxonomy.json` | 从语料中形成的类别定义与代表性证据 ID |
| `analysis/validation_report.json` | 可机器检查的完整性与一致性结果 |
| `analyzed_content.csv` | 在不改写原始证据的前提下合并译文与分类 |
| `analysis_report.html` | 带数量、分母、证据 ID 和原始链接的管理层报告 |

## 面向业务决策的分析方法

- **自下而上分类：** 类别来自真实语料，而不是固定模板。
- **供给—效果错位：** 同时比较发布占比、平均播放量和中位播放量。
- **客户声音分析：** 对具体问题和诉求做带分母的频次统计。
- **回复模式分析：** 区分有效回答、模板回复、渠道引导和未公开回复。
- **机会映射：** 把高需求、低供给主题转化为可验证的内容与服务机会。
- **证据阈值：** 小样本和歧义记录保留标记，不包装成确定结论。

分析方法见 [`references/analysis-playbook.md`](references/analysis-playbook.md)，Agent 文件规范见 [`references/analysis-handoff.md`](references/analysis-handoff.md)。

## 为可信复用而设计

- 原始证据与翻译、分类、结论始终分离。
- 稳定 ID 和原始链接让每个关键数字都可复核。
- 输入指纹防止旧分析误套到已经变化的新语料。
- 账号核验、平台验证和最终业务判断保留人工确认。
- 标准 CSV/JSON 接口便于继续增加合规连接器和报告格式。

公开信息采集规范见 [`references/collection-safety.md`](references/collection-safety.md)。仓库中的演示公司与数据全部为虚构内容。

欢迎贡献合规连接器、分析方法和报告主题，详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

[MIT](LICENSE)
