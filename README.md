# STB HG680P Telegram Bot - Multi-Version Armbian Support

## 🖥️ Enhanced Multi-Version Support

### ✅ Supported Armbian Versions:
- **🐛 Armbian 20.11 Bullseye** - credentials.json or env tokens
- **🐛 Armbian 25.11 Bookworm** - env tokens required
- **🔧 Error Fixing** - GPG keys, dependencies, broken packages
- **🌟 JMDKH Features** - Torrent, mirror, clone capabilities
- **🔗 AnyDesk Integration** - With dependency resolution

### ✅ Pre-configured Credentials:
- **Bot Token:** `8436081597:AAE-8bfWrbvhl26-l9y65p48DfWjQOYPR2A`
- **Channel ID:** `-1001802424804` (@ZalheraThink)

## 📋 Multi-Version Deployment

### 1. Extract and Setup
```bash
unzip telegram-bot-stb-armbian-multi-version.zip
cd telegram-bot-stb-armbian-multi-version
sudo ./setup.sh  # Auto-detects OS version and fixes errors
```

**What the setup fixes:**
- **GPG Key Errors** - Fixes missing Debian archive keys
- **Broken Dependencies** - Resolves AnyDesk libgtkglext1 issues
- **Repository Issues** - Updates archive.debian.org to current repos
- **Docker Detection** - Skips installation if already present
- **AnyDesk Dependencies** - Installs required GUI libraries

### 2. Configuration by OS Version

#### For Armbian 25.11 Bookworm:
```bash
nano .env
# REQUIRED for Bookworm:
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

#### For Armbian 20.11 Bullseye:
```bash
# Option 1: Use credentials.json file
mkdir -p credentials
# Place your credentials.json in ./credentials/

# Option 2: Use environment variables
nano .env
GOOGLE_CLIENT_ID=your_google_client_id  # Optional for Bullseye
GOOGLE_CLIENT_SECRET=your_google_client_secret  # Optional for Bullseye
```

### 3. Start Multi-Version Bot
```bash
./start.sh
# ✅ Auto-detects Armbian version
# ✅ Sets appropriate auth method
# ✅ Docker Compose deployment only
```

## 🔧 Error Fixing Features

### GPG Key Error Resolution:
**Error Fixed:**
```
W: GPG error: http://archive.debian.org/debian bullseye InRelease: 
The following signatures couldn't be verified because the public key is not available: 
NO_PUBKEY 0E98404D386FA1D9 NO_PUBKEY 6ED0E7B82643E131
```

**Solution Applied:**
```bash
# Add missing keys
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 0E98404D386FA1D9
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 6ED0E7B82643E131
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 605C66F00D6C9793

# Update repository sources from archive to current
```

### AnyDesk Dependency Error Resolution:
**Error Fixed:**
```
anydesk : Depends: libgtkglext1 but it is not installed
E: Unmet dependencies. Try 'apt --fix-broken install'
```

**Solution Applied:**
```bash
# Install dependencies first
apt-get install -y libgtkglext1 libgtkglext1-dev libglib2.0-0 libgtk2.0-0
# Then install AnyDesk
apt-get install -y anydesk
```

## 🎯 OS-Specific Features

### Armbian 20.11 Bullseye:
- **Auth Method:** credentials.json file OR env tokens
- **Python Version:** 3.9
- **Docker Base:** python:3.9-slim-bullseye
- **GUI Libraries:** Standard Debian Bullseye packages

### Armbian 25.11 Bookworm:
- **Auth Method:** Environment tokens (REQUIRED)
- **Python Version:** 3.11
- **Docker Base:** python:3.11-slim-bookworm
- **GUI Libraries:** Updated Bookworm packages with non-free-firmware

## 🔍 Expected Results

### Successful Multi-Version Setup:
```bash
📱 Detected System:
Armbian Version: 20.11.1 Bullseye
Base OS: bullseye
Board: HG680P
Architecture: aarch64

🔑 Fixing GPG key errors...
✅ GPG keys and repositories fixed

🔧 Fixing broken packages...
✅ Broken packages fixed

🖥️ Installing AnyDesk with dependency fixing for bullseye...
📦 Installing AnyDesk dependencies...
✅ AnyDesk installed successfully
🆔 AnyDesk ID: 123456789
```

### Working Multi-Version Commands:
```
User: /start
Bot: 🚀 STB Telegram Bot - HG680P Multi-Version Support
     🐛 Base OS: Bullseye
     🔑 Auth Method: Credentials File (Bullseye)

User: /system
Bot: 💻 STB HG680P Multi-Version System Information
     🐧 Multi-Version Armbian Information:
     • Version: 20.11.1 Bullseye
     • Base OS: Bullseye
     • Auth Method: Credentials File

User: /auth (on Bullseye)
Bot: 🔐 Google Drive Authentication - Multi-Version Support
     🐛 Detected OS: Bullseye
     🔑 Auth Method: Credentials File
```

## 🐳 Docker Compose Only Deployment

### Multi-Container Architecture:
```yaml
services:
  telegram-bot:
    container_name: telegram-bot-stb-multi
    build:
      args:
        BASE_OS: ${DETECTED_BASE}  # bullseye or bookworm

  aria2:
    container_name: aria2-stb-multi
```

### No Direct Docker/CLI Usage:
- **✅ Docker Compose Only** - All deployments through compose
- **❌ No docker run commands** - Simplified management
- **❌ No direct CLI execution** - Container-based operation
- **✅ Service orchestration** - Proper dependency management

## 📱 Multi-Version Remote Access

### AnyDesk with Dependency Fixing:
1. **Auto-dependency resolution** - Installs libgtkglext1 and related
2. **OS-specific packages** - Different packages for Bullseye/Bookworm  
3. **Fallback installation** - Uses .deb file if repo fails
4. **Service configuration** - Auto-configures unattended access

### Connection Instructions:
1. **Get AnyDesk ID:** Use `/anydesk` command
2. **Password:** `stbaccess` (auto-configured)
3. **GUI Access:** Whatever desktop is available on Armbian
4. **Troubleshooting:** Built-in dependency fixing

## ⚠️ Multi-Version Important Notes

### Docker Installation:
- **Auto-Detection** - Skips Docker install if already present
- **Version Check** - Verifies Docker and Docker Compose versions
- **ARM64 Support** - Installs correct architecture packages
- **Service Management** - Enables and starts Docker service

### Error Handling:
- **GPG Key Recovery** - Automatic key server retrieval
- **Repository Fallback** - Switches from archive to current repos
- **Broken Package Fix** - Automatic dependency resolution
- **Service Recovery** - Restarts failed services

## ✅ All Multi-Version Features Working

- ✅ **Armbian 20.11 Bullseye** - Full support with credentials.json
- ✅ **Armbian 25.11 Bookworm** - Full support with env tokens  
- ✅ **Error Fixing** - GPG keys, dependencies, repositories
- ✅ **AnyDesk Installation** - With dependency resolution
- ✅ **Docker Detection** - Skips if already installed
- ✅ **Multi-Auth Support** - OS-appropriate authentication
- ✅ **JMDKH Features** - Torrent, mirror, clone
- ✅ **Docker Compose Only** - No direct CLI usage

**🎉 Complete multi-version solution with comprehensive error fixing! 🚀**

**Extract → Setup (Auto-Fix) → Configure → Deploy → All Versions Working! 🖥️**
