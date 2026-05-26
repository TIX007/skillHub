#!/usr/bin/env python3
"""
导出工具：将结构化病历导出为 PDF / JSON / 企业微信推送
演示版本
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def export_json(record_md: str, output_path: str = None):
    """将病历 Markdown 转为结构化 JSON"""
    if output_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"record_{ts}.json"

    # 简单解析 Markdown 字段
    sections = {}
    current_section = None
    for line in record_md.split('\n'):
        if line.startswith('## '):
            current_section = line[3:].strip()
            sections[current_section] = []
        elif current_section and line.strip() and not line.startswith('#'):
            sections[current_section].append(line.strip())

    data = {
        "export_time": datetime.now().isoformat(),
        "format": "structured_json",
        "sections": {k: '\n'.join(v) for k, v in sections.items()},
        "meta": {
            "generator": "voice-to-medical-record-v1.0",
            "requires_doctor_review": True,
            "data_processed_locally": True
        }
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON 导出成功：{output_path}")
    return str(output_path)


def send_to_wecom(record_json_path: str, webhook_url: str = None):
    """推送到企业微信（HIS 系统集成）"""
    if webhook_url is None:
        webhook_url = os.environ.get('WECOM_WEBHOOK_URL')
        if not webhook_url:
            print("⚠️  未配置企业微信 Webhook，跳过推送")
            print("   设置方法：export WECOM_WEBHOOK_URL='https://qyapi.weixin.qq.com/...'")
            return False

    with open(record_json_path, encoding='utf-8') as f:
        data = json.load(f)

    # 企业微信消息格式
    message = {
        "msgtype": "markdown",
        "markdown": {
            "content": (
                "## 🏥 病历生成通知\n\n"
                "> **AI 辅助病历已生成，等待医生审核**\n\n"
                f"**生成时间：** {data['export_time']}\n\n"
                "**需要审核的字段：**\n"
                "- [ ] 主诉\n- [ ] 现病史\n- [ ] 诊断\n- [ ] 治疗方案\n\n"
                "⚠️ 请在 HIS 系统中打开病历进行审核确认"
            )
        }
    }

    try:
        import urllib.request
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(message).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            if result.get('errcode') == 0:
                print("✅ 企业微信推送成功")
                return True
            else:
                print(f"❌ 企业微信推送失败：{result}")
                return False
    except Exception as e:
        print(f"❌ 推送异常：{e}")
        return False


if __name__ == "__main__":
    # 演示：导出最新生成的病历
    md_files = list(OUTPUT_DIR.glob("medical_record_*.md"))
    if md_files:
        latest = max(md_files, key=lambda p: p.stat().st_mtime)
        with open(latest, encoding='utf-8') as f:
            record_md = f.read()
        json_path = export_json(record_md)
        send_to_wecom(json_path)
    else:
        print("未找到病历文件，请先运行 pipeline.py 生成病历")
