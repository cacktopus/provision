#!/bin/sh

### Reset
/sbin/iptables -F INPUT
/sbin/iptables -F OUTPUT

### Loopback
/sbin/iptables -A INPUT  -i lo -j ACCEPT
/sbin/iptables -A OUTPUT -o lo -j ACCEPT

### Local network
/sbin/iptables -A INPUT  -p all -s 10.0.0.0/8 -j ACCEPT
/sbin/iptables -A OUTPUT -p all -d 10.0.0.0/8 -j ACCEPT

### Established connections
/sbin/iptables -A INPUT  -m state --state ESTABLISHED,RELATED -j ACCEPT
/sbin/iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

### SSH
/sbin/iptables -A OUTPUT -o eth0 -p tcp --dport 22 -j ACCEPT

### Alert-manager
if [ $(getent group alertmanager) ]; then
    /sbin/iptables -A OUTPUT -m owner --gid-owner alertmanager -p tcp --dport 443 -j ACCEPT
    /sbin/iptables -A OUTPUT -m owner --gid-owner alertmanager -p tcp --dport 587 -j ACCEPT
fi

### NTP
if grep -q -E "^allow-ntp" /etc/taglist.txt; then
    /sbin/iptables -A INPUT  -p udp --dport 123 -j ACCEPT
    /sbin/iptables -A OUTPUT -p udp --dport 123 -j ACCEPT
fi

### Default rule
/sbin/iptables -A INPUT  -j REJECT
/sbin/iptables -A OUTPUT -j REJECT