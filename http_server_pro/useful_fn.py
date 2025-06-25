import socket

def get_local_ip():
    ip = '127.0.0.1'
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        pass
    finally:
        s.close()
    return ip

def format_size(bytes):
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.2f} KB"
    else:
        return f"{bytes / (1024 * 1024):.2f} MB"