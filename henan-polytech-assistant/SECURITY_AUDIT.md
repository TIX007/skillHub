# 安全审计报告

## 执行摘要
- **审计对象**: henan-polytech-assistant（河南理工大学校园智能助手）
- **审计路径**: C:\Users\TIX\.workbuddy\skills\henan-polytech-assistant
- **审计文件数**: 9个（1个SKILL.md + 4个Python脚本 + 3个配置文件 + 1个参考文档）
- **发现问题总数**: 0个
  - Malicious（恶意）: 0个
  - Suspicious（可疑）: 0个
  - 信息性提醒: 1个（非风险项）
- **安全评分**: 85分

---

## Malicious（恶意）风险发现

✅ 未发现 Malicious 风险

---

## Suspicious（可疑）风险发现

✅ 未发现 Suspicious 风险

---

## 信息性提醒（非风险项）

1. **依赖安装建议未固定版本**（信息性提醒）
   - **位置**: SKILL.md:294, SKILL.md:299, amap_helper.py:19, train_query.py:19
   - **代码片段**: `pip install requests`
   - **说明**: SKILL.md 和脚本错误提示中建议用户安装 `requests` 库，未固定版本号。但这些均为**用户手动执行的安装建议**，非 skill 自动执行，不构成供应链投毒风险。
   - **建议**: 可考虑固定版本为 `pip install requests>=2.28.0` 以提升安全性。

---

## 详细检查结果

### 命令执行与权限检查
- 发现次数: 0次
- 未检测到 `subprocess`、`os.system`、`eval`、`exec`、`popen`、`Runtime.exec`、`ProcessBuilder` 等危险命令执行调用。
- SKILL.md 中的 `bash` 关键词均为代码块标记（```bash），非实际执行的命令。

### 文件操作与敏感路径检查
- 发现次数: 0次（安全）
- 所有文件读写操作均限于 skill 自身目录内：
  - `config/config.json`（配置文件读写）
  - `config/schedule.json`（课程表数据读写）
  - `config/station_codes.json`（车站码缓存，自动生成）
- 未检测到对 `~/.ssh`、`.env`、`credentials`、`/etc/passwd` 等敏感路径的访问。
- 未检测到 `rm -rf`、`unlink`、`shutil.rmtree` 等文件删除操作。

### 网络请求检查
- 发现的URL（均为官方合法API）：
  - `restapi.amap.com`（高德地图官方API - 周边搜索、路线规划、地理编码）
  - `kyfw.12306.cn`（12306官方接口 - 车站查询、余票查询）
  - `tieba.baidu.com`（百度贴吧 - 搜索建议URL）
  - `www.xiaohongshu.com`（小红书 - 搜索建议URL）
  - `www.douyin.com`（抖音 - 搜索建议URL）
  - `s.weibo.com`（微博 - 搜索建议URL）
  - `lbs.amap.com`（高德开放平台注册页 - 文档引导）
- Base64编码检测: 未发现可疑编码字符串。
- 未检测到数据外送行为。API Key 仅用于调用对应官方API，未发送到第三方。

### 远程脚本深度分析
- 不适用。未发现自动下载并执行远程脚本的行为。

### 依赖安装风险检查
- **全局安装检测**: 未发现 skill 自动执行的全局安装命令。`pip install requests` 仅出现在用户手动安装建议中。
- **虚拟环境检查**: SKILL.md 中提供了使用 WorkBuddy 管理 venv 安装的替代方案。
- **依赖来源检查**: 未从非官方源安装依赖。

---

## 总体建议

该 Skill 设计合理，安全实践良好：
1. API Key 存储在本地配置文件中，未硬编码
2. 所有网络请求均指向官方API端点
3. 文件操作严格限制在 skill 自身目录内
4. 无自动执行的危险操作
5. 建议在安装提示中固定 `requests` 版本号以增强供应链安全

---

## 审计结论

**风险等级**: ✅ **Benign（可信）- 可以安全使用**（85分）

无投毒风险，无自动执行的危险操作，所有外部调用均为合法官方API。Skill 可安全安装和使用。
