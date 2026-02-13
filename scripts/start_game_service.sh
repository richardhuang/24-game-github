#!/bin/bash

# 24点游戏服务启动脚本
WORKSPACE="/Users/rhuang/.openclaw/workspace"
GAME_DIR="$WORKSPACE/my game"
LOG_DIR="$WORKSPACE/logs"
MONITOR_LOG="$LOG_DIR/monitor.log"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 启动Python HTTP服务器（在后台）
cd "$GAME_DIR"
python3 -m http.server 8080 > "$LOG_DIR/http_server.log" 2>&1 &
HTTP_PID=$!

echo "$(date): Started HTTP server with PID $HTTP_PID" >> "$MONITOR_LOG"

# 启动Cloudflare Tunnel（在后台）
cloudflared tunnel --url http://localhost:8080 > "$LOG_DIR/cloudflared.log" 2>&1 &
TUNNEL_PID=$!

echo "$(date): Started Cloudflare Tunnel with PID $TUNNEL_PID" >> "$MONITOR_LOG"

# 保存进程ID到文件
echo "$HTTP_PID" > "$LOG_DIR/http_server.pid"
echo "$TUNNEL_PID" > "$LOG_DIR/cloudflared.pid"

# 等待一段时间让Cloudflare Tunnel初始化
sleep 10

# 提取并保存当前的URL
CURRENT_URL=$(grep -o 'https://[a-zA-Z0-9\-]*\.trycloudflare\.com' "$LOG_DIR/cloudflared.log" | tail -1)
if [ -n "$CURRENT_URL" ]; then
    echo "$CURRENT_URL" > "$LOG_DIR/current_url.txt"
    echo "$(date): Current URL: $CURRENT_URL" >> "$MONITOR_LOG"
fi

echo "Game service started!"
echo "HTTP Server PID: $HTTP_PID"
echo "Cloudflare Tunnel PID: $TUNNEL_PID"
echo "Current URL: $CURRENT_URL"