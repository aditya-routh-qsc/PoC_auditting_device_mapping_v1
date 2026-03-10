import socket

port_number = 8181

def get_port_number():
    return port_number

def get_local_ip():
    """Automatically retrieves the local LAN IP address of this machine."""
    try:
        # Create a dummy UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Attempt to connect to an external IP. 
        # (It doesn't actually send packets or require internet access to work locally)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        # Fallback in case there is absolutely no network connection
        return "127.0.0.1"
    
def get_local_hostname():
    """Retrieves the hostname of this machine."""
    return socket.gethostname()