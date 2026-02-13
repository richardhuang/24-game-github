#!/usr/bin/env python3
"""
24点游戏服务监控器
- 监控本地 Python HTTP 服务器 (8080端口)
- 监控 Cloudflare Tunnel 进程
- 自动重启服务如果失败
- 发送通知消息
"""

import os
import sys
import time
import subprocess
import requests
import json
from datetime import datetime

# 配置
GAME_DIR = "/Users/rhuang/.openclaw/workspace/my game"
HTTP_PORT = 8080
CHECK_INTERVAL = 30  # 检查间隔（秒）
MAX_RESTART_ATTEMPTS = 3

# 进程信息
http_server_pid = None
cf_tunnel_pid = None
restart_attempts = 0

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    # 也可以写入日志文件
    with open("/Users/rhuang/.openclaw/workspace/game_monitor.log", "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def is_process_running(pid):
    """检查进程是否在运行"""
    if pid is None:
        return False
    try:
        os.kill(pid, 0)  # 不会真的杀死进程，只是检查是否存在
        return True
    except OSError:
        return False

def check_local_service():
    """检查本地 HTTP 服务是否正常"""
    try:
        response = requests.get(f"http://localhost:{HTTP_PORT}", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def start_http_server():
    """启动 Python HTTP 服务器"""
    global http_server_pid
    try:
        # 先确保没有重复的进程
        stop_http_server()
        
        # 启动新的 HTTP 服务器
        process = subprocess.Popen([
            sys.executable, "-m", "http.server", str(HTTP_PORT)
        ], cwd=GAME_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        http_server_pid = process.pid
        log(f"HTTP 服务器已启动，PID: {http_server_pid}")
        return True
    except Exception as e:
        log(f"启动 HTTP 服务器失败: {e}")
        return False

def stop_http_server():
    """停止 HTTP 服务器"""
    global http_server_pid
    if http_server_pid and is_process_running(http_server_pid):
        try:
            os.kill(http_server_pid, 9)  # 强制终止
            log(f"HTTP 服务器已停止，PID: {http_server_pid}")
        except OSError:
            pass
    http_server_pid = None

def start_cf_tunnel():
    """启动 Cloudflare Tunnel"""
    global cf_tunnel_pid
    try:
        # 先确保没有重复的进程
        stop_cf_tunnel()
        
        # 启动 Cloudflare Tunnel
        process = subprocess.Popen([
            "cloudflared", "tunnel", "--url", f"http://localhost:{HTTP_PORT}"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd="/tmp")
        
        cf_tunnel_pid = process.pid
        log(f"Cloudflare Tunnel 已启动，PID: {cf_tunnel_pid}")
        
        # 等待几秒获取 URL
        time.sleep(5)
        return True
    except Exception as e:
        log(f"启动 Cloudflare Tunnel 失败: {e}")
        return False

def stop_cf_tunnel():
    """停止 Cloudflare Tunnel"""
    global cf_tunnel_pid
    if cf_tunnel_pid and is_process_running(cf_tunnel_pid):
        try:
            os.kill(cf_tunnel_pid, 9)  # 强制终止
            log(f"Cloudflare Tunnel 已停止，PID: {cf_tunnel_pid}")
        except OSError:
            pass
    cf_tunnel_pid = None

def send_notification(message):
    """发送通知消息（通过 OpenClaw）"""
    try:
        # 使用 OpenClaw 的 message 工具发送 Slack 消息
        subprocess.run([
            "openclaw", "message", "send",
            "--channel", "slack",
            "--message", message
        ], capture_output=True, timeout=10)
        log("通知消息已发送")
    except Exception as e:
        log(f"发送通知失败: {e}")

def get_current_tunnel_url():
    """获取当前的隧道 URL（从进程输出中提取）"""
    # 这里简化处理，实际可以从 cloudflared 的输出中解析
    return "新的 Cloudflare Tunnel 链接"

def main():
    """主监控循环"""
    global restart_attempts
    
    log("24点游戏服务监控器启动")
    
    # 初始启动服务
    if not start_http_server():
        log("初始启动 HTTP 服务器失败")
        send_notification("❌ 24点游戏监控器启动失败：HTTP 服务器无法启动")
        return
    
    if not start_cf_tunnel():
        log("初始启动 Cloudflare Tunnel 失败")
        send_notification("❌ 24点游戏监控器启动失败：Cloudflare Tunnel 无法启动")
        return
    
    send_notification("✅ 24点游戏服务已启动！\n" + 
                     "🔗 访问链接: https://communicate-meets-nominations-specialty.trycloudflare.com")
    
    restart_attempts = 0
    
    while True:
        try:
            # 检查本地服务
            local_ok = check_local_service()
            http_running = is_process_running(http_server_pid)
            cf_running = is_process_running(cf_tunnel_pid)
            
            log(f"状态检查 - 本地服务: {'✅' if local_ok else '❌'}, " +
                f"HTTP进程: {'✅' if http_running else '❌'}, " +
                f"CF进程: {'✅' if cf_running else '❌'}")
            
            # 如果服务不正常，尝试恢复
            if not local_ok or not http_running or not cf_running:
                log("检测到服务异常，开始恢复...")
                
                if restart_attempts >= MAX_RESTART_ATTEMPTS:
                    error_msg = f"⚠️ 24点游戏服务多次重启失败！\n最后一次尝试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    send_notification(error_msg)
                    log("达到最大重启次数，停止自动恢复")
                    break
                
                # 停止所有服务
                stop_http_server()
                stop_cf_tunnel()
                
                # 重新启动
                time.sleep(2)
                http_success = start_http_server()
                time.sleep(2)
                cf_success = start_cf_tunnel()
                
                if http_success and cf_success:
                    restart_attempts = 0
                    success_msg = "✅ 24点游戏服务已自动恢复！\n" + \
                                 "🔗 请使用新的访问链接（可能已变更）"
                    send_notification(success_msg)
                    log("服务恢复成功")
                else:
                    restart_attempts += 1
                    fail_msg = f"🔄 24点游戏服务恢复尝试 {restart_attempts}/{MAX_RESTART_ATTEMPTS}..."
                    send_notification(fail_msg)
                    log(f"服务恢复失败，重试次数: {restart_attempts}")
            
            else:
                restart_attempts = 0  # 重置重试计数
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log("监控器被手动停止")
            break
        except Exception as e:
            log(f"监控器发生错误: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()