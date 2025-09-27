#!/bin/bash
set -e
apt-get update
apt-get install -y python3 python3-pip python3-full python3-venv curl wget git gcc g++ build-essential
export PIP_BREAK_SYSTEM_PACKAGES=1
