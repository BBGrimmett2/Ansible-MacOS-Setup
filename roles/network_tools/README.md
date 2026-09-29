# Network Tools Role

Install and configure network and VPN tools for macOS.

## Overview

This role manages installation of network utilities and API testing tools:

- **Bruno** - Open-source API client (Postman/Insomnia alternative)
- **OpenVPN** - VPN client
- **BIND tools** - DNS utilities (dig, nslookup, host)
- **Wireshark** - Network protocol analyzer
- **mtr** - Network diagnostic tool (traceroute + ping combined)
- **nmap** - Network scanner

## Requirements

- macOS
- Homebrew (installed by `homebrew` role)

## Role Variables

### Installation Control

```yaml
# Install or remove network tools
network_tools_state: present  # or 'absent'

# Install all tools (if false, only install enabled tools)
network_tools_install_all: true
```

### Individual Tool Control

```yaml
network_tools_bruno_enabled: true
network_tools_openvpn_enabled: true
network_tools_bind_enabled: true
network_tools_wireshark_enabled: false  # Requires manual setup
network_tools_mtr_enabled: true
network_tools_nmap_enabled: false  # Security tool, install if needed
```

### VPN Configuration

```yaml
# Configure VPN profiles
network_tools_vpn_configure: false

# VPN profiles directory
network_tools_vpn_profiles_dir: "{{ ansible_env.HOME }}/.vpn"

# Profile-specific VPN configuration
network_tools_vpn_personal_enabled: false
network_tools_vpn_work_enabled: false

# Work VPN configuration (Red Hat Shadowman)
network_tools_vpn_shadowman_enabled: false
network_tools_vpn_shadowman_profile_name: "shadowman"
```

## Dependencies

- `homebrew` role

## Public Functions (tasks_from)

```yaml
# Install individual tools
- ansible.builtin.import_role:
    name: network_tools
    tasks_from: install_bruno

- ansible.builtin.import_role:
    name: network_tools
    tasks_from: install_openvpn

- ansible.builtin.import_role:
    name: network_tools
    tasks_from: install_bind

- ansible.builtin.import_role:
    name: network_tools
    tasks_from: install_wireshark

- ansible.builtin.import_role:
    name: network_tools
    tasks_from: install_mtr

- ansible.builtin.import_role:
    name: network_tools
    tasks_from: install_nmap
```

## Example Playbook

### Install All Tools

```yaml
---
- name: Install network tools
  hosts: localhost
  roles:
    - role: network_tools
```

### Install Specific Tools Only

```yaml
---
- name: Install Bruno and DNS tools only
  hosts: localhost
  roles:
    - role: network_tools
      vars:
        network_tools_install_all: false
        network_tools_bruno_enabled: true
        network_tools_openvpn_enabled: false
        network_tools_bind_enabled: true
        network_tools_wireshark_enabled: false
        network_tools_mtr_enabled: false
        network_tools_nmap_enabled: false
```

## Tool Usage

### Bruno

```bash
# Open Bruno (GUI application)
open -a Bruno

# Bruno stores collections as files
# Collections can be version-controlled
# Default location: ~/Documents/Bruno/
```

**Features:**
- File-based collections (Git-friendly)
- No account required
- Environment variables
- Code generation for cURL, JavaScript, Python

### OpenVPN

```bash
# Connect to VPN
sudo openvpn --config /path/to/config.ovpn

# With authentication file
sudo openvpn --config config.ovpn --auth-user-pass auth.txt

# Daemonize
sudo openvpn --config config.ovpn --daemon
```

### BIND Tools (dig, nslookup, host)

```bash
# DNS lookup with dig
dig example.com

# Specific record type
dig example.com MX
dig example.com TXT

# Use specific nameserver
dig @8.8.8.8 example.com

# Reverse DNS lookup
dig -x 8.8.8.8

# Short answer
dig +short example.com

# nslookup
nslookup example.com

# host command
host example.com
host -t MX example.com
```

### Wireshark

```bash
# Launch Wireshark GUI
open -a Wireshark

# Command-line packet capture (tshark)
tshark -i en0

# Capture to file
tshark -i en0 -w capture.pcap

# Read from file
tshark -r capture.pcap

# Filter traffic
tshark -i en0 -f "tcp port 80"
```

**Note:** Wireshark requires additional setup for packet capture permissions on macOS.

### mtr

```bash
# Basic usage (combines ping + traceroute)
mtr example.com

# Generate report (-r) with 10 packets (-c 10)
mtr -r -c 10 example.com

# Show both hostnames and IPs
mtr -b example.com

# TCP mode (useful for firewall troubleshooting)
mtr --tcp example.com
```

### nmap

```bash
# Basic host scan
nmap 192.168.1.1

# Scan specific ports
nmap -p 80,443 example.com

# Scan port range
nmap -p 1-1000 example.com

# Service/version detection
nmap -sV example.com

# Operating system detection
sudo nmap -O example.com

# Fast scan (top 100 ports)
nmap -F example.com

# Scan entire subnet
nmap 192.168.1.0/24

# Save results
nmap -oN results.txt example.com
```

**Security Note:** Only scan networks you have permission to scan.

## Common Workflows

### API Testing with Bruno

1. Create a new collection
2. Add requests with variables
3. Organize into folders
4. Version control the collection folder
5. Share with team via Git

### Network Diagnostics

```bash
# Check connectivity
ping -c 4 example.com

# Trace route with timing
mtr example.com

# DNS resolution
dig +short example.com

# Check open ports
nmap -p 1-1000 localhost
```

### VPN Management

```bash
# Test VPN connection
ping vpn.example.com

# Check VPN is running
ps aux | grep openvpn

# View VPN logs
tail -f /var/log/openvpn.log
```

## Tags

- `validate` - Run validation tasks only
- `install` - Run installation tasks only

## Testing

### Syntax Check

```bash
ansible-playbook --syntax-check playbooks/tests/test_network_tools.yml
```

### Dry Run

```bash
ansible-playbook --check playbooks/tests/test_network_tools.yml
```

### Execute

```bash
ansible-playbook playbooks/tests/test_network_tools.yml
```

## Post-Installation

### Verify Installation

```bash
# Check tool versions
bruno --version
openvpn --version
dig -v
wireshark --version
mtr --version
nmap --version
```

### Bruno Setup

1. Open Bruno application
2. Create new collection or import existing
3. Set environment variables
4. Start making API requests

### Wireshark Permissions

macOS requires special permissions for packet capture:

```bash
# Install ChmodBPF (included with Wireshark installer)
# Or manually set permissions:
sudo chmod +r /dev/bpf*
```

## Security Considerations

- **nmap**: Only scan networks you own or have permission to scan
- **Wireshark**: Packet capture requires elevated permissions
- **OpenVPN**: Store credentials securely, never in version control
- **Bruno**: API keys should use environment variables, not hardcoded

## License

MIT

## Author

Brian Grimmett
