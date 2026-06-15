import sys

with open('/mnt/d/hermes/输出/签到系统/app.py', 'r') as f:
    lines = f.readlines()

# Find class_list_html end (line with "for cl in classes)\n")
# and the HTML card insertion point (before <!-- Add/Manage classes -->)
insert_var_at = None
insert_html_at = None

for i, line in enumerate(lines):
    if 'for cl in classes)' in line and i > 400 and i < 430:
        insert_var_at = i + 1  # after this line
    if '<!-- Add/Manage classes -->' in line and i > 480:
        insert_html_at = i  # before this line
        break

print(f"Insert var after line: {insert_var_at + 1}")
print(f"Insert HTML before line: {insert_html_at + 1}")

# The Python variable for course_list_html
course_list_var = '''
    # Build course list HTML for course management card
    course_list_html = ''.join(
        f\\'\\'\\'<div class="record-item" id="courseRow-{c[\\'id\\']}" style="align-items:center;flex-wrap:wrap">
<span style="flex:1;min-width:80px"><b id="courseCodeLabel-{c[\\'id\\']}">{c[\\'course_code\\']}</b></span>
<span style="flex:2;min-width:120px" id="courseNameLabel-{c[\\'id\\']}">{c[\\'course_name\\']}</span>
<span style="color:#999;font-size:12px;margin-right:8px">{c[\\'student_count\\']}人</span>
<input id="courseCodeInput-{c[\\'id\\']}" value="{c[\\'course_code\\']}" style="display:none;flex:1;min-width:80px;margin:0;padding:6px 10px;font-size:14px">
<input id="courseNameInput-{c[\\'id\\']}" value="{c[\\'course_name\\']}" style="display:none;flex:2;min-width:120px;margin:0;padding:6px 10px;font-size:14px">
<span style="display:flex;gap:8px">
<button onclick="startEditCourse({c[\\'id\\']})" id="editCourseBtn-{c[\\'id\\']}" style="padding:4px 12px;background:#3498db;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px">编辑</button>
<button onclick="cancelEditCourse({c[\\'id\\']})" id="cancelCourseBtn-{c[\\'id\\']}" style="display:none;padding:4px 12px;background:#999;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px">取消</button>
<button onclick="saveEditCourse({c[\\'id\\']})" id="saveCourseBtn-{c[\\'id\\']}" style="display:none;padding:4px 12px;background:#27ae60;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px">保存</button>
<button onclick="deleteCourse({c[\\'id\\']},\\'{c[\\'course_name\\']}\\')" style="padding:4px 12px;background:#e74c3c;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px">删除</button>
</span>
</div>\\'\\'\\' for c in courses)
'''

# The HTML card to insert before the class management section
course_card_html = '''
<!-- Course Management -->
<div class="card" style="margin-top:16px">
<div class="section-title" style="margin-bottom:12px">📚 课程管理</div>
<div id="courseList">
{course_list_html}
</div>
</div>

'''

# Insert
if insert_var_at:
    lines.insert(insert_var_at, course_list_var)
    insert_html_at += 1  # adjust for inserted line
if insert_html_at:
    lines.insert(insert_html_at, course_card_html)

with open('/mnt/d/hermes/输出/签到系统/app.py', 'w') as f:
    f.writelines(lines)

print("Done")
