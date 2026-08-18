#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
课程表解析与管理工具 - 河南理工大学校园助手模块
功能：OCR文本解析为结构化课程表、查看今日课程、下一节课提醒、空闲时间计算
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

# ============================================================
# 配置
# ============================================================

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(SKILL_DIR, "config")
SCHEDULE_PATH = os.path.join(CONFIG_DIR, "schedule.json")

# 河南理工大学标准上课时间表（可按实际调整）
# 每节课的开始和结束时间
CLASS_TIMES = [
    {"period": 1, "start": "08:00", "end": "08:45"},
    {"period": 2, "start": "08:55", "end": "09:40"},
    {"period": 3, "start": "10:00", "end": "10:45"},
    {"period": 4, "start": "10:55", "end": "11:40"},
    {"period": 5, "start": "14:30", "end": "15:15"},
    {"period": 6, "start": "15:25", "end": "16:10"},
    {"period": 7, "start": "16:30", "end": "17:15"},
    {"period": 8, "start": "17:25", "end": "18:10"},
    {"period": 9, "start": "19:00", "end": "19:45"},
    {"period": 10, "start": "19:55", "end": "20:40"},
    {"period": 11, "start": "20:50", "end": "21:35"},
]

# 星期映射
WEEKDAY_MAP = {
    "周一": 1, "周二": 2, "周三": 3, "周四": 4, "周五": 5,
    "周六": 6, "周日": 7, "星期一": 1, "星期二": 2, "星期三": 3,
    "星期四": 4, "星期五": 5, "星期六": 6, "星期日": 7, "星期天": 7,
    "monday": 1, "tuesday": 2, "wednesday": 3, "thursday": 4,
    "friday": 5, "saturday": 6, "sunday": 7,
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
}

WEEKDAY_NAMES = ["", "周一", "周二", "周三", "周四", "周五", "周六", "周日"]


# ============================================================
# 课程表加载与保存
# ============================================================

def load_schedule():
    """加载课程表"""
    if os.path.exists(SCHEDULE_PATH):
        with open(SCHEDULE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"courses": [], "semester": "", "updated_at": ""}


def save_schedule(schedule):
    """保存课程表"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    schedule["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SCHEDULE_PATH, "w", encoding="utf-8") as f:
        json.dump(schedule, f, ensure_ascii=False, indent=2)


# ============================================================
# OCR 文本解析
# ============================================================

def parse_schedule_text(text):
    """
    将 OCR 识别的文本解析为结构化课程表
    支持多种格式：
    - "周一 1-2节 高等数学 教1-101 张老师"
    - "星期一 第1-2节 高等数学 教1-101"
    - "Monday 1-2 高等数学"
    """
    courses = []
    lines = text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 尝试匹配各种格式
        course = _parse_line(line)
        if course:
            courses.append(course)

    return courses


def _parse_line(line):
    """解析单行课程信息"""
    import re

    # 匹配星期
    weekday = None
    weekday_str = ""
    for w, num in WEEKDAY_MAP.items():
        if w in line:
            weekday = num
            weekday_str = WEEKDAY_NAMES[num]
            # 从行中移除星期标记，避免干扰后续解析
            line_remain = line.replace(w, " ", 1)
            break
    else:
        line_remain = line

    if weekday is None:
        return None

    # 匹配节次（支持 "1-2节"、"第1-2节"、"1,2节"、"1-2" 等格式）
    period_pattern = r"(?:第)?(\d+)\s*[-~至到]\s*(\d+)\s*节?"
    match = re.search(period_pattern, line_remain)
    if match:
        start_period = int(match.group(1))
        end_period = int(match.group(2))
    else:
        # 尝试单节 "第3节" 或 "3节"
        single_pattern = r"(?:第)?(\d+)\s*节"
        match = re.search(single_pattern, line_remain)
        if match:
            start_period = end_period = int(match.group(1))
        else:
            return None

    # 移除已匹配的节次部分
    line_remain = re.sub(r"(?:第)?\d+\s*[-~至到]\s*\d+\s*节?", "", line_remain, count=1)
    line_remain = re.sub(r"(?:第)?\d+\s*节?", "", line_remain, count=1)

    # 剩余部分按空格分割，提取课程名、教室、教师
    parts = [p.strip() for p in line_remain.split() if p.strip()]
    parts = [p for p in parts if p and p not in ["|", "-", "—"]]

    course_name = ""
    classroom = ""
    teacher = ""
    weeks = ""

    if parts:
        course_name = parts[0]
    if len(parts) > 1:
        # 判断是否为教室（通常包含数字、楼、室等）
        classroom_candidates = [p for p in parts[1:] if re.search(r"\d|楼|室|教|号|栋|层", p)]
        if classroom_candidates:
            classroom = classroom_candidates[0]
        # 教师名通常在最后
        teacher_candidates = [p for p in parts[1:] if p not in classroom_candidates and len(p) <= 4]
        if teacher_candidates:
            teacher = teacher_candidates[-1]

    # 尝试匹配周次信息 "1-16周" "第1-16周"
    week_match = re.search(r"(?:第)?(\d+)\s*[-~至到]\s*(\d+)\s*周", line)
    if week_match:
        weeks = f"{week_match.group(1)}-{week_match.group(2)}周"

    # 计算时间
    start_time = ""
    end_time = ""
    if 1 <= start_period <= len(CLASS_TIMES):
        start_time = CLASS_TIMES[start_period - 1]["start"]
    if 1 <= end_period <= len(CLASS_TIMES):
        end_time = CLASS_TIMES[end_period - 1]["end"]

    return {
        "weekday": weekday,
        "weekday_name": weekday_str,
        "start_period": start_period,
        "end_period": end_period,
        "start_time": start_time,
        "end_time": end_time,
        "course_name": course_name,
        "classroom": classroom,
        "teacher": teacher,
        "weeks": weeks,
    }


# ============================================================
# 今日课程
# ============================================================

def get_today_courses():
    """获取今日课程"""
    schedule = load_schedule()
    today_weekday = datetime.now().weekday() + 1  # Monday=1

    courses = [c for c in schedule.get("courses", []) if c.get("weekday") == today_weekday]
    courses.sort(key=lambda c: c.get("start_period", 0))

    if not courses:
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "weekday": WEEKDAY_NAMES[today_weekday],
            "message": "今天没有课程",
            "courses": [],
        }

    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "weekday": WEEKDAY_NAMES[today_weekday],
        "total": len(courses),
        "courses": courses,
    }


# ============================================================
# 下一节课
# ============================================================

def get_next_course():
    """获取下一节课"""
    schedule = load_schedule()
    now = datetime.now()
    today_weekday = now.weekday() + 1
    current_time = now.strftime("%H:%M")

    courses = [c for c in schedule.get("courses", []) if c.get("weekday") == today_weekday]
    courses.sort(key=lambda c: c.get("start_period", 0))

    if not courses:
        return {
            "date": now.strftime("%Y-%m-%d"),
            "weekday": WEEKDAY_NAMES[today_weekday],
            "current_time": current_time,
            "message": "今天没有课程了",
            "next_course": None,
        }

    # 找到下一节课（开始时间晚于当前时间）
    next_courses = [c for c in courses if c.get("start_time", "") > current_time]

    if next_courses:
        next_c = next_courses[0]
        # 计算距离上课还有多久
        start_h, start_m = map(int, next_c["start_time"].split(":"))
        now_h, now_m = now.hour, now.minute
        diff_minutes = (start_h * 60 + start_m) - (now_h * 60 + now_m)

        reminder = ""
        if diff_minutes <= 15:
            reminder = f"即将上课！还有 {diff_minutes} 分钟"
        elif diff_minutes <= 30:
            reminder = f"还有 {diff_minutes} 分钟上课，请准备前往教室"
        else:
            hours = diff_minutes // 60
            mins = diff_minutes % 60
            if hours > 0:
                reminder = f"还有 {hours}小时{mins}分钟 上课"
            else:
                reminder = f"还有 {mins}分钟 上课"

        return {
            "date": now.strftime("%Y-%m-%d"),
            "weekday": WEEKDAY_NAMES[today_weekday],
            "current_time": current_time,
            "reminder": reminder,
            "next_course": next_c,
            "remaining_courses_today": len(next_courses),
        }
    else:
        return {
            "date": now.strftime("%Y-%m-%d"),
            "weekday": WEEKDAY_NAMES[today_weekday],
            "current_time": current_time,
            "message": "今天的课程已全部结束",
            "next_course": None,
        }


# ============================================================
# 空闲时间计算
# ============================================================

def get_free_time(weekday=None):
    """计算空闲时间段"""
    if weekday is None:
        weekday = datetime.now().weekday() + 1
    elif isinstance(weekday, str):
        weekday = WEEKDAY_MAP.get(weekday.lower(), WEEKDAY_MAP.get(weekday, int(weekday) if weekday.isdigit() else datetime.now().weekday() + 1))

    schedule = load_schedule()
    courses = [c for c in schedule.get("courses", []) if c.get("weekday") == weekday]
    courses.sort(key=lambda c: c.get("start_period", 0))

    if not courses:
        return {
            "weekday": WEEKDAY_NAMES.get(weekday, f"第{weekday}天"),
            "message": "全天无课，可以自由安排！",
            "free_slots": [{"start": "全天", "end": "全天", "duration": "全天空闲"}],
            "courses": [],
        }

    # 计算占用时间段
    busy_slots = []
    for c in courses:
        busy_slots.append({
            "start": c.get("start_time", ""),
            "end": c.get("end_time", ""),
            "course": c.get("course_name", ""),
        })

    # 计算空闲时间段
    free_slots = []
    # 早上第一节课之前
    first_start = busy_slots[0]["start"]
    if first_start > "08:00":
        free_slots.append({"start": "08:00", "end": first_start, "duration": _calc_duration("08:00", first_start)})

    # 课程之间的间隙
    for i in range(len(busy_slots) - 1):
        gap_start = busy_slots[i]["end"]
        gap_end = busy_slots[i + 1]["start"]
        if gap_start < gap_end:
            duration = _calc_duration(gap_start, gap_end)
            if duration and "分钟" in duration:
                mins = int(duration.replace("分钟", "").replace("小时", ""))
                if mins >= 30:  # 只显示30分钟以上的空闲
                    free_slots.append({"start": gap_start, "end": gap_end, "duration": duration})

    # 最后一节课之后
    last_end = busy_slots[-1]["end"]
    if last_end < "21:35":
        free_slots.append({"start": last_end, "end": "21:35", "duration": _calc_duration(last_end, "21:35")})

    return {
        "weekday": WEEKDAY_NAMES.get(weekday, f"第{weekday}天"),
        "total_courses": len(courses),
        "courses": busy_slots,
        "free_slots": free_slots,
        "free_slots_count": len(free_slots),
    }


def _calc_duration(start, end):
    """计算时间差"""
    try:
        sh, sm = map(int, start.split(":"))
        eh, em = map(int, end.split(":"))
        diff = (eh * 60 + em) - (sh * 60 + sm)
        if diff <= 0:
            return None
        if diff >= 60:
            hours = diff // 60
            mins = diff % 60
            return f"{hours}小时{mins}分钟" if mins else f"{hours}小时"
        return f"{diff}分钟"
    except (ValueError, IndexError):
        return None


# ============================================================
# CLI 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="课程表管理工具 - 河南理工大学校园助手")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # parse - 解析课程表文本
    parse_parser = subparsers.add_parser("parse", help="解析OCR文本为结构化课程表")
    parse_parser.add_argument("--file", help="从文件读取OCR文本")
    parse_parser.add_argument("--replace", action="store_true", help="替换已有课程表（默认追加）")

    # today - 今日课程
    subparsers.add_parser("today", help="查看今日课程")

    # next - 下一节课
    subparsers.add_parser("next", help="查看下一节课")

    # free - 空闲时间
    free_parser = subparsers.add_parser("free", help="查看空闲时间")
    free_parser.add_argument("--day", help="星期几（1-7或周一~周日），默认今天")

    # list - 列出所有课程
    subparsers.add_parser("list", help="列出所有课程")

    # clear - 清空课程表
    subparsers.add_parser("clear", help="清空课程表")

    args = parser.parse_args()

    if args.command == "parse":
        # 读取文本
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            text = sys.stdin.read()

        if not text.strip():
            print(json.dumps({"error": "未输入文本"}, ensure_ascii=False))
            sys.exit(1)

        courses = parse_schedule_text(text)
        if not courses:
            print(json.dumps({"error": "未能从文本中解析出课程信息", "input": text[:200]}, ensure_ascii=False))
            sys.exit(1)

        schedule = load_schedule()
        if args.replace:
            schedule["courses"] = courses
        else:
            schedule["courses"].extend(courses)
        save_schedule(schedule)

        print(json.dumps({
            "action": "parse",
            "mode": "replace" if args.replace else "append",
            "parsed_courses": len(courses),
            "total_courses": len(schedule["courses"]),
            "courses": courses,
        }, ensure_ascii=False, indent=2))

    elif args.command == "today":
        result = get_today_courses()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "next":
        result = get_next_course()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "free":
        result = get_free_time(args.day)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "list":
        schedule = load_schedule()
        courses = schedule.get("courses", [])
        # 按星期、节次排序
        courses.sort(key=lambda c: (c.get("weekday", 0), c.get("start_period", 0)))
        print(json.dumps({
            "total": len(courses),
            "semester": schedule.get("semester", ""),
            "updated_at": schedule.get("updated_at", ""),
            "courses": courses,
        }, ensure_ascii=False, indent=2))

    elif args.command == "clear":
        save_schedule({"courses": [], "semester": "", "updated_at": ""})
        print(json.dumps({"action": "clear", "message": "课程表已清空"}, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
