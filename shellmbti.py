#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shellmbti v0.1 — 你的终端历史，暴露了你是谁
读取本地 shell 历史(zsh/bash)，离线分析 → 终端 MBTI 人格 + 分享卡片
零依赖(python3 stdlib) · 数据不出本机
"""
import os, sys, re, json, argparse, webbrowser

# ---------- 颜色 ----------
class C:
    G="\033[32m"; Y="\033[33m"; R="\033[31m"; B="\033[36m"; Bd="\033[1m"; D="\033[2m"; _="\033[0m"

def out(s): print(s)

# ---------- 1. 定位并解析历史 ----------
def find_history():
    cands = []
    env = os.environ.get("HISTFILE")
    if env: cands.append(os.path.expanduser(env))
    cands += [os.path.expanduser(p) for p in ("~/.zsh_history","~/.bash_history","~/.local/share/fish/fish_history")]
    for p in cands:
        if p and os.path.isfile(p) and os.path.getsize(p) > 0:
            return p
    return None

def parse(path):
    """返回命令列表(干净的命令字符串) + 是否有时间戳"""
    cmds, has_ts = [], False
    zsh_meta = re.compile(r"^: (\d+):\d+;(.*)$", re.S)
    try:
        raw = open(path, encoding="utf-8", errors="ignore").read()
    except Exception as e:
        sys.exit(f"读取失败: {e}")
    lines = raw.split("\n")
    if path.endswith("fish_history"):
        cmds = [l[7:] for l in lines if l.startswith("- cmd: ")]
        return [c.strip() for c in cmds if c.strip()], False
    cur, cur_ts = None, None
    for ln in lines:
        if not ln.strip(): continue
        m = zsh_meta.match(ln)
        if m:
            if cur is not None: cmds.append(cur)
            cur, cur_ts = m.group(2), int(m.group(1)); has_ts = True
        else:
            # bash 普通行 或 zsh 多行续行
            if cur is not None and has_ts:
                cur += "\n" + ln          # zsh 多行续行
            else:
                if cur is not None: cmds.append(cur)
                cur, cur_ts = ln, None
    if cur is not None: cmds.append(cur)
    return [c.strip() for c in cmds if c.strip()], has_ts

# ---------- 2. 分析 ----------
CATS = {
    "git":   ["git"],
    "容器云": ["docker","kubectl","helm","podman","docker-compose","k9s"],
    "远程":  ["ssh","scp","sftp","mosh","telnet"],
    "网络":  ["curl","wget","ping","dig","nc","netstat","ss","traceroute","iftop"],
    "编辑":  ["vim","vi","nvim","nano","code","emacs","subl"],
    "系统":  ["sudo","chmod","chown","systemctl","launchctl","kill","killall","top","htop","df","du","ps","mount"],
    "包管理":["brew","apt","apt-get","yum","dnf","pip","pip3","npm","pnpm","yarn","cargo","gem","go"],
    "文件":  ["ls","cd","cp","mv","rm","mkdir","touch","cat","head","tail","less","find","grep","rg","tar","unzip","open","eza"],
    "脚本":  ["bash","sh","zsh","python","python3","node","make","./"],
}
NIGHT = ["vim","nvim","ssh","tail","grep","docker","curl","python3","git commit","git push"]
CREATIVE = ["vim","vi","nvim","nano","code","echo","touch","mkdir","git commit","git init","npm init","cargo new","python3","node","make"]
AUTOMATION = ["bash","sh","chmod","make","source","crontab","alias","python3","./","docker-compose"]

def first_token(c):
    t = c.strip().split()
    t0 = t[0] if t else ""
    return t0.split("/")[-1]

def analyze(cmds, has_ts, ts_list):
    total = len(cmds)
    firsts = [first_token(c) for c in cmds]
    uniq = set(firsts)
    diversity = len(uniq)/total if total else 0

    from collections import Counter
    fc = Counter(firsts)
    top10 = fc.most_common(10)
    top_share = sum(n for _,n in top10)/total if total else 0

    # 分类计数(一条命令可中多类)
    joined = "\n".join(cmds).lower()
    cat_hits = {}
    for cat, keys in CATS.items():
        cat_hits[cat] = sum(joined.count(" "+k+" ")+joined.count("\n"+k+" ")+ (1 if joined.startswith(k+" ") else 0) for k in keys)

    # 夜行(仅当有时间戳)
    night = None
    if has_ts and ts_list:
        import datetime
        hrs = [datetime.datetime.fromtimestamp(t).hour for t in ts_list if t]
        if hrs: night = round(100*sum(1 for h in hrs if h >= 0 and h < 6)/len(hrs))
    longest = max(cmds, key=len) if cmds else ""
    sudo_n = sum(1 for c in cmds if c.startswith("sudo "))
    git_n = sum(1 for c in cmds if c.startswith("git "))
    creative_n = sum(1 for c in cmds if any(c.lower().startswith(k) for k in CREATIVE))
    auto_n = sum(1 for c in cmds if any(c.lower().startswith(k) for k in AUTOMATION))
    sysops_n = sum(1 for c in cmds if any(first_token(c) in CATS["文件"] for _ in [0]))

    # MBTI 四维
    d1 = "E" if diversity >= 0.30 else "I"                       # 探索广度
    d2 = "N" if total and creative_n/total >= 0.22 else "S"      # 创造 vs 操作
    d3 = "T" if total and auto_n/total >= 0.05 else "F"          # 自动化 vs 手动
    d4 = "J" if top_share <= 0.55 else "P"                       # 多样节奏 vs 习惯重复
    mbti = d1+d2+d3+d4

    return dict(total=total, unique=len(uniq), diversity=round(diversity*100),
                top10=top10, top_share=round(top_share*100), cat=cat_hits,
                night=night, longest=longest, longest_len=len(longest),
                sudo=sudo_n, git=git_n, mbti=mbti)

# ---------- 3. 人格库 ----------
ARCH = {
 "INTP":"深夜炼金术士","INTJ":"沉默的架构师","INFP":"折腾星人","INFJ":"隐形的守护者",
 "ENTP":"万物皆可脚本","ENTJ":"自动化狂人","ENFP":"好奇心永动机","ENFJ":"全组工具人",
 "ISTP":"一次性方案大师","ISTJ":"定时任务成精","ISFP":"极简主义者","ISFJ":"无名守夜人",
 "ESTP":"先跑了再说","ESTJ":"流程铁面警","ESFP":"朋友圈炫技王","ESFJ":"人形百科全书",
}
DESC = {
 "I":"深耕机器内部","E":"天天往外探", "N":"爱造新东西","S":"稳扎稳打干操作",
 "T":"能自动绝不手点","F":"一条条手敲也很爽", "J":"节奏多样爱尝鲜","P":"肌肉记忆走天下",
}

def persona_line(m):
    d1,d2,d3,d4 = m
    return f"{d1}={DESC[d1]} · {d2}={DESC[d2]} · {d3}={DESC[d3]} · {d4}={DESC[d4]}"

# ---------- 4. 输出 ----------
def term_report(st, histfile):
    m = st["mbti"]
    out = []
    out.append("")
    out.append(f"{C.B}  ███████╗ ██╗  ██╗███████╗██╗     ██╗      ███╗   ███╗██████╗ ██████╗ ██╗{C._}")
    out.append(f"{C.B}  ██╔════╝ ██║  ██║██╔════╝██║     ██║      ████╗ ████║██╔══██╗██╔══██╗██║{C._}")
    out.append(f"{C.G}  ███████╗ ███████║█████╗  ██║     ██║      ██╔████╔██║██████╔╝██████╔╝██║{C._}")
    out.append(f"{C.G}  ╚════██║ ██╔══██║██╔══╝  ██║     ██║      ██║╚██╔╝██║██╔═══╝ ██╔═══╝ ██║{C._}")
    out.append(f"{C.G}  ███████║ ██║  ██║███████╗███████╗███████╗██║ ╚═╝ ██║██║     ██║     ███████╗{C._}")
    out.append(f"{C._}  ╚══════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝     ╚═╝╚═╝     ╚═╝     ╚══════╝{C._}")
    out.append("")
    out.append(f"  {C.B}你是 {C.G}{m[0]}{C.Y}{m[1]}{C.B}{m[2]}{C.R}{m[3]}{C._} {C.B}—— {C.G}{ARCH[m]}{C._}")
    out.append(f"  {C.D}{persona_line(m)}{C._}")
    out.append("")
    out.append(f"  {C.B}📊 你的终端数据{C._}   (来源: {histfile})")
    out.append(f"  ────────────────────────────────")
    out.append(f"  总命令数      {C.B}{st['total']:,}{C._} 条")
    out.append(f"  探索指数      {C.B}{st['diversity']}%{C._} ({st['unique']} 种不同命令)")
    out.append(f"  习惯浓度      {C.B}{st['top_share']}%{C._} (最常用10条命令的占比)")
    if st["night"] is not None:
        col = C.R if st["night"] >= 25 else C.G
        out.append(f"  夜行浓度      {col}{st['night']}%{C._} 的命令发生在 0-6 点")
    else:
        out.append(f"  夜行浓度      {C.D}无法判断(历史无时间戳){C._}")
    out.append(f"  git浓度       {C.B}{st['git']:,}{C._} 条")
    out.append(f"  sudo次数      {C.Y}{st['sudo']:,}{C._} 次 (权力越大责任越大)")
    lc = st["longest"]
    if lc:
        prev = lc if len(lc) <= 90 else lc[:87]+"..."
        out.append(f"  最长一条命令  {C.B}{st['longest_len']}{C._} 字符:")
        out.append(f"  {C.D}  {prev}{C._}")
    out.append("")
    out.append(f"  {C.B}🏷 分类画像{C._}")
    cats = sorted(st["cat"].items(), key=lambda x:-x[1])[:5]
    mx = max([v for _,v in cats] or [1]) or 1
    for name,v in cats:
        bar = "█"*max(1,int(v/mx*20))
        out.append(f"  {name:<6} {C.G}{bar}{C._} {v}")
    out.append("")
    out.append(f"  {C.Y}➜ 生成分享卡片: python3 shellmbti.py --card{C._}")
    out.append("")
    print("\n".join(out))

# ---------- 5. 分享卡片 ----------
CARD_TPL = """<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><title>shellmbti</title></head>
<body style="margin:0;background:#0b0e14;display:flex;flex-direction:column;align-items:center;gap:16px;padding:24px;">
<canvas id="c" width="1080" height="1440"></canvas>
<button onclick="dl()" style="background:#2da44e;color:#04260a;border:none;border-radius:99px;padding:14px 44px;font-size:20px;font-weight:900;cursor:pointer;">⬇️ 保存卡片图片</button>
<p style="color:#8b949e;font-size:13px;">截图或点按钮保存 → 发小红书/朋友圈/群</p>
<script>
const S = __DATA__;
const c = document.getElementById('c'), x = c.getContext('2d');
x.fillStyle = '#0b0e14'; x.fillRect(0,0,1080,1440);
// 边框
x.strokeStyle = '#30363d'; x.lineWidth = 3; x.strokeRect(28,28,1024,1384);
// 顶部
x.fillStyle = '#2da44e'; x.font = 'bold 34px sans-serif'; x.textAlign='left';
x.fillText('⌨ SHELL MBTI', 64, 96);
x.fillStyle = '#8b949e'; x.font = '24px sans-serif'; x.textAlign='right';
x.fillText('你的终端，暴露了你是谁', 1016, 96);
// 大字母
const L = S.mbti.split(''), cols = ['#58a6ff','#d2a8ff','#3fb950','#f0883e'];
L.forEach((ch,i)=>{
  x.fillStyle = cols[i]; x.font = '900 190px -apple-system,"PingFang SC",sans-serif';
  x.fillText(ch, 90 + i*230, 400);
});
// 人格名
x.fillStyle = '#ffffff'; x.font = 'bold 56px "PingFang SC",sans-serif'; x.textAlign='left';
x.fillText('__ARCH__', 64, 540);
x.fillStyle = '#8b949e'; x.font = '26px sans-serif';
x.fillText(S.persona, 64, 590);
// 数据条
const rows = [
  ['总命令数', S.total.toLocaleString()],
  ['探索指数', S.diversity + '%'],
  ['习惯浓度', S.top_share + '%'],
  ['夜行浓度', S.night===null ? '未知' : S.night + '%'],
  ['git 命令', String(S.git)],
  ['sudo 次数', String(S.sudo)],
];
rows.forEach((r,i)=>{
  const y = 690 + i*92;
  x.fillStyle = '#161b22'; x.fillRect(64, y-40, 952, 72);
  x.fillStyle = '#e6edf3'; x.font = 'bold 30px "PingFang SC",sans-serif'; x.textAlign='left';
  x.fillText(r[0], 92, y+8);
  x.fillStyle = '#3fb950'; x.font = '900 38px sans-serif'; x.textAlign='right';
  x.fillText(r[1], 986, y+10); x.textAlign='left';
});
// 最长命令彩蛋
x.fillStyle = '#8b949e'; x.font = '22px sans-serif';
x.fillText('最长一条命令 ' + S.longest_len + ' 字符 —— 你到底在写什么?!', 64, 1300);
x.fillStyle = '#58a6ff'; x.font = 'bold 26px sans-serif';
x.fillText('🔍 搜「小薅薅」看更多', 64, 1352);
x.textAlign='right'; x.fillStyle = '#8b949e'; x.font = '22px sans-serif';
x.fillText('数据 100% 本地分析 · shellmbti', 1016, 1352);
function dl(){ const a=document.createElement('a'); a.download='shellmbti.png'; a.href=c.toDataURL('image/png'); a.click(); }
</script></body></html>"""

# ---------- 6. main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", action="store_true", help="生成分享卡片 HTML")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    a = ap.parse_args()

    hist = find_history()
    if not hist:
        sys.exit("没找到 shell 历史文件 (~/.zsh_history / ~/.bash_history)。先随便敲几条命令再来。")
    cmds, has_ts = parse(hist)
    if len(cmds) < 10:
        sys.exit(f"历史只有 {len(cmds)} 条命令，太少了——先正常用几天终端再来(至少10条)。")

    import datetime
    ts_list = []
    if has_ts:
        for ln in open(hist, encoding="utf-8", errors="ignore"):
            m = re.match(r"^: (\d+):\d+;", ln)
            if m: ts_list.append(int(m.group(1)))

    st = analyze(cmds, has_ts, ts_list)
    st["mbti"] = analyze(cmds, has_ts, ts_list)["mbti"]  # 已含

    if a.json:
        print(json.dumps(st, ensure_ascii=False, indent=2)); return

    if a.card:
        arch = ARCH[st["mbti"]]
        data = dict(mbti=st["mbti"], arch=arch, persona=persona_line(st["mbti"]),
                    total=st["total"], diversity=st["diversity"], top_share=st["top_share"],
                    night=st["night"], git=st["git"], sudo=st["sudo"], longest_len=st["longest_len"])
        html = CARD_TPL.replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__ARCH__", arch)
        out_path = "shellmbti-card.html"
        open(out_path, "w", encoding="utf-8").write(html)
        try: webbrowser.open("file://" + os.path.abspath(out_path))
        except Exception: pass
        print(f"卡片已生成: {os.path.abspath(out_path)} (已在浏览器打开, 点按钮保存图片)")
        return

    term_report(st, hist)

if __name__ == "__main__":
    main()
