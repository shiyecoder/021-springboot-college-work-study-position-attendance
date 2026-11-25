# -*- coding: utf-8 -*-
"""生成 NEW-021 勤工助学系统的可点击 HTML 设计稿（内置假数据，纯静态）。"""
import os, pathlib

BASE = pathlib.Path(__file__).parent
(BASE / "pages").mkdir(exist_ok=True)

FONT = "-apple-system,'PingFang SC','Microsoft YaHei',sans-serif"

CSS = """
:root{--pri:#173B57;--sec:#287271;--bg:#F4F7F9;--acc:#2F6B8A;--ok:#287D4F;--dan:#B42318;
--text:#1B2A35;--text2:#5A6B77;--text3:#8A99A5;--border:#DFE7EC;--radius:7px}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:%s;background:var(--bg);color:var(--text);font-size:13px;line-height:1.6}
.num{font-variant-numeric:tabular-nums}
a{color:var(--acc);text-decoration:none}
.layout{display:flex;height:100vh;overflow:hidden}
.side{width:220px;background:var(--pri);color:#fff;display:flex;flex-direction:column;flex:none}
.brand{height:56px;display:flex;align-items:center;gap:9px;padding:0 18px;font-size:15px;font-weight:600;
border-bottom:1px solid rgba(255,255,255,.12)}
.brand i{width:20px;height:20px;border-radius:5px;background:var(--sec);display:inline-block}
.menu{flex:1;overflow:auto;padding:8px 0}
.grp{padding:12px 18px 5px;font-size:11px;letter-spacing:1px;color:rgba(255,255,255,.45)}
.menu a{display:block;padding:9px 18px;color:rgba(255,255,255,.8);font-size:13px;border-left:3px solid transparent}
.menu a:hover{background:rgba(255,255,255,.06);color:#fff}
.menu a.on{background:rgba(255,255,255,.12);color:#fff;border-left-color:#7FB2C9;font-weight:500}
.main{flex:1;display:flex;flex-direction:column;min-width:0}
.top{height:56px;background:#fff;border-bottom:1px solid var(--border);display:flex;align-items:center;
gap:14px;padding:0 24px;flex:none}
.crumb{color:var(--text3);font-size:12px}
.top .right{margin-left:auto;display:flex;align-items:center;gap:16px;font-size:12px;color:var(--text2)}
.avatar{width:30px;height:30px;border-radius:50%%;background:#D7E3EA;display:inline-block}
.content{flex:1;overflow:auto;padding:24px}
.card{background:#fff;border:1px solid var(--border);border-radius:var(--radius);margin-bottom:16px}
.card-h{display:flex;align-items:center;gap:10px;padding:14px 18px;border-bottom:1px solid var(--border)}
.card-h h2{font-size:14px;font-weight:600}
.card-b{padding:16px 18px}
.filter{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
select,input[type=text],input[type=date]{height:32px;border:1px solid var(--border);border-radius:5px;
padding:0 10px;font-size:13px;background:#fff;color:var(--text);font-family:inherit}
select{min-width:180px}
.btn{height:32px;padding:0 15px;border-radius:5px;border:1px solid var(--border);background:#fff;
font-size:13px;cursor:pointer;font-family:inherit;color:var(--text)}
.btn.pri{background:var(--pri);border-color:var(--pri);color:#fff}
.btn.sec{background:var(--sec);border-color:var(--sec);color:#fff}
.btn.dan{background:#fff;border-color:var(--dan);color:var(--dan)}
.btn.link{border:none;background:none;color:var(--acc);padding:0 6px;height:auto}
table{width:100%%;border-collapse:collapse}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--border);font-size:13px}
th{background:#F8FAFB;color:var(--text2);font-weight:500;white-space:nowrap}
td{white-space:nowrap}
tbody tr:hover{background:#FAFCFD}
.tag{display:inline-block;padding:1px 9px;border-radius:11px;font-size:12px;border:1px solid}
.t-ok{color:var(--ok);border-color:#BFDCCA;background:#F1F8F3}
.t-wa{color:#8A5A00;border-color:#EAD6A8;background:#FDF7E9}
.t-pr{color:var(--acc);border-color:#C3DAE4;background:#F1F7FA}
.t-da{color:var(--dan);border-color:#EBC5C1;background:#FCF3F2}
.t-in{color:var(--text2);border-color:var(--border);background:#F6F8F9}
.stats{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:16px}
.stat{background:#fff;border:1px solid var(--border);border-radius:var(--radius);padding:14px 16px}
.stat .k{font-size:12px;color:var(--text2)}
.stat .v{font-size:22px;font-weight:600;margin-top:4px;color:var(--pri)}
.stat .d{font-size:11px;color:var(--text3);margin-top:2px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.chart{height:210px;display:flex;align-items:flex-end;gap:14px;padding:10px 4px 0}
.bar{flex:1;background:linear-gradient(180deg,#2F6B8A,#173B57);border-radius:4px 4px 0 0;position:relative}
.bar span{position:absolute;top:-18px;left:0;right:0;text-align:center;font-size:11px;color:var(--text2)}
.lbl{display:flex;gap:6px;justify-content:space-around;font-size:11px;color:var(--text3);padding-top:6px}
.tabs{display:flex;gap:4px;border-bottom:1px solid var(--border);margin-bottom:14px}
.tabs div{padding:8px 16px;font-size:13px;color:var(--text2);cursor:pointer;border-bottom:2px solid transparent}
.tabs div.on{color:var(--pri);border-bottom-color:var(--pri);font-weight:500}
.pager{display:flex;justify-content:flex-end;align-items:center;gap:8px;padding:12px 16px;color:var(--text2);font-size:12px}
.pager span{padding:3px 9px;border:1px solid var(--border);border-radius:4px;background:#fff}
.pager span.on{background:var(--pri);color:#fff;border-color:var(--pri)}
.muted{color:var(--text3);font-size:12px}
.timeline{padding-left:6px}
.tl{display:flex;gap:12px;padding-bottom:16px;position:relative}
.tl:before{content:'';position:absolute;left:5px;top:14px;bottom:0;width:1px;background:var(--border)}
.tl:last-child:before{display:none}
.dot{width:11px;height:11px;border-radius:50%%;background:#fff;border:2px solid var(--sec);margin-top:4px;flex:none}
.tl .txt b{font-size:13px;display:block}
.tl .txt span{font-size:12px;color:var(--text3)}
.form{display:grid;grid-template-columns:120px 1fr;gap:12px 10px;align-items:center;max-width:620px}
.form label{color:var(--text2);font-size:13px;text-align:right}
.form input,.form select,.form textarea{width:100%%;border:1px solid var(--border);border-radius:5px;
padding:6px 10px;font-size:13px;font-family:inherit;background:#fff}
.form textarea{grid-column:2;height:70px;resize:vertical}
.kv{display:grid;grid-template-columns:110px 1fr 110px 1fr;gap:10px 8px;font-size:13px}
.kv dt{color:var(--text3)}
.score-row{display:flex;align-items:center;gap:10px;margin-bottom:10px;font-size:13px}
.score-row .nm{width:96px;color:var(--text2)}
.score-row .bar2{flex:1;height:8px;background:#EDF2F5;border-radius:4px;overflow:hidden}
.score-row .bar2 i{display:block;height:100%%;background:var(--sec)}
.thumb{width:56px;height:42px;border-radius:4px;object-fit:cover;background:#E7EEF2;display:inline-block}
.empty{padding:38px;text-align:center;color:var(--text3)}
""" % FONT

MENUS = [
    ("工作台", [("dashboard", "资助总览"), ("todo", "我的待办")]),
    ("岗位与申请", [("post-square", "岗位广场"), ("my-apply", "我的申请"), ("post-mgr", "岗位管理"), ("post-audit", "岗位审批")]),
    ("录用与排班", [("employment", "录用审核台"), ("shift", "排班管理"), ("my-shift", "我的排班")]),
    ("考勤与工时", [("attendance", "考勤复核"), ("check", "签到签退"), ("hours", "工时复核")]),
    ("补贴与评价", [("subsidy", "补贴核算"), ("pay", "发放登记"), ("evaluate", "学期评价")]),
    ("配置与统计", [("standard", "学期与标准"), ("rule", "匹配规则"), ("score", "计算留痕"), ("report", "用工分析")]),
    ("系统", [("user", "用户管理"), ("role", "角色管理"), ("menu", "菜单管理")]),
]


def shell(title, active, body, role="资助中心管理员"):
    links = []
    for grp, items in MENUS:
        links.append(f'<div class="grp">{grp}</div>')
        for slug, name in items:
            on = " on" if slug == active else ""
            links.append(f'<a class="{on.strip()}" href="{slug}.html">{name}</a>')
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>{title} · 勤工助学岗位与考勤管理系统</title><link rel="stylesheet" href="assets/style.css"></head>
<body><div class="layout">
<aside class="side"><div class="brand"><i></i>勤工助学管理</div><nav class="menu">
{''.join(links)}</nav></aside>
<div class="main"><header class="top"><span class="crumb">首页 / {title}</span>
<div class="right"><span>{role}</span><span class="avatar"></span></div></header>
<main class="content">{body}</main></div></div></body></html>"""


def page_stat(k, v, d=""):
    return f'<div class="stat"><div class="k">{k}</div><div class="v num">{v}</div><div class="d">{d}</div></div>'


def table(headers, rows, pager="共 32 条"):
    th = "".join(f"<th>{h}</th>" for h in headers)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"""<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>
<div class="pager"><span>{pager}</span><span class="on">1</span><span>2</span><span>3</span><span>4</span>
<span class="muted">10 条/页</span></div>"""


PAGES = {}

# 1 工作台
PAGES["dashboard"] = ("资助总览", "dashboard", f"""
<div class="stats">
{page_stat("在招岗位", "26", "较上月 +4")}{page_stat("申请人数", "318", "本周 42")}
{page_stat("录用率", "38.6%", "目标 35%")}{page_stat("本月完成工时", "4,286", "上限内 96%")}
{page_stat("考勤缺勤率", "2.4%", "较上月 -0.6pp")}{page_stat("本月补贴支出", "¥ 62,480", "待发放 1 批")}
</div>
<div class="grid2">
<div class="card"><div class="card-h"><h2>近 6 个月申请与录用趋势</h2><span class="muted" style="margin-left:auto">单位：人</span></div>
<div class="card-b"><div class="chart">
<div class="bar" style="height:52%"><span>38</span></div><div class="bar" style="height:63%"><span>45</span></div>
<div class="bar" style="height:71%"><span>52</span></div><div class="bar" style="height:58%"><span>41</span></div>
<div class="bar" style="height:82%"><span>60</span></div><div class="bar" style="height:76%"><span>56</span></div>
</div><div class="lbl"><span>5月</span><span>6月</span><span>7月</span><span>8月</span><span>9月</span><span>10月</span></div></div></div>
<div class="card"><div class="card-h"><h2>岗位状态分布</h2></div><div class="card-b">
<div class="score-row"><span class="nm">招聘中</span><div class="bar2"><i style="width:46%"></i></div><span class="num">12</span></div>
<div class="score-row"><span class="nm">待审核</span><div class="bar2"><i style="width:23%"></i></div><span class="num">6</span></div>
<div class="score-row"><span class="nm">已满额</span><div class="bar2"><i style="width:19%"></i></div><span class="num">5</span></div>
<div class="score-row"><span class="nm">已结束</span><div class="bar2"><i style="width:12%"></i></div><span class="num">3</span></div>
<div class="score-row"><span class="nm">草稿</span><div class="bar2"><i style="width:8%"></i></div><span class="num">2</span></div>
</div></div></div>
<div class="grid2">
<div class="card"><div class="card-h"><h2>用工部门工时排行</h2></div><div class="card-b">
{"".join(f'<div class="score-row"><span class="nm">{n}</span><div class="bar2"><i style="width:{w}%%"></i></div><span class="num">{h}</span></div>' for n, w, h in [("图书馆", 92, "1,024"), ("教务处", 74, "826"), ("实验中心", 61, "688"), ("后勤保障处", 48, "542"), ("学工部", 33, "376")])}
</div></div>
<div class="card"><div class="card-h"><h2>考勤异常类型构成</h2></div><div class="card-b">
{"".join(f'<div class="score-row"><span class="nm">{n}</span><div class="bar2"><i style="width:{w}%%"></i></div><span class="num">{h}</span></div>' for n, w, h in [("迟到", 58, "31"), ("早退", 41, "22"), ("缺勤", 26, "14"), ("未签退", 33, "18")])}
</div></div></div>
<div class="card"><div class="card-h"><h2>待我处理</h2><span class="muted" style="margin-left:auto">按待办优先、更新时间倒序</span></div>
{table(["业务编号", "类型", "岗位/学生", "当前状态", "责任人", "更新时间", "操作"],
 [["WS-2026-0087", "岗位审批", "图书馆阅览室值班", '<span class="tag t-wa">待审核</span>', "资助中心 王敏", "2026-10-31 09:12:04", '<button class="btn link">审批</button>'],
  ["AP-2026-0412", "录用审核", "张一凡 · 实验中心助理", '<span class="tag t-pr">待面试</span>', "实验中心 李强", "2026-10-30 16:40:11", '<button class="btn link">处理</button>'],
  ["AP-2026-0409", "工时申诉", "陈思远 · 10 月工时", '<span class="tag t-da">已退回</span>', "图书馆 周岚", "2026-10-30 11:08:37", '<button class="btn link">复核</button>']])}
</div>""")

# 2 岗位广场
rows = [[f'<span class="thumb"></span>', f"WS-2026-00{i:02d}<br><b>{n}</b>", d, f"{c}", f"{p} 元/时",
         f"{h} 时/周", '<span class="tag t-ok">招聘中</span>', '<button class="btn link">查看</button><button class="btn link">申请</button>']
        for i, (n, d, c, p, h) in enumerate([
            ("图书馆阅览室值班", "图书馆", "2 人", "22", "8"), ("实验中心设备维护助理", "实验中心", "3 人", "25", "10"),
            ("教务处资料整理", "教务处", "1 人", "20", "6"), ("迎新志愿服务岗", "学工部", "8 人", "18", "6"),
            ("档案室数字化助理", "档案馆", "2 人", "22", "8"), ("体育场馆管理员", "体育部", "2 人", "20", "8"),
            ("机房值守助理", "信息中心", "4 人", "24", "10"), ("食堂文明督导", "后勤保障处", "6 人", "18", "6")], start=1)]
PAGES["post-square"] = ("岗位广场", "post-square", f"""
<div class="card"><div class="card-b"><div class="filter">
<select><option>全部用工部门</option><option>图书馆</option><option>实验中心</option></select>
<select><option>全部岗位类型</option><option>助管</option><option>助教</option><option>助研</option></select>
<select><option>全部时段</option><option>工作日上午</option><option>工作日下午</option><option>周末</option></select>
<select><option>全部状态</option><option>招聘中</option></select>
<input type="text" placeholder="岗位名称 / 编号" style="width:220px">
<button class="btn pri">查询</button><button class="btn">重置</button>
<button class="btn" style="margin-left:auto">高级筛选</button></div></div></div>
<div class="card"><div class="card-h"><h2>可申请岗位</h2><span class="muted" style="margin-left:auto">共 26 个岗位在招</span></div>
{table(["封面", "岗位编号 / 名称", "用工部门", "招聘人数", "时薪标准", "周工时", "状态", "操作"], rows)}
</div>""")

# 3 岗位审批
PAGES["post-audit"] = ("岗位审批", "post-audit", f"""
<div class="stats">{page_stat("待审核", "6", "超 3 天 1 个")}{page_stat("本月通过", "18", "通过率 75%")}
{page_stat("本月驳回", "6", "预算超 2 例")}{page_stat("在用岗位", "26", "覆盖 9 个部门")}</div>
<div class="card"><div class="card-h"><h2>待审核岗位</h2>
<div style="margin-left:auto" class="filter"><select><option>全部部门</option></select>
<button class="btn">批量通过</button></div></div>
{table(["岗位编号", "岗位名称", "用工部门", "招聘人数", "预算(元)", "指导老师", "提交时间", "状态", "操作"],
 [["WS-2026-0087", "图书馆阅览室值班", "图书馆", "2", "12,800", "周岚", "2026-10-31 09:12", '<span class="tag t-wa">待审核</span>', '<button class="btn link">审批</button>'],
  ["WS-2026-0088", "实验中心设备维护助理", "实验中心", "3", "24,000", "李强", "2026-10-30 15:22", '<span class="tag t-wa">待审核</span>', '<button class="btn link">审批</button>'],
  ["WS-2026-0089", "迎新志愿服务岗", "学工部", "8", "18,600", "赵敏", "2026-10-30 10:05", '<span class="tag t-wa">待审核</span>', '<button class="btn link">审批</button>'],
  ["WS-2026-0086", "机房值守助理", "信息中心", "4", "31,200", "孙浩", "2026-10-28 14:31", '<span class="tag t-ok">招聘中</span>', '<button class="btn link">查看</button>'],
  ["WS-2026-0085", "档案室数字化助理", "档案馆", "2", "13,600", "钱伟", "2026-10-27 09:48", '<span class="tag t-ok">招聘中</span>', '<button class="btn link">查看</button>']])}
</div>
<div class="card"><div class="card-h"><h2>审批抽屉预览（必要性 / 预算 / 安全风险 / 人数）</h2></div>
<div class="card-b"><div class="kv">
<dt>岗位编号</dt><dd class="num">WS-2026-0087</dd><dt>当前状态</dt><dd><span class="tag t-wa">待审核</span></dd>
<dt>用工部门</dt><dd>图书馆</dd><dt>责任人</dt><dd>周岚</dd>
<dt>预算合计</dt><dd class="num">¥ 12,800</dd><dt>招聘人数</dt><dd class="num">2</dd>
<dt>必要性说明</dt><dd style="grid-column:span 3">阅览室晚间开放时段需 2 名学生值守，负责借还登记与秩序维护，工作量经测算为每周 8 小时/人。</dd>
</div><div style="margin-top:14px" class="filter"><button class="btn sec">通过并发布</button>
<button class="btn dan">驳回</button><button class="btn">退回修改</button></div></div></div>""")

# 4 录用审核台（创新点）
PAGES["employment"] = ("录用审核台", "employment", f"""
<div class="card"><div class="card-b"><div class="kv">
<dt>申请编号</dt><dd class="num">AP-2026-0412</dd><dt>当前状态</dt><dd><span class="tag t-pr">待面试</span></dd>
<dt>岗位</dt><dd>实验中心设备维护助理</dd><dt>责任人</dt><dd>李强</dd>
<dt>创建时间</dt><dd class="num">2026-10-28 10:22:31</dd><dt>最近更新</dt><dd class="num">2026-10-30 16:40:11</dd></div></div></div>
<div class="grid2">
<div class="card"><div class="card-h"><h2>公平匹配参考分（规则 v3 · 2026-09-01 生效）</h2>
<span class="tag t-ok" style="margin-left:auto">推荐录用</span></div><div class="card-b">
<div style="font-size:30px;font-weight:600;color:var(--pri)" class="num">82.6<span class="muted" style="font-size:13px"> / 100</span></div>
<div class="muted" style="margin-bottom:14px">等级：A（建议优先录用）。所有输入项与得分对审核老师可见。</div>
{"".join(f'<div class="score-row"><span class="nm">{n}</span><div class="bar2"><i style="width:{v}%%"></i></div><span class="num">{v} × {w}%%</span></div>' for n, v, w in [("困难等级", 96, 30), ("课表冲突", 80, 15), ("技能匹配度", 88, 20), ("已获工时", 70, 15), ("历史缺勤次数", 90, 10), ("岗位偏好", 75, 10)])}
<div style="margin-top:14px;padding:10px 12px;background:#F6F9FA;border-left:3px solid var(--sec);font-size:12px;color:var(--text2)">
< b>主要影响因素：</b>困难认定等级为特别困难（+28.8 分）；技能匹配「计算机/网络维护」标签命中 4 项。<br>
<b>未满足条件：</b>周二下午有课程冲突（<span style="color:var(--dan)">-3.0 分</span>）。<br>
<b>可改进项：</b>若调整班次至周四晚间，预计总分提升至 85.2。</div></div></div>
<div class="card"><div class="card-h"><h2>人工修正记录</h2></div><div class="card-b"><div class="timeline">
<div class="tl"><div class="dot"></div><div class="txt"><b>系统计算 82.6 分 · A 级</b><span>2026-10-30 16:12:08 · 规则 v3</span></div></div>
<div class="tl"><div class="dot"></div><div class="txt"><b>李强 人工调整为 B 级</b><span>2026-10-30 16:20:44 · 原因：面试沟通表达明显不足，暂列候补</span></div></div>
<div class="tl"><div class="dot"></div><div class="txt"><b>李强 录用</b><span>2026-10-30 16:40:11 · 原因：候补第一位，岗位缺员补充</span></div></div>
</div><div class="filter" style="margin-top:8px"><button class="btn sec">录用</button><button class="btn dan">驳回</button>
<button class="btn">人工修正</button></div></div></div></div>
<div class="card"><div class="card-h"><h2>候选人对比（同岗位 6 人）</h2></div>
{table(["排名", "学生", "学院", "困难等级", "匹配分", "课表冲突", "历史缺勤", "建议", "操作"],
 [["1", "张一凡", "计算机学院", "特别困难", "82.6", "周二下午", "0", '<span class="tag t-ok">推荐</span>', '<button class="btn link">录用</button>'],
  ["2", "陈思远", "电子信息学院", "一般困难", "76.4", "无", "1", '<span class="tag t-pr">备选</span>', '<button class="btn link">录用</button>'],
  ["3", "李梦瑶", "机械工程学院", "不困难", "68.1", "周四上午", "0", '<span class="tag t-in">一般</span>', '<button class="btn link">录用</button>'],
  ["4", "王浩然", "计算机学院", "特别困难", "65.9", "周三全天", "3", '<span class="tag t-wa">不推荐</span>', '<button class="btn link">驳回</button>']])}</div>""")

# 5 排班管理
PAGES["shift"] = ("排班管理", "shift", f"""
<div class="card"><div class="card-b"><div class="filter">
<select><option>图书馆阅览室值班</option></select><input type="date" value="2026-10-26">
<button class="btn pri">查询</button><button class="btn sec" style="margin-left:auto">按周生成班次</button>
<button class="btn">冲突检测</button></div></div></div>
<div class="card"><div class="card-h"><h2>2026-10-26 ~ 2026-11-01 排班表</h2>
<span class="tag t-wa" style="margin-left:auto">检测到 2 处冲突</span></div>
{table(["班次编号", "日期", "时段", "地点", "学生", "计划工时", "冲突校验", "状态", "操作"],
 [["SH-2610-01", "10-26 周一", "18:00-22:00", "图书馆 3F", "张一凡", "4.0", '<span class="tag t-ok">通过</span>', '<span class="tag t-ok">已确认</span>', '<button class="btn link">编辑</button>'],
  ["SH-2610-02", "10-27 周二", "18:00-22:00", "图书馆 3F", "陈思远", "4.0", '<span class="tag t-da">与课程冲突</span>', '<span class="tag t-wa">待调整</span>', '<button class="btn link">编辑</button>'],
  ["SH-2610-03", "10-28 周三", "14:00-18:00", "图书馆 2F", "李梦瑶", "4.0", '<span class="tag t-ok">通过</span>', '<span class="tag t-ok">已确认</span>', '<button class="btn link">编辑</button>'],
  ["SH-2610-04", "10-29 周四", "18:00-22:00", "图书馆 3F", "张一凡", "4.0", '<span class="tag t-da">已有班次</span>', '<span class="tag t-wa">待调整</span>', '<button class="btn link">编辑</button>'],
  ["SH-2610-05", "10-31 周六", "09:00-17:00", "图书馆 1F", "王浩然", "7.0", '<span class="tag t-ok">通过</span>', '<span class="tag t-ok">已确认</span>', '<button class="btn link">编辑</button>']])}</div>""")

# 6 签到签退
PAGES["check"] = ("签到签退", "check", f"""
<div class="grid3">
<div class="card"><div class="card-h"><h2>今日班次</h2></div><div class="card-b">
<div class="kv" style="grid-template-columns:88px 1fr"><dt>班次</dt><dd class="num">SH-2610-05</dd>
<dt>岗位</dt><dd>图书馆阅览室值班</dd><dt>时段</dt><dd class="num">09:00-17:00</dd>
<dt>地点</dt><dd>图书馆 1F</dd></div>
<div class="filter" style="margin-top:16px"><button class="btn sec">签到</button><button class="btn">签退</button>
<button class="btn">补卡申请</button></div></div></div>
<div class="card"><div class="card-h"><h2>页面验证码</h2></div><div class="card-b">
<div style="font-size:26px;letter-spacing:8px;font-weight:600;color:var(--pri);background:#F1F7FA;border:1px dashed var(--border);border-radius:6px;text-align:center;padding:18px 0" class="num">7 3 8 2</div>
<input type="text" placeholder="请输入验证码" style="width:100%%;margin-top:12px;height:34px;border:1px solid var(--border);border-radius:5px;padding:0 10px">
<div class="muted" style="margin-top:8px">验证码 5 分钟内有效，连续 3 次错误需重新获取</div></div></div>
<div class="card"><div class="card-h"><h2>本月考勤</h2></div><div class="card-b">
<div class="kv" style="grid-template-columns:88px 1fr"><dt>出勤</dt><dd class="num">18 天</dd><dt>迟到</dt><dd class="num">1 次</dd>
<dt>早退</dt><dd class="num">0 次</dd><dt>缺勤</dt><dd class="num">0 次</dd><dt>有效工时</dt><dd class="num">71.5 时</dd></div></div></div></div>
<div class="card"><div class="card-h"><h2>考勤明细</h2></div>
{table(["日期", "班次", "签到", "签退", "实际工时", "状态", "异常说明"],
 [["2026-10-31", "SH-2610-05", "08:56:12", "--", "--", '<span class="tag t-pr">进行中</span>', "-"],
  ["2026-10-29", "SH-2610-04", "18:02:41", "22:05:10", "4.0", '<span class="tag t-ok">正常</span>', "-"],
  ["2026-10-28", "SH-2610-03", "14:09:33", "18:03:02", "3.9", '<span class="tag t-wa">迟到</span>', "迟到 9 分钟，已扣减 0.5 时"],
  ["2026-10-27", "SH-2610-02", "17:58:04", "22:01:55", "4.0", '<span class="tag t-ok">正常</span>', "-"],
  ["2026-10-26", "SH-2610-01", "18:01:20", "21:48:11", "3.8", '<span class="tag t-wa">早退</span>', "早退 12 分钟"]])}</div>""")

# 7 工时复核
PAGES["hours"] = ("工时复核", "hours", f"""
<div class="tabs"><div class="on">待复核 12</div><div>已确认 46</div><div>申诉中 3</div><div>全部</div></div>
<div class="card"><div class="card-h"><h2>2026 年 10 月工时汇总</h2>
<div class="filter" style="margin-left:auto"><select><option>全部部门</option></select>
<button class="btn sec">批量确认</button><button class="btn">导出</button></div></div>
{table(["学生", "学院", "岗位", "排班工时", "实际工时", "有效工时", "月上限", "状态", "操作"],
 [["张一凡", "计算机学院", "图书馆阅览室值班", "32.0", "31.8", "31.5", "40", '<span class="tag t-wa">待确认</span>', '<button class="btn link">复核</button>'],
  ["陈思远", "电子信息学院", "实验中心设备维护", "40.0", "41.2", "39.0", "40", '<span class="tag t-wa">待确认</span>', '<button class="btn link">复核</button>'],
  ["李梦瑶", "机械工程学院", "档案室数字化助理", "24.0", "24.0", "24.0", "40", '<span class="tag t-ok">已确认</span>', '<button class="btn link">查看</button>'],
  ["王浩然", "计算机学院", "机房值守助理", "44.0", "44.0", "40.0", "40", '<span class="tag t-da">超上限待审批</span>', '<button class="btn link">特别审批</button>']])}</div>
<div class="card"><div class="card-h"><h2>工时申诉</h2></div>
{table(["申诉编号", "学生", "月份", "申诉工时", "原因", "提交时间", "状态", "操作"],
 [["APL-0007", "陈思远", "2026-10", "2.0", "10-22 临时顶班未计入排班", "2026-10-30 11:08", '<span class="tag t-wa">待处理</span>', '<button class="btn link">处理</button>'],
  ["APL-0006", "张一凡", "2026-10", "0.5", "迟到扣减不合理，当日系统故障", "2026-10-29 09:12", '<span class="tag t-ok">已通过</span>', '<button class="btn link">查看</button>']])}</div>""")

# 8 补贴核算
PAGES["subsidy"] = ("补贴核算", "subsidy", f"""
<div class="stats">{page_stat("本月批次", "2", "1 待审核")}{page_stat("核算人数", "46", "覆盖 9 部门")}
{page_stat("补贴总额", "¥ 62,480", "较上月 +6.2%")}{page_stat("已发放", "¥ 0", "财务待登记")}
{page_stat("异常待处理", "3", "含 1 笔退回")}{page_stat("平均时薪", "¥ 21.6", "含系数 1.2")}</div>
<div class="card"><div class="card-h"><h2>补贴批次</h2><button class="btn pri" style="margin-left:auto">生成批次</button></div>
{table(["批次号", "学期", "月份", "人数", "总工时", "补贴总额", "状态", "操作"],
 [["SB-2026-10-A", "2026 秋季", "2026-10", "46", "2,893", "¥ 62,480", '<span class="tag t-wa">待财务审核</span>', '<button class="btn link">查看明细</button>'],
  ["SB-2026-09-A", "2026 秋季", "2026-09", "44", "2,712", "¥ 58,836", '<span class="tag t-ok">已发放</span>', '<button class="btn link">查看明细</button>'],
  ["SB-2026-06-A", "2026 春季", "2026-06", "41", "2,486", "¥ 52,206", '<span class="tag t-ok">已发放</span>', '<button class="btn link">查看明细</button>']])}</div>
<div class="card"><div class="card-h"><h2>批次明细（SB-2026-10-A）</h2><span class="muted" style="margin-left:auto">金额由后端按工时 × 标准 × 系数计算</span></div>
{table(["学生", "岗位", "有效工时", "时薪", "系数", "应发金额", "发放状态"],
 [["张一凡", "图书馆阅览室值班", "31.5", "22.00", "1.0", "¥ 693.00", '<span class="tag t-in">待发放</span>'],
  ["陈思远", "实验中心设备维护助理", "39.0", "25.00", "1.2", "¥ 1,170.00", '<span class="tag t-in">待发放</span>'],
  ["李梦瑶", "档案室数字化助理", "24.0", "22.00", "1.0", "¥ 528.00", '<span class="tag t-in">待发放</span>'],
  ["王浩然", "机房值守助理", "40.0", "24.00", "1.0", "¥ 960.00", '<span class="tag t-da">发放失败</span>']])}</div>""")

# 9 发放登记
PAGES["pay"] = ("发放登记", "pay", f"""
<div class="card"><div class="card-b"><div class="filter"><select><option>SB-2026-10-A</option></select>
<select><option>全部状态</option><option>待发放</option><option>已发放</option><option>失败</option></select>
<button class="btn pri">查询</button><button class="btn sec" style="margin-left:auto">登记已发放</button></div></div></div>
<div class="card"><div class="card-h"><h2>发放明细</h2><span class="tag t-in" style="margin-left:auto">批次已审核，金额锁定不可修改</span></div>
{table(["学生", "学号", "金额", "银行卡后四位", "发放状态", "发放时间", "操作"],
 [["张一凡", "2023010214", "¥ 693.00", "4821", '<span class="tag t-ok">已发放</span>', "2026-10-31 14:22", '<button class="btn link">查看</button>'],
  ["陈思远", "2023020377", "¥ 1,170.00", "9034", '<span class="tag t-ok">已发放</span>', "2026-10-31 14:22", '<button class="btn link">查看</button>'],
  ["王浩然", "2023030119", "¥ 960.00", "1177", '<span class="tag t-da">发放失败</span>', "2026-10-31 14:22", '<button class="btn link">重试</button>'],
  ["李梦瑶", "2023040552", "¥ 528.00", "6620", '<span class="tag t-in">待发放</span>', "-", '<button class="btn link">登记</button>']])}</div>
<div class="card"><div class="card-h"><h2>差错调整单</h2></div>
{table(["调整单号", "关联批次", "学生", "调整金额", "原因", "状态"],
 [["ADJ-0003", "SB-2026-09-A", "王浩然", "- ¥ 120.00", "9 月重复计入 5 小时工时", '<span class="tag t-wa">下期调整</span>']])}</div>""")

# 10 学期与标准
PAGES["standard"] = ("学期与标准", "standard", f"""
<div class="grid2">
<div class="card"><div class="card-h"><h2>学期配置</h2><button class="btn pri" style="margin-left:auto">新增学期</button></div>
{table(["学期", "起止日期", "状态", "月工时上限", "操作"],
 [["2026 秋季", "2026-09-01 ~ 2027-01-15", '<span class="tag t-ok">进行中</span>', "40", '<button class="btn link">编辑</button>'],
  ["2026 春季", "2026-02-24 ~ 2026-07-10", '<span class="tag t-in">已结束</span>', "40", '<button class="btn link">编辑</button>']])}</div>
<div class="card"><div class="card-h"><h2>补贴标准</h2></div>
{table(["适用学期", "每小时标准", "月工时上限", "特殊岗位系数", "生效时间"],
 [["2026 秋季", "¥ 22.00", "40", "1.2", "2026-09-01"],
  ["2026 春季", "¥ 21.00", "40", "1.15", "2026-02-24"]])}</div></div>
<div class="card"><div class="card-h"><h2>特殊岗位系数</h2><button class="btn" style="margin-left:auto">新增系数</button></div>
{table(["岗位类型", "系数", "说明", "状态"],
 [["实验室助理/设备维护", "1.20", "含设备操作风险", '<span class="tag t-ok">启用</span>'],
  ["夜间值守", "1.15", "22:00 后时段", '<span class="tag t-ok">启用</span>'],
  ["普通助管", "1.00", "默认系数", '<span class="tag t-ok">启用</span>']])}</div></div>""")

# 11 匹配规则
PAGES["rule"] = ("匹配规则", "rule", f"""
<div class="card"><div class="card-h"><h2>公平匹配权重配置（当前生效版本 v3）</h2>
<span class="tag t-ok" style="margin-left:auto">权重合计 100%</span></div><div class="card-b">
{"".join(f'<div class="score-row"><span class="nm">{n}</span><input type="text" value="{w}" style="width:90px;height:30px;border:1px solid var(--border);border-radius:5px;padding:0 8px" class="num"><span class="muted">%　{n2}</span></div>' for n, w, n2 in [("困难等级", 30, "特别困难 100 分，困难 80，一般 60，不困难 40"), ("课表冲突", 15, "无冲突 90，冲突 1 段 60，2 段以上 30"), ("技能匹配度", 20, "按岗位技能标签命中比例"), ("已获工时", 15, "越接近上限得分越低"), ("历史缺勤次数", 10, "每次扣 10 分，3 次以上 0 分"), ("岗位偏好", 10, "首选 100，次选 80，未填 50")])}
<div style="margin-top:16px;padding:10px 12px;background:#F6F9FA;border-left:3px solid var(--acc);font-size:12px;color:var(--text2)">
修改后需保存为新版本，记录生效时间；已生成的计算结果不受影响，只有新计算或主动重算才会使用新权重。</div>
<div class="filter" style="margin-top:14px"><button class="btn pri">保存为新版本</button><button class="btn">恢复默认</button>
<span class="muted" style="margin-left:auto">校验：合计必须等于 100%，否则拒绝保存</span></div></div></div>
<div class="card"><div class="card-h"><h2>规则版本历史</h2></div>
{table(["版本", "生效时间", "修改人", "权重摘要", "状态"],
 [["v3", "2026-09-01 00:00:00", "王敏", "30/15/20/15/10/10", '<span class="tag t-ok">生效中</span>'],
  ["v2", "2026-03-01 00:00:00", "王敏", "25/20/20/15/10/10", '<span class="tag t-in">已归档</span>']])}</div>""")

# 12 计算留痕
PAGES["score"] = ("计算留痕", "score", f"""
<div class="card"><div class="card-b"><div class="filter"><select><option>全部岗位</option></select>
<select><option>全部规则版本</option><option>v3</option><option>v2</option></select>
<input type="date" value="2026-10-01"><button class="btn pri">查询</button>
<span class="muted" style="margin-left:auto">相同输入 + 相同规则版本 = 相同结果（可复算）</span></div></div></div>
<div class="card"><div class="card-h"><h2>计算结果留痕</h2></div>
{table(["计算编号", "学生", "岗位", "规则版本", "总分", "等级", "人工调整", "计算时间", "操作"],
 [["SC-000412", "张一凡", "实验中心设备维护助理", "v3", "82.6", '<span class="tag t-ok">A</span>', "B（李强）", "2026-10-30 16:12:08", '<button class="btn link">查看快照</button>'],
  ["SC-000411", "陈思远", "实验中心设备维护助理", "v3", "76.4", '<span class="tag t-pr">B</span>', "无", "2026-10-30 16:11:52", '<button class="btn link">查看快照</button>'],
  ["SC-000410", "王浩然", "机房值守助理", "v3", "65.9", '<span class="tag t-wa">C</span>', "无", "2026-10-30 15:44:03", '<button class="btn link">查看快照</button>'],
  ["SC-000398", "李梦瑶", "档案室数字化助理", "v2", "68.1", '<span class="tag t-wa">C</span>', "无", "2026-09-18 10:02:31", '<button class="btn link">查看快照</button>']])}</div>
<div class="card"><div class="card-h"><h2>输入快照（SC-000412）</h2></div><div class="card-b">
<div class="kv"><dt>困难等级</dt><dd>特别困难（96 分）</dd><dt>课表冲突</dt><dd>周二下午（80 分）</dd>
<dt>技能匹配</dt><dd>命中 4/5 项（88 分）</dd><dt>已获工时</dt><dd>本月 12 时（70 分）</dd>
<dt>历史缺勤</dt><dd>0 次（90 分）</dd><dt>岗位偏好</dt><dd>次选（75 分）</dd></div>
<div class="muted" style="margin-top:12px">生成时间 2026-10-30 16:12:08 · 规则快照 JSON 已归档，可一键复算验证一致性。</div></div></div>""")

# 13 用工分析
PAGES["report"] = ("用工分析", "report", f"""
<div class="stats">{page_stat("岗位数", "26", "9 个部门")}{page_stat("申请人数", "318", "录用 123")}
{page_stat("录用率", "38.6%", "环比 +2.1pp")}{page_stat("完成工时", "2,893", "本月")}
{page_stat("缺勤率", "2.4%", "异常 85 条")}{page_stat("支出", "¥ 62,480", "本月")}</div>
<div class="grid3">
<div class="card"><div class="card-h"><h2>岗位类型分布</h2></div><div class="card-b">
{"".join(f'<div class="score-row"><span class="nm">{n}</span><div class="bar2"><i style="width:{w}%%"></i></div><span class="num">{c}</span></div>' for n, w, c in [("助管", 88, "11"), ("助教", 46, "6"), ("助研", 40, "5"), ("志愿", 32, "4")])}</div></div>
<div class="card"><div class="card-h"><h2>申请/录用转化</h2></div><div class="card-b"><div class="chart">
<div class="bar" style="height:90%"><span>318</span></div><div class="bar" style="height:52%"><span>186</span></div>
<div class="bar" style="height:35%"><span>123</span></div></div>
<div class="lbl"><span>申请</span><span>面试</span><span>录用</span></div></div></div>
<div class="card"><div class="card-h"><h2>满意度分布</h2></div><div class="card-b">
{"".join(f'<div class="score-row"><span class="nm">{n}</span><div class="bar2"><i style="width:{w}%%"></i></div><span class="num">{c}</span></div>' for n, w, c in [("5 分", 62, "28"), ("4 分", 76, "34"), ("3 分", 20, "9"), ("2 分以下", 6, "2")])}</div></div></div>
<div class="card"><div class="card-h"><h2>推荐采纳率与人工调整率</h2><span class="muted" style="margin-left:auto">用于验证创新模块效果</span></div>
{table(["岗位", "计算次数", "推荐采纳", "人工调整", "采纳率", "调整后结果"],
 [["实验中心设备维护助理", "6", "4", "2", "66.7%", "2 人录用、1 人候补"],
  ["机房值守助理", "9", "7", "2", "77.8%", "4 人录用"],
  ["图书馆阅览室值班", "12", "10", "2", "83.3%", "2 人录用"]])}</div>""")

# 14 学期评价
PAGES["evaluate"] = ("学期评价", "evaluate", f"""
<div class="card"><div class="b card-h"><h2>2026 秋季学期评价</h2>
<span class="muted" style="margin-left:auto">用工老师评分 + 学生岗位反馈</span></div>
{table(["学生", "岗位", "出勤(30)", "责任(30)", "技能(25)", "协作(15)", "总分", "学生反馈", "状态"],
 [["张一凡", "图书馆阅览室值班", "28", "27", "23", "14", "92.0", "岗位与专业相关，希望增加培训", '<span class="tag t-ok">已完成</span>'],
  ["陈思远", "实验中心设备维护助理", "26", "24", "24", "12", "86.0", "工作强度适中", '<span class="tag t-wa">待学生确认</span>'],
  ["李梦瑶", "档案室数字化助理", "30", "28", "21", "13", "92.0", "—", '<span class="tag t-in">待评价</span>']])}</div>
<div class="card"><div class="card-h"><h2>评分录入</h2></div><div class="card-b"><div class="form">
<label>学生</label><input type="text" value="张一凡" readonly>
<label>出勤（30）</label><input type="text" value="28">
<label>责任（30）</label><input type="text" value="27">
<label>技能（25）</label><input type="text" value="23">
<label>协作（15）</label><input type="text" value="14">
<label>评语</label><textarea>值守认真，借还登记准确，建议下学期继续留用。</textarea>
</div><div class="filter" style="margin-top:14px"><button class="btn pri">提交评价</button></div></div></div>""")

# 15 用户管理
PAGES["user"] = ("用户管理", "user", f"""
<div class="card"><div class="card-b"><div class="filter"><input type="text" placeholder="姓名 / 学号 / 账号" style="width:220px">
<select><option>全部角色</option><option>学生</option><option>用工部门老师</option><option>资助中心管理员</option><option>财务审核员</option></select>
<button class="btn pri">查询</button><button class="btn pri" style="margin-left:auto">新建用户</button></div></div></div>
<div class="card"><div class="card-h"><h2>用户列表</h2><span class="muted" style="margin-left:auto">共 54 条</span></div>
{table(["头像", "账号", "姓名", "角色", "所属部门/学院", "联系电话", "状态", "操作"],
 [['<span class="avatar"></span>', "admin", "王敏", "资助中心管理员", "学生资助管理中心", "138****2201", '<span class="tag t-ok">启用</span>', '<button class="btn link">编辑</button>'],
  ['<span class="avatar"></span>', "t_zhou", "周岚", "用工部门老师", "图书馆", "139****8820", '<span class="tag t-ok">启用</span>', '<button class="btn link">编辑</button>'],
  ['<span class="avatar"></span>', "s_2023010214", "张一凡", "学生", "计算机学院", "137****4412", '<span class="tag t-ok">启用</span>', '<button class="btn link">编辑</button>'],
  ['<span class="avatar"></span>', "fin_liu", "刘颖", "财务审核员", "计划财务处", "136****9033", '<span class="tag t-in">停用</span>', '<button class="btn link">编辑</button>']])}</div>""")

# 16 角色管理
PAGES["role"] = ("角色管理", "role", f"""
<div class="card"><div class="card-h"><h2>角色与数据范围</h2><button class="btn pri" style="margin-left:auto">新增角色</button></div>
{table(["角色编码", "角色名称", "数据范围", "用户数", "状态", "操作"],
 [["ADMIN", "资助中心管理员", "全部", "2", '<span class="tag t-ok">启用</span>', '<button class="btn link">分配菜单</button>'],
  ["DEPT", "用工部门老师", "本部门", "12", '<span class="tag t-ok">启用</span>', '<button class="btn link">分配菜单</button>'],
  ["STUDENT", "学生", "本人", "38", '<span class="tag t-ok">启用</span>', '<button class="btn link">分配菜单</button>'],
  ["FINANCE", "财务审核员", "全部（只读）", "2", '<span class="tag t-ok">启用</span>', '<button class="btn link">分配菜单</button>']])}</div>
<div class="card"><div class="card-h"><h2>为「用工部门老师」分配菜单</h2></div><div class="card-b">
<div style="font-size:13px;line-height:2.2">
<label><input type="checkbox" checked> 工作台</label>　<label><input type="checkbox" checked> 我的待办</label><br>
<label><input type="checkbox" checked> 岗位与申请</label>　　<label><input type="checkbox" checked> 岗位管理</label>
<label><input type="checkbox" checked> 录用审核台</label><br>
<label><input type="checkbox" checked> 排班管理</label>　<label><input type="checkbox" checked> 考勤复核</label>
<label><input type="checkbox" checked> 工时复核</label><br>
<label><input type="checkbox" checked> 学期评价</label>　<label><input type="checkbox"> 补贴核算</label>
</div><div class="filter" style="margin-top:16px"><button class="btn pri">保存授权</button></div></div></div>""")

# 17 菜单管理
PAGES["menu"] = ("菜单管理", "menu", f"""
<div class="card"><div class="card-h"><h2>菜单树</h2><button class="btn pri" style="margin-left:auto">新增菜单</button></div>
{table(["菜单名称", "类型", "路由", "权限标识", "排序", "可见", "操作"],
 [["工作台", "目录", "/dashboard", "-", "1", "是", '<button class="btn link">编辑</button>'],
  ["岗位广场", "菜单", "/post-square", "post:list", "2", "是", '<button class="btn link">编辑</button>'],
  ["岗位审批", "菜单", "/post-audit", "post:audit", "3", "是", '<button class="btn link">编辑</button>'],
  ["录用审核台", "菜单", "/employment", "employ:review", "4", "是", '<button class="btn link">编辑</button>'],
  ["补贴核算", "菜单", "/subsidy", "subsidy:calc", "5", "是", '<button class="btn link">编辑</button>'],
  ["菜单管理", "菜单", "/menu", "sys:menu", "99", "隐藏", '<button class="btn link">编辑</button>']])}</div>""")

# 18 我的申请
PAGES["my-apply"] = ("我的申请", "my-apply", f"""
<div class="tabs"><div class="on">全部 6</div><div>待筛选 2</div><div>待面试 1</div><div>已录用 2</div><div>已驳回 1</div></div>
<div class="card"><div class="card-h"><h2>我的岗位申请</h2></div>
{table(["申请编号", "岗位", "用工部门", "申请时间", "面试时间", "状态", "操作"],
 [["AP-2026-0412", "实验中心设备维护助理", "实验中心", "2026-10-28 10:22", "2026-11-02 14:00", '<span class="tag t-pr">待面试</span>', '<button class="btn link">撤回</button><button class="btn link">详情</button>'],
  ["AP-2026-0409", "图书馆阅览室值班", "图书馆", "2026-10-25 15:40", "—", '<span class="tag t-ok">已录用</span>', '<button class="btn link">详情</button>'],
  ["AP-2026-0402", "机房值守助理", "信息中心", "2026-10-20 09:12", "—", '<span class="tag t-wa">待筛选</span>', '<button class="btn link">撤回</button>'],
  ["AP-2026-0388", "食堂文明督导", "后勤保障处", "2026-10-12 16:30", "—", '<span class="tag t-da">已驳回</span>', '<button class="btn link">原因</button>']])}</div>
<div class="card"><div class="card-h"><h2>提交申请</h2></div><div class="card-b"><div class="form">
<label>目标岗位</label><input type="text" value="实验中心设备维护助理" readonly>
<label>申请理由</label><textarea>本人为计算机专业大二学生，熟悉常见设备维护，希望通过勤工助学减轻家庭负担并提升实践能力。</textarea>
<label>可用时段</label><input type="text" value="周一至周五 18:00 后，周六全天">
<label>个人简历</label><input type="text" value="已上传：简历-张一凡.pdf">
</div><div class="filter" style="margin-top:14px"><button class="btn pri">提交申请</button><button class="btn">保存草稿</button></div></div></div>""")

# 19 我的排班
PAGES["my-shift"] = ("我的排班", "my-shift", f"""
<div class="card"><div class="card-h"><h2>本周排班（2026-10-26 ~ 11-01）</h2>
<span class="tag t-wa" style="margin-left:auto">周四班次与课程冲突，待老师调整</span></div>
{table(["班次", "日期", "时段", "地点", "岗位", "计划工时", "状态"],
 [["SH-2610-01", "10-26 周一", "18:00-22:00", "图书馆 3F", "阅览室值班", "4.0", '<span class="tag t-ok">已确认</span>'],
  ["SH-2610-04", "10-29 周四", "18:00-22:00", "图书馆 3F", "阅览室值班", "4.0", '<span class="tag t-da">冲突</span>'],
  ["SH-2610-07", "10-31 周六", "09:00-13:00", "图书馆 1F", "阅览室值班", "4.0", '<span class="tag t-ok">已确认</span>']])}</div>
<div class="card"><div class="card-h"><h2>我的工时与补贴</h2></div><div class="card-b">
<div class="stats" style="grid-template-columns:repeat(4,1fr);margin:0">
{page_stat("本月有效工时", "31.5", "上限 40")}{page_stat("预计补贴", "¥ 693.00", "22 元/时")}
{page_stat("累计工时", "186.5", "本学年")}{page_stat("考勤异常", "1", "10-28 迟到")}</div></div></div>""")

# 20 我的待办
PAGES["todo"] = ("我的待办", "todo", f"""
<div class="stats">{page_stat("待处理", "7", "超时 1")}{page_stat("处理中", "4", "—")}
{page_stat("已完成", "126", "本月")}{page_stat("异常", "2", "需关注")}</div>
<div class="card"><div class="card-h"><h2>待我处理</h2><div class="filter" style="margin-left:auto">
<select><option>全部类型</option><option>岗位审批</option><option>录用审核</option><option>工时申诉</option></select></div></div>
{table(["业务编号", "类型", "摘要", "当前状态", "截止时间", "操作"],
 [["WS-2026-0087", "岗位审批", "图书馆阅览室值班", '<span class="tag t-wa">待审核</span>', "2026-11-02", '<button class="btn link">处理</button>'],
  ["APL-0007", "工时申诉", "陈思远 10 月申诉 2.0 时", '<span class="tag t-wa">待处理</span>', "2026-11-03", '<button class="btn link">处理</button>'],
  ["SB-2026-10-A", "补贴审核", "10 月批次待财务审核", '<span class="tag t-wa">待审核</span>', "2026-11-05", '<button class="btn link">处理</button>']])}</div>""")

# 21 登录
LOGIN = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><title>登录 · 勤工助学岗位与考勤管理系统</title>
<link rel="stylesheet" href="assets/style.css"><style>
body{{background:linear-gradient(120deg,#0F2A3D 0%,#173B57 48%,#287271 100%);height:100vh;overflow:hidden}}
.wrap{{display:flex;height:100vh;align-items:center;justify-content:center;gap:0}}
.left{{color:#fff;width:520px;padding-right:60px}}
.left h1{{font-size:30px;line-height:1.4;font-weight:600;margin-bottom:14px}}
.left p{{color:rgba(255,255,255,.72);font-size:14px;line-height:2}}
.pill{{display:inline-block;margin-top:26px;padding:6px 14px;border:1px solid rgba(255,255,255,.28);border-radius:20px;font-size:12px;color:rgba(255,255,255,.85)}}
.panel{{width:372px;background:#fff;border-radius:12px;padding:34px 32px;box-shadow:0 18px 50px rgba(8,24,36,.32)}}
.panel h2{{font-size:20px;margin-bottom:6px;color:#173B57}}
.panel .sub{{font-size:12px;color:#8A99A5;margin-bottom:24px}}
.fld{{margin-bottom:16px}} .fld label{{display:block;font-size:12px;color:#5A6B77;margin-bottom:6px}}
.fld input{{width:100%;height:42px;border:1px solid #DFE7EC;border-radius:7px;padding:0 12px;font-size:14px;font-family:inherit}}
.fld input:focus{{outline:none;border-color:#2F6B8A;box-shadow:0 0 0 3px rgba(47,107,138,.12)}}
.btn-login{{width:100%;height:42px;border:none;border-radius:7px;background:#173B57;color:#fff;font-size:15px;cursor:pointer;margin-top:6px}}
.roles{{display:flex;gap:6px;margin-top:18px;flex-wrap:wrap}}
.roles span{{font-size:11px;padding:3px 9px;border:1px solid #DFE7EC;border-radius:12px;color:#5A6B77;cursor:pointer}}
.roles span:hover{{border-color:#2F6B8A;color:#173B57}}
</style></head><body><div class="wrap">
<div class="left"><h1>高校勤工助学<br>岗位与考勤管理系统</h1>
<p>岗位申报 · 资格审核 · 排班考勤 · 工时复核 · 补贴核算<br>全流程线上留痕，补贴发放可追溯</p>
<span class="pill">2026 秋季学期 · 学生资助管理中心</span></div>
<div class="panel"><h2>账号登录</h2><div class="sub">使用学号或工号登录，首次登录请修改初始密码</div>
<form onsubmit="location.href='dashboard.html';return false">
<div class="fld"><label>账号</label><input type="text" value="admin" autocomplete="username"></div>
<div class="fld"><label>密码</label><input type="password" value="admin123" autocomplete="current-password"></div>
<button class="btn-login" type="submit">登 录</button></form>
<div class="roles"><span>学生 s_2023010214</span><span>用工老师 t_zhou</span><span>财务 fin_liu</span></div>
</div></div></body></html>"""


def main():
    (BASE / "assets" / "style.css").write_text(CSS.strip(), encoding="utf-8")
    (BASE / "login.html").write_text(LOGIN, encoding="utf-8")
    (BASE / "index.html").write_text(
        '<!DOCTYPE html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=login.html">', encoding="utf-8")
    for slug, (title, active, body) in PAGES.items():
        (BASE / f"{slug}.html").write_text(shell(title, active, body), encoding="utf-8")
        (BASE / "pages" / f"{slug}.html").write_text(shell(title, active, body), encoding="utf-8")
    print("pages:", len(PAGES) + 2)


if __name__ == "__main__":
    main()
