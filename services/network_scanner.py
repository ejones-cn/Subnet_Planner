#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
网络扫描服务模块
提供ICMP Ping和TCP端口扫描功能，支持多线程并发扫描
"""

import ipaddress
import platform
import socket
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional


class NetworkScanner:
    """网络扫描器，支持ICMP Ping和TCP端口扫描"""

    def __init__(self):
        self._lock = threading.Lock()
        self._cancelled = False
        self._scanned_count = 0
        self._active_ips = []
        self._total_ips = 0

    def reset(self):
        """重置扫描状态"""
        with self._lock:
            self._cancelled = False
            self._scanned_count = 0
            self._active_ips = []
            self._total_ips = 0

    def cancel(self):
        """取消扫描"""
        with self._lock:
            self._cancelled = True

    def is_cancelled(self) -> bool:
        """检查是否已取消"""
        with self._lock:
            return self._cancelled

    def get_progress(self) -> tuple[int, int, int]:
        """获取当前扫描进度

        Returns:
            tuple[int, int, int]: (已扫描数, 活动IP数, 总IP数)
        """
        with self._lock:
            return self._scanned_count, len(self._active_ips), self._total_ips

    @staticmethod
    def ping_host(ip_address: str, timeout_ms: int = 500) -> bool:
        """使用ICMP Ping检测主机是否存活

        Args:
            ip_address: 目标IP地址
            timeout_ms: 超时时间（毫秒）

        Returns:
            bool: 主机是否存活
        """
        system = platform.system().lower()
        try:
            if system == 'windows':
                cmd = ['ping', '-n', '1', '-w', str(timeout_ms), ip_address]
            else:
                timeout_sec = max(1, timeout_ms // 1000)
                cmd = ['ping', '-c', '1', '-W', str(timeout_sec), ip_address]

            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=min(timeout_ms * 2, 3000) / 1000.0
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False

    @staticmethod
    def tcp_check_host(ip_address: str, timeout_sec: float = 0.5, ports: Optional[list[int]] = None) -> bool:
        """使用TCP连接检测主机是否存活

        Args:
            ip_address: 目标IP地址
            timeout_sec: 超时时间（秒）
            ports: 要检查的端口列表，默认检查常见端口

        Returns:
            bool: 主机是否有任何端口开放
        """
        if ports is None:
            ports = [80, 443, 22, 135, 445, 3389]

        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout_sec)
                result = sock.connect_ex((ip_address, port))
                sock.close()
                if result == 0:
                    return True
            except (socket.error, socket.timeout, OSError):
                continue
        return False

    @staticmethod
    def resolve_hostname(ip_address: str, timeout_sec: float = 0.5) -> str:
        """反向DNS解析主机名

        Args:
            ip_address: IP地址
            timeout_sec: 超时时间（秒）

        Returns:
            str: 主机名，解析失败返回空字符串
        """
        try:
            old_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(timeout_sec)
            try:
                hostname, _, _ = socket.gethostbyaddr(ip_address)
                return hostname
            finally:
                socket.setdefaulttimeout(old_timeout)
        except (socket.error, socket.herror, socket.gaierror, OSError):
            return ""

    def scan_network(
        self,
        network: str,
        thread_count: int = 10,
        timeout_ms: int = 500,
        scan_method: str = 'ping',
        on_progress: Optional[Callable[[int, int, int, str], None]] = None,
        on_ip_found: Optional[Callable[[dict], None]] = None,
        on_complete: Optional[Callable[[list[dict]], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        """扫描网络中的活动主机（在后台线程中执行）

        Args:
            network: 网络地址（CIDR格式）
            thread_count: 并发线程数
            timeout_ms: 超时时间（毫秒）
            scan_method: 扫描方式 ('ping' 或 'tcp')
            on_progress: 进度回调 (scanned, active, total, current_ip)
            on_ip_found: 发现活动IP回调 (ip_info_dict)
            on_complete: 扫描完成回调 (active_ips_list)
            on_error: 错误回调 (error_message)
        """
        self.reset()

        try:
            ip_network = ipaddress.ip_network(network, strict=False)
        except ValueError as e:
            if on_error:
                on_error(str(e))
            return

        scan_ips = list(ip_network.hosts())
        with self._lock:
            self._total_ips = len(scan_ips)

        if self._total_ips == 0:
            if on_complete:
                on_complete([])
            return

        timeout_sec = timeout_ms / 1000.0
        last_progress_time = [0.0]
        progress_interval = 0.1

        def scan_single_ip(ip):
            """扫描单个IP地址"""
            if self.is_cancelled():
                return None

            ip_str = str(ip)
            is_alive = False

            if scan_method == 'ping':
                is_alive = self.ping_host(ip_str, timeout_ms)
            else:
                is_alive = self.tcp_check_host(ip_str, timeout_sec)

            with self._lock:
                self._scanned_count += 1
                current_scanned = self._scanned_count
                current_active = len(self._active_ips)

            if on_progress:
                now = time.monotonic()
                if (now - last_progress_time[0] >= progress_interval
                        or current_scanned == self._total_ips):
                    last_progress_time[0] = now
                    on_progress(current_scanned, current_active, self._total_ips, ip_str)

            if is_alive and not self.is_cancelled():
                hostname = self.resolve_hostname(ip_str, timeout_sec=0.3)
                ip_info = {
                    'ip_address': ip_str,
                    'hostname': hostname,
                    'description': '',
                }
                with self._lock:
                    self._active_ips.append(ip_info)
                if on_ip_found:
                    on_ip_found(ip_info)
                return ip_info

            return None

        try:
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = {executor.submit(scan_single_ip, ip): ip for ip in scan_ips}

                for future in as_completed(futures):
                    if self.is_cancelled():
                        for f in futures:
                            if not f.done():
                                f.cancel()
                        break
                    try:
                        future.result()
                    except Exception:
                        pass

        except Exception as e:
            if on_error:
                on_error(str(e))
            return

        if not self.is_cancelled() and on_complete:
            with self._lock:
                result = list(self._active_ips)
            on_complete(result)
        elif self.is_cancelled() and on_complete:
            with self._lock:
                result = list(self._active_ips)
            on_complete(result)
