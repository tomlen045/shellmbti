# ⌨ shellmbti

> **你的终端历史，暴露了你是谁。** 一条命令 → Shell MBTI 人格 + 可晒的分享卡片。

[English](README.md) | 简体中文

![演示](screenshots/card-demo.png)

## 这是什么

`shellmbti` 读取你本地的 shell 历史（zsh / bash / fish），**100% 离线分析**，然后告诉你：

- 🧠 **你的 Shell MBTI 人格**——16 种原型：「定时任务成精」「万物皆可脚本」「无名守夜人」……
- 📊 真实数据：总命令数、探索指数、习惯浓度、夜行浓度、git 浓度、sudo 次数、最长一条命令（附吐槽）
- 🎴 **可保存的分享卡片**（1080×1440，小红书完美尺寸），canvas 本地渲染，一键导出 PNG

不调 API、不上传、不注册。你的命令历史永远不会离开你的电脑——谁也不敢把 history 贴进陌生网页，所以这必须是本地工具。

## 为什么是 MBTI

没人爱看仪表盘，但人人都爱晒人格测试结果。分析用的是透明的启发式规则（命令多样性 → E/I，创造类 vs 操作类 → N/S，自动化 → T/F，习惯浓度 → J/P）——图一乐，且坦诚图一乐。

## 玩法

```bash
git clone https://github.com/tomlen045/shellmbti.git
cd shellmbti
python3 shellmbti.py          # 终端人格报告
python3 shellmbti.py --card   # 生成分享卡片
```

要求：python3（纯标准库，零依赖）。支持 zsh（含扩展历史时间戳）、bash、fish。

## License

MIT

---

## 🫰 关注「小薅薅」· 每天发现一个宝藏工具

> **小薅薅** — 年轻人的赛博工具箱。每天为你发现一个好玩、实用、开源的小工具，帮你节省 1 小时探索时间。
>
> 📱 **微信搜索「小薅薅」** 或扫描下方二维码关注
>
> 后台回复关键词获取：
> - 回复 **「工具」** → 获取全部工具合集（离线可用）
> - 回复 **「运维」** → 获取运维/安全资源包
> - 回复 **「加群」** → 加入工具交流群

<div align="center">

| 🎯 更多作品 | 描述 | Stars |
|:---|:---|:---|
| [ops-skills](https://github.com/tomlen045/ops-skills) | 10个AI运维技能包，让Claude Code变成SRE专家 | [⭐ 新项目](https://github.com/tomlen045/ops-skills) |
| [ops-doctor](https://github.com/tomlen045/ops-doctor) | 一条命令给Linux服务器做全套体检+健康分 | [⭐ 实用工具](https://github.com/tomlen045/ops-doctor) |
| [naicha-mbti](https://github.com/tomlen045/naicha-mbti) | 8道题测出你的奶茶人格，生成分享卡片 | [🧋 爆款](https://github.com/tomlen045/naicha-mbti) |
| [fafa-generator](https://github.com/tomlen045/fafa-generator) | 发疯文学生成器——一键生成发疯文案+卡片 | [🔥 热门](https://github.com/tomlen045/fafa-generator) |
| [life-progress](https://github.com/tomlen045/life-progress) | 人生进度条——把你的时间摆在眼前 | [⏳ 走心](https://github.com/tomlen045/life-progress) |

</div>

<div align="center">

**觉得有用？给个 ⭐ 让更多人看到 → [GitHub](https://github.com/tomlen045) | [Gitee](https://gitee.com/tomlen)**

</div>
