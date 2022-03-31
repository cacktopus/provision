#!/bin/sh

### Reset
/sbin/iptables -F INPUT
/sbin/iptables -F OUTPUT

### Loopback
/sbin/iptables -A INPUT  -i lo -j ACCEPT
/sbin/iptables -A OUTPUT -o lo -j ACCEPT

### Local network
/sbin/iptables -A INPUT  -p all -s {{network}} -j ACCEPT
/sbin/iptables -A OUTPUT -p all -d {{network}} -j ACCEPT

### Established connections
/sbin/iptables -A INPUT  -m state --state ESTABLISHED,RELATED -j ACCEPT
/sbin/iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

### SSH
/sbin/iptables -A OUTPUT -p tcp --dport 22 -j ACCEPT
/sbin/iptables -A INPUT -p tcp --dport 22 -j ACCEPT

### Accept Rules
{% for ip in allow -%}
/sbin/iptables -A INPUT   -s {{ip}} -j ACCEPT
/sbin/iptables -A OUTPUT  -d {{ip}} -j ACCEPT
/sbin/iptables -A FORWARD -d {{ip}} -j ACCEPT
{% endfor %}

### Reject Rules
{% for ip in block -%}
/sbin/iptables -A INPUT   -s {{ip}} -j REJECT
/sbin/iptables -A OUTPUT  -d {{ip}} -j REJECT
/sbin/iptables -A FORWARD -d {{ip}} -j REJECT
{% endfor %}
