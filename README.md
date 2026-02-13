# 24点游戏 - 内网穿透版

![24点游戏截图](screenshot.png)

一个支持手机触摸操作的24点游戏，通过 Cloudflare Tunnel 实现内网穿透，让你可以从任何地方访问本地部署的游戏。

## 🎮 游戏特色

- **手机友好**：大按钮设计，无需键盘输入
- **拖拽式操作**：点击数字和运算符按钮构建表达式
- **实时验证**：自动检查答案是否正确
- **内网穿透**：通过 Cloudflare Tunnel 从公网访问
- **自动监控**：服务中断时自动恢复

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/your-username/24-game-github.git
cd 24-game-github
```

### 2. 安装依赖
```bash
# 安装 Cloudflare CLI
brew install cloudflared
# 或者从 https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation 下载
```

### 3. 启动游戏服务
```bash
# 启动游戏服务器和 Cloudflare Tunnel
./scripts/start_game_service.sh
```

### 4. 访问游戏
启动脚本会输出类似这样的链接：
```
https://your-random-subdomain.trycloudflare.com
```
在手机或电脑浏览器中打开即可开始游戏！

## 📱 游戏玩法

1. 点击 **"🎲 新游戏"** 获取四个随机数字
2. 使用按钮构建表达式：
   - 点击数字按钮（显示当前的四个数字）
   - 点击运算符按钮（+、-、×、÷）
   - 点击括号按钮（(、)）调整运算优先级
3. 点击 **"✅ 验证"** 检查答案
4. 如果正确，会显示绿色成功信息！

## 🔧 监控系统

项目包含自动监控脚本，可以：

- 每5分钟检查服务状态
- 自动重启失败的服务
- 发送通知消息（需要配置 OpenClaw）

### 手动运行监控
```bash
python3 scripts/game_monitor.py
```

### 配置自动监控
编辑 `scripts/game_monitor.py` 中的通知配置部分。

## 📁 项目结构

```
24-game-github/
├── README.md                 # 项目说明文档
├── game/                     # 游戏核心文件
│   └── index.html            # 24点游戏主页面
├── scripts/                  # 部署和监控脚本
│   ├── start_game_service.sh # 启动脚本
│   └── game_monitor.py       # 监控脚本
└── logs/                     # 日志目录（运行时生成）
```

## ⚙️ 技术原理

### Cloudflare Tunnel 内网穿透

传统的内网穿透需要：
- 公网IP地址
- 路由器端口转发
- 手动配置SSL证书

Cloudflare Tunnel 的创新方案：
- **反向连接**：本地客户端主动连接 Cloudflare 边缘网络
- **无需公网IP**：只建立出站连接，内网服务不直接暴露
- **自动HTTPS**：Cloudflare 自动提供SSL证书
- **全球加速**：利用 Cloudflare 的全球边缘网络

工作流程：
```
用户浏览器 → Cloudflare边缘节点 → 本地隧道连接 → 本地Web服务
```

## 🛡️ 安全性

- 内网服务不直接暴露在公网
- 所有流量通过加密隧道传输
- Cloudflare 提供DDoS防护和安全过滤
- 临时域名每次重启都会变化（增加安全性）

## 📝 注意事项

- Cloudflare Tunnel 临时服务没有 uptime 保证
- 如需生产环境使用，建议注册 Cloudflare 账户并设置命名隧道
- 监控脚本需要 OpenClaw 环境才能发送通知
- 游戏仅支持基本的四则运算和括号

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [Cloudflare](https://www.cloudflare.com/) - 提供免费的内网穿透服务
- [OpenClaw](https://openclaw.ai/) - 提供智能助手和自动化能力