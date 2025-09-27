
#!/bin/bash
set -e
apt-get update
apt-get install -y ca-certificates curl gnupg lsb-release python3 python3-pip python3-full git build-essential
# docker engine
if ! command -v docker >/dev/null; then curl -fsSL https://get.docker.com | sh ; fi
# compose plugin
apt-get install -y docker-compose-plugin
echo "export PIP_BREAK_SYSTEM_PACKAGES=1" >> /etc/profile
