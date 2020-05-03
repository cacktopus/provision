data_dir = "/home/consul/consul-data"
server = {{server}}
{{bootstrap}}
node_name = "{{hostname}}"
bind_addr = {{bind_addr}}
enable_local_script_checks = true
client_addr = "0.0.0.0"
recursors = ["8.8.8.8", "4.4.4.4"] # TODO
ui = true
telemetry = {
    prometheus_retention_time = "60m"
    disable_hostname = true
}
retry_join = [{{retry_join}}]
addresses = {
    dns = "0.0.0.0"
}