import socket

def scan_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            return port, "Open" if result == 0 else "Closed"
    except Exception as e:
        return port, f"Error: {str(e)}"
