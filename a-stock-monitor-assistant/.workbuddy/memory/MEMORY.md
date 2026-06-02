# a-stock-monitor Skill 长期记忆索引

## 版本历史

- **v1.1.0** (2026-06-02): 新增自进化记忆系统（记忆块+睡眠反思）+ Python 精准推送控制器
- **v1.0.0** (2026-05-27): 初始版本，含五大核心模块 + 时段门控

## 自进化记忆系统

### 记忆块存储
- 会话日志：`.workbuddy/memory/YYYY-MM-DD.md`
- 记忆索引库：`.workbuddy/memory/MEMORY.md`（本文件）
- 推送状态：`.workbuddy/push_state.json`（自动创建）

### 睡眠反思
- 每日反思：交易日 15:00-15:30 自动触发
- 每周反思：每周五收盘后自动触发

### 自进化参数
- 异动阈值自动调整规则：连续3次虚假→收紧10%，连续3次漏报→放宽10%
- 分析权重：用户连续质疑某维度→自动降低权重

## Python 推送控制器

- 脚本：`scripts/push_controller.py`
- Python 版本：3.13.12（managed）
- 核心命令：timegate / check / record / status / report / detect-missed
- 状态文件：`.workbuddy/push_state.json`

## 2026年法定节假日（持仓监控用）
- 元旦：1月1日
- 春节：2月16-22日
- 清明：4月5日
- 劳动节：5月1-3日
- 端午：6月19日
- 中秋：9月25日
- 国庆：10月1-7日
