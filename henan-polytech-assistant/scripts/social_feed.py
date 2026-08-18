#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校园社交媒体动态获取工具 - 河南理工大学校园助手模块
功能：获取贴吧、小红书、抖音等平台的河南理工大学相关动态
说明：本脚本为辅助搜索工具，实际数据获取依赖 WebSearch / WebFetch
"""

import argparse
import json
import sys

# ============================================================
# 搜索关键词配置
# ============================================================

SCHOOL_NAME = "河南理工大学"
SCHOOL_ABBR = "HPU"
SCHOOL_KEYWORDS = [
    "河南理工大学",
    "河南理工",
    "HPU",
    "理工大焦作",
]

# 各平台搜索 URL 模板
PLATFORM_URLS = {
    "tieba": {
        "name": "百度贴吧",
        "search_url": "https://tieba.baidu.com/f?kw={keyword}",
        "websearch_pattern": "site:tieba.baidu.com {keyword}",
        "description": "河南理工大学吧 - 校园讨论主阵地",
    },
    "xiaohongshu": {
        "name": "小红书",
        "search_url": "https://www.xiaohongshu.com/search_result?keyword={keyword}",
        "websearch_pattern": "小红书 {keyword} 最新",
        "description": "校园生活分享、美食探店、穿搭美妆",
    },
    "douyin": {
        "name": "抖音",
        "search_url": "https://www.douyin.com/search/{keyword}",
        "websearch_pattern": "抖音 {keyword} 最新活动",
        "description": "校园短视频、活动直播、热门话题",
    },
    "weibo": {
        "name": "微博",
        "search_url": "https://s.weibo.com/weibo?q={keyword}",
        "websearch_pattern": "site:weibo.com {keyword}",
        "description": "校园官方微博、话题讨论",
    },
}


def generate_search_queries(platform, limit=10):
    """
    为指定平台生成搜索关键词
    供 Agent 使用 WebSearch / WebFetch 时参考
    """
    if platform not in PLATFORM_URLS:
        return {"error": f"不支持的平台: {platform}（可选: {', '.join(PLATFORM_URLS.keys())}）"}

    p_info = PLATFORM_URLS[platform]
    queries = []
    for kw in SCHOOL_KEYWORDS:
        url = p_info["search_url"].format(keyword=kw)
        ws_query = p_info["websearch_pattern"].format(keyword=kw)
        queries.append({
            "keyword": kw,
            "platform_url": url,
            "websearch_query": ws_query,
        })

    return {
        "platform": platform,
        "platform_name": p_info["name"],
        "description": p_info["description"],
        "limit": limit,
        "search_queries": queries,
        "hint": "请使用 WebSearch 工具执行上述 websearch_query，或使用 WebFetch 访问 platform_url 获取内容",
    }


def generate_all_queries(limit=10):
    """生成所有平台的搜索建议"""
    all_queries = {}
    for platform in PLATFORM_URLS:
        all_queries[platform] = generate_search_queries(platform, limit)
    return {
        "school": SCHOOL_NAME,
        "total_platforms": len(PLATFORM_URLS),
        "platforms": all_queries,
        "hint": "建议并行执行多个平台的 WebSearch，汇总后去重排序输出",
    }


def get_activity_recommendations():
    """获取校园活动搜索建议关键词"""
    return {
        "activity_keywords": [
            f"{SCHOOL_NAME} 社团招新",
            f"{SCHOOL_NAME} 校园活动",
            f"{SCHOOL_NAME} 讲座",
            f"{SCHOOL_NAME} 比赛",
            f"{SCHOOL_NAME} 迎新",
            f"{SCHOOL_NAME} 运动会",
            f"{SCHOOL_NAME} 晚会",
            f"{SCHOOL_NAME} 志愿服务",
            f"{SCHOOL_ABBR} 活动",
            "焦作大学城 活动",
        ],
        "search_strategy": [
            "1. 使用 WebSearch 搜索上述关键词",
            "2. 使用 WebFetch 访问贴吧首页获取最新帖子",
            "3. 汇总多个平台的结果，按时间排序",
            "4. 提取活动名称、时间、地点、参与方式",
        ],
    }


# ============================================================
# CLI 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="校园社交媒体动态获取 - 河南理工大学校园助手")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # fetch - 生成搜索建议
    fetch_parser = subparsers.add_parser("fetch", help="生成平台搜索建议")
    fetch_parser.add_argument("--platform", default="all", help="平台: all/tieba/xiaohongshu/douyin/weibo")
    fetch_parser.add_argument("--limit", type=int, default=10, help="每平台结果数")

    # activity - 活动搜索建议
    subparsers.add_parser("activity", help="获取校园活动搜索关键词建议")

    # platforms - 列出支持的平台
    subparsers.add_parser("platforms", help="列出支持的平台")

    args = parser.parse_args()

    if args.command == "fetch":
        if args.platform == "all":
            result = generate_all_queries(args.limit)
        else:
            result = generate_search_queries(args.platform, args.limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "activity":
        result = get_activity_recommendations()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "platforms":
        platforms = []
        for key, info in PLATFORM_URLS.items():
            platforms.append({
                "id": key,
                "name": info["name"],
                "description": info["description"],
                "url_template": info["search_url"],
            })
        print(json.dumps({"platforms": platforms}, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
