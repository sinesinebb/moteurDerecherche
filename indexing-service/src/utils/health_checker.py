# src/utils/health_checker.py
import socket
import urllib.request
from typing import Tuple, Iterable, Optional


def check_tcp(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def check_http(url: str, timeout: float = 2.0) -> Tuple[bool, Optional[int]]:
    """
    Performs a simple HTTP GET and returns (ok, status_code)
    """
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, getattr(resp, "status", None)
    except Exception:
        return False, None


def check_elasticsearch_hosts(hosts: Iterable[str]) -> dict:
    """
    hosts: iterable of 'http://host:port' strings.
    Returns mapping host->(ok, status_code)
    """
    results = {}
    for h in hosts:
        try:
            ok, status = check_http(h)
            results[h] = {"ok": ok, "status": status}
        except Exception:
            results[h] = {"ok": False, "status": None}
    return results
