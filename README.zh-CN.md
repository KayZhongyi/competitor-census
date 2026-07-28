<p align="center">
  <img src="assets/hero.svg" alt="Competitor Census — 从公开信号到可追溯策略" width="100%" />
</p>

# Competitor Census｜竞品公开信息普查

这是一个可安装的 Agent Skill 与公开工具包：先普查竞品真正活跃的平台，再对声明范围内的公开内容做尽可能完整的采集，保留发布日期、播放量、点赞、评论、分享、原文、译文与链接，最后生成每条结论都能回到证据的竞品报告。v0.2 已加入可实际运行的 YouTube 公开元数据采集器，并保留零依赖离线 Demo。

核心原则是：**先普查、后深挖；先证据、后结论。**

## 真实 YouTube 频道试跑

先安装最新版 [`yt-dlp`](https://github.com/yt-dlp/yt-dlp/wiki/Installation)：

```bash
git clone https://github.com/KayZhongyi/competitor-census.git
cd competitor-census
python3 -m pip install -U "yt-dlp[default]"
python3 scripts/collect_youtube.py \
  --company "OpenAI" \
  --channel "https://www.youtube.com/@OpenAI" \
  --tabs videos \
  --max-items-per-tab 10
```

运行后打开 `runs/openai/report.html`。同一目录还会生成内容 CSV、平台普查表、JSON 摘要和记录范围/局限的 Manifest。试跑成功后，把公司名和频道地址替换成目标友商。

<p align="center">
  <img src="assets/youtube-live-demo.gif" alt="从 YouTube 公开元数据采集到证据库与报告" width="100%" />
</p>

确认账号和字段无误后，可对所选公开标签页做尽可能完整的采集：

```bash
python3 scripts/collect_youtube.py \
  --company "目标公司" \
  --channel "https://www.youtube.com/@TargetHandle" \
  --tabs videos,shorts,streams \
  --max-items-per-tab 0
```

采集器不会下载视频文件。它会在公开页面可提供的范围内记录视频 ID、发布日期、标题与简介、时长、播放量、点赞数、可见评论数、账号字段和原始链接。翻译与内容类型暂时留空，由 Agent 读取真实语料后自下而上完成，避免用关键词预设分类。

## 60 秒离线体验

无需 API Key、浏览器登录或安装第三方包：

```bash
git clone https://github.com/KayZhongyi/competitor-census.git
cd competitor-census
python3 scripts/run_demo.py
```

打开 `demo/output/report.html`，或查看[在线虚构案例](https://kayzhongyi.github.io/competitor-census/)。

## 它解决什么问题

- 不预设 TikTok、Facebook 或其他平台，先用账号活跃度决定深挖哪些渠道；
- 不把几十条抽样包装成全局结论，而是记录采集范围、截止时间、覆盖率与局限；
- 原始证据与翻译、分类、报告分离，避免结论污染数据；
- 内容分类从真实语料自下而上形成；
- 用内容供给与传播效果错位、客户诉求频次、官方回复方式等方法做分析；
- 所有关键结论附带 `n/N`、数据行 ID 或原始链接；
- 遇到人机验证时暂停并由人处理，不绕过验证码或平台保护机制。

## 作为 Skill 安装

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

详细流程见 [SKILL.md](SKILL.md)，字段结构见 [`references/data-schema.md`](references/data-schema.md)，分析方法见 [`references/analysis-playbook.md`](references/analysis-playbook.md)。

## 合规边界

只处理授权访问下公开可见的信息，不绕过登录、验证码、限流、robots 控制或其他平台保护措施。“普查”指在明确范围和截止时间下，对公开可见内容的尽可能完整采集，不代表能够获得隐藏、删除、个性化或受限数据。

本仓库的演示公司和全部演示记录均为虚构数据，不包含雇主、客户或真实用户资料。

## License

[MIT](LICENSE)
