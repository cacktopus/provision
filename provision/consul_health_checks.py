from typing import Dict, Any


def check_http(service: str, method: str, url: str) -> Dict[str, Any]:
    return {
        "name": f"{service} http health check",
        "http": url,
        "method": method,
        "interval": "10s",
        "timeout": "5s",
        "status": "success",
    }


def check_tcp(service: str, host: str, port: int) -> Dict[str, Any]:
    return {
        "name": f"{service} tcp health check",
        "tcp": f"{host}:{port}",
        "interval": "10s",
        "timeout": "5s",
        "status": "success",
    }
