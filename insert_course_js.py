#!/usr/bin/env python3
"""Insert course management JS into app.py"""
APP = '/mnt/d/hermes/输出/签到系统/app.py'

with open(APP, 'r') as f:
    lines = f.readlines()

# Find the </script> that closes teacher_config (around line 787)
insert_at = None
for i, line in enumerate(lines):
    if line.strip() == '</script>' and 780 < i < 800:
        # Verify by checking next line
        if i+1 < len(lines) and '</body></html>' in lines[i+1]:
            insert_at = i
            break

if not insert_at:
    print("ERROR: insertion point not found")
    exit(1)

print(f"Inserting before line {insert_at + 1}")

js_code = [
    '\n',
    '// ======== Course Management ========\n',
    'function startEditCourse(id) {\n',
    "    document.getElementById('courseCodeLabel-'+id).style.display='none';\n",
    "    document.getElementById('courseNameLabel-'+id).style.display='none';\n",
    "    document.getElementById('courseCodeInput-'+id).style.display='block';\n",
    "    document.getElementById('courseNameInput-'+id).style.display='block';\n",
    "    document.getElementById('editCourseBtn-'+id).style.display='none';\n",
    "    document.getElementById('cancelCourseBtn-'+id).style.display='inline';\n",
    "    document.getElementById('saveCourseBtn-'+id).style.display='inline';\n",
    '}\n',
    'function cancelEditCourse(id) {\n',
    "    document.getElementById('courseCodeLabel-'+id).style.display='';\n",
    "    document.getElementById('courseNameLabel-'+id).style.display='';\n",
    "    document.getElementById('courseCodeInput-'+id).style.display='none';\n",
    "    document.getElementById('courseNameInput-'+id).style.display='none';\n",
    "    document.getElementById('editCourseBtn-'+id).style.display='inline';\n",
    "    document.getElementById('cancelCourseBtn-'+id).style.display='none';\n",
    "    document.getElementById('saveCourseBtn-'+id).style.display='none';\n",
    '}\n',
    'async function saveEditCourse(id) {\n',
    "    var code = document.getElementById('courseCodeInput-'+id).value.trim();\n",
    "    var name = document.getElementById('courseNameInput-'+id).value.trim();\n",
    "    if (!code || !name) { alert('课程代码和名称不能为空'); return; }\n",
    '    try {\n',
    "        let r = await fetch('/api/update_course', {\n",
    "            method: 'POST',\n",
    "            headers: {'Content-Type': 'application/json'},\n",
    '            body: JSON.stringify({course_id: id, course_code: code, course_name: name})\n',
    '        });\n',
    '        let d = await r.json();\n',
    '        if (d.success) {\n',
    '            location.reload();\n',
    '        } else {\n',
    "            alert(d.message);\n",
    '            cancelEditCourse(id);\n',
    '        }\n',
    "    } catch(e) { alert('网络错误'); }\n",
    '}\n',
    'async function deleteCourse(id, name) {\n',
    "    if (!confirm('确定要删除课程 \"' + name + '\" 吗？\\n\\n此操作将同时删除该课程的所有签到记录和学生关联，不可恢复。')) return;\n",
    '    try {\n',
    "        let r = await fetch('/api/delete_course', {\n",
    "            method: 'POST',\n",
    "            headers: {'Content-Type': 'application/json'},\n",
    '            body: JSON.stringify({course_id: id})\n',
    '        });\n',
    '        let d = await r.json();\n',
    '        if (d.success) {\n',
    "            var row = document.getElementById('courseRow-'+id);\n",
    "            if (row) row.remove();\n",
    '            location.reload();\n',
    '        } else {\n',
    "            alert(d.message);\n",
    '        }\n',
    "    } catch(e) { alert('网络错误'); }\n",
    '}\n',
]

for i, line in enumerate(js_code):
    lines.insert(insert_at + i, line)

with open(APP, 'w') as f:
    f.writelines(lines)

print(f"Inserted {len(js_code)} lines")
