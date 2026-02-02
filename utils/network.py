import socket


def is_ip_active(ip: str, ports=(22, 80, 443), timeout=1) -> bool:
    """
    Comprueba si una IP está activa intentando conexión TCP
    a puertos comunes.
    """
    for port in ports:
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            continue
    return False
