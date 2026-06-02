#!/usr/bin/env python3
"""
A股智能持仓监控助手 — 精准推送控制器

功能：
  1. 交易日历判断（排除周末/节假日，处理调休补班）
  2. 交易时段门控（盘前/盘中/午休/盘后精确判断）
  3. 防重复推送（时间窗口 + 内容去重 + 状态持久化）
  4. 漏推检测与补偿
  5. 推送状态追踪与报告

用法：
  python push_controller.py timegate                    # 检查当前时段
  python push_controller.py check --stock sh600519 ...  # 推送前检查
  python push_controller.py record --stock sh600519 ... # 推送后记录
  python push_controller.py status --stock sh600519     # 查看状态
  python push_controller.py report                      # 今日报告
  python push_controller.py detect-missed               # 漏推检测
"""

import argparse
import json
import os
import sys
from datetime import datetime, date, time, timedelta
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path


# ============================================================
# 配置
# ============================================================

class Session(Enum):
    """A股交易时段枚举"""
    PRE_MARKET = "PRE_MARKET"           # 盘前竞价 09:00-09:25
    TRADING_MORNING = "TRADING_MORNING" # 上午交易 09:30-11:30
    LUNCH_BREAK = "LUNCH_BREAK"        # 午间休市 11:30-13:00
    TRADING_AFTERNOON = "TRADING_AFTERNOON"  # 下午交易 13:00-15:00
    AFTER_HOURS = "AFTER_HOURS"        # 盘后 15:00-次日09:00
    WEEKEND = "WEEKEND"                # 周末
    HOLIDAY = "HOLIDAY"                # 法定节假日


# A股交易日时间常量
TRADING_TIMES = {
    Session.PRE_MARKET:       (time(9, 0),  time(9, 25)),
    Session.TRADING_MORNING:  (time(9, 30), time(11, 30)),
    Session.LUNCH_BREAK:      (time(11, 30), time(13, 0)),
    Session.TRADING_AFTERNOON:(time(13, 0), time(15, 0)),
}

# 2026年法定节假日（需每年更新一次）
HOLIDAYS_2026: set = {
    date(2026, 1, 1),    # 元旦
    # 春节：2026年农历正月初一为2月17日，假期2月16-22日
    date(2026, 2, 16), date(2026, 2, 17), date(2026, 2, 18),
    date(2026, 2, 19), date(2026, 2, 20), date(2026, 2, 22),
    date(2026, 4, 5),    # 清明节
    date(2026, 5, 1), date(2026, 5, 2), date(2026, 5, 3),  # 劳动节
    date(2026, 6, 19),   # 端午节
    date(2026, 9, 25),   # 中秋节
    # 国庆节
    date(2026, 10, 1), date(2026, 10, 2), date(2026, 10, 3),
    date(2026, 10, 4), date(2026, 10, 5), date(2026, 10, 6), date(2026, 10, 7),
}

# 调休补班日（周末但开市）
MAKEUP_DAYS_2026: set = {
    # date(2026, 1, 10),  # 示例：如有调休补班，在此添加
}

# 推送冷却时间配置（分钟）
COOLDOWN_CONFIG = {
    "default": 30,
    "price": 15,
    "volume": 30,
    "news": 120,
    "technical": 60,
    "fund": 45,
    "announcement": 120,
}

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PUSH_STATE_FILE = PROJECT_ROOT / ".workbuddy" / "push_state.json"


# ============================================================
# 交易日历
# ============================================================

class TradingCalendar:
    """A股交易日历"""

    def __init__(self, holidays: set = None, makeup_days: set = None):
        self.holidays = holidays or HOLIDAYS_2026
        self.makeup_days = makeup_days or MAKEUP_DAYS_2026

    def is_weekend(self, d: date) -> bool:
        """判断是否为周六日"""
        return d.weekday() >= 5  # 5=周六, 6=周日

    def is_holiday(self, d: date) -> bool:
        """判断是否为法定节假日"""
        return d in self.holidays

    def is_makeup_day(self, d: date) -> bool:
        """判断是否为调休补班日"""
        return d in self.makeup_days

    def is_trading_day(self, d: date) -> bool:
        """
        判断是否为 A 股交易日
        规则：非节假日 + (非周末 或 调休补班)
        """
        if self.is_holiday(d):
            return False
        if self.is_weekend(d):
            return self.is_makeup_day(d)
        return True

    def get_next_trading_day(self, from_date: date) -> date:
        """获取下一个交易日"""
        d = from_date + timedelta(days=1)
        while not self.is_trading_day(d):
            d += timedelta(days=1)
        return d


# ============================================================
# 时段门控
# ============================================================

class TimeGate:
    """交易时段判断门控"""

    def __init__(self, calendar: TradingCalendar = None):
        self.calendar = calendar or TradingCalendar()

    def get_current_session(self, dt: datetime = None) -> Tuple[Session, dict]:
        """
        判断当前所处的交易时段
        返回: (Session, info_dict)
        """
        if dt is None:
            dt = datetime.now()

        d = dt.date()
        t = dt.time()

        # 1. 先判断是否为交易日
        if not self.calendar.is_trading_day(d):
            if self.calendar.is_weekend(d):
                return Session.WEEKEND, {
                    "is_trading_day": False,
                    "reason": "周末休市",
                    "next_trading_day": str(self.calendar.get_next_trading_day(d)),
                }
            return Session.HOLIDAY, {
                "is_trading_day": False,
                "reason": "法定节假日",
                "next_trading_day": str(self.calendar.get_next_trading_day(d)),
            }

        # 2. 判断具体时段
        for session, (start, end) in TRADING_TIMES.items():
            if start <= t <= end:
                return session, {
                    "is_trading_day": True,
                    "session": session.value,
                    "start": str(start),
                    "end": str(end),
                }

        # 3. 不在任何特定时段 → 盘后
        if t < time(9, 0):
            return Session.AFTER_HOURS, {
                "is_trading_day": True,
                "session": "AFTER_HOURS",
                "reason": "盘前等待（距离开盘还有 {:.0f} 分钟）".format(
                    (datetime.combine(d, time(9, 0)) - dt).total_seconds() / 60
                ),
            }
        else:
            return Session.AFTER_HOURS, {
                "is_trading_day": True,
                "session": "AFTER_HOURS",
                "reason": "已收盘",
            }

    def is_push_allowed(self, dt: datetime = None) -> Tuple[bool, str]:
        """
        检查当前是否允许推送异动报告
        返回: (allowed, reason)
        """
        if dt is None:
            dt = datetime.now()

        session, info = self.get_current_session(dt)

        ALLOWED_SESSIONS = {
            Session.TRADING_MORNING,
            Session.TRADING_AFTERNOON,
        }

        if session in ALLOWED_SESSIONS:
            return True, f"盘中交易时段，允许推送 ({session.value})"

        messages = {
            Session.PRE_MARKET: "盘前竞价时段，仅允许推送盘前摘要，不推送异动预警",
            Session.LUNCH_BREAK: "午间休市，静默不推送",
            Session.AFTER_HOURS: "盘后时段，静默不推送",
            Session.WEEKEND: "周末休市，静默不推送",
            Session.HOLIDAY: "法定节假日，静默不推送",
        }

        return False, messages.get(session, "未知时段，不允许推送")

    def get_remaining_trade_time(self, dt: datetime = None) -> int:
        """获取当日剩余交易时间（分钟）"""
        if dt is None:
            dt = datetime.now()

        session, _ = self.get_current_session(dt)

        if session == Session.TRADING_MORNING:
            end = datetime.combine(dt.date(), time(11, 30))
            return max(0, (end - dt).total_seconds() // 60)
        elif session == Session.TRADING_AFTERNOON:
            end = datetime.combine(dt.date(), time(15, 0))
            return max(0, (end - dt).total_seconds() // 60)
        return 0


# ============================================================
# 去重引擎
# ============================================================

class Deduplication:
    """推送去重引擎"""

    def __init__(self, state_file: Path = PUSH_STATE_FILE):
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> dict:
        """加载推送状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {
            "last_push_time": {},
            "push_history": [],
            "cooldown_config": COOLDOWN_CONFIG.copy(),
        }

    def _save_state(self) -> None:
        """持久化推送状态"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def get_key(self, stock_code: str, alert_type: str) -> str:
        """生成去重键"""
        return f"{stock_code}_{alert_type.upper()}_ALERT"

    def has_pushed_recently(self, stock_code: str, alert_type: str) -> Tuple[bool, str]:
        """
        检查是否在冷却期内已推送过
        返回: (has_pushed, reason)
        """
        key = self.get_key(stock_code, alert_type)
        last_push = self.state["last_push_time"].get(key)

        if last_push is None:
            return False, "首次推送"

        try:
            last_dt = datetime.fromisoformat(last_push)
            cooldown_minutes = self.state["cooldown_config"].get(
                alert_type,
                self.state["cooldown_config"]["default"]
            )
            elapsed = (datetime.now() - last_dt).total_seconds() / 60

            if elapsed < cooldown_minutes:
                remaining = cooldown_minutes - elapsed
                return True, f"冷却中（{remaining:.0f} 分钟后可再次推送）"

            return False, f"冷却期已过（{elapsed:.0f} 分钟前推送）"
        except (ValueError, TypeError):
            return False, "时间解析异常，允许推送"

    def record_push(self, stock_code: str, alert_type: str,
                    content: str = "", threshold: float = 0.0) -> dict:
        """
        记录一次推送
        返回: 推送记录
        """
        key = self.get_key(stock_code, alert_type)
        now = datetime.now()
        now_iso = now.isoformat()

        record = {
            "key": key,
            "stock_code": stock_code,
            "alert_type": alert_type,
            "timestamp": now_iso,
            "content": content[:200],  # 截断存储
            "threshold": threshold,
        }

        # 更新最后推送时间
        self.state["last_push_time"][key] = now_iso

        # 维护推送历史（保留最近 100 条）
        self.state["push_history"].insert(0, record)
        if len(self.state["push_history"]) > 100:
            self.state["push_history"] = self.state["push_history"][:100]

        self._save_state()
        return record

    def get_push_history(self, stock_code: str = None, limit: int = 20) -> list:
        """获取推送历史"""
        history = self.state["push_history"]
        if stock_code:
            history = [h for h in history if h["stock_code"] == stock_code]
        return history[:limit]


# ============================================================
# 状态追踪与漏推检测
# ============================================================

class StateTracker:
    """推送状态追踪与漏推检测"""

    def __init__(self, calendar: TradingCalendar = None,
                 dedup: Deduplication = None):
        self.calendar = calendar or TradingCalendar()
        self.dedup = dedup or Deduplication()

    def detect_missed_push(self, monitor_list: List[dict]) -> List[dict]:
        """
        检测漏推
        monitor_list: [{"code": "sh600519", "name": "贵州茅台",
                        "alert_types": ["price", "volume"]}, ...]

        返回: 漏推列表
        """
        now = datetime.now()
        gate = TimeGate(self.calendar)

        # 非交易时段不检测漏推
        allowed, reason = gate.is_push_allowed(now)
        if not allowed:
            return []

        missed = []

        for stock in monitor_list:
            stock_code = stock["code"]
            stock_name = stock.get("name", stock_code)
            alert_types = stock.get("alert_types", ["price", "volume", "fund", "news"])

            for atype in alert_types:
                has_pushed, detail = self.dedup.has_pushed_recently(stock_code, atype)

                if not has_pushed:
                    # 检查本交易日是否已推送过
                    today_records = [
                        r for r in self.dedup.get_push_history(stock_code)
                        if r.get("key", "").startswith(f"{stock_code}_{atype.upper()}")
                        and r.get("timestamp", "")[:10] == now.strftime("%Y-%m-%d")
                    ]

                    if not today_records:
                        missed.append({
                            "stock_code": stock_code,
                            "stock_name": stock_name,
                            "alert_type": atype,
                            "reason": "本交易日尚未推送",
                            "last_push": self.dedup.state["last_push_time"].get(
                                self.dedup.get_key(stock_code, atype), "从未推送"
                            ),
                        })

        return missed

    def generate_report(self) -> dict:
        """生成今日推送报告"""
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")

        today_records = [
            r for r in self.dedup.get_push_history(limit=100)
            if r.get("timestamp", "")[:10] == today_str
        ]

        gate = TimeGate(self.calendar)
        session, info = gate.get_current_session(now)
        allowed, reason = gate.is_push_allowed(now)

        return {
            "date": today_str,
            "time": now.strftime("%H:%M:%S"),
            "session": session.value,
            "push_allowed": allowed,
            "reason": reason,
            "today_push_count": len(today_records),
            "today_pushes": today_records,
            "unique_stocks": len(set(r["stock_code"] for r in today_records)),
        }


# ============================================================
# CLI 入口
# ============================================================

def cmd_timegate():
    """检查当前时段"""
    gate = TimeGate()
    now = datetime.now()
    session, info = gate.get_current_session(now)
    allowed, reason = gate.is_push_allowed(now)

    result = {
        "datetime": now.isoformat(),
        "weekday": now.strftime("%A"),
        "session": session.value,
        "is_trading_day": info.get("is_trading_day", False),
        "push_allowed": allowed,
        "reason": reason,
        "remaining_trade_minutes": gate.get_remaining_trade_time(now),
        **{k: v for k, v in info.items() if k not in ("is_trading_day", "session", "start", "end")},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_check(args):
    """推送前检查"""
    gate = TimeGate()
    dedup = Deduplication()

    # 1. 时段检查
    allowed, reason = gate.is_push_allowed()
    if not allowed:
        result = {"allow_push": False, "reason": reason, "cooldown_ok": False}
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)

    # 2. 去重检查
    has_pushed, cooldown_reason = dedup.has_pushed_recently(
        args.stock, args.alert_type
    )

    if has_pushed:
        result = {
            "allow_push": False,
            "reason": f"时段允许，但 {cooldown_reason}",
            "cooldown_ok": False,
            "session": "TRADING",
        }
    else:
        result = {
            "allow_push": True,
            "reason": "盘中交易时段，冷却期已过",
            "cooldown_ok": True,
            "session": "TRADING",
            "remaining_minutes": gate.get_remaining_trade_time(),
        }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["allow_push"] else 1)


def cmd_record(args):
    """推送后记录"""
    dedup = Deduplication()
    record = dedup.record_push(
        stock_code=args.stock,
        alert_type=args.alert_type,
        content=args.content or "",
        threshold=args.threshold or 0.0,
    )
    print(json.dumps(record, ensure_ascii=False, indent=2))


def cmd_status(args):
    """查看推送状态"""
    dedup = Deduplication()
    history = dedup.get_push_history(stock_code=args.stock)

    result = {
        "stock_code": args.stock,
        "last_pushes": history,
        "total_pushes": len(dedup.state["push_history"]),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_report():
    """生成今日推送报告"""
    tracker = StateTracker()
    report = tracker.generate_report()
    print(json.dumps(report, ensure_ascii=False, indent=2))


def cmd_detect_missed(args):
    """漏推检测"""
    tracker = StateTracker()

    # 从参数或默认监控列表获取
    if args.monitor_file:
        with open(args.monitor_file, 'r', encoding='utf-8') as f:
            monitor_list = json.load(f)
    else:
        # 默认空列表（实际使用时从 SKILL.md 的监控池读取）
        monitor_list = []

    missed = tracker.detect_missed_push(monitor_list)

    result = {
        "datetime": datetime.now().isoformat(),
        "monitor_count": len(monitor_list),
        "missed_count": len(missed),
        "missed_pushes": missed,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(1 if missed else 0)


def main():
    parser = argparse.ArgumentParser(
        description="A股智能持仓监控 — 精准推送控制器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python push_controller.py timegate
  python push_controller.py check --stock sh600519 --alert-type price
  python push_controller.py record --stock sh600519 --alert-type price
  python push_controller.py status --stock sh600519
  python push_controller.py report
  python push_controller.py detect-missed
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # timegate
    subparsers.add_parser("timegate", help="检查当前时段是否允许推送")

    # check
    check_parser = subparsers.add_parser("check", help="推送前检查（时段+去重）")
    check_parser.add_argument("--stock", required=True, help="股票代码（如 sh600519）")
    check_parser.add_argument("--alert-type", required=True,
                              choices=["price", "volume", "fund", "news",
                                       "technical", "announcement"],
                              help="异动类型")
    check_parser.add_argument("--threshold", type=float, default=3.0,
                              help="异动阈值")

    # record
    record_parser = subparsers.add_parser("record", help="记录一次推送")
    record_parser.add_argument("--stock", required=True, help="股票代码")
    record_parser.add_argument("--alert-type", required=True,
                               choices=["price", "volume", "fund", "news",
                                        "technical", "announcement"],
                               help="异动类型")
    record_parser.add_argument("--content", default="", help="推送内容摘要")
    record_parser.add_argument("--threshold", type=float, default=0.0,
                               help="触发阈值")

    # status
    status_parser = subparsers.add_parser("status", help="查看推送状态")
    status_parser.add_argument("--stock", required=True, help="股票代码")

    # report
    subparsers.add_parser("report", help="生成今日推送报告")

    # detect-missed
    missed_parser = subparsers.add_parser("detect-missed", help="漏推检测")
    missed_parser.add_argument("--monitor-file", default="",
                               help="监控列表 JSON 文件路径")

    args = parser.parse_args()

    if args.command == "timegate":
        cmd_timegate()
    elif args.command == "check":
        cmd_check(args)
    elif args.command == "record":
        cmd_record(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "report":
        cmd_report()
    elif args.command == "detect-missed":
        cmd_detect_missed(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
