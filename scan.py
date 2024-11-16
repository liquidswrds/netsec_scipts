import socket
import ipaddress
from scapy.all import sr1, IP, ICMP, UDP

FOUND_HOSTS_FILE = "found_hosts.txt"

def check_host(host):
    """Check if the host is reachable by sending an ICMP ping."""
    pkt = IP(dst=host) / ICMP()
    response = sr1(pkt, timeout=2, verbose=0)

    if response is not None and response.haslayer(ICMP):
        return True
    return False

def check_network(network):
    """Check if each host in a network range exists by pinging each IP and save found hosts."""
    reachable_hosts = []
    for ip in ipaddress.IPv4Network(network, strict=False):
        if check_host(str(ip)):
            reachable_hosts.append(str(ip))
            print(f"{ip} is reachable.")
    with open(FOUND_HOSTS_FILE, 'w') as f:
        for host in reachable_hosts:
            f.write(f"{host}\n")
    print("\nReachable hosts saved to found_hosts.txt.")
    return reachable_hosts

def scan_tcp_ports(hosts, ports):
    """Scan specified TCP ports on the list of hosts."""
    print("\nStarting TCP port scan...")
    for host in hosts:
        print(f"\nScanning {host} for TCP ports...")
        open_ports = []
        for port in ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                if result == 0:
                    open_ports.append(port)
                    print(f"Host {host} - Open UDP Ports: {open_ports}")

def scan_udp_ports(hosts, ports):
    """Scan specified UDP ports on the list of hosts using scapy."""
    print("\nStarting UDP port scan...")
    for host in hosts:
        print(f"\nScanning {host} for UDP ports...")
        open_ports = []
        for port in ports:
            pkt = IP(dst=host) / UDP(dport=port)
            response = sr1(pkt, timeout=2, verbose=0)
            if response is None:
                open_ports.append(port)  # Likely open or filtered
                print(f"Host {host} - Open UDP Ports: {open_ports}")

def load_found_hosts():
    """Load found hosts from file."""
    try:
        with open(FOUND_HOSTS_FILE, 'r') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print("No hosts found. Please perform a network scan first.")
        return []

def main_menu():
    while True:
        print("\n--- Main Menu ---")
        print("1. Scan Network for Hosts")
        print("2. Scan Found Hosts for Open Ports")
        print("3. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            network = input("Enter a network address (e.g., 192.168.1.0/24): ")
            check_network(network)
        elif choice == '2':
            hosts = load_found_hosts()
            if hosts:
                port_scan_menu(hosts)
        elif choice == '3':
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please try again.")

def port_scan_menu(hosts):
    while True:
        print("\n--- Port Scan Menu ---")
        print("1. TCP Port Scan")
        print("2. UDP Port Scan")
        print("3. Back to Main Menu")
        choice = input("Select an option: ")

        if choice == '1':
            tcp_scan_menu(hosts)
        elif choice == '2':
            udp_scan_menu(hosts)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

def tcp_scan_menu(hosts):
    while True:
        print("\n--- TCP Port Scan Menu ---")
        print("1. Scan Standard TCP Ports")
        print("2. Enter Custom Ports")
        print("3. Scan All Ports (1-65535)")
        print("4. Back to Port Scan Menu")
        choice = input("Select an option: ")

        if choice == '1':
            tcp_ports = [21, 22, 23, 80, 443]  # Standard TCP ports
            scan_tcp_ports(hosts, tcp_ports)
        elif choice == '2':
            custom_ports = input("Enter ports (comma-separated, range, or single port): ")
            ports = parse_custom_ports(custom_ports)
            scan_tcp_ports(hosts, ports)
        elif choice == '3':
            all_ports = list(range(1, 65536))
            scan_tcp_ports(hosts, all_ports)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

def udp_scan_menu(hosts):
    while True:
        print("\n--- UDP Port Scan Menu ---")
        print("1. Scan Standard UDP Ports")
        print("2. Enter Custom Ports")
        print("3. Scan All Ports (1-65535)")
        print("4. Back to Port Scan Menu")
        choice = input("Select an option: ")

        if choice == '1':
            udp_ports = [53, 67, 68, 123, 161]  # Standard UDP ports
            scan_udp_ports(hosts, udp_ports)
        elif choice == '2':
            custom_ports = input("Enter ports (comma-separated, range, or single port): ")
            ports = parse_custom_ports(custom_ports)
            scan_udp_ports(hosts, ports)
        elif choice == '3':
            all_ports = list(range(1, 65536))
            scan_udp_ports(hosts, all_ports)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

def parse_custom_ports(custom_ports):
    ports = set()
    for part in custom_ports.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.update(range(start, end + 1))
        else:
            ports.add(int(part))
    return list(ports)

if __name__ == "__main__":
    main_menu()
