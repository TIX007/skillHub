#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
火车票查询工具 - 河南理工大学校园助手模块
功能：12306余票查询、家位置管理、车站名码查询
依赖：requests
"""

import argparse
import json
import os
import sys
import re
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print(json.dumps({"error": "缺少 requests 库，请执行: pip install requests"}, ensure_ascii=False))
    sys.exit(1)

# ============================================================
# 配置
# ============================================================

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SKILL_DIR, "config", "config.json")

# 12306 接口
STATION_NAME_URL = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js"
LEFT_TICKET_URL = "https://kyfw.12306.cn/otn/leftTicket/queryZ"
LEFT_TICKET_FALLBACK_URL = "https://kyfw.12306.cn/otn/leftTicket/query"

# 默认车站
DEFAULT_FROM_STATION = "焦作"  # 河南理工大学最近火车站
NEAREST_STATIONS = ["焦作", "焦作西"]

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://kyfw.12306.cn/otn/leftTicket/init",
    "X-Requested-With": "XMLHttpRequest",
}

# 车站名码缓存
_station_codes = None


def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(config):
    """保存配置文件"""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


# ============================================================
# 车站名码查询
# ============================================================

def load_station_codes():
    """加载 12306 车站名码表"""
    global _station_codes
    if _station_codes is not None:
        return _station_codes

    # 尝试从缓存文件加载
    cache_path = os.path.join(SKILL_DIR, "config", "station_codes.json")
    if os.path.exists(cache_path):
        mtime = os.path.getmtime(cache_path)
        # 缓存7天有效
        if (time.time() - mtime) < 7 * 86400:
            with open(cache_path, "r", encoding="utf-8") as f:
                _station_codes = json.load(f)
                return _station_codes

    # 从 12306 下载
    try:
        resp = requests.get(STATION_NAME_URL, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        text = resp.text
        # 格式: var station_names = '@bjb|北京北|VAP|beijingbei|bjb|0@...'
        pattern = r"@([a-z]+)\|([^\|]+)\|([A-Z]+)\|"
        matches = re.findall(pattern, text)
        _station_codes = {}
        for py, name, code in matches:
            _station_codes[name] = code
            _station_codes[name.lower()] = code
            _station_codes[py] = code

        # 写入缓存
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(_station_codes, f, ensure_ascii=False)

        return _station_codes
    except Exception as e:
        # 尝试使用缓存
        cache_path_fallback = os.path.join(SKILL_DIR, "config", "station_codes.json")
        if os.path.exists(cache_path_fallback):
            with open(cache_path_fallback, "r", encoding="utf-8") as f:
                _station_codes = json.load(f)
                return _station_codes
        print(json.dumps({"error": f"获取车站名码失败: {str(e)}"}, ensure_ascii=False))
        sys.exit(1)


def get_station_code(name):
    """获取车站三字码"""
    codes = load_station_codes()
    # 精确匹配
    if name in codes:
        return codes[name]
    # 模糊匹配
    for key, code in codes.items():
        if name in key or key in name:
            return code
    return None


# ============================================================
# 日期解析
# ============================================================

def parse_date(date_str):
    """解析日期字符串"""
    if not date_str or date_str == "today":
        return datetime.now().strftime("%Y-%m-%d")
    elif date_str == "tomorrow":
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    elif date_str == "day_after_tomorrow":
        return (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    else:
        # 尝试解析 YYYY-MM-DD
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            pass
        # 尝试解析 MM-DD
        try:
            year = datetime.now().year
            datetime.strptime(f"{year}-{date_str}", "%Y-%m-%d")
            return f"{year}-{date_str}"
        except ValueError:
            pass
    print(json.dumps({"error": f"日期格式无效: {date_str}，支持: today/tomorrow/YYYY-MM-DD"}, ensure_ascii=False))
    sys.exit(1)


# ============================================================
# 余票查询
# ============================================================

def query_trains(from_station, to_station, date_str):
    """
    查询余票
    :param from_station: 出发站名（中文）
    :param to_station: 到达站名（中文）
    :param date_str: 日期 YYYY-MM-DD
    """
    from_code = get_station_code(from_station)
    to_code = get_station_code(to_station)

    if not from_code:
        print(json.dumps({"error": f"未找到车站: {from_station}"}, ensure_ascii=False))
        sys.exit(1)
    if not to_code:
        print(json.dumps({"error": f"未找到车站: {to_station}"}, ensure_ascii=False))
        sys.exit(1)

    date = parse_date(date_str)

    params = {
        "leftTicketDTO.train_date": date,
        "leftTicketDTO.from_station": from_code,
        "leftTicketDTO.to_station": to_code,
        "purpose_codes": "ADULT",
    }

    # 尝试多个接口
    urls = [LEFT_TICKET_URL, LEFT_TICKET_FALLBACK_URL]
    data = None
    last_error = ""

    for url in urls:
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
            data = resp.json()
            if data.get("httpstatus") == 200:
                break
            else:
                last_error = data.get("messages", ["未知错误"])
                if isinstance(last_error, list) and last_error:
                    last_error = last_error[0]
        except Exception as e:
            last_error = str(e)
            continue

    if not data or data.get("httpstatus") != 200:
        print(json.dumps({
            "error": f"12306查询失败: {last_error}",
            "hint": "12306接口可能暂时不可用或正在维护，请稍后重试或访问 12306官网/APP 查询"
        }, ensure_ascii=False))
        sys.exit(1)

    result = data.get("data", {})
    raw_trains = result.get("result", [])
    map_info = result.get("map", {})

    if not raw_trains:
        print(json.dumps({
            "date": date,
            "from": from_station,
            "to": to_station,
            "trains": [],
            "message": "未查询到车次，可能该日期无直达车次"
        }, ensure_ascii=False, indent=2))
        return

    trains = []
    for raw in raw_trains:
        parts = raw.split("|")
        if len(parts) < 37:
            continue

        # 12306 返回字段说明（按 | 分割后的索引）：
        # 0: secret_str, 1: 预留, 2: 车次代码, 3: 车次号
        # 6: 出发站码, 7: 到达站码
        # 8: 出发时间, 9: 到达时间, 10: 历时
        # 21-28: 各种座位余票
        # 30-31: 商务座/特等座, 32: 一等座, 33: 二等座
        # 26: 硬座, 27: 软座, 28: 硬卧, 29: 软卧, 23: 无座

        train_no = parts[2] if len(parts) > 2 else ""
        from_name = map_info.get(parts[6], parts[6]) if len(parts) > 6 else ""
        to_name = map_info.get(parts[7], parts[7]) if len(parts) > 7 else ""
        start_time = parts[8] if len(parts) > 8 else ""
        arrive_time = parts[9] if len(parts) > 9 else ""
        duration = parts[10] if len(parts) > 10 else ""

        # 座位信息（索引参考12306返回格式）
        def get_seat(idx):
            if idx < len(parts):
                val = parts[idx]
                if val and val != "" and val != "无":
                    return val
            return "--"

        train = {
            "train_no": train_no,
            "from_station": from_name,
            "to_station": to_name,
            "start_time": start_time,
            "arrive_time": arrive_time,
            "duration": _format_duration(duration),
            "business_seat": get_seat(32),       # 商务座/特等座
            "first_seat": get_seat(31),          # 一等座
            "second_seat": get_seat(30),         # 二等座
            "soft_sleeper": get_seat(23),        # 软卧/一等卧
            "hard_sleeper": get_seat(28),        # 硬卧/二等卧
            "soft_seat": get_seat(24),           # 软座
            "hard_seat": get_seat(29),           # 硬座
            "no_seat": get_seat(26),             # 无座
        }
        trains.append(train)

    output = {
        "date": date,
        "from": from_station,
        "to": to_station,
        "total": len(trains),
        "trains": trains,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def _format_duration(raw):
    """格式化历时"""
    if not raw:
        return "未知"
    # 格式如 "02:30" 或 "12:30:00"
    parts = raw.split(":")
    if len(parts) >= 2:
        hours = int(parts[0])
        minutes = int(parts[1])
        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        return f"{minutes}分钟"
    return raw


# ============================================================
# 家位置管理
# ============================================================

def set_home(city, station=None, address=None):
    """设置家位置"""
    config = load_config()
    if not config:
        config = {}

    home = {
        "city": city,
        "station": station or city,
    }
    if address:
        home["address"] = address

    config["home"] = home
    save_config(config)

    # 验证车站是否存在
    code = get_station_code(home["station"])
    result = {
        "action": "set_home",
        "home": home,
        "station_code": code,
        "message": f"家位置已设置为: {city}" + (f"（车站: {station}）" if station else ""),
    }
    if not code:
        result["warning"] = f"未在12306找到车站「{home['station']}」，请检查车站名"
    print(json.dumps(result, ensure_ascii=False, indent=2))


def query_home(date_str):
    """查询从学校到家的火车票"""
    config = load_config()
    home = config.get("home")
    if not home:
        print(json.dumps({
            "error": "未设置家位置",
            "hint": "请先设置家位置: python train_query.py sethome --city 郑州 --station 郑州东"
        }, ensure_ascii=False))
        sys.exit(1)

    from_station = DEFAULT_FROM_STATION
    to_station = home.get("station", home.get("city", ""))

    print(json.dumps({"info": f"查询 {from_station} → {to_station} 的火车票", "date": parse_date(date_str)}, ensure_ascii=False), file=sys.stderr)
    query_trains(from_station, to_station, date_str)


def query_to_school(date_str):
    """查询从家到学校的火车票（返校）"""
    config = load_config()
    home = config.get("home")
    if not home:
        print(json.dumps({
            "error": "未设置家位置",
            "hint": "请先设置家位置: python train_query.py sethome --city 郑州 --station 郑州东"
        }, ensure_ascii=False))
        sys.exit(1)

    from_station = home.get("station", home.get("city", ""))
    to_station = DEFAULT_FROM_STATION

    print(json.dumps({"info": f"查询 {from_station} → {to_station} 的火车票（返校）", "date": parse_date(date_str)}, ensure_ascii=False), file=sys.stderr)
    query_trains(from_station, to_station, date_str)


# ============================================================
# CLI 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="火车票查询工具 - 河南理工大学校园助手")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # query - 查询车票
    query_parser = subparsers.add_parser("query", help="查询火车票")
    query_parser.add_argument("--from", dest="from_station", required=True, help="出发站名")
    query_parser.add_argument("--to", dest="to_station", required=True, help="到达站名")
    query_parser.add_argument("--date", default="today", help="日期: today/tomorrow/YYYY-MM-DD")

    # home - 查询回家车票
    home_parser = subparsers.add_parser("home", help="查询从学校回家的火车票")
    home_parser.add_argument("--date", default="today", help="日期: today/tomorrow/YYYY-MM-DD")

    # toschool - 查询返校车票
    school_parser = subparsers.add_parser("toschool", help="查询从家到学校的火车票")
    school_parser.add_argument("--date", default="today", help="日期: today/tomorrow/YYYY-MM-DD")

    # sethome - 设置家位置
    sethome_parser = subparsers.add_parser("sethome", help="设置家位置")
    sethome_parser.add_argument("--city", required=True, help="城市名")
    sethome_parser.add_argument("--station", help="火车站名（默认与城市同名）")
    sethome_parser.add_argument("--address", help="详细地址（可选）")

    # search - 搜索车站
    search_parser = subparsers.add_parser("search", help="搜索车站代码")
    search_parser.add_argument("name", help="车站名关键词")

    args = parser.parse_args()

    if args.command == "query":
        query_trains(args.from_station, args.to_station, args.date)
    elif args.command == "home":
        query_home(args.date)
    elif args.command == "toschool":
        query_to_school(args.date)
    elif args.command == "sethome":
        set_home(args.city, args.station, args.address)
    elif args.command == "search":
        codes = load_station_codes()
        results = {k: v for k, v in codes.items() if args.name in k}
        if results:
            print(json.dumps({"keyword": args.name, "matches": results}, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"error": f"未找到匹配「{args.name}」的车站"}, ensure_ascii=False))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
