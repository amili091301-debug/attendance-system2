#!/usr/bin/env python3
"""学生签到系统 - 纯Python标准库实现（零依赖）"""

import http.server, json, sqlite3, os, urllib.parse, secrets
from datetime import datetime, date, time
from http.cookies import SimpleCookie

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.db')
HOST, PORT = '0.0.0.0', 5000

# ============================================================
# CSS
# ============================================================
CSS = '''
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Microsoft YaHei',sans-serif;background:#f5f7fa;min-height:100vh}
.header{background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:16px 20px;display:flex;justify-content:space-between;align-items:center}
.header h1{font-size:20px}
.header a{color:white;text-decoration:none;font-size:14px;opacity:.8}
.container{max-width:960px;margin:0 auto;padding:20px}
.card{background:white;border-radius:16px;padding:24px;box-shadow:0 4px 12px rgba(0,0,0,.08);margin-bottom:16px}
.btn{display:block;width:100%;padding:14px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;border-radius:8px;font-size:18px;cursor:pointer;font-weight:bold}
.btn:active{opacity:.9}.btn:disabled{opacity:.5;cursor:not-allowed}
input,select{width:100%;padding:12px 16px;margin-bottom:12px;border:2px solid #e0e0e0;border-radius:8px;font-size:16px;outline:none}
input:focus,select:focus{border-color:#667eea}
input.error{border-color:#e74c3c;background:#fff5f5}
table{width:100%;border-collapse:collapse;font-size:14px}
th{background:#f8f9fa;padding:12px 8px;text-align:left;border-bottom:2px solid #e0e0e0;color:#666}
td{padding:10px 8px;border-bottom:1px solid #f0f0f0}
.stats{display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap}
.stat-card{flex:1;min-width:100px;background:white;border-radius:12px;padding:16px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.stat-card .num{font-size:28px;font-weight:bold}
.stat-card .label{font-size:13px;color:#999;margin-top:4px}
.green .num{color:#27ae60}.red .num{color:#e74c3c}.orange .num{color:#f39c12}.gray .num{color:#999}
.toast{position:fixed;top:20px;left:50%;transform:translateX(-50%);padding:12px 24px;border-radius:8px;color:white;font-size:16px;z-index:1000}
.toast.success{background:#27ae60}.toast.error{background:#e74c3c}
.toolbar{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:16px}
.toolbar input[type="date"]{width:auto;padding:8px 12px;margin:0}
.toolbar button{width:auto;padding:8px 16px;background:#3498db;color:white;border:none;border-radius:8px;cursor:pointer;font-size:14px}
.toolbar select{width:auto;padding:8px 12px;margin:0;font-size:14px}
.hint{text-align:center;color:#999;margin-top:16px;font-size:13px}
.hint code{background:#f0f0f0;padding:2px 6px;border-radius:3px}
.result{margin-top:16px;text-align:center;font-size:18px}
.status-已签到{color:#27ae60;font-weight:bold}
.status-缺勤{color:#e74c3c;font-weight:bold}
.status-请假{color:#f39c12;font-weight:bold}
.filter-bar{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap}
.filter-btn{flex:1;min-width:80px;padding:10px 8px;border:2px solid #e0e0e0;border-radius:10px;background:white;cursor:pointer;font-size:14px;font-weight:600;text-align:center;transition:all .2s}
.filter-btn:hover{background:#f8f9fa}
.filter-btn.active{border-color:#667eea;background:#f0f4ff;color:#667eea}
.filter-btn .count{font-size:12px;color:#999;font-weight:normal}
.filter-btn.active .count{color:#667eea}
.filter-hint{text-align:center;color:#999;font-size:13px;margin-bottom:12px}
.records h3{font-size:16px;color:#666;margin-bottom:8px}
.record-item{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f0f0f0;font-size:14px}
.config-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.config-grid label{font-size:14px;color:#666;margin-bottom:4px}
.course-info{background:#f0f4ff;border:2px solid #667eea;border-radius:12px;padding:16px;margin-bottom:16px}
.course-info .ci-title{font-size:18px;font-weight:bold;color:#333;margin-bottom:4px}
.course-info .ci-meta{font-size:14px;color:#666}
.confirm-section{border:2px dashed #e0e0e0;border-radius:12px;padding:16px;margin-bottom:16px}
.confirm-section.active{border-color:#27ae60;background:#f0fff4}
.confirm-section .confirm-hint{font-size:14px;color:#e67e22;margin-bottom:8px}
.confirm-section .confirm-ok{font-size:14px;color:#27ae60;margin-bottom:8px}
.time-section{border:2px solid #e0e0e0;border-radius:12px;padding:16px;margin-bottom:16px}
.section-title{font-size:14px;font-weight:bold;color:#666;margin-bottom:12px;text-transform:uppercase;letter-spacing:1px}
.current-course{display:inline-block;background:rgba(255,255,255,.2);padding:4px 12px;border-radius:20px;font-size:13px;margin-right:12px}
'''

# ============================================================
# HTML Pages
# ============================================================
def login_page(error=None):
    err_html = f'<p style="color:#e74c3c;text-align:center;margin-bottom:12px">{error}</p>' if error else ''
    return f'''<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>签到系统 - 登录</title><style>body{{display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#667eea,#764ba2)}}{CSS}</style></head><body>
<div class="card" style="width:90%;max-width:400px"><h1 style="text-align:center;margin-bottom:8px">📋 学生签到系统</h1>
<p style="text-align:center;color:#999;margin-bottom:24px">请登录</p>{err_html}
<form method="post"><input name="username" placeholder="用户名（学号）" required><input type="password" name="password" placeholder="密码" required><button class="btn">登 录</button></form>
<p class="hint">教师: <code>teacher</code>/<code>admin123</code> | 学生: 学号/<code>123456</code></p></div></body></html>'''

def student_page(user, courses_status, records, selected_course_id):
    course_opts = ''.join(
        f'<option value="{cs["course_id"]}" {"selected" if cs["course_id"]==selected_course_id else ""}>{cs["course_name"]} {"✅" if cs["already_signed"] else "⏰" if not cs["in_window"] else "📝"}</option>'
        for cs in courses_status)
    
    # Selected course details
    sel = next((cs for cs in courses_status if cs['course_id'] == selected_course_id), courses_status[0])
    now_t = datetime.now().time()
    
    if sel['already_signed']:
        btn_text = '今日已签到'
        btn_style = 'style="background:#ccc"'
        btn_disabled = 'disabled'
        info_msg = '<div class="result" style="color:#e67e22">⚠️ 本课程今日已签到</div>'
    elif not sel['in_window']:
        btn_text = f'不在签到时段（{sel["start_time"]}-{sel["end_time"]}）'
        btn_style = 'style="background:#ccc"'
        btn_disabled = 'disabled'
        info_msg = f'<div class="result" style="color:#e74c3c">⏰ 签到时间：{sel["start_time"]} - {sel["end_time"]}</div>'
    else:
        btn_text = '签 到'
        btn_style = 'style="background:linear-gradient(135deg,#27ae60,#2ecc71);box-shadow:0 4px 15px rgba(39,174,96,.4)"'
        btn_disabled = ''
        info_msg = ''

    rec_html = ''.join(
        f'<div class="record-item"><span>{r["sign_date"]} {r["sign_time"]}</span><span style="font-size:12px;color:#999">{r["course_name"]}</span><span class="status-{r["status"]}">{r["status"]}</span></div>'
        for r in records) if records else '<p style="color:#999;text-align:center;padding:20px">暂无签到记录</p>'

    return f'''<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>学生签到</title><style>{CSS}</style></head><body>
<div class="header"><h1>📋 学生签到</h1><a href="/logout">退出</a></div>
<div class="container" style="max-width:480px">
<div class="card"><div style="text-align:center;margin-bottom:20px">
<div style="font-size:28px;font-weight:bold">{user['name']}</div>
<div style="font-size:14px;color:#999;margin-top:4px">学号：{user['student_id']} | {user['class_name']}</div></div>
<select id="courseSel" onchange="switchCourse()" style="margin-bottom:12px">{course_opts}</select>
<button class="btn" {btn_style} {btn_disabled} onclick="checkin()" id="ckbtn">{btn_text}</button>
<div class="result" id="result">{info_msg}</div>
<p class="hint">切换课程查看各课签到状态，每门课每天可签到一次</p></div>
<div class="card records"><h3>📅 我的签到记录</h3>{rec_html}</div></div>
<div id="toast"></div>
<script>
var selectedCourse = {selected_course_id};
function switchCourse(){{selectedCourse=parseInt(document.getElementById('courseSel').value);window.location='/student?course_id='+selectedCourse}}
async function checkin(){{document.getElementById('ckbtn').disabled=true;document.getElementById('ckbtn').textContent='签到中...';
try{{let r=await fetch('/api/checkin',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{course_id:selectedCourse}})}});let d=await r.json();show(d.message,d.success);if(d.success){{document.getElementById('result').innerHTML='<span style="color:#27ae60">✅ 签到成功</span><br><span style="color:#999;font-size:14px">'+d.time+'</span>';setTimeout(()=>location.reload(),800)}}}}
catch(e){{show('网络错误','error')}}finally{{let b=document.getElementById('ckbtn');b.disabled=false;b.textContent='签 到'}}}}
function show(m,t){{let e=document.getElementById('toast');e.className='toast '+t;e.textContent=m;e.style.display='block';setTimeout(()=>e.style.display='none',2500)}}</script>
</body></html>'''

def pie_chart_svg(signed, absent, leave):
    """Generate SVG donut chart for sign-in distribution"""
    total = signed + absent + leave
    if total == 0:
        return '<svg width="160" height="160" viewBox="0 0 160 160"><circle cx="80" cy="80" r="60" fill="#eee"/><text x="80" y="85" text-anchor="middle" font-size="14" fill="#999">无数据</text></svg>'
    
    colors = {'已签到': '#27ae60', '缺勤': '#e74c3c', '请假': '#f39c12'}
    data = [('已签到', signed, '#27ae60'), ('缺勤', absent, '#e74c3c'), ('请假', leave, '#f39c12')]
    data = [d for d in data if d[1] > 0]
    
    parts = []
    cx, cy, r_outer, r_inner = 80, 80, 60, 35
    angle = -90  # start from top
    
    for name, count, color in data:
        sweep = count * 360.0 / total
        if sweep >= 360:
            sweep = 359.9  # avoid full circle rendering issues
        start_rad = angle * 3.14159 / 180
        end_rad = (angle + sweep) * 3.14159 / 180
        
        x1 = cx + r_outer * __import__('math').cos(start_rad)
        y1 = cy + r_outer * __import__('math').sin(start_rad)
        x2 = cx + r_outer * __import__('math').cos(end_rad)
        y2 = cy + r_outer * __import__('math').sin(end_rad)
        x3 = cx + r_inner * __import__('math').cos(end_rad)
        y3 = cy + r_inner * __import__('math').sin(end_rad)
        x4 = cx + r_inner * __import__('math').cos(start_rad)
        y4 = cy + r_inner * __import__('math').sin(start_rad)
        
        large = 1 if sweep > 180 else 0
        
        path = f'M {x1:.1f} {y1:.1f} A {r_outer} {r_outer} 0 {large} 1 {x2:.1f} {y2:.1f} L {x3:.1f} {y3:.1f} A {r_inner} {r_inner} 0 {large} 0 {x4:.1f} {y4:.1f} Z'
        
        # Label at middle of arc
        mid_rad = (start_rad + end_rad) / 2
        mid_r = (r_outer + r_inner) / 2
        lx = cx + mid_r * __import__('math').cos(mid_rad)
        ly = cy + mid_r * __import__('math').sin(mid_rad)
        pct = int(count * 100 / total)
        
        parts.append(f'<path d="{path}" fill="{color}" stroke="white" stroke-width="2"/>')
        if pct >= 8:  # Only show label if slice is big enough
            parts.append(f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle" dominant-baseline="central" font-size="12" font-weight="bold" fill="white">{pct}%</text>')
        
        angle += sweep
    
    return f'<svg width="160" height="160" viewBox="0 0 160 160">{"".join(parts)}</svg>'

def teacher_page(records, stats, filter_date, courses, classes, selected_course_id, config, status_filter='', class_filter=''):
    course_options = ''.join(
        f'<option value="{c["id"]}" {"selected" if c["id"]==selected_course_id else ""}>{c["course_name"]}（{c["course_code"]}）</option>'
        for c in courses)

    class_options = '<option value="">全部班级</option>' + ''.join(
        f'<option value="{cl}" {"selected" if cl==class_filter else ""}>{cl}</option>'
        for cl in classes)
    
    selected_name = next((c['course_name'] for c in courses if c['id'] == selected_course_id), '未知')
    
    # Build filter bar
    filters = [
        ('', '全部', stats['total']),
        ('已签到', '已签到', stats['signed']),
        ('缺勤', '缺勤', stats['absent']),
        ('请假', '请假', stats['leave']),
    ]
    filter_html = ''.join(
        f'<button class="filter-btn{" active" if v==status_filter else ""}" onclick="filterBy(\'{v}\')">{label}<br><span class="count">{count}人</span></button>'
        for v, label, count in filters)
    
    # Hint when filtered
    label_map = {'': '全部学生', '已签到': '已签到', '缺勤': '缺勤', '请假': '请假'}
    hint = f'<div class="filter-hint">🔍 当前筛选：<b>{label_map.get(status_filter, "全部学生")}</b>（{len(records)}人）</div>' if status_filter else ''
    
    rows = ''.join(f'''<tr><td>{r['student_id']}</td><td>{r['student_name']}</td><td>{r['class_name']}</td>
<td>{r['course_name'] if r['course_name'] else '-'}</td><td>{r['sign_time'] or '-'}</td><td><select onchange="updateStatus('{r['student_id']}','{filter_date}',this.value)" style="padding:4px 8px;border-radius:4px;border:1px solid #ddd">
<option value="已签到" {'selected' if r['status']=='已签到' else ''}>已签到</option>
<option value="缺勤" {'selected' if r['status']=='缺勤' else ''}>缺勤</option>
<option value="请假" {'selected' if r['status']=='请假' else ''}>请假</option></select></td></tr>''' for r in records)

    return f'''<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>教师端 - 签到管理</title><style>{CSS}</style></head><body>
<div class="header" style="background:linear-gradient(135deg,#2c3e50,#34495e)"><h1>📊 签到管理</h1><div><a href="/teacher_config" style="color:white;text-decoration:none;margin-right:16px">⚙️ 设置</a><a href="/logout">退出</a></div></div>
<div class="container">
<div class="toolbar" style="margin-bottom:16px;justify-content:space-between">
<div style="display:flex;gap:12px;align-items:center">
<span style="font-weight:bold;font-size:16px">📚</span>
<select id="courseSel" onchange="switchCourse()">
{course_options}
</select>
<span style="font-weight:bold;font-size:16px">🏫</span>
<select id="classSel" onchange="switchClass()">
{class_options}
</select>
<span style="font-size:14px;color:#999">当前：{selected_name}</span>
</div>
<div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;padding:6px 14px;font-size:13px;color:#856404">
⏰ 签到时段：{config['start_time']} - {config['end_time']}
</div>
</div>
<div class="stats">
<div class="stat-card green"><div class="num">{stats['signed']}</div><div class="label">已签到</div></div>
<div class="stat-card red"><div class="num">{stats['absent']}</div><div class="label">缺勤</div></div>
<div class="stat-card orange"><div class="num">{stats['leave']}</div><div class="label">请假</div></div>
<div class="stat-card gray"><div class="num">{stats['total']}</div><div class="label">总人数</div></div></div>
<div class="card" style="display:flex;align-items:center;gap:24px;flex-wrap:wrap">
<div style="flex-shrink:0">{pie_chart_svg(stats['signed'], stats['absent'], stats['leave'])}</div>
<div style="flex:1;min-width:200px">
<h3 style="font-size:16px;color:#333;margin-bottom:12px">📊 {selected_name} 签到分布</h3>
<div style="display:flex;flex-direction:column;gap:8px">
<div style="display:flex;align-items:center;gap:8px"><div style="width:14px;height:14px;border-radius:3px;background:#27ae60"></div><span style="font-size:14px">已签到：{stats['signed']}人（{stats['signed']*100//max(stats['total'],1)}%）</span></div>
<div style="display:flex;align-items:center;gap:8px"><div style="width:14px;height:14px;border-radius:3px;background:#e74c3c"></div><span style="font-size:14px">缺勤：{stats['absent']}人（{stats['absent']*100//max(stats['total'],1)}%）</span></div>
<div style="display:flex;align-items:center;gap:8px"><div style="width:14px;height:14px;border-radius:3px;background:#f39c12"></div><span style="font-size:14px">请假：{stats['leave']}人（{stats['leave']*100//max(stats['total'],1)}%）</span></div>
</div></div></div>
<div class="filter-bar">{filter_html}</div>
{hint}
<div class="card"><div class="toolbar"><span style="font-weight:bold;font-size:16px">日期：</span>
<input type="date" id="d" value="{filter_date}" onchange="go()"><button onclick="today()" style="background:#27ae60">今天</button><button onclick="go()">查询</button></div>
<table><thead><tr><th>学号</th><th>姓名</th><th>班级</th><th>课程</th><th>签到时间</th><th>状态</th></tr></thead><tbody>{rows}</tbody></table></div></div>
<div id="toast"></div>
<script>
var currentCourse = {selected_course_id};
if(currentCourse){{var bl=document.getElementById('batchImportLink');if(bl)bl.style.display='block'}}
var currentStatus = '{status_filter}';
var currentClass = '{class_filter}';
function switchCourse(){{currentCourse=parseInt(document.getElementById('courseSel').value);go()}}
function switchClass(){{currentClass=document.getElementById('classSel').value;go()}}
function go(){{window.location='/teacher?date='+document.getElementById('d').value+'&course_id='+currentCourse+'&status='+currentStatus+'&class_filter='+encodeURIComponent(currentClass)}}
function today(){{var d=new Date();document.getElementById('d').value=d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2);go()}}
function filterBy(st){{currentStatus=st;go()}}
async function updateStatus(sid,sd,st){{try{{let r=await fetch('/api/update_status',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{student_id:sid,sign_date:sd,status:st,course_id:currentCourse}})}});let d=await r.json();show(d.message,d.success?'success':'error');setTimeout(()=>location.reload(),500)}}catch(e){{show('网络错误','error')}}}}
function show(m,t){{let e=document.getElementById('toast');e.className='toast '+t;e.textContent=m;e.style.display='block';setTimeout(()=>e.style.display='none',2500)}}</script>
</body></html>'''

def manage_students_page(students, classes, courses, selected_course_id=0, class_filter='', error=None, success=None):
    err_html = f'<p style="color:#e74c3c;text-align:center;margin-bottom:8px">{error}</p>' if error else ''
    suc_html = f'<p style="color:#27ae60;text-align:center;margin-bottom:8px">{success}</p>' if success else ''

    course_opts = ''.join(f'<option value="{c["id"]}" {"selected" if c["id"]==selected_course_id else ""}>{c["course_name"]}（{c["course_code"]}）</option>' for c in courses)
    class_opts_add = ''.join(f'<option value="{cl}">{cl}</option>' for cl in classes)
    class_opts_filter = '<option value="">全部班级</option>' + ''.join(f'<option value="{cl}" {"selected" if cl==class_filter else ""}>{cl}</option>' for cl in classes)

    # Student list rows
    rows = ''.join(f'''<tr id="studentRow-{s['student_id']}">
<td>{s['student_id']}</td><td>{s['name']}</td><td>{s['class_name']}</td>
<td>{s['course_count']}</td>
<td><button onclick="deleteStudent('{s['student_id']}','{s['name']}')" style="padding:4px 12px;background:#e74c3c;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px">删除</button></td>
</tr>''' for s in students)

    return f'''<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>管理学生</title><style>{CSS}</style></head><body>
<div class="header" style="background:linear-gradient(135deg,#2c3e50,#34495e)"><h1>👥 管理学生</h1><a href="/teacher_config">返回</a></div>
<div class="container" style="max-width:800px">
<div class="card">{err_html}{suc_html}

<!-- Course selector -->
<div class="section-title" style="margin-bottom:12px">📚 选择课程</div>
<select id="courseSel" onchange="switchCourse()" style="margin-bottom:16px">
<option value="">-- 请选择课程后添加学生 --</option>
{course_opts}
</select>

<!-- Add student form -->
<div class="course-info" style="margin-bottom:16px" id="addSection">
<div class="section-title" style="margin-bottom:12px">➕ 添加学生到课程</div>
<div style="display:flex;gap:8px;flex-wrap:wrap">
<input type="text" id="newSid" placeholder="学号" style="flex:1;min-width:100px;margin-bottom:0">
<input type="text" id="newSname" placeholder="姓名" style="flex:1;min-width:100px;margin-bottom:0">
<select id="newSclass" style="flex:1;min-width:120px;margin-bottom:0;padding:12px 8px">
<option value="">-- 班级 --</option>
{class_opts_add}
</select>
<button onclick="addStudent()" style="padding:12px 20px;background:#27ae60;color:white;border:none;border-radius:8px;cursor:pointer;font-size:14px;white-space:nowrap">确认添加</button>
</div>
<div id="addStudentMsg" style="margin-top:8px;font-size:13px"></div>
<div id="batchImportLink" style="margin-top:12px;text-align:right;display:none"><a href="/batch_import?course_id={selected_course_id}" style="padding:10px 18px;background:#3498db;color:white;border-radius:8px;text-decoration:none;font-size:13px;display:inline-block">📥 批量导入（CSV粘贴）</a></div>
</div>

<!-- Student list -->
<div class="toolbar" style="margin-bottom:12px">
<span style="font-weight:bold">🏫 筛选班级：</span>
<select id="classFilter" onchange="filterClass()">
{class_opts_filter}
</select>
<span style="margin-left:12px;color:#999;font-size:14px">共 {len(students)} 人</span>
</div>
<table><thead><tr><th>学号</th><th>姓名</th><th>班级</th><th>课程数</th><th>操作</th></tr></thead><tbody>
{rows if rows else '<tr><td colspan="5" style="text-align:center;color:#999;padding:20px">暂无学生</td></tr>'}
</tbody></table>
</div></div>
<div id="toast"></div>
<script>
var currentCourse = {selected_course_id};
if(currentCourse){{var bl=document.getElementById('batchImportLink');if(bl)bl.style.display='block'}}
var currentClass = '{class_filter}';
function switchCourse(){{currentCourse=parseInt(document.getElementById('courseSel').value);var bl=document.getElementById('batchImportLink');if(bl)bl.style.display=currentCourse?'block':'none';window.location='/manage_students?course_id='+currentCourse+'&class_filter='+encodeURIComponent(currentClass)}}
function filterClass(){{window.location='/manage_students?course_id='+currentCourse+'&class_filter='+encodeURIComponent(document.getElementById('classFilter').value)}}
async function addStudent(){{
    var sid=document.getElementById('newSid').value.trim(),nm=document.getElementById('newSname').value.trim(),cl=document.getElementById('newSclass').value,msg=document.getElementById('addStudentMsg');
    if(!currentCourse){{msg.innerHTML='<span style="color:#e74c3c">请先选择课程</span>';return}}
    if(!sid||!nm||!cl){{msg.innerHTML='<span style="color:#e74c3c">请填写所有字段</span>';return}}
    try{{
        let r=await fetch('/add_student',{{method:'POST',headers:{{'Content-Type':'application/x-www-form-urlencoded'}},body:'course_id='+currentCourse+'&student_id='+encodeURIComponent(sid)+'&student_name='+encodeURIComponent(nm)+'&class_name='+encodeURIComponent(cl)}});
        if(r.redirected){{window.location=r.url}}
        else{{let t=await r.text();msg.innerHTML='<span style="color:#e74c3c">添加失败</span>'}}
    }}catch(e){{msg.innerHTML='<span style="color:#e74c3c">网络错误</span>'}}
}}
async function deleteStudent(sid,name){{
    if(!confirm('确定要删除学生 "'+name+'"（'+sid+'）吗？\\n\\n此操作不可恢复，将同时删除该学生的登录账号和所有课程关联。'))return;
    try{{
        let r=await fetch('/api/delete_student',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{student_id:sid}})}});
        let d=await r.json();
        if(d.success){{var row=document.getElementById('studentRow-'+sid);if(row)row.remove();show(d.message,'success')}}else{{show(d.message,'error')}}
    }}catch(e){{show('网络错误','error')}}
}}
function show(m,t){{var e=document.getElementById('toast');e.className='toast '+t;e.textContent=m;e.style.display='block';setTimeout(function(){{e.style.display='none'}},2500)}}
</script>
</body></html>'''

def add_student_page(course, classes, error=None, success=None):
    err_html = f'<p style="color:#e74c3c;text-align:center;margin-bottom:8px">{error}</p>' if error else ''
    suc_html = f'<p style="color:#27ae60;text-align:center;margin-bottom:8px">{success}</p>' if success else ''
    class_opts = ''.join(f'<option value="{cl}">{cl}</option>' for cl in classes)
    return f'''<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>添加学生</title><style>{CSS}</style></head><body>
<div class="header" style="background:linear-gradient(135deg,#2c3e50,#34495e)"><h1>📝 添加学生到课程</h1><a href="/teacher_config?course_id={course['id']}">返回</a></div>
<div class="container" style="max-width:540px">
<div class="card">{err_html}{suc_html}
<div class="course-info" style="margin-bottom:20px">
<div class="ci-title">{course['course_name']}</div>
<div class="ci-meta">课程代码：{course['course_code']} | 已有学生：{course['student_count']} 人</div>
</div>
<form method="post" action="/add_student" onsubmit="return validate()">
<input type="hidden" name="course_id" value="{course['id']}">
<label style="font-size:14px;color:#666">学号</label>
<input name="student_id" id="sid" placeholder="输入学号（如 223050053）" required>
<label style="font-size:14px;color:#666">姓名</label>
<input name="student_name" id="sname" placeholder="输入姓名（如 张三）" required>
<label style="font-size:14px;color:#666">班级</label>
<select name="class_name" id="sclass" required>
<option value="">-- 请选择班级 --</option>
{class_opts}
</select>
<p class="hint" style="text-align:left;margin-top:4px">如需新增班级，请到「设置」页操作</p>
<button class="btn" type="submit">✅ 确认添加</button>
</form>
<p class="hint">新学生将自动创建登录账号（密码：123456）并加入此课程</p>
</div></div>
<script>
function validate(){{var sid=document.getElementById('sid').value.trim(),nm=document.getElementById('sname').value.trim(),cl=document.getElementById('sclass').value;if(!sid||!nm||!cl){{alert('请填写所有字段');return false}}return true}}
</script>
</body></html>'''

def teacher_config_page(courses, current_config, classes, url_class_filter="", error=None, success=None, has_config=False):
    err_html = f'<p style="color:#e74c3c;text-align:center;margin-bottom:8px">{error}</p>' if error else ''
    suc_html = f'<p style="color:#27ae60;text-align:center;margin-bottom:8px">{success}</p>' if success else ''

    course_options = ''.join(
        f'<option value="{c["id"]}" data-name="{c["course_name"]}" data-code="{c["course_code"]}" data-count="{c["student_count"]}" {"selected" if c["id"]==current_config["course_id"] else ""}>{c["course_name"]}（{c["course_code"]} · {c["student_count"]}人）</option>'
        for c in courses)

    # Class dropdown
    class_filter = url_class_filter
    class_options = '<option value="">全部班级（一起上课）</option>' + ''.join(
        f'<option value="{cl}" {"selected" if cl==class_filter else ""}>{cl}</option>'
        for cl in classes)

    # Pre-fill selected course info for display on page load
    sel_course = next((c for c in courses if c['id'] == current_config.get('course_id')), None)
    pre_name = sel_course['course_name'] if sel_course else ''
    pre_code = sel_course['course_code'] if sel_course else ''
    pre_count = sel_course['student_count'] if sel_course else '0'
    pre_hint = f'⚠️ 请在下框中输入 "{pre_name}" 以确认选择' if pre_name else ''

    # Build class list HTML for the management card
    class_list_html = ''.join(
        f'''<div class="record-item" id="classRow-{cl}" style="align-items:center">
<span id="className-{cl}">{cl}</span>
<input id="classInput-{cl}" value="{cl}" style="display:none;flex:1;margin:0;padding:6px 10px;font-size:14px">
<span style="display:flex;gap:8px">
<button onclick="startRename('{cl}')" id="renameBtn-{cl}" style="padding:4px 12px;background:#3498db;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px">改名</button>
<button onclick="cancelRename('{cl}')" id="cancelBtn-{cl}" style="display:none;padding:4px 12px;background:#999;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px">取消</button>
<button onclick="saveRename('{cl}')" id="saveBtn-{cl}" style="display:none;padding:4px 12px;background:#27ae60;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px">保存</button>
<button onclick="deleteClass('{cl}')" style="padding:4px 12px;background:#e74c3c;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px">删除</button>
</span>
</div>''' for cl in classes)



    return f'''<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>签到设置</title><style>{CSS}</style></head><body>
<div class="header" style="background:linear-gradient(135deg,#2c3e50,#34495e)"><h1>⚙️ 签到时段设置</h1><a href="/teacher">返回</a></div>
<div class="container" style="max-width:540px">
<div class="card">{err_html}{suc_html}

<form method="post" action="/api/update_config" onsubmit="return validateForm()">

<!-- Step 1: Select Course -->
<div class="section-title">📚 第一步：选择课程</div>
<select name="course_id" id="courseSelect" onchange="onCourseChange()" required>
<option value="">-- 请选择课程 --</option>
{course_options}
</select>

<!-- Step 1.5: Select Class -->
<div class="section-title" style="margin-top:16px">🏫 第二步：选择发布班级</div>
<select name="class_filter" id="classSelect" onchange="onClassChange()">
{class_options}
</select>
<p style="font-size:13px;color:#999;margin-top:4px">选择「全部班级」则所有班级同时签到；选具体班级则仅该班级可签到</p>

<!-- Course Info Preview -->
<div class="course-info" id="courseInfo"{' style="display:none"' if not current_config.get('course_id') else ''}>
<div class="ci-title" id="ciName">{pre_name}</div>
<div class="ci-meta">课程代码：<span id="ciCode">{pre_code}</span> | 学生人数：<span id="ciCount">{pre_count}</span> 人</div>
</div>

<!-- Step 2: Confirm Course -->
<div class="confirm-section" id="confirmSection"{' style="display:none"' if not current_config.get('course_id') else ''}>
<div class="section-title">🔐 第三步：确认课程（防止选错）</div>
<div class="confirm-hint" id="confirmHint">{pre_hint}</div>
<div id="confirmOk" class="confirm-ok" style="display:none">✅ 课程名称验证通过</div>
<input type="text" id="confirmInput" placeholder="请在此输入课程名称以确认..." oninput="onConfirmInput()" autocomplete="off">
</div>

<!-- Step 3: Set Time -->
<div class="time-section" id="timeSection"{' style="display:none"' if not current_config.get('course_id') else ''}>
<div class="section-title">⏰ 第四步：设置签到时间</div>
<div class="config-grid">
<div><label>开始时间</label><input type="time" name="start_time" id="startTime" value="{current_config.get('start_time', '08:00')}" required></div>
<div><label>结束时间</label><input type="time" name="end_time" id="endTime" value="{current_config.get('end_time', '18:00')}" required></div>
</div>
</div>

<button class="btn" type="submit" id="saveBtn" disabled>{'💾 首次保存签到设置' if not has_config else '🔒 已配置（请使用下方修改按钮）'}</button>
</form>

<div style="margin-top:12px;display:flex;gap:12px">
<button id="modifyBtn" class="btn" style="flex:1;background:linear-gradient(135deg,#e67e22,#f39c12);opacity:.4;cursor:not-allowed" disabled onclick="modifyTime()">{'✏️ 修改签到时间' if has_config else '🔒 请先保存设置后再修改'}</button>
</div>

<p class="hint">{'请完成以上三步后点击保存' if not has_config else '如需修改签到时间，请使用下方修改按钮'}</p>

<!-- Manage students -->
<a href="/manage_students"><div class="card" style="margin-top:16px;cursor:pointer">
<div class="section-title">👥 管理学生</div>
</div></a>

<!-- Manage courses -->
<a href="/manage_courses"><div class="card" style="margin-top:16px;cursor:pointer">
<div class="section-title">📚 管理课程</div>
</div></a>




<!-- Add/Manage classes -->
<div class="card" style="margin-top:16px">
<div class="section-title" style="margin-bottom:12px">🏫 班级管理</div>
<div style="display:flex;gap:8px;margin-bottom:16px">
<input type="text" id="newClassName" placeholder="输入新班级名称" style="flex:2;margin-bottom:0">
<button onclick="addClass()" style="padding:12px 20px;background:#667eea;color:white;border:none;border-radius:8px;cursor:pointer;font-size:14px;white-space:nowrap">添加</button>
</div>
<div id="addClassMsg" style="margin-bottom:8px;font-size:13px"></div>
<div id="classList">
{class_list_html}
</div>
</div>

</div></div>

<script>
let selectedCourseName = {json.dumps(pre_name)};
let confirmed = false;
let courseSelected = {'true' if pre_name else 'false'};
let hasConfig = {'true' if has_config else 'false'};

// Page already loaded with correct course from server
// Course info is rendered server-side; no pre-load needed
updateSaveBtn();

function onCourseChange() {{
    let sel = document.getElementById('courseSelect');
    let opt = sel.options[sel.selectedIndex];
    if (!sel.value) {{
        document.getElementById('courseInfo').style.display = 'none';
        document.getElementById('confirmSection').style.display = 'none';
        document.getElementById('timeSection').style.display = 'none';
        courseSelected = false;
        updateSaveBtn();
        return;
    }}
    // Reload page with the selected course + class so hasConfig stays in sync
    let cls = document.getElementById('classSelect').value;
    window.location = '/teacher_config?course_id=' + sel.value + '&class_filter=' + encodeURIComponent(cls);
}}

function onClassChange() {{
    let sel = document.getElementById('courseSelect');
    if (!sel.value) return;
    let cls = document.getElementById('classSelect').value;
    window.location = '/teacher_config?course_id=' + sel.value + '&class_filter=' + encodeURIComponent(cls);
}}

function onConfirmInput() {{
    let input = document.getElementById('confirmInput');
    let val = input.value.trim();
    let section = document.getElementById('confirmSection');
    let ok = document.getElementById('confirmOk');

    if (val === selectedCourseName) {{
        confirmed = true;
        input.className = '';
        ok.style.display = 'block';
        section.className = 'confirm-section active';
    }} else {{
        confirmed = false;
        ok.style.display = 'none';
        if (val.length > 0) {{
            input.className = 'error';
        }} else {{
            input.className = '';
        }}
        section.className = 'confirm-section';
    }}
    updateSaveBtn();
}}

function updateSaveBtn() {{
    // Save button: only enabled when NOT configured yet
    if (hasConfig) {{
        document.getElementById('saveBtn').disabled = true;
    }} else {{
        document.getElementById('saveBtn').disabled = !(courseSelected && confirmed);
    }}
    // Modify button: only enabled when already configured
    if (hasConfig && courseSelected && confirmed) {{
        document.getElementById('modifyBtn').disabled = false;
        document.getElementById('modifyBtn').style.opacity = '1';
        document.getElementById('modifyBtn').style.cursor = 'pointer';
    }} else {{
        document.getElementById('modifyBtn').disabled = true;
        document.getElementById('modifyBtn').style.opacity = '.4';
        document.getElementById('modifyBtn').style.cursor = 'not-allowed';
    }}
}}

function validateForm() {{
    if (!confirmed) {{
        alert('请先输入正确的课程名称以确认选择！');
        return false;
    }}
    return true;
}}

function modifyTime() {{
    if (!hasConfig) {{
        alert('该课程尚未配置签到时间，请先使用保存按钮设置。');
        return;
    }}
    if (!courseSelected || !confirmed) {{
        alert('请先完成课程选择和确认！');
        return;
    }}
    var st = document.getElementById('startTime').value;
    var et = document.getElementById('endTime').value;
    if (!confirm('确定要修改签到时间？\\n\\n课程：' + selectedCourseName +
        '\\n开始时间：' + st + '\\n结束时间：' + et +
        '\\n\\n修改后学生将按新的时间段签到。')) {{
        return;
    }}
    // Submit the form
    var form = document.querySelector('form');
    form.submit();
}}

async function addClass() {{
    var nm = document.getElementById('newClassName').value.trim();
    var msg = document.getElementById('addClassMsg');
    if (!nm) {{
        msg.innerHTML = '<span style="color:#e74c3c">请输入班级名称</span>';
        return;
    }}
    try {{
        let r = await fetch('/api/add_class', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{class_name: nm}})
        }});
        let d = await r.json();
        if (d.success) {{
            msg.innerHTML = '<span style="color:#27ae60">✅ ' + d.message + '</span>';
            document.getElementById('newClassName').value = '';
            setTimeout(function(){{ location.reload(); }}, 800);
        }} else {{
            msg.innerHTML = '<span style="color:#e74c3c">❌ ' + d.message + '</span>';
        }}
    }} catch(e) {{
        msg.innerHTML = '<span style="color:#e74c3c">网络错误</span>';
    }}
}}

function startRename(oldName) {{
    document.getElementById('className-'+oldName).style.display = 'none';
    document.getElementById('classInput-'+oldName).style.display = 'block';
    document.getElementById('renameBtn-'+oldName).style.display = 'none';
    document.getElementById('cancelBtn-'+oldName).style.display = 'inline-block';
    document.getElementById('saveBtn-'+oldName).style.display = 'inline-block';
    document.getElementById('classInput-'+oldName).focus();
}}
function cancelRename(oldName) {{
    document.getElementById('className-'+oldName).style.display = 'inline';
    document.getElementById('classInput-'+oldName).style.display = 'none';
    document.getElementById('renameBtn-'+oldName).style.display = 'inline-block';
    document.getElementById('cancelBtn-'+oldName).style.display = 'none';
    document.getElementById('saveBtn-'+oldName).style.display = 'none';
    document.getElementById('classInput-'+oldName).value = oldName;
}}
async function saveRename(oldName) {{
    var newName = document.getElementById('classInput-'+oldName).value.trim();
    var msg = document.getElementById('addClassMsg');
    if (!newName || newName === oldName) {{ cancelRename(oldName); return; }}
    try {{
        let r = await fetch('/api/rename_class', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{old_name: oldName, new_name: newName}})
        }});
        let d = await r.json();
        if (d.success) {{
            location.reload();
        }} else {{
            msg.innerHTML = '<span style="color:#e74c3c">❌ ' + d.message + '</span>';
            cancelRename(oldName);
        }}
    }} catch(e) {{
        msg.innerHTML = '<span style="color:#e74c3c">网络错误</span>';
    }}
}}
async function deleteClass(className) {{
    var msg = document.getElementById('addClassMsg');
    try {{
        // First check student count
        let r0 = await fetch('/api/delete_class', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{class_name: className, check_only: true}})
        }});
        let d0 = await r0.json();
        var prompt = d0.count > 0
            ? '班级 "' + className + '" 中有 ' + d0.count + ' 名学生。\\n\\n确定要删除该班级吗？'
            : '确定要删除班级 "' + className + '" 吗？';
        if (!confirm(prompt)) return;
        // Actual delete
        let r = await fetch('/api/delete_class', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{class_name: className}})
        }});
        let d = await r.json();
        if (d.success) {{ location.reload(); }}
        else {{ msg.innerHTML = '<span style="color:#e74c3c">❌ ' + d.message + '</span>'; }}
    }} catch(e) {{ msg.innerHTML = '<span style="color:#e74c3c">网络错误</span>'; }}
}}

async function addStudentToCourse() {{
    var sid = document.getElementById('newStudentId').value.trim();
    var msg = document.getElementById('addStudentMsg');
    var cid = document.getElementById('courseSelect').value;
    if (!sid) {{
        msg.innerHTML = '<span style="color:#e74c3c">请输入学号</span>';
        return;
    }}
    if (!cid) {{
        msg.innerHTML = '<span style="color:#e74c3c">请先选择课程</span>';
        return;
    }}
    try {{
        let r = await fetch('/api/add_student_to_course', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{course_id: parseInt(cid), student_id: sid}})
        }});
        let d = await r.json();
        if (d.success) {{
            msg.innerHTML = '<span style="color:#27ae60">✅ ' + d.message + '</span>';
            document.getElementById('newStudentId').value = '';
            setTimeout(function(){{ location.reload(); }}, 800);
        }} else {{
            msg.innerHTML = '<span style="color:#e74c3c">❌ ' + d.message + '</span>';
        }}
    }} catch(e) {{
        msg.innerHTML = '<span style="color:#e74c3c">网络错误</span>';
    }}
}}

</script>
</body></html>'''

# ============================================================
# Database Init
# ============================================================
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT UNIQUE NOT NULL, name TEXT NOT NULL, class_name TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS sign_records (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT NOT NULL, student_name TEXT NOT NULL, sign_date TEXT NOT NULL, sign_time TEXT NOT NULL, status TEXT NOT NULL DEFAULT '已签到', UNIQUE(student_id, sign_date));
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'student', student_id TEXT);
        CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY AUTOINCREMENT, course_code TEXT NOT NULL, course_name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS course_students (id INTEGER PRIMARY KEY AUTOINCREMENT, course_id INTEGER NOT NULL, student_id TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS attendance_config (id INTEGER PRIMARY KEY AUTOINCREMENT, course_id INTEGER, start_time TEXT NOT NULL DEFAULT '08:00', end_time TEXT NOT NULL DEFAULT '18:00', class_filter TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS classes (id INTEGER PRIMARY KEY AUTOINCREMENT, class_name TEXT UNIQUE NOT NULL);
    """)
    c.execute("SELECT COUNT(*) FROM attendance_config")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO attendance_config (course_id, start_time, end_time, class_filter) VALUES (1, '08:00', '18:00', '')")
    # Seed classes from existing students
    c.execute("INSERT OR IGNORE INTO classes (class_name) SELECT DISTINCT class_name FROM students WHERE class_name != ''")
    conn.commit()
    conn.close()

# ============================================================
# Session
# ============================================================
SESSIONS = {}

def get_session(cookie_str):
    cookies = SimpleCookie()
    cookies.load(cookie_str or '')
    token = cookies.get('session', None)
    return SESSIONS.get(token.value if token else '', None)

def get_config(conn, course_id=None, class_filter=None):
    conn.row_factory = sqlite3.Row
    if course_id:
        # First try exact (course_id, class_filter) match
        row = conn.execute('SELECT * FROM attendance_config WHERE course_id=? AND class_filter=? LIMIT 1',
                           (course_id, class_filter or '')).fetchone()
        if row:
            return row
        # Fall back to all-classes config for this course
        if class_filter:
            row = conn.execute('SELECT * FROM attendance_config WHERE course_id=? AND class_filter=? LIMIT 1',
                               (course_id, '')).fetchone()
            return row if row else None
        return None
    return conn.execute('SELECT * FROM attendance_config LIMIT 1').fetchone()

def get_courses(conn):
    conn.row_factory = sqlite3.Row
    return conn.execute('''SELECT c.*, COUNT(cs.id) as student_count 
        FROM courses c LEFT JOIN course_students cs ON c.id=cs.course_id 
        GROUP BY c.id ORDER BY c.id''').fetchall()

def get_student_course(conn, student_id):
    conn.row_factory = sqlite3.Row
    row = conn.execute('''SELECT c.id, c.course_name FROM courses c 
        JOIN course_students cs ON c.id=cs.course_id 
        WHERE cs.student_id=? LIMIT 1''', (student_id,)).fetchone()
    if row:
        return row
    return conn.execute('SELECT id, course_name FROM courses LIMIT 1').fetchone()

def parse_xlsx(file_bytes):
    """解析 .xlsx 文件为 CSV 文本。纯 stdlib，零依赖。"""
    import zipfile, xml.etree.ElementTree as ET, io, re

    NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as z:
            # 1. Shared strings
            shared = []
            if 'xl/sharedStrings.xml' in z.namelist():
                tree = ET.parse(z.open('xl/sharedStrings.xml'))
                for si in tree.findall(f'.//{{{NS}}}si'):
                    parts = [t.text or '' for t in si.findall(f'.//{{{NS}}}t')]
                    shared.append(''.join(parts))

            # 2. Sheet data - use findall with explicit path to avoid iter() hang
            tree = ET.parse(z.open('xl/worksheets/sheet1.xml'))
            sheet_data = tree.find(f'.//{{{NS}}}sheetData')
            if sheet_data is None:
                return None

            # 3. Process rows
            rows_out = []
            for row_elem in sheet_data.findall(f'{{{NS}}}row'):
                cells = {}
                for c in row_elem.findall(f'{{{NS}}}c'):
                    ref = c.get('r', '')
                    t = c.get('t', '')
                    v = c.find(f'{{{NS}}}v')
                    if v is None or v.text is None:
                        continue
                    m = re.match(r'([A-Z]+)(\d+)', ref)
                    if not m:
                        continue
                    col, _ = m.group(1), m.group(2)

                    if t == 's':
                        idx = int(v.text)
                        cells[col] = shared[idx] if idx < len(shared) else ''
                    else:
                        cells[col] = v.text

                if not cells:
                    continue
                # Sort by column letter
                sorted_cols = sorted(cells.keys(), key=lambda x: (len(x), x))
                line = ','.join(str(cells[c]) for c in sorted_cols)
                if line.strip():
                    rows_out.append(line)

            return '\n'.join(rows_out) if rows_out else ''

    except Exception:
        return None


def parse_multipart(content_type, body):
    """解析 multipart/form-data，返回 {field_name: value} 字典。
    value 对于文件字段是 bytes，对于普通字段是 str。"""
    import re
    # 提取 boundary
    m = re.search(r'boundary=(.+)', content_type or '')
    if not m:
        return {}
    boundary = m.group(1).strip()
    if boundary.startswith('"') and boundary.endswith('"'):
        boundary = boundary[1:-1]
    boundary_bytes = boundary.encode() if isinstance(boundary, str) else boundary
    body = body if isinstance(body, bytes) else body.encode('latin-1')

    # 分割各 part
    delimiter = b'--' + boundary_bytes
    parts = body.split(delimiter)
    result = {}

    for part in parts:
        if not part or part == b'--\r\n' or part == b'--':
            continue
        # 去掉开头的 \r\n
        if part.startswith(b'\r\n'):
            part = part[2:]
        elif part.startswith(b'\n'):
            part = part[1:]

        # 分割 headers 和 body
        if b'\r\n\r\n' in part:
            header_section, data = part.split(b'\r\n\r\n', 1)
        elif b'\n\n' in part:
            header_section, data = part.split(b'\n\n', 1)
        else:
            continue

        # 去掉末尾的 \r\n
        data = re.sub(rb'\r\n$', b'', data)

        # 解析 headers
        headers = header_section.decode('latin-1', errors='replace')
        name_match = re.search(r'name="([^"]*)"', headers)
        if not name_match:
            continue
        name = name_match.group(1)
        filename_match = re.search(r'filename="([^"]*)"', headers)

        if filename_match:
            result[name] = data  # 文件内容，保持 bytes
        else:
            result[name] = data.decode('utf-8')

    return result

def batch_import_page(course, results=None):
    """CSV批量导入学生页面 - 文件上传版"""
    result_html = ''
    if results:
        res_class = 'success' if results.get('added', 0) > 0 else ''
        res_title = '✅ 导入完成' if results.get('added', 0) > 0 else '⚠️ 导入完成（无新增）'
        result_html = f'''<div class="result-box {res_class} show">
<div class="res-title">{res_title}</div>
<div class="res-item">✅ 新增学生：<b>{results.get('added', 0)}</b> 人</div>
<div class="res-item">⏭️ 跳过（已在课程中）：<b>{results.get('skipped', 0)}</b> 人</div>
<div class="res-item" style="color:#e74c3c">❌ 格式错误：<b>{results.get('errors', 0)}</b> 行</div>
'''
        if results.get('details'):
            result_html += '<div style="margin-top:8px"><a href="javascript:void(0)" onclick="toggleDetail()" style="font-size:13px;color:#3498db" id="detailLink">查看详情 ▼</a></div>'
            result_html += '<div class="detail-table" id="detailTable">'
            for d in results['details']:
                color = '#27ae60' if d['status'] == '已添加' else ('#f39c12' if d['status'] == '已跳过' else '#e74c3c')
                result_html += f'<div class="res-item" style="color:{color}">【{d["status"]}】{d["student_id"]} {d["name"]}</div>'
            result_html += '</div>'
        result_html += '</div>'

    return f'''<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>批量导入</title><style>{CSS}
.section-title{{font-size:16px;font-weight:bold;color:#333;margin-bottom:12px;padding-bottom:8px;border-bottom:2px solid #f0f0f0}}
.csv-hint{{background:#f8f9fa;border-radius:8px;padding:12px 16px;font-size:13px;color:#666;margin-bottom:16px;line-height:1.8}}
.csv-hint code{{background:#e8e8e8;padding:2px 6px;border-radius:3px;font-size:12px}}
.result-box{{margin-top:16px;padding:16px;border-radius:8px;display:none}}
.result-box.show{{display:block}}
.result-box.success{{background:#eafaf1;border:1px solid #27ae60}}
.result-box.error{{background:#fdecea;border:1px solid #e74c3c}}
.result-box .res-title{{font-size:15px;font-weight:bold;margin-bottom:8px}}
.result-box .res-item{{font-size:13px;margin:4px 0;padding:2px 0}}
.detail-table{{margin-top:8px;display:none;max-height:300px;overflow-y:auto;font-size:12px}}
.detail-table.show{{display:block}}
#detailTable.show{{display:block}}
</style></head><body>
<div class="header" style="background:linear-gradient(135deg,#3498db,#2980b9)"><h1>📥 批量导入学生</h1><a href="/manage_students?course_id={course['id']}">返回</a></div>
<div class="container" style="max-width:700px">
<div class="card">
<div class="course-info" style="margin-bottom:20px">
<div class="ci-title">{course['course_name']}</div>
<div class="ci-meta" style="margin-top:8px">课程代码：{course['course_code']} | 已有学生：{course['student_count']} 人</div>
</div>
<div class="section-title">📋 CSV 格式说明</div>
<div class="csv-hint">
每行一个学生，用逗号分隔三列：<br>
<code>学号,姓名,班级</code><br><br>
示例：<br>
<code>223050001,张三,大数据管理2301班</code><br>
<code>223050002,李四,大数据管理2301班</code><br>
<code>223050003,王五,大数据管理2302班</code><br><br>
⚠️ 支持 CSV / TXT / Excel(.xlsx) 文件。<br>
⚠️ 如遇到乱码，请将 Excel 另存为 CSV UTF-8 格式。
</div>
{result_html}
<div class="section-title">📁 上传文件</div>
<form method="post" action="/batch_import" enctype="multipart/form-data">
<input type="hidden" name="course_id" value="{course['id']}">
<label style="display:block;border:2px dashed #bbb;border-radius:8px;padding:32px;text-align:center;cursor:pointer;margin-bottom:16px;transition:border-color .2s" id="dropZone" ondragover="this.style.borderColor='#667eea';return false" ondragleave="this.style.borderColor='#bbb'" ondrop="handleDrop(event);return false">
<div style="font-size:40px;margin-bottom:8px">📂</div>
<div style="font-size:15px;color:#666" id="fileLabel">点击选择文件或拖拽到此处</div>
<div style="font-size:12px;color:#999;margin-top:4px">支持 .csv / .txt 文件</div>
<input type="file" name="csv_file" accept=".csv,.txt,.xlsx" id="fileInput" onchange="updateLabel()" style="display:none">
</label>
<button class="btn" type="submit" style="background:linear-gradient(135deg,#27ae60,#2ecc71)">🚀 开始导入</button>
</form>
</div></div>
<script>
function updateLabel(){{var f=document.getElementById('fileInput').files[0];document.getElementById('fileLabel').innerText=f?f.name:'点击选择文件或拖拽到此处'}}
// dropZone click handled by native label behavior (no JS needed)
function handleDrop(e){{e.preventDefault();var f=e.dataTransfer.files[0];document.getElementById('fileInput').files=e.dataTransfer.files;if(f)document.getElementById('fileLabel').innerText=f.name}}
function toggleDetail(){{var t=document.getElementById('detailTable');if(t.className.indexOf('show')>=0){{t.className='detail-table';document.getElementById('detailLink').innerHTML='查看详情 ▼'}}else{{t.className='detail-table show';document.getElementById('detailLink').innerHTML='收起详情 ▲'}}}}
</script>
</body></html>'''
def manage_courses_page(courses, error=None, success=None):
    """课程管理页面 - 列出所有课程，支持改名和删除"""
    err_html = f'<p style="color:#e74c3c;text-align:center;margin-bottom:8px">{error}</p>' if error else ''
    suc_html = f'<p style="color:#27ae60;text-align:center;margin-bottom:8px">{success}</p>' if success else ''

    rows = ''.join(f'''<tr id="courseRow-{c['id']}">
<td><span id="codeLabel-{c['id']}">{c['course_code']}</span><input id="codeInput-{c['id']}" value="{c['course_code']}" style="display:none;width:100%;padding:6px 8px;font-size:13px;margin:0"></td>
<td><span id="nameLabel-{c['id']}">{c['course_name']}</span><input id="nameInput-{c['id']}" value="{c['course_name']}" style="display:none;width:100%;padding:6px 8px;font-size:13px;margin:0"></td>
<td>{c['student_count']}</td>
<td>
<button id="editBtn-{c['id']}" onclick="startEdit({c['id']})" style="padding:4px 12px;background:#3498db;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px;margin-right:6px">编辑</button>
<button id="saveBtn-{c['id']}" onclick="saveEdit({c['id']})" style="display:none;padding:4px 12px;background:#27ae60;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px;margin-right:6px">保存</button>
<button id="cancelBtn-{c['id']}" onclick="cancelEdit({c['id']})" style="display:none;padding:4px 12px;background:#999;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px;margin-right:6px">取消</button>
<button onclick="deleteCourse({c['id']},'{c['course_name']}')" style="padding:4px 12px;background:#e74c3c;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px">删除</button>
</td>
</tr>''' for c in courses)

    return f'''<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>管理课程</title><style>{CSS}</style></head><body>
<div class="header" style="background:linear-gradient(135deg,#2c3e50,#34495e)"><h1>📚 管理课程</h1><a href="/teacher_config">返回</a></div>
<div class="container" style="max-width:800px">
<div class="card">{err_html}{suc_html}
<!-- Add new course -->
<div style="margin-bottom:20px;padding-bottom:16px;border-bottom:2px solid #f0f0f0">
<div class="section-title" style="margin-bottom:12px">➕ 新增课程</div>
<div style="display:flex;gap:8px;flex-wrap:wrap">
<input type="text" id="newCode" placeholder="课程代码" style="flex:1;min-width:100px;margin-bottom:0">
<input type="text" id="newName" placeholder="课程名称" style="flex:2;min-width:120px;margin-bottom:0">
<button onclick="addCourse()" style="padding:12px 20px;background:#27ae60;color:white;border:none;border-radius:8px;cursor:pointer;font-size:14px;white-space:nowrap">添加</button>
</div>
<div id="addMsg" style="margin-top:8px;font-size:13px"></div>
</div>
<!-- Course list -->
<table><thead><tr><th>课程代码</th><th>课程名称</th><th>学生数</th><th>操作</th></tr></thead><tbody>
{rows if rows else '<tr><td colspan="4" style="text-align:center;color:#999;padding:20px">暂无课程</td></tr>'}
</tbody></table>
</div></div>
<script>
async function addCourse(){{
var code=document.getElementById('newCode').value.trim();
var name=document.getElementById('newName').value.trim();
var msg=document.getElementById('addMsg');
if(!code||!name){{msg.innerHTML='<span style="color:#e74c3c">请填写课程代码和名称</span>';return}}
try{{
let r=await fetch('/api/add_course',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{course_code:code,course_name:name}})}});
let d=await r.json();
if(d.success){{location.reload()}}else{{msg.innerHTML='<span style="color:#e74c3c">'+d.message+'</span>'}}
}}catch(e){{msg.innerHTML='<span style="color:#e74c3c">网络错误</span>'}}
}}
function startEdit(id){{
document.getElementById('codeLabel-'+id).style.display='none';
document.getElementById('nameLabel-'+id).style.display='none';
document.getElementById('codeInput-'+id).style.display='block';
document.getElementById('nameInput-'+id).style.display='block';
document.getElementById('editBtn-'+id).style.display='none';
document.getElementById('saveBtn-'+id).style.display='inline';
document.getElementById('cancelBtn-'+id).style.display='inline';
}}
function cancelEdit(id){{
document.getElementById('codeLabel-'+id).style.display='';
document.getElementById('nameLabel-'+id).style.display='';
document.getElementById('codeInput-'+id).style.display='none';
document.getElementById('nameInput-'+id).style.display='none';
document.getElementById('editBtn-'+id).style.display='inline';
document.getElementById('saveBtn-'+id).style.display='none';
document.getElementById('cancelBtn-'+id).style.display='none';
}}
async function saveEdit(id){{
var code=document.getElementById('codeInput-'+id).value.trim();
var name=document.getElementById('nameInput-'+id).value.trim();
if(!code||!name){{alert('课程代码和名称不能为空');return}}
try{{
let r=await fetch('/api/update_course',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{course_id:id,course_code:code,course_name:name}})}});
let d=await r.json();
if(d.success){{location.reload()}}else{{alert(d.message);cancelEdit(id)}}
}}catch(e){{alert('网络错误')}}
}}
async function deleteCourse(id,name){{
if(!confirm('确定要删除课程 "'+name+'" 吗？此操作将同时删除所有签到记录和学生关联，不可恢复。'))return;
try{{
let r=await fetch('/api/delete_course',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{course_id:id}})}});
let d=await r.json();
if(d.success){{var row=document.getElementById('courseRow-'+id);if(row)row.remove();alert(d.message);if(!document.querySelector('tbody tr'))location.reload()}}
else{{alert(d.message)}}
}}catch(e){{alert('网络错误')}}
}}
</script>
</body></html>'''

# ============================================================
# Handler
# ============================================================
class SignHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        user = get_session(self.headers.get('Cookie'))

        if path == '/':
            self._send_html(login_page())
        elif path == '/logout':
            cookie_str = self.headers.get('Cookie', '')
            cookies = SimpleCookie()
            cookies.load(cookie_str)
            token = cookies.get('session', None)
            if token and token.value in SESSIONS:
                del SESSIONS[token.value]
            self._send_redirect('/')
        elif path == '/student':
            if not user or user['role'] != 'student':
                self._send_redirect('/'); return
            self._serve_student(user)
        elif path == '/teacher':
            if not user or user['role'] != 'teacher':
                self._send_redirect('/'); return
            self._serve_teacher(qs)
        elif path == '/teacher_config':
            if not user or user['role'] != 'teacher':
                self._send_redirect('/'); return
            self._serve_teacher_config(qs)
        elif path == '/add_student':
            if not user or user['role'] != 'teacher':
                self._send_redirect('/'); return
            self._serve_add_student(qs)
        elif path == '/manage_students':
            if not user or user['role'] != 'teacher':
                self._send_redirect('/'); return
            self._serve_manage_students(qs)
        elif path == '/batch_import':
            if not user or user['role'] != 'teacher':
                self._send_redirect('/'); return
            self._serve_batch_import(qs)
        elif path == '/manage_courses':
            if not user or user['role'] != 'teacher':
                self._send_redirect('/'); return
            self._serve_manage_courses(qs)
        else:
            self._send_html('<h1>404</h1>', 404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path

        if path == '/':
            self._handle_login()
            return

        if path == '/add_student':
            user = get_session(self.headers.get('Cookie'))
            if not user or user['role'] != 'teacher':
                self._send_redirect('/'); return
            self._handle_add_student(user)
            return

        if path == '/batch_import':
            user = get_session(self.headers.get('Cookie'))
            if not user or user['role'] != 'teacher':
                self._send_redirect('/'); return
            self._handle_batch_import(user)
            return

        user = get_session(self.headers.get('Cookie'))
        if not user:
            self._send_json({'success': False, 'message': '请先登录'})
            return

        if path == '/api/checkin':
            self._handle_checkin(user)
        elif path == '/api/update_status':
            self._handle_update_status(user)
        elif path == '/api/update_config':
            self._handle_update_config(user)
        elif path == '/api/add_course':
            self._handle_add_course(user)
        elif path == '/api/add_student_to_course':
            self._handle_add_student_to_course(user)
        elif path == '/api/add_class':
            self._handle_add_class(user)
        elif path == '/api/rename_class':
            self._handle_rename_class(user)
        elif path == '/api/delete_class':
            self._handle_delete_class(user)
        elif path == '/api/delete_student':
            self._handle_delete_student(user)
        elif path == '/api/delete_course':
            self._handle_delete_course(user)
        elif path == '/api/update_course':
            self._handle_update_course(user)
        elif path == '/api/batch_import':
            self._handle_batch_import(user)
        else:
            self._send_json({'success': False}, 404)

    def _handle_login(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode()
        data = urllib.parse.parse_qs(body)
        username = data.get('username', [''])[0].strip()
        password = data.get('password', [''])[0].strip()

        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        row = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password)).fetchone()
        conn.close()

        if row:
            token = secrets.token_hex(16)
            SESSIONS[token] = {'id': row['id'], 'username': row['username'], 'role': row['role']}
            redirect_to = '/student' if row['role'] == 'student' else '/teacher'
            self.send_response(302)
            self.send_header('Set-Cookie', f'session={token}; Path=/; HttpOnly')
            self.send_header('Location', redirect_to)
            self.end_headers()
        else:
            self._send_html(login_page('用户名或密码错误'), 401)

    def _handle_checkin(self, user):
        today = date.today().isoformat()
        now = datetime.now()
        now_str = now.strftime('%H:%M:%S')
        student_id = user['username']

        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length).decode())
        course_id = int(body.get('course_id', 1))

        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row

        # Get student's class for config lookup
        student = conn.execute('SELECT * FROM students WHERE student_id=?', (student_id,)).fetchone()
        if not student:
            conn.close()
            self._send_json({'success': False, 'message': '未找到学生信息'}); return

        config = get_config(conn, course_id, student['class_name'])
        if not config:
            conn.close()
            self._send_json({'success': False, 'message': '该课程尚未设置签到时间，请联系教师'}); return

        # Check time window
        now_t = now.time()
        start_t = time.fromisoformat(config['start_time'])
        end_t = time.fromisoformat(config['end_time'])
        if not (start_t <= now_t <= end_t):
            conn.close()
            self._send_json({'success': False, 'message': f'不在签到时段（{config["start_time"]} - {config["end_time"]}）'})
            return

        existing = conn.execute('SELECT * FROM sign_records WHERE student_id=? AND sign_date=? AND course_id=?',
                                (student_id, today, course_id)).fetchone()
        if existing:
            conn.close()
            self._send_json({'success': False, 'message': '本课程今日已签到，请勿重复操作'}); return

        conn.execute('INSERT INTO sign_records (student_id,student_name,sign_date,sign_time,status,course_id) VALUES (?,?,?,?,?,?)',
                     (student_id, student['name'], today, now_str, '已签到', course_id))
        conn.commit()
        conn.close()
        self._send_json({'success': True, 'message': '签到成功', 'time': now_str})

    def _handle_update_status(self, user):
        if user['role'] != 'teacher':
            self._send_json({'success': False, 'message': '权限不足'}); return

        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length).decode())
        sid, sdate, status = data.get('student_id'), data.get('sign_date'), data.get('status')
        course_id = int(data.get('course_id', 1))

        if status not in ('已签到', '缺勤', '请假'):
            self._send_json({'success': False, 'message': '无效状态'}); return

        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        existing = conn.execute('SELECT * FROM sign_records WHERE student_id=? AND sign_date=? AND course_id=?',
                                (sid, sdate, course_id)).fetchone()

        if existing:
            conn.execute('UPDATE sign_records SET status=? WHERE student_id=? AND sign_date=? AND course_id=?',
                         (status, sid, sdate, course_id))
        elif status != '缺勤':
            student = conn.execute('SELECT * FROM students WHERE student_id=?', (sid,)).fetchone()
            if student:
                conn.execute('INSERT INTO sign_records (student_id,student_name,sign_date,sign_time,status,course_id) VALUES (?,?,?,?,?,?)',
                             (sid, student['name'], sdate, datetime.now().strftime('%H:%M:%S'), status, course_id))
        conn.commit()
        conn.close()
        self._send_json({'success': True, 'message': '状态已更新'})

    def _handle_update_config(self, user):
        if user['role'] != 'teacher':
            self._send_json({'success': False, 'message': '权限不足'}); return

        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode()
        data = urllib.parse.parse_qs(body)
        course_id = data.get('course_id', [''])[0]
        class_filter = data.get('class_filter', [''])[0]
        start_time = data.get('start_time', ['08:00'])[0]
        end_time = data.get('end_time', ['18:00'])[0]

        if not course_id:
            self._send_redirect('/teacher_config?error=请选择课程')
            return

        conn = sqlite3.connect(DB)
        if not class_filter:
            # All classes: delete any class-specific configs for this course
            conn.execute('DELETE FROM attendance_config WHERE course_id=? AND class_filter!=?', (course_id, ''))
        # Upsert config for this (course, class) pair
        existing = conn.execute('SELECT id FROM attendance_config WHERE course_id=? AND class_filter=?',
                                (course_id, class_filter)).fetchone()
        if existing:
            conn.execute('UPDATE attendance_config SET start_time=?, end_time=? WHERE course_id=? AND class_filter=?',
                         (start_time, end_time, course_id, class_filter))
        else:
            conn.execute('INSERT INTO attendance_config (course_id, start_time, end_time, class_filter) VALUES (?,?,?,?)',
                         (course_id, start_time, end_time, class_filter))

        # Reset today's sign-ins for this (course, class) scope
        today = date.today().isoformat()
        if class_filter:
            # Specific class: only delete records for students in that class
            conn.execute('''DELETE FROM sign_records WHERE course_id=? AND sign_date=?
                AND student_id IN (SELECT student_id FROM students WHERE class_name=?)''',
                (course_id, today, class_filter))
        else:
            # All classes: delete all records for this course
            conn.execute('''DELETE FROM sign_records WHERE course_id=? AND sign_date=?''',
                (course_id, today))

        conn.commit()
        conn.close()
        self._send_redirect(f'/teacher_config?course_id={course_id}&class_filter={urllib.parse.quote(class_filter)}&success=1')

    def _handle_add_course(self, user):
        if user['role'] != 'teacher':
            self._send_json({'success': False, 'message': '权限不足'}); return

        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length).decode())
        code = data.get('course_code', '').strip()
        name = data.get('course_name', '').strip()

        if not code or not name:
            self._send_json({'success': False, 'message': '课程代码和名称不能为空'}); return

        class_filter = data.get('class_filter', '').strip()

        conn = sqlite3.connect(DB)
        # Check if code already exists
        existing = conn.execute('SELECT id FROM courses WHERE course_code=?', (code,)).fetchone()
        if existing:
            conn.close()
            self._send_json({'success': False, 'message': f'课程代码 {code} 已存在'}); return

        # Insert course
        c = conn.cursor()
        c.execute('INSERT INTO courses (course_code, course_name) VALUES (?,?)', (code, name))
        new_id = c.lastrowid

        # Assign students: all or by class
        if class_filter:
            students = [row[0] for row in c.execute(
                'SELECT student_id FROM students WHERE class_name=?', (class_filter,)).fetchall()]
        else:
            students = [row[0] for row in c.execute('SELECT student_id FROM students').fetchall()]
        for sid in students:
            c.execute('INSERT INTO course_students (course_id, student_id) VALUES (?,?)', (new_id, sid))

        # Do NOT auto-create config — teacher must explicitly save via the form
        conn.commit()
        conn.close()
        label = f'（{class_filter}·{len(students)}人）' if class_filter else f'（全部·{len(students)}人）'
        self._send_json({'success': True, 'message': f'课程 "{name}" 已添加{label}，请前往设置签到时间'})

    def _handle_delete_course(self, user):
        if user['role'] != 'teacher':
            self._send_json({'success': False, 'message': '权限不足'}); return
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length).decode())
        course_id = data.get('course_id')
        if not course_id:
            self._send_json({'success': False, 'message': '参数不完整'}); return
        conn = sqlite3.connect(DB)
        course = conn.execute('SELECT * FROM courses WHERE id=?', (course_id,)).fetchone()
        if not course:
            conn.close()
            self._send_json({'success': False, 'message': '课程不存在'}); return
        conn.execute('DELETE FROM course_students WHERE course_id=?', (course_id,))
        conn.execute('DELETE FROM sign_records WHERE course_id=?', (course_id,))
        conn.execute('DELETE FROM attendance_config WHERE course_id=?', (course_id,))
        conn.execute('DELETE FROM courses WHERE id=?', (course_id,))
        conn.commit()
        conn.close()
        self._send_json({'success': True, 'message': f'课程 "{course[1]}" 已删除'})

    def _handle_update_course(self, user):
        if user['role'] != 'teacher':
            self._send_json({'success': False, 'message': '权限不足'}); return
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length).decode())
        course_id = data.get('course_id')
        new_code = data.get('course_code', '').strip()
        new_name = data.get('course_name', '').strip()
        if not course_id or not new_code or not new_name:
            self._send_json({'success': False, 'message': '参数不完整'}); return
        conn = sqlite3.connect(DB)
        course = conn.execute('SELECT * FROM courses WHERE id=?', (course_id,)).fetchone()
        if not course:
            conn.close()
            self._send_json({'success': False, 'message': '课程不存在'}); return
        # Check code uniqueness
        dup = conn.execute('SELECT id FROM courses WHERE course_code=? AND id!=?', (new_code, course_id)).fetchone()
        if dup:
            conn.close()
            self._send_json({'success': False, 'message': f'课程代码 {new_code} 已被其他课程使用'}); return
        conn.execute('UPDATE courses SET course_code=?, course_name=? WHERE id=?', (new_code, new_name, course_id))
        conn.commit()
        conn.close()
        self._send_json({'success': True, 'message': f'课程已更新为 "{new_name}"（{new_code}）'})

    def _handle_add_student_to_course(self, user):
        if user['role'] != 'teacher':
            self._send_json({'success': False, 'message': '权限不足'}); return

        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length).decode())
        course_id = int(data.get('course_id', 0))
        student_id = data.get('student_id', '').strip()

        if not course_id or not student_id:
            self._send_json({'success': False, 'message': '课程ID和学号不能为空'}); return

        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row

        # Check course exists
        course = conn.execute('SELECT * FROM courses WHERE id=?', (course_id,)).fetchone()
        if not course:
            conn.close()
            self._send_json({'success': False, 'message': '课程不存在'}); return

        # Check student exists
        student = conn.execute('SELECT * FROM students WHERE student_id=?', (student_id,)).fetchone()
        if not student:
            conn.close()
            self._send_json({'success': False, 'message': f'学号 {student_id} 不存在，请先在系统中录入该学生'}); return

        # Check if already enrolled
        existing = conn.execute('SELECT id FROM course_students WHERE course_id=? AND student_id=?',
                                (course_id, student_id)).fetchone()
        if existing:
            conn.close()
            self._send_json({'success': False, 'message': f'学生 {student["name"]}（{student_id}）已在课程 "{course["course_name"]}" 中'}); return

        # Add to course
        conn.execute('INSERT INTO course_students (course_id, student_id) VALUES (?,?)',
                     (course_id, student_id))
        conn.commit()
        conn.close()
        self._send_json({'success': True, 'message': f'✅ 学生 {student["name"]}（{student_id}）已添加到课程 "{course["course_name"]}"'})

    def _handle_add_class(self, user):
        if user['role'] != 'teacher':
            self._send_json({'success': False, 'message': '权限不足'}); return
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length).decode())
        class_name = data.get('class_name', '').strip()
        if not class_name:
            self._send_json({'success': False, 'message': '班级名称不能为空'}); return
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        existing = conn.execute('SELECT id FROM classes WHERE class_name=?', (class_name,)).fetchone()
        if existing:
            conn.close()
            self._send_json({'success': False, 'message': f'班级 "{class_name}" 已存在'}); return
        conn.execute('INSERT INTO classes (class_name) VALUES (?)', (class_name,))
        conn.commit()
        conn.close()
        self._send_json({'success': True, 'message': f'班级 "{class_name}" 创建成功'})

    def _handle_rename_class(self, user):
        if user['role'] != 'teacher':
            self._send_json({'success': False, 'message': '权限不足'}); return
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length).decode())
        old_name = data.get('old_name', '').strip()
        new_name = data.get('new_name', '').strip()
        if not old_name or not new_name:
            self._send_json({'success': False, 'message': '参数不完整'}); return
        if old_name == new_name:
            self._send_json({'success': False, 'message': '新旧名称相同'}); return
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        existing = conn.execute('SELECT id FROM classes WHERE class_name=?', (new_name,)).fetchone()
        if existing:
            conn.close()
            self._send_json({'success': False, 'message': f'班级 "{new_name}" 已存在'}); return
        conn.execute('UPDATE classes SET class_name=? WHERE class_name=?', (new_name, old_name))
        conn.execute('UPDATE students SET class_name=? WHERE class_name=?', (new_name, old_name))
        conn.commit()
        conn.close()
        self._send_json({'success': True, 'message': f'已改名: {old_name} → {new_name}'})

    def _handle_delete_class(self, user):
        if user['role'] != 'teacher':
            self._send_json({'success': False, 'message': '权限不足'}); return
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length).decode())
        class_name = data.get('class_name', '').strip()
        check_only = data.get('check_only', False)
        if not class_name:
            self._send_json({'success': False, 'message': '参数不完整'}); return
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        count = conn.execute('SELECT COUNT(*) as n FROM students WHERE class_name=?', (class_name,)).fetchone()['n']
        if check_only:
            conn.close()
            self._send_json({'count': count}); return
        # Delete - just remove from classes table. Students keep their class_name.
        conn.execute('DELETE FROM classes WHERE class_name=?', (class_name,))
        conn.commit()
        conn.close()
        self._send_json({'success': True, 'message': f'班级 "{class_name}" 已删除'})

    def _serve_student(self, user):
        today = date.today().isoformat()
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        selected_course_id = int(qs.get('course_id', ['1'])[0])
        
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        student = conn.execute('SELECT * FROM students WHERE student_id=?', (user['username'],)).fetchone()
        if not student: conn.close(); self._send_html('<h1>未找到学生信息</h1>', 404); return
        
        # Get all courses for this student with sign-in status
        courses = conn.execute('''SELECT c.id as course_id, c.course_name,
            CASE WHEN sr.id IS NOT NULL THEN 1 ELSE 0 END as already_signed
            FROM courses c
            JOIN course_students cs ON c.id = cs.course_id AND cs.student_id = ?
            LEFT JOIN sign_records sr ON sr.student_id=? AND sr.course_id=c.id AND sr.sign_date=?
            ORDER BY c.id''', (user['username'], user['username'], today)).fetchall()
        
        now_t = datetime.now().time()
        courses_status = []
        student_class = student['class_name']
        for c in courses:
            cfg = get_config(conn, c['course_id'], student_class)
            if cfg:
                start_t = time.fromisoformat(cfg['start_time'])
                end_t = time.fromisoformat(cfg['end_time'])
                in_window = start_t <= now_t <= end_t
                st, et = cfg['start_time'], cfg['end_time']
            else:
                in_window = False
                st, et = '--:--', '--:--'
            courses_status.append({
                'course_id': c['course_id'],
                'course_name': c['course_name'],
                'already_signed': bool(c['already_signed']),
                'in_window': in_window,
                'start_time': st,
                'end_time': et,
            })
        
        records = conn.execute('''SELECT sr.*, c.course_name FROM sign_records sr
            JOIN courses c ON sr.course_id = c.id
            WHERE sr.student_id=? ORDER BY sr.sign_date DESC, sr.course_id LIMIT 20''',
            (user['username'],)).fetchall()
        conn.close()
        self._send_html(student_page(dict(student), courses_status, records, selected_course_id))

    def _serve_teacher(self, qs):
        filter_date = qs.get('date', [date.today().isoformat()])[0]
        course_id = int(qs.get('course_id', ['1'])[0])
        status_filter = qs.get('status', [''])[0]
        class_filter = qs.get('class_filter', [''])[0]

        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        courses = get_courses(conn)
        classes = [r[0] for r in conn.execute('SELECT class_name FROM classes ORDER BY class_name').fetchall()]

        # Build query with optional class filter
        if class_filter:
            records = conn.execute('''SELECT s.student_id, s.name as student_name, s.class_name,
                c.course_name, COALESCE(sr.sign_time,'') as sign_time, COALESCE(sr.status,'缺勤') as status
                FROM students s
                JOIN course_students cs ON s.student_id = cs.student_id AND cs.course_id = ?
                LEFT JOIN courses c ON cs.course_id = c.id
                LEFT JOIN sign_records sr ON s.student_id=sr.student_id AND sr.course_id=cs.course_id AND sr.sign_date=?
                WHERE s.class_name = ?
                ORDER BY s.student_id''', (course_id, filter_date, class_filter)).fetchall()
        else:
            records = conn.execute('''SELECT s.student_id, s.name as student_name, s.class_name,
                c.course_name, COALESCE(sr.sign_time,'') as sign_time, COALESCE(sr.status,'缺勤') as status
                FROM students s
                JOIN course_students cs ON s.student_id = cs.student_id AND cs.course_id = ?
                LEFT JOIN courses c ON cs.course_id = c.id
                LEFT JOIN sign_records sr ON s.student_id=sr.student_id AND sr.course_id=cs.course_id AND sr.sign_date=?
                ORDER BY s.student_id''', (course_id, filter_date)).fetchall()

        stats = {'signed': 0, 'absent': 0, 'leave': 0, 'total': len(records)}
        for r in records:
            if r['status'] == '已签到': stats['signed'] += 1
            elif r['status'] == '缺勤': stats['absent'] += 1
            elif r['status'] == '请假': stats['leave'] += 1
        
        # Apply status filter for display (stats remain full)
        if status_filter:
            records = [r for r in records if r['status'] == status_filter]

        config = get_config(conn, course_id, class_filter)
        if not config:
            config = {'start_time': '08:00', 'end_time': '18:00'}
        conn.close()
        self._send_html(teacher_page(records, stats, filter_date, courses, classes, course_id, dict(config), status_filter, class_filter))

    def _serve_teacher_config(self, qs):
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        courses = get_courses(conn)
        classes = [r[0] for r in conn.execute('SELECT class_name FROM classes ORDER BY class_name').fetchall()]
        # Get config for the selected course + class
        course_id = int(qs.get('course_id', [1])[0]) if qs.get('course_id') else 1
        class_filter = qs.get('class_filter', [''])[0]
        config_row = get_config(conn, course_id, class_filter)
        has_config = config_row is not None
        if not config_row:
            config = {'course_id': course_id, 'class_filter': class_filter, 'start_time': '08:00', 'end_time': '18:00'}
        else:
            config = dict(config_row)
        conn.close()

        error = '请先选择课程' if qs.get('error') else None
        success = '设置已保存' if qs.get('success') else None
        self._send_html(teacher_config_page(courses, config, classes, url_class_filter=class_filter, error=error, success=success, has_config=has_config))

    def _serve_manage_students(self, qs):
        course_id = int(qs.get('course_id', ['0'])[0])
        class_filter = qs.get('class_filter', [''])[0]
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        courses = get_courses(conn)
        classes = [r[0] for r in conn.execute('SELECT class_name FROM classes ORDER BY class_name').fetchall()]
        if class_filter:
            students = conn.execute('''SELECT s.student_id, s.name, s.class_name,
                (SELECT COUNT(*) FROM course_students cs WHERE cs.student_id=s.student_id) as course_count
                FROM students s WHERE s.class_name=? ORDER BY s.student_id''', (class_filter,)).fetchall()
        else:
            students = conn.execute('''SELECT s.student_id, s.name, s.class_name,
                (SELECT COUNT(*) FROM course_students cs WHERE cs.student_id=s.student_id) as course_count
                FROM students s ORDER BY s.student_id''').fetchall()
        error = qs.get('error', [None])[0]
        success = qs.get('success', [None])[0]
        conn.close()
        self._send_html(manage_students_page(students, classes, courses, course_id, class_filter, error=error, success=success))

    def _serve_manage_courses(self, qs):
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        courses = get_courses(conn)
        error = qs.get('error', [None])[0]
        success = qs.get('success', [None])[0]
        conn.close()
        self._send_html(manage_courses_page(courses, error=error, success=success))

    def _serve_batch_import(self, qs):
        course_id = int(qs.get('course_id', ['0'])[0])
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        course = conn.execute('SELECT * FROM courses WHERE id=?', (course_id,)).fetchone()
        if not course:
            conn.close()
            self._send_html('<h1>课程不存在</h1>', 404); return
        course = dict(course)
        course['student_count'] = conn.execute('SELECT COUNT(*) FROM course_students WHERE course_id=?', (course_id,)).fetchone()[0]
        conn.close()
        self._send_html(batch_import_page(course))

    def _handle_delete_student(self, user):
        if user['role'] != 'teacher':
            self._send_json({'success': False, 'message': '权限不足'}); return
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length).decode())
        student_id = data.get('student_id', '').strip()
        if not student_id:
            self._send_json({'success': False, 'message': '参数不完整'}); return
        conn = sqlite3.connect(DB)
        student = conn.execute('SELECT * FROM students WHERE student_id=?', (student_id,)).fetchone()
        if not student:
            conn.close()
            self._send_json({'success': False, 'message': '学生不存在'}); return
        conn.execute('DELETE FROM course_students WHERE student_id=?', (student_id,))
        conn.execute('DELETE FROM sign_records WHERE student_id=?', (student_id,))
        conn.execute('DELETE FROM users WHERE username=?', (student_id,))
        conn.execute('DELETE FROM students WHERE student_id=?', (student_id,))
        conn.commit()
        conn.close()
        self._send_json({'success': True, 'message': f'学生 {student[1]}（{student_id}）已删除'})

    def _handle_batch_import(self, user):
        if user['role'] != 'teacher':
            self._send_redirect('/'); return
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        content_type = self.headers.get('Content-Type', '')
        data = parse_multipart(content_type, body)

        course_id = data.get('course_id', '')
        file_content = data.get('csv_file', b'')
        if isinstance(file_content, str):
            file_content = file_content.encode('utf-8')

        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        course = conn.execute('SELECT * FROM courses WHERE id=?', (course_id,)).fetchone()
        if not course:
            conn.close()
            self._send_redirect('/teacher_config?error=课程不存在'); return
        course = dict(course)
        course['student_count'] = conn.execute('SELECT COUNT(*) FROM course_students WHERE course_id=?', (course_id,)).fetchone()[0]

        if not file_content:
            conn.close()
            self._send_html(batch_import_page(course, {'added': 0, 'skipped': 0, 'errors': 0, 'details': []}))
            return

        # Check if it's an Excel file — try to parse it directly
        if file_content[:2] == b'PK':
            csv_text = parse_xlsx(file_content)
            if csv_text is None or not csv_text.strip():
                conn.close()
                self._send_html(batch_import_page(course, {'added': 0, 'skipped': 0, 'errors': 0, 'details': [
                    {'status': '格式错误', 'student_id': '', 'name': '无法解析 Excel 文件，请确认文件未损坏，或另存为 CSV UTF-8 格式再上传'}]}))
                return
        else:
            # Try decode — try multiple common Chinese encodings
            csv_text = None
            for enc in ['utf-8-sig', 'utf-8', 'gb18030', 'gbk', 'gb2312']:
                try:
                    csv_text = file_content.decode(enc)
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            if csv_text is None:
                conn.close()
                self._send_html(batch_import_page(course, {'added': 0, 'skipped': 0, 'errors': 0, 'details': [
                    {'status': '编码错误', 'student_id': '', 'name': '无法识别文件编码，请用 Excel 打开后"另存为"→ CSV UTF-8 格式再上传'}]}))
                return

        existing_classes = set(r[0] for r in conn.execute('SELECT class_name FROM classes').fetchall())

        added = 0
        skipped = 0
        errors = 0
        details = []

        try:
            # Detect BOM and skip header row
            lines = csv_text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
            for i, line in enumerate(lines):
                line = line.strip().lstrip('\ufeff')  # Remove BOM
                if not line:
                    continue
                # Try comma, then tab
                parts = [p.strip().strip('"') for p in line.split(',')]  # also strip quotes
                if len(parts) < 3:
                    parts = [p.strip().strip('"') for p in line.split('\t')]
                # Skip header row
                if i == 0 and (parts[0] == '学号' or parts[0].lower() == 'student_id'):
                    continue
                if len(parts) < 3:
                    errors += 1
                    details.append({'status': '格式错误', 'student_id': line[:20], 'name': ''})
                    continue

                student_id, student_name, class_name = parts[0], parts[1], parts[2]
                if not student_id or not student_name or not class_name:
                    errors += 1
                    details.append({'status': '格式错误', 'student_id': student_id or '?', 'name': student_name or '?'})
                    continue

                enrolled = conn.execute('SELECT id FROM course_students WHERE course_id=? AND student_id=?',
                                         (course_id, student_id)).fetchone()
                if enrolled:
                    skipped += 1
                    details.append({'status': '已跳过', 'student_id': student_id, 'name': student_name})
                    continue

                if class_name not in existing_classes:
                    conn.execute('INSERT INTO classes (class_name) VALUES (?)', (class_name,))
                    existing_classes.add(class_name)

                existing = conn.execute('SELECT * FROM students WHERE student_id=?', (student_id,)).fetchone()
                if not existing:
                    conn.execute('INSERT INTO students (student_id, name, class_name) VALUES (?,?,?)',
                                (student_id, student_name, class_name))
                    conn.execute('INSERT OR IGNORE INTO users (username, password, role, student_id) VALUES (?,?,?,?)',
                                (student_id, '123456', 'student', student_id))

                conn.execute('INSERT OR IGNORE INTO course_students (course_id, student_id) VALUES (?,?)',
                            (course_id, student_id))
                added += 1
                details.append({'status': '已添加', 'student_id': student_id, 'name': student_name})

            conn.commit()
        except Exception as e:
            conn.rollback()
            details.append({'status': '系统错误', 'student_id': '', 'name': str(e)[:100]})
        conn.close()
        results = {'added': added, 'skipped': skipped, 'errors': errors, 'details': details}
        self._send_html(batch_import_page(course, results))

    def _serve_add_student(self, qs):
        course_id = int(qs.get('course_id', ['0'])[0])
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        course = conn.execute('SELECT * FROM courses WHERE id=?', (course_id,)).fetchone()
        if not course:
            conn.close()
            self._send_html('<h1>课程不存在</h1>', 404); return
        course = dict(course)
        course['student_count'] = conn.execute('SELECT COUNT(*) as n FROM course_students WHERE course_id=?', (course_id,)).fetchone()['n']
        classes = [r[0] for r in conn.execute('SELECT class_name FROM classes ORDER BY class_name').fetchall()]
        error = qs.get('error', [None])[0]
        success = qs.get('success', [None])[0]
        conn.close()
        self._send_html(add_student_page(course, classes, error=error, success=success))

    def _handle_add_student(self, user):
        if user['role'] != 'teacher':
            self._send_redirect('/teacher_config?error=权限不足'); return

        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode()
        data = urllib.parse.parse_qs(body)
        course_id = data.get('course_id', [''])[0]
        student_id = data.get('student_id', [''])[0].strip()
        student_name = data.get('student_name', [''])[0].strip()
        class_name = data.get('class_name', [''])[0].strip()

        if not course_id or not student_id or not student_name or not class_name:
            self._send_redirect(f'/add_student?course_id={course_id}&error=请填写所有字段'); return

        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row

        # Check course exists
        course = conn.execute('SELECT * FROM courses WHERE id=?', (course_id,)).fetchone()
        if not course:
            conn.close()
            self._send_redirect('/teacher_config?error=课程不存在'); return

        course = dict(course)

        # Check if student already exists
        existing_student = conn.execute('SELECT * FROM students WHERE student_id=?', (student_id,)).fetchone()
        if existing_student:
            # Student exists - check if already in course
            in_course = conn.execute('SELECT id FROM course_students WHERE course_id=? AND student_id=?',
                                     (course_id, student_id)).fetchone()
            if in_course:
                conn.close()
                self._send_redirect(f'/add_student?course_id={course_id}&error=学生 {existing_student["name"]}（{student_id}）已在此课程中'); return
        else:
            # Create new student
            conn.execute('INSERT INTO students (student_id, name, class_name) VALUES (?,?,?)',
                        (student_id, student_name, class_name))
            # Create user account
            conn.execute('INSERT INTO users (username, password, role, student_id) VALUES (?,?,?,?)',
                        (student_id, '123456', 'student', student_id))

        # Add to course
        conn.execute('INSERT OR IGNORE INTO course_students (course_id, student_id) VALUES (?,?)',
                     (course_id, student_id))
        conn.commit()
        conn.close()

        self._send_redirect(f'/add_student?course_id={course_id}&success=学生 {student_name}（{student_id}）添加成功')

    def _send_html(self, html, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def _send_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _send_redirect(self, location):
        self.send_response(302)
        self.send_header('Location', urllib.parse.quote(location, safe='/:?=&'))
        self.end_headers()

if __name__ == '__main__':
    init_db()
    server = http.server.HTTPServer((HOST, PORT), SignHandler)
    print(f'\n  ✅ 学生签到系统已启动')
    print(f'  🌐 http://localhost:{PORT}')
    print(f'\n  测试账号:')
    print(f'    教师: teacher / admin123')
    print(f'    学生: 学号 / 123456\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  服务器已停止')
        server.shutdown()
