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
⚠️ 支持 CSV/TXT 文件，编码 UTF-8。<br>
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
<input type="file" name="csv_file" accept=".csv,.txt" id="fileInput" onchange="updateLabel()" style="display:none">
</label>
<button class="btn" type="submit" style="background:linear-gradient(135deg,#27ae60,#2ecc71)">🚀 开始导入</button>
</form>
</div></div>
<script>
function updateLabel(){{var f=document.getElementById('fileInput').files[0];document.getElementById('fileLabel').innerText=f?f.name:'点击选择文件或拖拽到此处'}}
document.getElementById('dropZone').addEventListener('click',function(){{document.getElementById('fileInput').click()}})
function handleDrop(e){{e.preventDefault();var f=e.dataTransfer.files[0];document.getElementById('fileInput').files=e.dataTransfer.files;if(f)document.getElementById('fileLabel').innerText=f.name}}
function toggleDetail(){{var t=document.getElementById('detailTable');if(t.className.indexOf('show')>=0){{t.className='detail-table';document.getElementById('detailLink').innerHTML='查看详情 ▼'}}else{{t.className='detail-table show';document.getElementById('detailLink').innerHTML='收起详情 ▲'}}}}
</script>
</body></html>'''
