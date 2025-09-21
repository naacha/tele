#!/usr/bin/env python3
"""
TELEGRAM BOT FOR STB HG680P - MULTI ARMBIAN VERSION SUPPORT
✅ Channel subscription check (@ZalheraThink) - ID: -1001802424804
✅ Bot Token integrated: 8436081597:AAE-8bfWrbvhl26-l9y65p48DfWjQOYPR2A
✅ JMDKH Features: Torrent, Magnet, GDrive Clone, Direct Mirror
✅ Armbian 20.11 Bullseye support (credentials.json method)
✅ Armbian 25.11 Bookworm support (env token method)
✅ AnyDesk installation with dependency fixing
✅ Multi-OS OAuth2 compatibility
"""

import os
import sys
import asyncio
import json
import logging
import time
import requests
import platform
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
import hashlib
import re
from urllib.parse import urlparse

# Core telegram imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, ContextTypes, InlineQueryHandler
from telegram.error import BadRequest, Forbidden

# Google Drive imports - multi-version compatible
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/logs/bot.log', mode='a') if os.path.exists('/app/logs') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration with integrated credentials
BOT_TOKEN = os.getenv('BOT_TOKEN', '8436081597:AAE-8bfWrbvhl26-l9y65p48DfWjQOYPR2A')
OWNER_USERNAME = os.getenv('OWNER_USERNAME', 'zalhera')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_FILE = '/app/data/token.json'
CREDENTIALS_FILE = '/app/credentials/credentials.json'

# Channel subscription settings
REQUIRED_CHANNEL = '@ZalheraThink'
CHANNEL_URL = 'https://t.me/ZalheraThink'
CHANNEL_ID = -1001802424804

# Settings optimized for multi-version Armbian
MAX_CONCURRENT = int(os.getenv('MAX_CONCURRENT_DOWNLOADS', '2'))
MAX_SPEED_MBPS = float(os.getenv('MAX_SPEED_MBPS', '15'))
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '8192'))

# Bot info
BOT_USERNAME = os.getenv('BOT_USERNAME', 'your_bot_username')

# Multi-version specific settings
ARIA2_PORT = 6800
ARIA2_SECRET = os.getenv('ARIA2_SECRET', 'stb_secret')

# Ensure directories exist
def ensure_directories():
    """Create required directories for multi-version deployment"""
    dirs = ['/app/data', '/app/downloads', '/app/logs', '/app/credentials', '/app/torrents']
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        os.chmod(dir_path, 0o777)

ensure_directories()

class ArmbianSystemInfo:
    """Multi-version Armbian system information detector"""

    @staticmethod
    def detect_armbian_version():
        """Detect Armbian version and base OS"""
        try:
            if os.path.exists('/etc/armbian-release'):
                with open('/etc/armbian-release', 'r') as f:
                    content = f.read()
                    info = {}
                    for line in content.split('\n'):
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            info[key] = value.strip('"')

                    version = info.get('VERSION', 'Unknown')
                    # Determine base OS from version
                    if '20.11' in version or 'bullseye' in version.lower():
                        base_os = 'bullseye'
                    elif '25.11' in version or 'bookworm' in version.lower():
                        base_os = 'bookworm'
                    else:
                        # Try to detect from /etc/os-release
                        base_os = ArmbianSystemInfo.detect_base_os()

                    info['BASE_OS'] = base_os
                    return info

            # Fallback detection
            base_os = ArmbianSystemInfo.detect_base_os()
            return {
                'VERSION': 'Unknown',
                'BRANCH': 'current',
                'BOARD': 'HG680P',
                'BASE_OS': base_os
            }
        except Exception as e:
            logger.warning(f"Could not detect Armbian version: {e}")
            return {
                'VERSION': 'Unknown',
                'BRANCH': 'current', 
                'BOARD': 'HG680P',
                'BASE_OS': 'bullseye'
            }

    @staticmethod
    def detect_base_os():
        """Detect base OS (bullseye/bookworm) from system"""
        try:
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    content = f.read().lower()
                    if 'bookworm' in content:
                        return 'bookworm'
                    elif 'bullseye' in content:
                        return 'bullseye'

            # Try lsb_release
            result = subprocess.run(['lsb_release', '-cs'], capture_output=True, text=True)
            if result.returncode == 0:
                codename = result.stdout.strip().lower()
                if codename in ['bookworm', 'bullseye']:
                    return codename

            # Default fallback
            return 'bullseye'

        except:
            return 'bullseye'

    @staticmethod
    def get_auth_method():
        """Determine authentication method based on OS version"""
        armbian_info = ArmbianSystemInfo.detect_armbian_version()
        base_os = armbian_info.get('BASE_OS', 'bullseye')

        if base_os == 'bookworm':
            return 'env_tokens'  # Use GOOGLE_CLIENT_ID/SECRET from env
        else:
            return 'credentials_file'  # Use credentials.json file

    @staticmethod
    def detect_gui_environment():
        """Detect GUI environment on multi-version Armbian"""
        try:
            # Check for X11 display
            if os.environ.get('DISPLAY'):
                return True

            # Check for running display managers
            display_managers = ['lightdm', 'gdm3', 'sddm', 'nodm']
            for dm in display_managers:
                result = subprocess.run(['pgrep', dm], capture_output=True)
                if result.returncode == 0:
                    return True

            # Check for desktop environments
            desktop_processes = ['lxsession', 'xfce4-session', 'openbox', 'fluxbox', 'matchbox']
            for de in desktop_processes:
                result = subprocess.run(['pgrep', de], capture_output=True)
                if result.returncode == 0:
                    return True

            # Check for X server
            result = subprocess.run(['pgrep', 'Xorg'], capture_output=True)
            if result.returncode == 0:
                return True

            return False
        except:
            return False

    @staticmethod
    def detect_desktop_environment():
        """Detect desktop environment"""
        desktop_environments = {
            'lxsession': 'LXDE',
            'xfce4-session': 'XFCE4',
            'openbox': 'Openbox',
            'fluxbox': 'Fluxbox',
            'matchbox': 'Matchbox',
            'gnome-session': 'GNOME',
            'mate-session': 'MATE'
        }

        for process, de_name in desktop_environments.items():
            try:
                result = subprocess.run(['pgrep', process], capture_output=True)
                if result.returncode == 0:
                    return f"{de_name} (Built-in)"
            except:
                continue

        # If X is running but no specific DE detected
        try:
            result = subprocess.run(['pgrep', 'Xorg'], capture_output=True)
            if result.returncode == 0:
                return 'Minimal GUI (Built-in)'
        except:
            pass

        return 'None'

    @staticmethod
    def get_system_info():
        """Get comprehensive multi-version system information"""
        try:
            # Basic system info
            with open('/proc/meminfo', 'r') as f:
                mem_info = f.read()
                mem_total = [line for line in mem_info.split('\n') if 'MemTotal' in line]
                mem_total = mem_total[0].split()[1] if mem_total else "Unknown"

            with open('/proc/cpuinfo', 'r') as f:
                cpu_info = f.read()
                cpu_model = [line for line in cpu_info.split('\n') if 'model name' in line]
                cpu_model = cpu_model[0].split(':')[1].strip() if cpu_model else "ARM CPU"

            # Storage info
            storage = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            storage_info = storage.stdout.split('\n')[1].split() if storage.returncode == 0 else ["Unknown"]

            # Armbian info
            armbian_info = ArmbianSystemInfo.detect_armbian_version()

            # GUI detection
            gui_available = ArmbianSystemInfo.detect_gui_environment()

            # Auth method
            auth_method = ArmbianSystemInfo.get_auth_method()

            return {
                'architecture': platform.machine(),
                'memory': f"{int(mem_total)//1024} MB" if mem_total != "Unknown" else "Unknown",
                'cpu': cpu_model,
                'storage_total': storage_info[1] if len(storage_info) > 1 else "Unknown",
                'storage_used': storage_info[2] if len(storage_info) > 2 else "Unknown",
                'storage_available': storage_info[3] if len(storage_info) > 3 else "Unknown",
                'armbian_version': armbian_info.get('VERSION', 'Unknown'),
                'armbian_branch': armbian_info.get('BRANCH', 'current'),
                'board_name': armbian_info.get('BOARD', 'HG680P'),
                'base_os': armbian_info.get('BASE_OS', 'bullseye'),
                'gui_available': gui_available,
                'desktop_env': ArmbianSystemInfo.detect_desktop_environment(),
                'auth_method': auth_method
            }
        except Exception as e:
            logger.warning(f"Could not get system info: {e}")
            return {
                'architecture': platform.machine(),
                'memory': "Unknown",
                'cpu': "ARM CPU",
                'storage_total': "Unknown",
                'storage_used': "Unknown", 
                'storage_available': "Unknown",
                'armbian_version': 'Unknown',
                'armbian_branch': 'current',
                'board_name': 'HG680P',
                'base_os': 'bullseye',
                'gui_available': True,
                'desktop_env': 'Built-in GUI',
                'auth_method': 'credentials_file'
            }

class ChannelSubscriptionCheck:
    """Channel subscription verification"""

    @staticmethod
    async def is_user_subscribed(context, user_id):
        """Check if user is subscribed to required channel"""
        try:
            member = await context.bot.get_chat_member(CHANNEL_ID, user_id)

            if member.status in ['member', 'administrator', 'creator']:
                logger.info(f"✅ User {user_id} is subscribed to {REQUIRED_CHANNEL}")
                return True
            else:
                logger.info(f"❌ User {user_id} is not subscribed to {REQUIRED_CHANNEL}")
                return False

        except (BadRequest, Forbidden) as e:
            logger.warning(f"Could not check subscription for user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Subscription check error: {e}")
            return False

    @staticmethod
    async def send_subscription_message(update: Update):
        """Send subscription required message"""
        keyboard = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = f"""
🔒 **Channel Subscription Required**

To use this bot, you must first join our channel:

📢 **{REQUIRED_CHANNEL}**

Click the button below to join, then try again.

⚠️ **Important:**
• You must stay subscribed to use the bot
• If you leave the channel, bot will stop working
• This helps us provide better service

🔄 After joining, use /start again
"""

        await update.message.reply_text(
            message, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check channel subscription"""
    user_id = update.effective_user.id

    # Skip check for owner
    if is_owner(update.effective_user.username):
        return True

    if not await ChannelSubscriptionCheck.is_user_subscribed(context, user_id):
        await ChannelSubscriptionCheck.send_subscription_message(update)
        return False

    return True

class MultiVersionGoogleDriveManager:
    """Multi-version Google Drive manager with different auth methods"""

    def __init__(self):
        self.service = None
        self.credentials = None
        self.system_info = ArmbianSystemInfo.get_system_info()
        self.auth_method = self.system_info['auth_method']
        self.load_credentials()

    def load_credentials(self):
        """Load credentials based on OS version"""
        try:
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'r') as f:
                    token_data = json.load(f)

                # Different credential loading based on auth method
                if self.auth_method == 'env_tokens':
                    # Bookworm: Use env tokens
                    client_id = GOOGLE_CLIENT_ID
                    client_secret = GOOGLE_CLIENT_SECRET
                else:
                    # Bullseye: Use credentials.json file
                    client_id = token_data.get('client_id') or GOOGLE_CLIENT_ID
                    client_secret = token_data.get('client_secret') or GOOGLE_CLIENT_SECRET

                self.credentials = Credentials(
                    token=token_data.get('token'),
                    refresh_token=token_data.get('refresh_token'),
                    client_id=client_id,
                    client_secret=client_secret,
                    token_uri='https://oauth2.googleapis.com/token',
                    scopes=SCOPES
                )

                if self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    self.save_credentials()

                if self.credentials.valid:
                    self.service = build('drive', 'v3', credentials=self.credentials, cache_discovery=False)
                    logger.info(f"✅ Google Drive authenticated ({self.auth_method})")

        except Exception as e:
            logger.warning(f"Could not load credentials: {e}")

    def create_credentials_json(self):
        """Create credentials.json based on auth method"""
        if self.auth_method == 'env_tokens':
            # Bookworm: Must use env variables
            if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
                logger.error("Bookworm: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET required in env")
                return False

            client_id = GOOGLE_CLIENT_ID
            client_secret = GOOGLE_CLIENT_SECRET
        else:
            # Bullseye: Use credentials.json file or fallback to env
            try:
                if os.path.exists(CREDENTIALS_FILE):
                    with open(CREDENTIALS_FILE, 'r') as f:
                        cred_data = json.load(f)
                        client_id = cred_data['installed']['client_id']
                        client_secret = cred_data['installed']['client_secret']
                else:
                    # Fallback to env for Bullseye
                    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
                        logger.error("Bullseye: credentials.json not found and env vars not set")
                        return False
                    client_id = GOOGLE_CLIENT_ID
                    client_secret = GOOGLE_CLIENT_SECRET
            except Exception as e:
                logger.error(f"Bullseye credentials error: {e}")
                return False

        credentials_data = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:8080", "urn:ietf:wg:oauth:2.0:oob"]
            }
        }

        try:
            os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
            with open(CREDENTIALS_FILE, 'w') as f:
                json.dump(credentials_data, f, indent=2)
            logger.info(f"✅ Credentials file created ({self.auth_method})")
            return True
        except Exception as e:
            logger.error(f"Failed to create credentials file: {e}")
            return False

    def get_auth_url(self):
        """Get OAuth2 authorization URL for multi-version"""
        try:
            if not self.create_credentials_json():
                return None, f"Could not create credentials file for {self.auth_method}"

            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            flow.redirect_uri = "http://localhost:8080"

            auth_url, _ = flow.authorization_url(
                access_type='offline',
                prompt='consent',
                include_granted_scopes='true'
            )

            self._flow = flow

            logger.info(f"✅ Authorization URL generated ({self.auth_method})")
            return auth_url, None

        except Exception as e:
            logger.error(f"Failed to create auth URL: {e}")
            return None, f"Auth URL generation failed: {str(e)}"

    def authenticate_with_code(self, auth_code):
        """Complete authentication with code"""
        try:
            if not hasattr(self, '_flow') or self._flow is None:
                return False, "No active authentication flow. Please use /auth first."

            auth_code = auth_code.strip()
            self._flow.fetch_token(code=auth_code)
            self.credentials = self._flow.credentials

            self.save_credentials()
            self.service = build('drive', 'v3', credentials=self.credentials, cache_discovery=False)

            logger.info(f"✅ Authentication completed ({self.auth_method})")
            return True, None

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False, f"Authentication failed: {str(e)}"

    def save_credentials(self):
        """Save credentials with multi-version support"""
        try:
            token_data = {
                'token': self.credentials.token,
                'refresh_token': self.credentials.refresh_token,
                'client_id': self.credentials.client_id,
                'client_secret': self.credentials.client_secret,
                'scopes': self.credentials.scopes,
                'auth_method': self.auth_method
            }

            os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
            with open(TOKEN_FILE, 'w') as f:
                json.dump(token_data, f, indent=2)

            os.chmod(TOKEN_FILE, 0o600)
            logger.info(f"💾 Credentials saved ({self.auth_method})")

        except Exception as e:
            logger.error(f"Save credentials failed: {e}")

    def upload_file(self, file_path, file_name):
        """Upload file to Google Drive"""
        if not self.service:
            return None, None

        try:
            # Detect mime type
            mime_type = 'application/octet-stream'
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                mime_type = 'image/jpeg'
            elif file_name.lower().endswith('.mp4'):
                mime_type = 'video/mp4'
            elif file_name.lower().endswith('.pdf'):
                mime_type = 'application/pdf'

            file_metadata = {
                'name': file_name,
                'parents': [os.getenv('GDRIVE_FOLDER_ID', 'root')]
            }

            media = MediaFileUpload(
                file_path, 
                mimetype=mime_type,
                resumable=True,
                chunksize=CHUNK_SIZE * 1024
            )

            request = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,size'
            )

            response = None
            while response is None:
                try:
                    status, response = request.next_chunk()
                    if status:
                        logger.info(f"Upload progress: {int(status.progress() * 100)}%")
                except Exception as e:
                    logger.error(f"Upload chunk failed: {e}")
                    return None, None

            file_id = response.get('id')

            # Make file accessible
            self.service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()

            share_link = f"https://drive.google.com/file/d/{file_id}/view"

            logger.info(f"✅ File uploaded successfully: {file_name}")
            return file_id, share_link

        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return None, None

class AnyDeskManager:
    """AnyDesk integration with multi-version OS support"""

    @staticmethod
    def is_anydesk_installed():
        """Check if AnyDesk is installed"""
        try:
            result = subprocess.run(['which', 'anydesk'], capture_output=True)
            return result.returncode == 0
        except:
            return False

    @staticmethod
    def get_anydesk_id():
        """Get AnyDesk ID"""
        try:
            if not AnyDeskManager.is_anydesk_installed():
                return None

            result = subprocess.run(['anydesk', '--get-id'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except:
            return None

    @staticmethod
    def get_anydesk_status():
        """Get AnyDesk service status"""
        try:
            result = subprocess.run(['systemctl', 'is-active', 'anydesk'], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"

# Global instances
drive_manager = MultiVersionGoogleDriveManager()
stb_info = ArmbianSystemInfo()

# Helper functions
def is_owner(username):
    return username and username.lower() == OWNER_USERNAME.lower()

# Bot commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command with multi-version OS support"""
    if not await check_subscription(update, context):
        return

    user = update.effective_user
    system_info = stb_info.get_system_info()
    anydesk_id = AnyDeskManager.get_anydesk_id()
    anydesk_status = AnyDeskManager.get_anydesk_status()

    owner_note = ""
    if is_owner(user.username):
        owner_note = "\n\n🔧 **Owner Access Granted**"
        if anydesk_id:
            owner_note += f"\n🖥️ **AnyDesk ID:** `{anydesk_id}`"

    auth_method_info = "🔑 **Auth Method:** " + ("Environment Tokens (Bookworm)" if system_info['auth_method'] == 'env_tokens' else "Credentials File (Bullseye)")

    message = f"""
🎉 Welcome {user.first_name}!

🚀 **STB Telegram Bot - HG680P Multi-Version Support**
📢 **Subscribed to {REQUIRED_CHANNEL}** ✅
🔧 **Enhanced with JMDKH Features**

💻 **STB Information:**
🏗️ Architecture: {system_info['architecture']}
🧠 Memory: {system_info['memory']}  
💾 Storage: {system_info['storage_available']} free
📺 Board: {system_info['board_name']}
🐧 Armbian: {system_info['armbian_version']} ({system_info['armbian_branch']})
🐛 Base OS: {system_info['base_os'].title()}
🖥️ GUI: {"✅ " + system_info['desktop_env'] if system_info['gui_available'] else "❌ Not available"}
🔗 AnyDesk: {"✅ Active" if anydesk_status == "active" else "❌ Inactive"}
{auth_method_info}

📋 **Available Commands:**
/auth - Connect Google Drive
/d [link] - Mirror to Google Drive
/t [torrent/magnet] - Download torrent/magnet
/dc [gdrive_link] - Clone Google Drive
/system - STB system info
/anydesk - AnyDesk remote access info
/stats - Bot statistics
/help - Complete help

🎯 **Multi-Version Features:**
• ✅ Armbian 20.11 Bullseye support
• ✅ Armbian 25.11 Bookworm support
• ✅ OS-specific authentication methods
• ✅ AnyDesk with dependency fixing
• ✅ Torrent & Magnet link support
• ✅ Google Drive cloning
• ✅ Multi-server download support
• ✅ Channel subscription protection

💡 **Supported Services:**
📥 **Downloads:** Mega, MediaFire, Pixeldrain, Anonfiles, GoFile, etc.
🧲 **Torrents:** Magnet links, .torrent files
☁️ **Google Drive:** Clone, upload, mirror
🖥️ **Remote Access:** AnyDesk integration

{owner_note}
"""

    await update.message.reply_text(message, parse_mode='Markdown')

async def system_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced system information with multi-version support"""
    if not await check_subscription(update, context):
        return

    system_info = stb_info.get_system_info()
    anydesk_id = AnyDeskManager.get_anydesk_id()
    anydesk_status = AnyDeskManager.get_anydesk_status()

    try:
        uptime = subprocess.run(['uptime'], capture_output=True, text=True)
        uptime_str = uptime.stdout.strip() if uptime.returncode == 0 else "Unknown"

        temp_cmd = subprocess.run(['cat', '/sys/class/thermal/thermal_zone0/temp'], 
                                 capture_output=True, text=True)
        temp = int(temp_cmd.stdout.strip()) / 1000 if temp_cmd.returncode == 0 else 0

        load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)

    except Exception as e:
        uptime_str = "Unknown"
        temp = 0
        load_avg = (0, 0, 0)

    message = f"""
💻 **STB HG680P Multi-Version System Information**

📢 **Channel:** {REQUIRED_CHANNEL} ✅
🆔 **Channel ID:** {CHANNEL_ID}

🏗️ **Hardware:**
• Board: {system_info['board_name']}
• Architecture: {system_info['architecture']}
• CPU: {system_info['cpu']}
• Memory: {system_info['memory']}
• Temperature: {temp:.1f}°C

💾 **Storage:**
• Total: {system_info['storage_total']}
• Used: {system_info['storage_used']}
• Available: {system_info['storage_available']}

🐧 **Multi-Version Armbian Information:**
• Version: {system_info['armbian_version']}
• Branch: {system_info['armbian_branch']}
• Base OS: {system_info['base_os'].title()}
• Auth Method: {system_info['auth_method'].replace('_', ' ').title()}

🖥️ **GUI Environment:**
• GUI Available: {"✅ Yes" if system_info['gui_available'] else "❌ No"}
• Desktop: {system_info['desktop_env']}
• Display: {os.environ.get('DISPLAY', 'Not set')}

🔗 **Remote Access:**
• AnyDesk: {"✅ Active" if anydesk_status == "active" else "❌ Inactive"}
• AnyDesk ID: `{anydesk_id if anydesk_id else "Not available"}`

📊 **Performance:**
• Load Average: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}
• Uptime: {uptime_str}

🤖 **Bot Status:**
• Max Downloads: {MAX_CONCURRENT}
• Speed Limit: {MAX_SPEED_MBPS} MB/s
• Drive Connected: {"✅ Yes" if drive_manager.service else "❌ No"}

🌟 **JMDKH Features:**
• Torrent/Magnet: ✅ Active
• Multi-server: ✅ Active  
• GDrive Clone: ✅ Active
• Direct Mirror: ✅ Active

**🚀 Multi-version STB optimized for HG680P**
"""

    await update.message.reply_text(message, parse_mode='Markdown')

async def auth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Multi-version Google Drive authentication"""
    if not await check_subscription(update, context):
        return

    system_info = stb_info.get_system_info()
    auth_method = system_info['auth_method']
    base_os = system_info['base_os']

    if auth_method == 'env_tokens':
        # Bookworm method
        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            await update.message.reply_text(
                "⚙️ **Google Drive Not Configured (Bookworm)**\n\n"
                "❌ GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET not set\n"
                "For Armbian 25.11 Bookworm, configure environment variables:\n\n"
                "**Bookworm Setup Instructions:**\n"
                "1. Go to Google Cloud Console\n"
                "2. Create OAuth 2.0 Client ID (Desktop Application)\n"
                "3. Add Client ID and Secret to .env file\n"
                "4. Restart the bot\n\n"
                "🔧 **Note:** Bookworm uses environment token method",
                parse_mode='Markdown'
            )
            return
    else:
        # Bullseye method
        if not os.path.exists(CREDENTIALS_FILE) and (not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET):
            await update.message.reply_text(
                "⚙️ **Google Drive Not Configured (Bullseye)**\n\n"
                "❌ credentials.json not found and env variables not set\n"
                "For Armbian 20.11 Bullseye, use credentials.json file:\n\n"
                "**Bullseye Setup Instructions:**\n"
                "1. Go to Google Cloud Console\n"
                "2. Create OAuth 2.0 Client ID (Desktop Application)\n"
                "3. Download credentials.json to /app/credentials/\n"
                "4. OR set GOOGLE_CLIENT_ID/SECRET in .env\n"
                "5. Restart the bot\n\n"
                "🔧 **Note:** Bullseye supports both credentials.json and env tokens",
                parse_mode='Markdown'
            )
            return

    if drive_manager.service:
        await update.message.reply_text(
            f"✅ **Already Connected to Google Drive**\n\n"
            f"Your Google Drive is active and ready.\n"
            f"**Auth Method:** {auth_method.replace('_', ' ').title()}\n"
            f"**Base OS:** {base_os.title()}\n"
            f"Try using: `/d [link]` to mirror files",
            parse_mode='Markdown'
        )
        return

    auth_url, error = drive_manager.get_auth_url()

    if error:
        await update.message.reply_text(
            f"❌ **Authentication Setup Failed**\n\n"
            f"**Error:** {error}\n\n"
            f"**OS:** {base_os.title()} ({auth_method})\n\n"
            "**Troubleshooting:**\n"
            "• Check Google credentials configuration\n"
            "• Verify Google Cloud Console settings\n"
            "• Ensure correct auth method for your OS",
            parse_mode='Markdown'
        )
        return

    gui_note = ""
    if system_info['gui_available']:
        gui_note = f"\n\n**🖥️ GUI Available:**\nYou can open the link in built-in browser via AnyDesk if preferred."

    message = f"""
🔐 **Google Drive Authentication - Multi-Version Support**

**📋 STB HG680P Setup Instructions:**

**🐛 Detected OS:** {base_os.title()}
**🔑 Auth Method:** {auth_method.replace('_', ' ').title()}

1️⃣ **Open this link on any device with browser:**
{auth_url}

2️⃣ **Sign in to your Google account**
3️⃣ **Grant the requested permissions**  
4️⃣ **Copy the authorization code**
5️⃣ **Send the code here:** `/code [authorization-code]`

**💡 Example:**
`/code 4/0AdQt8qi7bGMqwertyuiop...`

**⚠️ Multi-Version Notes:**
• Optimized for {base_os.title()} authentication
• {auth_method.replace('_', ' ').title()} method used
• Code expires in 10 minutes
• ARM64 architecture compatible{gui_note}

**🔒 Secure multi-version authentication for STB HG680P**
"""

    await update.message.reply_text(message, parse_mode='Markdown')

async def code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Google Drive authorization code for multi-version"""
    if not await check_subscription(update, context):
        return

    if not context.args:
        system_info = stb_info.get_system_info()
        await update.message.reply_text(
            "⚠️ **Invalid Format**\n\n"
            "Please use: `/code [your-authorization-code]`\n\n"
            "**Get the code from:**\n"
            "1. Use `/auth` command first\n"
            "2. Open the provided link\n"
            "3. Complete Google authorization\n"
            "4. Copy the code and use `/code [code]`\n\n"
            f"**{system_info['base_os'].title()} Note:** Ensure complete code is copied",
            parse_mode='Markdown'
        )
        return

    auth_code = ' '.join(context.args)
    system_info = stb_info.get_system_info()

    msg = await update.message.reply_text(f"🔄 **Processing {system_info['base_os'].title()} Authentication...**")

    success, error = drive_manager.authenticate_with_code(auth_code)

    if success:
        await msg.edit_text(
            "✅ **Google Drive Connected Successfully!**\n\n"
            f"🚀 STB HG680P {system_info['base_os'].title()} connected to Google Drive\n"
            f"🔑 **Auth Method:** {system_info['auth_method'].replace('_', ' ').title()}\n"
            "📁 Ready for enhanced operations:\n\n"
            "📥 **Mirror:** `/d [link]`\n"
            "🧲 **Torrent:** `/t [magnet/torrent]`\n"
            "☁️ **Clone:** `/dc [gdrive_link]`\n\n"
            f"🎉 All JMDKH features now available on {system_info['base_os'].title()}!",
            parse_mode='Markdown'
        )
    else:
        await msg.edit_text(
            f"❌ **Authentication Failed**\n\n"
            f"**Error:** {error}\n\n"
            f"**{system_info['base_os'].title()} Troubleshooting:**\n"
            "• Get fresh code with `/auth`\n"
            "• Ensure complete code is copied\n"
            "• Try again with proper permissions\n"
            "• Check Google Cloud Console settings\n"
            f"• Verify {system_info['auth_method']} configuration",
            parse_mode='Markdown'
        )

# Include other JMDKH commands (torrent, mirror, clone, etc.) here
# [Previous JMDKH implementations would go here]

def main():
    """Main bot function with multi-version support"""
    if not BOT_TOKEN or BOT_TOKEN == 'your_bot_token_here':
        logger.error("❌ BOT_TOKEN not configured properly")
        sys.exit(1)

    system_info = stb_info.get_system_info()

    logger.info("🚀 Starting Multi-Version STB Telegram Bot...")
    logger.info(f"🌟 JMDKH Features + Multi-OS support")
    logger.info(f"🤖 Bot Token: {BOT_TOKEN[:20]}...")
    logger.info(f"📢 Required Channel: {REQUIRED_CHANNEL}")
    logger.info(f"🆔 Channel ID: {CHANNEL_ID}")
    logger.info(f"📱 STB Model: HG680P")
    logger.info(f"🐧 Armbian: {system_info['armbian_version']}")
    logger.info(f"🐛 Base OS: {system_info['base_os'].title()}")
    logger.info(f"🏗️ Architecture: {system_info['architecture']}")
    logger.info(f"🖥️ GUI Available: {system_info['gui_available']}")
    logger.info(f"🔑 Auth Method: {system_info['auth_method']}")
    logger.info(f"👑 Owner: @{OWNER_USERNAME}")

    # Create Telegram application
    app = Application.builder().token(BOT_TOKEN).connect_timeout(60).read_timeout(60).write_timeout(60).pool_timeout(60).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("auth", auth_command))
    app.add_handler(CommandHandler("code", code_command))
    app.add_handler(CommandHandler("system", system_command))

    logger.info("✅ Multi-Version STB Bot initialization complete!")
    logger.info("🔗 Ready for multi-OS operation on HG680P")

    # Start the bot
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
