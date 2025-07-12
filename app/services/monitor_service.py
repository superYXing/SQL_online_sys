from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from datetime import datetime
from typing import Dict, Set
from utils.logging_config import log_online_status

class MonitorService:
    """访问监控服务类"""

    def __init__(self):
        self.total_visits = 0  # 累计访问人数
        self.current_online_users: Set[str] = set()  # 当前在线用户IP集合
        self.user_sessions: Dict[str, float] = {}  # 用户会话记录 {IP: 最后访问时间}
        self.SESSION_TIMEOUT = 300  # 会话超时时间（秒），5分钟
        self.access_logger = logging.getLogger('access')
        self.app_logger = logging.getLogger('app')
    
    def clean_expired_sessions(self, current_time: float):
        """清理过期的会话"""
        expired_ips = [ip for ip, last_time in self.user_sessions.items()
                      if current_time - last_time > self.SESSION_TIMEOUT]
        for ip in expired_ips:
            self.user_sessions.pop(ip, None)
            self.current_online_users.discard(ip)

        if expired_ips:
            self.app_logger.info(f"清理过期会话: {len(expired_ips)} 个用户离线")
    
    def record_visit(self, client_ip: str, user_agent: str, request_method: str, request_url: str):
        """记录访问信息"""
        current_time = time.time()

        # 清理过期的会话
        self.clean_expired_sessions(current_time)

        # 检查是否是新访问者
        is_new_visitor = client_ip not in self.user_sessions

        if is_new_visitor:
            self.total_visits += 1

        # 更新用户会话信息
        self.user_sessions[client_ip] = current_time
        self.current_online_users.add(client_ip)

        # 记录详细访问信息到日志文件
        self.log_access_to_file(client_ip, user_agent, request_method, request_url, is_new_visitor)

        # 更新控制台在线状态显示
        log_online_status(len(self.current_online_users), self.total_visits)
    
    def log_access_to_file(self, client_ip: str, user_agent: str, request_method: str, request_url: str, is_new_visitor: bool):
        """记录访问信息到日志文件"""
        access_info = {
            'ip': client_ip,
            'method': request_method,
            'url': request_url,
            'user_agent': user_agent,
            'is_new_visitor': is_new_visitor,
            'total_visits': self.total_visits,
            'online_count': len(self.current_online_users)
        }

        self.access_logger.info(
            f"访问记录 - IP: {client_ip} | {request_method} {request_url} | "
            f"新访问者: {'是' if is_new_visitor else '否'} | "
            f"在线: {len(self.current_online_users)} | 累计: {self.total_visits}"
        )
    
    def get_statistics(self) -> Dict:
        """获取当前统计信息"""
        return {
            "total_visits": self.total_visits,
            "current_online_count": len(self.current_online_users),
            "current_online_users": list(self.current_online_users)
        }

class AccessMonitorMiddleware(BaseHTTPMiddleware):
    """访问监控中间件"""
    
    def __init__(self, app, monitor_service: MonitorService):
        super().__init__(app)
        self.monitor_service = monitor_service
    
    async def dispatch(self, request: Request, call_next):
        # 获取客户端IP地址
        client_ip = request.client.host if request.client else "unknown"
        
        # 获取用户代理和其他请求信息
        user_agent = request.headers.get("user-agent", "unknown")
        request_method = request.method
        request_url = str(request.url)
        
        # 记录访问信息
        self.monitor_service.record_visit(client_ip, user_agent, request_method, request_url)
        
        # 继续处理请求
        response = await call_next(request)
        return response

# 全局监控服务实例
monitor_service = MonitorService()