#!/usr/bin/env python3
"""Insert course_list_html into app.py"""
import os

APP = '/mnt/d/hermes/输出/签到系统/app.py'

with open(APP, 'r') as f:
    lines = f.readlines()

# Find the line "for cl in classes)" to insert after
insert_at = None
for i, line in enumerate(lines):
    if 'for cl in classes)' in line and 400 < i < 450:
        insert_at = i + 1
        break

if not insert_at:
    print("ERROR: insertion point not found")
    exit(1)

# Build the new code block line by line
new_lines = [
    '\n',
    '    # Build course list HTML for course management card\n',
    "    course_list_html = ''.join(\n",
    "        f'''<div class=\"record-item\" id=\"courseRow-{c['id']}\" style=\"align-items:center;flex-wrap:wrap\">\n",
    "<span style=\"flex:1;min-width:80px\"><b id=\"courseCodeLabel-{c['id']}\">{c['course_code']}</b></span>\n",
    "<span style=\"flex:2;min-width:120px\" id=\"courseNameLabel-{c['id']}\">{c['course_name']}</span>\n",
    "<span style=\"color:#999;font-size:12px;margin-right:8px\">{c['student_count']}人</span>\n",
    "<input id=\"courseCodeInput-{c['id']}\" value=\"{c['course_code']}\" style=\"display:none;flex:1;min-width:80px;margin:0;padding:6px 10px;font-size:14px\">\n",
    "<input id=\"courseNameInput-{c['id']}\" value=\"{c['course_name']}\" style=\"display:none;flex:2;min-width:120px;margin:0;padding:6px 10px;font-size:14px\">\n",
    "<span style=\"display:flex;gap:8px\">\n",
    "<button onclick=\"startEditCourse({c['id']})\" id=\"editCourseBtn-{c['id']}\" style=\"padding:4px 12px;background:#3498db;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px\">编辑</button>\n",
    "<button onclick=\"cancelEditCourse({c['id']})\" id=\"cancelCourseBtn-{c['id']}\" style=\"display:none;padding:4px 12px;background:#999;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px\">取消</button>\n",
    "<button onclick=\"saveEditCourse({c['id']})\" id=\"saveCourseBtn-{c['id']}\" style=\"display:none;padding:4px 12px;background:#27ae60;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px\">保存</button>\n",
    "<button onclick=\"deleteCourse({c['id']},'{c['course_name']}')\" style=\"padding:4px 12px;background:#e74c3c;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px\">删除</button>\n",
    "</span>\n",
    "</div>''' for c in courses)\n",
    '\n',
]

# Insert
for i, line in enumerate(new_lines):
    lines.insert(insert_at + i, line)

with open(APP, 'w') as f:
    f.writelines(lines)

print(f"Inserted {len(new_lines)} lines after line {insert_at}")
