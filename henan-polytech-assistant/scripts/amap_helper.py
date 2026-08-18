#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高德地图辅助工具 - 河南理工大学校园助手模块
功能：周边搜索（美食/景区）+ 路线规划（步行/公交/驾车）
依赖：requests
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print(json.dumps({"error": "缺少 requests 库，请执行: pip install requests"}, ensure_ascii=False))
    sys.exit(1)

# ============================================================
# 配置加载
# ============================================================

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SKILL_DIR, "config", "config.json")

# 河南理工大学南校区默认坐标（GCJ-02）
DEFAULT_LOCATION = "113.2486,35.2347"
DEFAULT_CAMPUS_NAME = "河南理工大学"

# 高德 POI 类型码映射
POI_TYPES = {
    "food": "050000",          # 餐饮服务
    "restaurant": "050000",
    "scenic": "110000",         # 风景名胜
    "scenery": "110000",
    "shopping": "060000",       # 购物服务
    "hotel": "100000",          # 住宿服务
    "hospital": "090000",       # 医疗保健
    "bank": "160000",           # 银行
    "bus": "150700",            # 公交站
    "train": "150500",          # 火车站
    "park": "110101",           # 公园
    "cinema": "080600",         # 影剧院
    "gym": "080500",            # 运动健身
    "cafe": "050500",           # 咖啡厅
    "snack": "050300",          # 快餐
}

# 高德 API 端点
AMAP_PLACE_AROUND = "https://restapi.amap.com/v3/place/around"
AMAP_GEOCODE = "https://restapi.amap.com/v3/geocode/geo"
AMAP_RE_GEO = "https://restapi.amap.com/v3/geocode/regeo"
AMAP_DIRECTION_WALKING = "https://restapi.amap.com/v3/direction/walking"
AMAP_DIRECTION_TRANSIT = "https://restapi.amap.com/v3/direction/transit/integrated"
AMAP_DIRECTION_DRIVING = "https://restapi.amap.com/v3/direction/driving"


def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_amap_key():
    """获取高德 API Key"""
    config = load_config()
    key = config.get("amap_key", "")
    if not key:
        print(json.dumps({
            "error": "未配置高德 API Key",
            "hint": f"请编辑 {CONFIG_PATH}，填入 amap_key 字段",
            "register_url": "https://lbs.amap.com/"
        }, ensure_ascii=False))
        sys.exit(1)
    return key


def get_campus_location():
    """获取校园坐标"""
    config = load_config()
    campus = config.get("campus", {})
    location = campus.get("location", DEFAULT_LOCATION)
    return location


# ============================================================
# 周边搜索
# ============================================================

def search_nearby(keyword=None, poi_type=None, location=None, radius=3000, limit=20):
    """
    搜索周边 POI
    :param keyword: 搜索关键词（与 poi_type 二选一）
    :param poi_type: POI类型码或别名（food/scenic/...）
    :param location: 中心坐标 "lng,lat"
    :param radius: 搜索半径（米）
    :param limit: 返回条数
    """
    key = get_amap_key()
    if not location:
        location = get_campus_location()

    # 解析 POI 类型
    type_code = ""
    if poi_type:
        type_code = POI_TYPES.get(poi_type.lower(), poi_type)

    params = {
        "key": key,
        "location": location,
        "radius": radius,
        "offset": min(limit, 25),
        "page": 1,
        "extensions": "all",
        "output": "json",
    }
    if keyword:
        params["keywords"] = keyword
    if type_code:
        params["types"] = type_code

    try:
        resp = requests.get(AMAP_PLACE_AROUND, params=params, timeout=10)
        data = resp.json()
    except Exception as e:
        print(json.dumps({"error": f"请求失败: {str(e)}"}, ensure_ascii=False))
        sys.exit(1)

    if data.get("status") != "1":
        print(json.dumps({"error": f"高德API返回错误: {data.get('info', '未知错误')}"}, ensure_ascii=False))
        sys.exit(1)

    pois = data.get("pois", [])
    results = []
    for poi in pois[:limit]:
        result = {
            "name": poi.get("name", ""),
            "address": poi.get("address", "") or poi.get("pname", "") + poi.get("cityname", "") + poi.get("adname", ""),
            "tel": poi.get("tel", ""),
            "type": poi.get("type", ""),
            "location": poi.get("location", ""),
        }
        # 距离信息
        distance = poi.get("distance", "")
        if distance:
            try:
                dist_m = int(distance)
                if dist_m >= 1000:
                    result["distance"] = f"{dist_m/1000:.1f}km"
                else:
                    result["distance"] = f"{dist_m}m"
                result["distance_m"] = dist_m
            except (ValueError, TypeError):
                result["distance"] = distance
        # 评分（高德部分POI有biz_ext.rating）
        biz_ext = poi.get("biz_ext", {})
        rating = biz_ext.get("rating", "")
        if rating and rating != "[]":
            result["rating"] = rating

        results.append(result)

    # 按距离排序
    results.sort(key=lambda x: x.get("distance_m", 999999))

    output = {
        "total": data.get("count", 0),
        "returned": len(results),
        "center": location,
        "radius_m": radius,
        "results": results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


# ============================================================
# 地理编码
# ============================================================

def geocode(address, city=None):
    """地址转坐标"""
    key = get_amap_key()
    params = {
        "key": key,
        "address": address,
        "output": "json",
    }
    if city:
        params["city"] = city

    try:
        resp = requests.get(AMAP_GEOCODE, params=params, timeout=10)
        data = resp.json()
    except Exception as e:
        return None

    if data.get("status") == "1" and data.get("geocodes"):
        return data["geocodes"][0].get("location", "")
    return None


# ============================================================
# 路线规划
# ============================================================

def format_duration(seconds):
    """格式化时长"""
    try:
        seconds = int(seconds)
    except (ValueError, TypeError):
        return "未知"
    if seconds < 60:
        return f"{seconds}秒"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}分钟"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"{hours}小时"
    return f"{hours}小时{mins}分钟"


def format_distance(meters):
    """格式化距离"""
    try:
        meters = int(meters)
    except (ValueError, TypeError):
        return "未知"
    if meters >= 1000:
        return f"{meters/1000:.1f}公里"
    return f"{meters}米"


def plan_route(origin=None, destination=None, mode="walking"):
    """
    路线规划
    :param origin: 起点坐标 "lng,lat"（默认校园）
    :param destination: 终点坐标 "lng,lat" 或地址
    :param mode: walking/transit/driving
    """
    key = get_amap_key()
    if not origin:
        origin = get_campus_location()

    # 如果 destination 是地址而非坐标，先地理编码
    if destination and "," not in destination:
        coords = geocode(destination, city="焦作")
        if coords:
            destination = coords
        else:
            print(json.dumps({"error": f"无法解析地址: {destination}"}, ensure_ascii=False))
            sys.exit(1)

    if not destination:
        print(json.dumps({"error": "未指定目的地"}, ensure_ascii=False))
        sys.exit(1)

    try:
        if mode == "walking":
            result = _plan_walking(key, origin, destination)
        elif mode == "transit":
            result = _plan_transit(key, origin, destination)
        elif mode == "driving":
            result = _plan_driving(key, origin, destination)
        else:
            print(json.dumps({"error": f"不支持的出行方式: {mode}（可选: walking/transit/driving）"}, ensure_ascii=False))
            sys.exit(1)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": f"路线规划失败: {str(e)}"}, ensure_ascii=False))
        sys.exit(1)


def _plan_walking(key, origin, destination):
    """步行路线"""
    params = {"key": key, "origin": origin, "destination": destination, "output": "json"}
    resp = requests.get(AMAP_DIRECTION_WALKING, params=params, timeout=10)
    data = resp.json()
    if data.get("status") != "1":
        return {"error": f"高德API错误: {data.get('info')}"}

    path = data.get("route", {}).get("paths", [{}])[0]
    distance = path.get("distance", "0")
    duration = path.get("duration", "0")
    steps = []
    for step in path.get("steps", []):
        steps.append({
            "instruction": step.get("instruction", ""),
            "distance": format_distance(step.get("distance", 0)),
            "duration": format_duration(step.get("duration", 0)),
        })

    return {
        "mode": "步行",
        "origin": origin,
        "destination": destination,
        "distance": format_distance(distance),
        "distance_m": int(distance),
        "duration": format_duration(duration),
        "duration_s": int(duration),
        "steps": steps,
    }


def _plan_transit(key, origin, destination):
    """公交路线"""
    params = {
        "key": key, "origin": origin, "destination": destination,
        "city": "焦作", "cityd": "焦作", "output": "json"
    }
    resp = requests.get(AMAP_DIRECTION_TRANSIT, params=params, timeout=15)
    data = resp.json()
    if data.get("status") != "1":
        return {"error": f"高德API错误: {data.get('info')}"}

    transits = data.get("route", {}).get("transits", [])
    if not transits:
        return {"error": "未找到公交路线", "origin": origin, "destination": destination}

    plans = []
    for i, transit in enumerate(transits[:3]):  # 最多3个方案
        distance = transit.get("distance", "0")
        duration = transit.get("duration", "0")
        cost = transit.get("cost", "")
        segments = []
        for seg in transit.get("segments", []):
            bus = seg.get("bus", {})
            buslines = bus.get("buslines", [])
            if buslines:
                line = buslines[0]
                segments.append({
                    "type": "公交",
                    "line_name": line.get("name", ""),
                    "departure_stop": line.get("departure_stop", {}).get("name", ""),
                    "arrival_stop": line.get("arrival_stop", {}).get("name", ""),
                    "via_stops": line.get("via_num", "0"),
                    "distance": format_distance(line.get("distance", 0)),
                })
            walking = seg.get("walking", {})
            if walking and walking.get("distance", "0") != "0":
                segments.append({
                    "type": "步行",
                    "distance": format_distance(walking.get("distance", 0)),
                    "duration": format_duration(walking.get("duration", 0)),
                })

        plans.append({
            "plan_index": i + 1,
            "distance": format_distance(distance),
            "duration": format_duration(duration),
            "cost": cost,
            "segments": segments,
        })

    return {
        "mode": "公交",
        "origin": origin,
        "destination": destination,
        "plans": plans,
    }


def _plan_driving(key, origin, destination):
    """驾车路线"""
    params = {"key": key, "origin": origin, "destination": destination, "output": "json"}
    resp = requests.get(AMAP_DIRECTION_DRIVING, params=params, timeout=10)
    data = resp.json()
    if data.get("status") != "1":
        return {"error": f"高德API错误: {data.get('info')}"}

    path = data.get("route", {}).get("paths", [{}])[0]
    distance = path.get("distance", "0")
    duration = path.get("duration", "0")
    tolls = path.get("tolls", "0")
    steps = []
    for step in path.get("steps", []):
        steps.append({
            "instruction": step.get("instruction", ""),
            "distance": format_distance(step.get("distance", 0)),
            "duration": format_duration(step.get("duration", 0)),
        })

    return {
        "mode": "驾车",
        "origin": origin,
        "destination": destination,
        "distance": format_distance(distance),
        "distance_m": int(distance),
        "duration": format_duration(duration),
        "duration_s": int(duration),
        "tolls": f"{tolls}元" if tolls and tolls != "0" else "无",
        "steps": steps,
    }


# ============================================================
# CLI 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="高德地图辅助工具 - 河南理工大学校园助手")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # nearby - 周边搜索
    nearby_parser = subparsers.add_parser("nearby", help="搜索周边POI")
    nearby_parser.add_argument("--keyword", help="搜索关键词")
    nearby_parser.add_argument("--type", help="POI类型: food/scenic/shopping/hotel/cafe/park/cinema/gym 等")
    nearby_parser.add_argument("--location", help="中心坐标 lng,lat（默认校园）")
    nearby_parser.add_argument("--radius", type=int, default=3000, help="搜索半径（米），默认3000")
    nearby_parser.add_argument("--limit", type=int, default=20, help="返回条数，默认20")

    # route - 路线规划
    route_parser = subparsers.add_parser("route", help="路线规划")
    route_parser.add_argument("--from", dest="origin", help="起点坐标 lng,lat（默认校园）")
    route_parser.add_argument("--to", dest="destination", required=True, help="终点坐标或地址")
    route_parser.add_argument("--mode", default="walking", choices=["walking", "transit", "driving"], help="出行方式")

    # geocode - 地址转坐标
    geo_parser = subparsers.add_parser("geocode", help="地址转坐标")
    geo_parser.add_argument("address", help="地址")
    geo_parser.add_argument("--city", help="城市名")

    args = parser.parse_args()

    if args.command == "nearby":
        search_nearby(
            keyword=args.keyword,
            poi_type=args.type,
            location=args.location,
            radius=args.radius,
            limit=args.limit,
        )
    elif args.command == "route":
        plan_route(origin=args.origin, destination=args.destination, mode=args.mode)
    elif args.command == "geocode":
        coords = geocode(args.address, args.city)
        if coords:
            print(json.dumps({"address": args.address, "location": coords}, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"error": f"无法解析地址: {args.address}"}, ensure_ascii=False))
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
