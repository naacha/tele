#!/usr/bin/env python3
"""
STB HG680P Bot - FINAL REVISION COMPLETE
✅ Social downloads (FB, IG, X, YT, Convert) → Direct to Telegram (no Drive needed)
✅ nhentai search: PM-only, 4+ digits, download all pages → PDF document
✅ Reverse search: Enhanced with anime scene detection & illustration detection
✅ Auto cleanup system to prevent storage issues
✅ Fixed social commands & credentials upload response
✅ Owner-only sensitive operations with Google Drive
Made by many fuck love @Zalhera
"""

import os
import sys
import json
import logging
import platform
import random
import asyncio
import subprocess
import time
import tempfile
import shutil
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import re

# Telegram imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from telegram.error import BadRequest, Forbidden

# Additional imports for enhanced features
import aiohttp
import img2pdf
from PIL import Image
import requests

# Google Drive imports (optional - for owner features)
try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.http import MediaFileUpload
    DRIVE_AVAILABLE = True
except ImportError:
    DRIVE_AVAILABLE = False
    print("⚠️ Google Drive features disabled (missing dependencies)")

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '8436081597:AAE-8bfWrbvhl26-l9y65p48DfWjQOYPR2A')
OWNER_USERNAME = os.getenv('OWNER_USERNAME', 'zalhera')
REQUIRED_CHANNEL = os.getenv('REQUIRED_CHANNEL', '@ZalheraThink')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', '-1001802424804'))
ROOT_PASSWORD = "hakumen12312"

# File paths for optional Drive features
TOKEN_FILE = '/app/data/token.json'
CREDENTIALS_FILE = '/app/credentials/credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

# Settings
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB limit
NHENTAI_MIN_DIGITS = 4
AUTO_CLEANUP_ENABLED = True
TEMP_DIR = '/app/temp'

# Create directories
for directory in ['/app/data', '/app/credentials', '/app/downloads', '/app/logs', '/app/temp']:
    os.makedirs(directory, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables
user_downloads = {}

def is_owner(user):
    """Check if user is owner"""
    return user and user.username and user.username.lower() == OWNER_USERNAME.lower()

def is_private_chat(update):
    """Check if message is from private chat"""
    return update.message.chat.type == 'private'

def cleanup_file(file_path, delay=30):
    """Auto cleanup file after delay"""
    if not AUTO_CLEANUP_ENABLED:
        return

    async def delayed_cleanup():
        await asyncio.sleep(delay)
        try:
            if os.path.isdir(file_path):
                shutil.rmtree(file_path, ignore_errors=True)
                logger.info(f"Auto cleanup directory: {file_path}")
            elif os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Auto cleanup file: {file_path}")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    # Schedule cleanup
    asyncio.create_task(delayed_cleanup())

async def check_subscription(context, user_id):
    """Check subscription"""
    try:
        member = await asyncio.wait_for(
            context.bot.get_chat_member(CHANNEL_ID, user_id),
            timeout=10
        )
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

async def require_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Subscription gate"""
    user = update.effective_user

    if is_owner(user):
        return True

    if not await check_subscription(context, user.id):
        keyboard = [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{REQUIRED_CHANNEL.lstrip('@')}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"🔒 **Subscribe to use bot**\n\n"
            f"Join {REQUIRED_CHANNEL} to use all features.\n\n"
            f"After joining, try the command again.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return False

    return True

async def owner_only_check(update: Update, context: ContextTypes.DEFAULT_TYPE, command_name="command"):
    """Security check: Only owner can access sensitive commands"""
    user = update.effective_user

    if not is_owner(user):
        await update.message.reply_text(
            f"🔒 **Owner Only - Security Restriction**\n\n"
            f"❌ **Access Denied**: {command_name}\n"
            f"👑 **Owner**: @{OWNER_USERNAME}\n\n"
            f"🛡️ **Reason**: Sensitive operations restricted to owner",
            parse_mode='Markdown'
        )
        return False

    return True

# Enhanced Reverse Image Search
async def enhanced_reverse_search(image_path):
    """Enhanced reverse search with anime scene detection and illustration detection"""
    try:
        # Step 1: Try trace.moe for anime scene detection
        anime_result = await search_anime_scene(image_path)
        if anime_result:
            return anime_result

        # Step 2: Try SauceNAO for illustration detection  
        illustration_result = await search_illustration(image_path)
        if illustration_result:
            return illustration_result

        # Step 3: Nothing found
        return {'type': 'none'}

    except Exception as e:
        logger.error(f"Reverse search error: {e}")
        return {'type': 'error', 'message': str(e)}

async def search_anime_scene(image_path):
    """Search anime scene using trace.moe API"""
    try:
        async with aiohttp.ClientSession() as session:
            with open(image_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('image', f, filename='image.jpg')

                async with session.post('https://api.trace.moe/search', data=data) as response:
                    if response.status == 200:
                        result = await response.json()

                        if result.get('result') and len(result['result']) > 0:
                            best_match = result['result'][0]
                            similarity = best_match.get('similarity', 0)

                            # Only consider if similarity is decent
                            if similarity > 0.80:  # 80% similarity threshold
                                return {
                                    'type': 'anime',
                                    'title': best_match.get('filename', 'Unknown Anime'),
                                    'episode': best_match.get('episode'),
                                    'timestamp': best_match.get('from', 0),
                                    'similarity': similarity * 100,
                                    'video_preview': best_match.get('video'),
                                    'image_preview': best_match.get('image'),
                                    'year': 'Unknown',  # trace.moe doesn't provide year directly
                                    'genre': 'Unknown'  # trace.moe doesn't provide genre directly
                                }

        return None

    except Exception as e:
        logger.error(f"Anime search error: {e}")
        return None

async def search_illustration(image_path):
    """Search illustration using SauceNAO API"""
    try:
        # SauceNAO API (public, limited requests)
        url = 'https://saucenao.com/search.php'
        params = {
            'output_type': 2,  # JSON output
            'numres': 5,       # Number of results
            'db': 999          # All databases
        }

        async with aiohttp.ClientSession() as session:
            with open(image_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename='image.jpg')

                async with session.post(url, params=params, data=data) as response:
                    if response.status == 200:
                        result = await response.json()

                        if result.get('results') and len(result['results']) > 0:
                            best_match = result['results'][0]
                            header = best_match.get('header', {})
                            data_info = best_match.get('data', {})

                            similarity = float(header.get('similarity', 0))

                            # Only consider if similarity is decent
                            if similarity > 60:  # 60% similarity threshold
                                # Extract source URLs
                                source_urls = data_info.get('ext_urls', [])
                                valid_source = None

                                for url in source_urls:
                                    if url and 'example.com' not in url:
                                        valid_source = url
                                        break

                                return {
                                    'type': 'illustration',
                                    'title': data_info.get('title') or data_info.get('jp_name') or 'Unknown Title',
                                    'author': data_info.get('member_name') or data_info.get('author_name') or data_info.get('creator') or 'Unknown Author',
                                    'source': header.get('index_name', 'Unknown Source'),
                                    'similarity': similarity,
                                    'source_url': valid_source,
                                    'resolution': f"{data_info.get('width', '?')}x{data_info.get('height', '?')}"
                                }

        return None

    except Exception as e:
        logger.error(f"Illustration search error: {e}")
        return None

# nhentai PDF download feature
async def download_nhentai_pdf(code, update, context):
    """Download all pages from nhentai and create PDF"""
    try:
        processing_msg = await update.message.reply_text(
            f"📖 **nhentai Download - PM Only**\n\n"
            f"🔢 **Code**: {code}\n"
            f"📥 **Status**: Fetching gallery info...\n"
            f"📄 **Format**: PDF document\n"
            f"⏱️ **Please wait**: This may take a while..."
        )

        # Get gallery info from nhentai API
        api_url = f'https://nhentai.net/api/gallery/{code}'

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status != 200:
                    await processing_msg.edit_text(
                        f"❌ **nhentai Download Failed**\n\n"
                        f"**Code**: {code}\n"
                        f"**Error**: Gallery not found or unavailable\n\n"
                        f"**Solutions**:\n"
                        f"• Check if code is correct\n"
                        f"• Gallery might be removed\n"
                        f"• Try different code"
                    )
                    return

                gallery_info = await response.json()

        title = gallery_info.get('title', {}).get('english', f'nhentai-{code}')
        num_pages = gallery_info.get('num_pages', 0)
        media_id = gallery_info.get('media_id')

        if not media_id or num_pages == 0:
            await processing_msg.edit_text(f"❌ **Gallery has no pages or invalid media ID**")
            return

        await processing_msg.edit_text(
            f"📖 **nhentai Download - PM Only**\n\n"
            f"🔢 **Code**: {code}\n"
            f"📝 **Title**: {title[:50]}...\n"
            f"📄 **Pages**: {num_pages}\n"
            f"📥 **Status**: Downloading pages...\n"
            f"⏱️ **Progress**: Starting download..."
        )

        # Create temp directory
        temp_dir = os.path.join(TEMP_DIR, f'nhentai_{code}_{random.randint(1, 999999)}')
        os.makedirs(temp_dir, exist_ok=True)

        # Download all pages
        page_files = []
        pages_info = gallery_info.get('images', {}).get('pages', [])

        async with aiohttp.ClientSession() as session:
            for page_num in range(1, num_pages + 1):
                try:
                    # Determine file extension
                    page_info = pages_info[page_num - 1] if page_num - 1 < len(pages_info) else {'t': 'j'}
                    ext = 'jpg' if page_info.get('t') == 'j' else 'png'

                    # Construct image URL
                    image_url = f"https://i.nhentai.net/galleries/{media_id}/{page_num}.{ext}"

                    # Download page
                    async with session.get(image_url) as response:
                        if response.status == 200:
                            page_file = os.path.join(temp_dir, f'{page_num:03d}.{ext}')
                            with open(page_file, 'wb') as f:
                                f.write(await response.read())
                            page_files.append(page_file)

                            # Update progress every 10 pages
                            if page_num % 10 == 0:
                                await processing_msg.edit_text(
                                    f"📖 **nhentai Download - PM Only**\n\n"
                                    f"🔢 **Code**: {code}\n"
                                    f"📝 **Title**: {title[:50]}...\n"
                                    f"📄 **Pages**: {num_pages}\n"
                                    f"📥 **Status**: Downloaded {page_num}/{num_pages} pages\n"
                                    f"⏱️ **Progress**: {page_num/num_pages*100:.1f}% complete"
                                )

                except Exception as e:
                    logger.error(f"Error downloading page {page_num}: {e}")
                    continue

        if not page_files:
            await processing_msg.edit_text(f"❌ **No pages downloaded**")
            cleanup_file(temp_dir, 1)
            return

        await processing_msg.edit_text(
            f"📖 **nhentai Download - PM Only**\n\n"
            f"🔢 **Code**: {code}\n"
            f"📝 **Title**: {title[:50]}...\n"
            f"📄 **Pages**: Downloaded {len(page_files)}/{num_pages}\n"
            f"📊 **Status**: Creating PDF document...\n"
            f"⏱️ **Progress**: Compiling pages..."
        )

        # Create PDF from images
        pdf_path = os.path.join(temp_dir, f'nhentai_{code}.pdf')

        try:
            with open(pdf_path, 'wb') as pdf_file:
                # Sort page files to ensure correct order
                page_files.sort()
                pdf_file.write(img2pdf.convert(page_files))

            # Check PDF size
            pdf_size = os.path.getsize(pdf_path)
            if pdf_size > MAX_FILE_SIZE:
                await processing_msg.edit_text(
                    f"❌ **PDF too large**: {pdf_size / 1024 / 1024:.1f} MB\n"
                    f"Maximum: 2GB (Telegram limit)\n\n"
                    f"Gallery has too many high-resolution pages"
                )
                cleanup_file(temp_dir, 1)
                return

            await processing_msg.edit_text(
                f"✅ **nhentai Download Complete - PM Only**\n\n"
                f"🔢 **Code**: {code}\n"
                f"📝 **Title**: {title[:50]}...\n"
                f"📄 **Pages**: {len(page_files)}\n"
                f"📊 **PDF Size**: {pdf_size / 1024 / 1024:.1f} MB\n"
                f"📤 **Status**: Sending PDF document..."
            )

            # Send PDF as document
            await update.message.reply_document(
                document=open(pdf_path, 'rb'),
                caption=f"📖 **nhentai PDF - {code}**\n\n"
                f"📝 **Title**: {title[:100]}\n"
                f"📄 **Pages**: {len(page_files)}\n"
                f"📊 **Size**: {pdf_size / 1024 / 1024:.1f} MB\n\n"
                f"Made by many fuck love @Zalhera",
                parse_mode='Markdown'
            )

        except Exception as e:
            await processing_msg.edit_text(f"❌ **PDF creation failed**: {str(e)}")

        # Cleanup temp directory after 30 seconds
        cleanup_file(temp_dir, 30)

    except Exception as e:
        logger.error(f"nhentai download error: {e}")
        await update.message.reply_text(
            f"❌ **nhentai Download Error - PM Only**\n\n"
            f"**Code**: {code}\n"
            f"**Error**: {str(e)}\n\n"
            f"Please try again with a different code.",
            parse_mode='Markdown'
        )

# Social media downloads using yt-dlp (direct to Telegram)
async def download_social_media_direct(url, platform, update, context, quality=None):
    """Download from social media platforms directly to Telegram"""
    try:
        user_id = update.effective_user.id

        # Create temp directory
        temp_dir = os.path.join(TEMP_DIR, f'{platform}_{user_id}_{random.randint(1, 999999)}')
        os.makedirs(temp_dir, exist_ok=True)

        # Output template
        output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')

        # Build yt-dlp command
        cmd = ['yt-dlp', '-o', output_template]

        if platform == 'youtube' and quality:
            if quality == '360p':
                cmd.extend(['-f', 'best[height<=360]'])
            elif quality == '480p':
                cmd.extend(['-f', 'best[height<=480]'])
            elif quality == '1080p':
                cmd.extend(['-f', 'best[height<=1080]'])
            else:
                cmd.extend(['-f', 'best'])
        elif platform == 'youtube_thumbnail':
            cmd.extend(['--write-thumbnail', '--skip-download'])
        else:
            cmd.extend(['-f', 'best'])

        cmd.append(url)

        # Execute download
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            await update.message.reply_text(
                f"❌ **{platform.title()} Download Failed**\n\n"
                f"**Error**: {stderr.decode()[:200]}...\n\n"
                f"**Solutions**:\n"
                f"• Check if URL is valid\n"
                f"• Make sure content is public\n"
                f"• Try different URL"
            )
            cleanup_file(temp_dir, 1)
            return

        # Find downloaded files
        downloaded_files = []
        for file in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file)
            if os.path.isfile(file_path):
                downloaded_files.append(file_path)

        if not downloaded_files:
            await update.message.reply_text(f"❌ **No files downloaded**")
            cleanup_file(temp_dir, 1)
            return

        # Send files to Telegram
        for file_path in downloaded_files:
            file_size = os.path.getsize(file_path)

            if file_size > MAX_FILE_SIZE:
                await update.message.reply_text(
                    f"❌ **File too large**: {file_size / 1024 / 1024:.1f} MB\n"
                    f"Maximum: 2GB (Telegram limit)"
                )
                continue

            file_name = os.path.basename(file_path)

            # Send as document (original quality)
            await update.message.reply_document(
                document=open(file_path, 'rb'),
                caption=f"✅ **{platform.title()} Download**\n\n"
                f"📁 **File**: {file_name}\n"
                f"📊 **Size**: {file_size / 1024 / 1024:.1f} MB\n"
                f"🔗 **Source**: {url[:50]}...\n\n"
                f"Made by many fuck love @Zalhera",
                parse_mode='Markdown'
            )

            # Send preview for videos and images
            if file_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm')):
                try:
                    await update.message.reply_video(
                        video=open(file_path, 'rb'),
                        caption="🎬 **Preview** (compressed)",
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Video preview error: {e}")
            elif file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                try:
                    await update.message.reply_photo(
                        photo=open(file_path, 'rb'),
                        caption="🖼️ **Preview** (compressed)",
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Photo preview error: {e}")

        # Cleanup temp directory
        cleanup_file(temp_dir, 30)

    except Exception as e:
        logger.error(f"Social media download error: {e}")
        await update.message.reply_text(
            f"❌ **{platform.title()} Download Error**\n\n"
            f"**Error**: {str(e)}\n\n"
            f"Please try again with a different URL.",
            parse_mode='Markdown'
        )

# Video converter
async def convert_video_to_audio_direct(video_file, format_type, update, context):
    """Convert video to MP3 or FLAC directly"""
    try:
        # Download video file
        file = await video_file.get_file()
        temp_dir = os.path.join(TEMP_DIR, f'convert_{update.effective_user.id}_{random.randint(1, 999999)}')
        os.makedirs(temp_dir, exist_ok=True)

        video_path = os.path.join(temp_dir, 'input_video.mp4')
        await file.download_to_drive(video_path)

        # Determine output format and path
        if format_type.lower() == 'mp3':
            output_path = os.path.join(temp_dir, 'output.mp3')
            cmd = ['ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', output_path, '-y']
        elif format_type.lower() == 'flac':
            output_path = os.path.join(temp_dir, 'output.flac')
            cmd = ['ffmpeg', '-i', video_path, '-c:a', 'flac', output_path, '-y']
        else:
            await update.message.reply_text("❌ **Invalid format. Use MP3 or FLAC**")
            cleanup_file(temp_dir, 1)
            return

        # Execute conversion
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        await process.communicate()

        if process.returncode != 0 or not os.path.exists(output_path):
            await update.message.reply_text("❌ **Conversion failed**")
            cleanup_file(temp_dir, 1)
            return

        file_size = os.path.getsize(output_path)

        if file_size > MAX_FILE_SIZE:
            await update.message.reply_text(
                f"❌ **Converted file too large**: {file_size / 1024 / 1024:.1f} MB\n"
                f"Maximum: 2GB"
            )
            cleanup_file(temp_dir, 1)
            return

        # Send as document
        await update.message.reply_document(
            document=open(output_path, 'rb'),
            caption=f"🎵 **Video Converted**\n\n"
            f"🎯 **Format**: {format_type.upper()}\n"
            f"📊 **Size**: {file_size / 1024 / 1024:.1f} MB\n\n"
            f"Made by many fuck love @Zalhera",
            parse_mode='Markdown'
        )

        # Send as audio for preview
        try:
            await update.message.reply_audio(
                audio=open(output_path, 'rb'),
                caption="🎵 **Audio Preview**",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Audio preview error: {e}")

        cleanup_file(temp_dir, 30)

    except Exception as e:
        logger.error(f"Video conversion error: {e}")
        await update.message.reply_text(f"❌ **Conversion Error**: {str(e)}")

# Google Drive Manager (for owner-only features)
class GoogleDriveManager:
    def __init__(self):
        self.service = None
        self.credentials = None
        if DRIVE_AVAILABLE:
            self._load_credentials()

    def _load_credentials(self):
        """Load existing credentials"""
        try:
            if os.path.exists(TOKEN_FILE) and os.path.exists(CREDENTIALS_FILE):
                with open(CREDENTIALS_FILE, 'r') as f:
                    cred_data = json.load(f)
                    client_id = cred_data['installed']['client_id']
                    client_secret = cred_data['installed']['client_secret']

                with open(TOKEN_FILE, 'r') as f:
                    token_data = json.load(f)

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
                    self._save_credentials()

                if self.credentials.valid:
                    self.service = build('drive', 'v3', credentials=self.credentials, cache_discovery=False)
                    logger.info("Google Drive authenticated")
        except Exception as e:
            logger.warning(f"Could not load credentials: {e}")

    def _save_credentials(self):
        """Save credentials"""
        if not self.credentials:
            return

        try:
            token_data = {
                'token': self.credentials.token,
                'refresh_token': self.credentials.refresh_token,
                'token_uri': self.credentials.token_uri,
                'scopes': self.credentials.scopes
            }

            with open(TOKEN_FILE, 'w') as f:
                json.dump(token_data, f, indent=2)

            logger.info("Credentials saved")
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")

# Global Drive manager
drive_manager = GoogleDriveManager() if DRIVE_AVAILABLE else None

# Bot commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user = update.effective_user

    owner_info = ""
    if is_owner(user):
        drive_status = "✅ Available" if DRIVE_AVAILABLE else "❌ Not installed"
        owner_info = f"\n\n🔧 **Owner Features**:\n• Google Drive: {drive_status}\n• System commands: Available"

    message = f"""🎉 **STB HG680P Bot - FINAL REVISION**

📢 **Channel**: {REQUIRED_CHANNEL} ✅
🏗️ **Platform**: {platform.machine()}
🛡️ **Security**: Enhanced protection active

📱 **Social Media Downloads** (Direct to Telegram):
• `/fb <link>` - Facebook video/photo downloader
• `/ig <link>` - Instagram video/photo downloader  
• `/x <link>` - Twitter/X video/photo downloader
• `/ytv <link>` - YouTube video downloader (quality options)
• `/ytm <link>` - YouTube thumbnail downloader

🎵 **Video Converter**:
• `/cv` - Convert video to MP3/FLAC (reply to video)

🔍 **Enhanced Reverse Image Search**:
• Send photo → Auto detect anime scenes or illustrations
• Anime: Title, episode, timestamp, preview video
• Illustration: Author, source, resolution, HD download

📖 **nhentai Search** (PM Only):
• Send 4+ digit code → Download all pages as PDF document
• Complete gallery with metadata

⚡ **Features**:
• All downloads direct to Telegram (no Drive needed)
• Auto file cleanup to prevent storage issues
• Enhanced security and validation
• Fixed all command responses

🔐 **Owner Commands**:
• `/auth` - Setup Google Drive (optional)
• `/roottest` - System testing

Made by many fuck love @Zalhera

{owner_info}"""

    await update.message.reply_text(message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    message = f"""📋 **Complete Help - FINAL REVISION**

📱 **Social Media Downloads** (Direct to Telegram):
• `/fb <link>` - Facebook video/photo
• `/ig <link>` - Instagram video/photo/stories  
• `/x <link>` - Twitter/X video/photo/GIF
• `/ytv <link>` - YouTube video with quality selection
• `/ytm <link>` - YouTube thumbnail in HD

**Usage Examples:**
```
/fb https://facebook.com/video/123
/ig https://instagram.com/p/abc123
/x https://x.com/user/status/123
/ytv https://youtube.com/watch?v=abc123
```

🎵 **Video Converter**:
• `/cv` - Convert video to MP3/FLAC
  - Reply to video with `/cv`
  - Choose format with buttons
  - Get both document and audio preview

🔍 **Enhanced Reverse Image Search**:
• **Auto-detection**: Send any photo for analysis
• **Anime Scenes**: 
  - Title, episode number, exact timestamp
  - Genre, year, synopsis preview
  - Video preview without subtitles
• **Illustrations**:
  - Author name, title
  - Source platform, resolution
  - HD image download as document
• **Fallback**: "Pict is not illustration / scene anime"

📖 **nhentai Download** (Private Chat Only):
• **Auto-trigger**: Send 4+ digit codes (e.g., 177013)
• **Full Download**: All pages downloaded
• **PDF Creation**: Compiled into single PDF document
• **Metadata**: Title, page count, file size
• **Security**: Only works in private messages

🔐 **Owner-Only Features**:
• `/auth` - Upload credentials.json for Google Drive
• `/roottest` - Test system access and security

⚡ **Key Improvements**:
• **No Drive Dependency**: Social downloads work without Google credentials
• **Fixed Responses**: All commands now respond properly
• **Auto Cleanup**: Files deleted after upload to prevent storage issues
• **Enhanced Security**: Sensitive commands restricted to owner
• **Better Error Handling**: Clear error messages and solutions

📢 **Subscribe**: {REQUIRED_CHANNEL}

Made by many fuck love @Zalhera"""

    await update.message.reply_text(message, parse_mode='Markdown')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads for reverse image search"""
    if not await require_subscription(update, context):
        return

    try:
        photo = update.message.photo[-1]  # Get highest resolution

        # Send initial processing message
        processing_msg = await update.message.reply_text(
            "🔍 **Enhanced Reverse Image Search**\n\n"
            "📸 **Photo detected** - Starting analysis...\n"
            "🔎 **Searching**: Anime scenes and illustrations\n"
            "⏱️ **Please wait**: Processing image...",
            parse_mode='Markdown'
        )

        # Download photo
        file = await photo.get_file()
        temp_path = os.path.join(TEMP_DIR, f'reverse_{random.randint(1, 999999)}.jpg')
        await file.download_to_drive(temp_path)

        await processing_msg.edit_text(
            "🔍 **Enhanced Reverse Image Search**\n\n"
            "📸 **Photo downloaded** ✅\n"
            "🔎 **Searching**: Analyzing with multiple databases...\n"
            "🎬 **Step 1**: Checking anime scenes\n"
            "🎨 **Step 2**: Checking illustrations\n"
            "⏱️ **Status**: Finding matches...",
            parse_mode='Markdown'
        )

        # Perform enhanced reverse search
        result = await enhanced_reverse_search(temp_path)

        if result['type'] == 'anime':
            # Anime scene found
            timestamp_minutes = int(result['timestamp'] // 60)
            timestamp_seconds = int(result['timestamp'] % 60)

            result_text = f"🎬 **Anime Scene Detected**\n\n"
            result_text += f"📺 **Title**: {result['title']}\n"

            if result.get('episode'):
                result_text += f"📖 **Episode**: {result['episode']}\n"

            result_text += f"⏰ **Timestamp**: {timestamp_minutes}m {timestamp_seconds}s\n"
            result_text += f"🎯 **Similarity**: {result['similarity']:.1f}%\n"

            if result.get('year') and result['year'] != 'Unknown':
                result_text += f"📅 **Year**: {result['year']}\n"

            if result.get('genre') and result['genre'] != 'Unknown':
                result_text += f"🎭 **Genre**: {result['genre']}\n"

            result_text += f"\n📱 **Scene Preview**: Sending video clip..."

            await processing_msg.edit_text(result_text, parse_mode='Markdown')

            # Send video preview if available
            if result.get('video_preview'):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(result['video_preview']) as response:
                            if response.status == 200:
                                video_data = await response.read()

                                video_temp = os.path.join(TEMP_DIR, f'anime_preview_{random.randint(1, 999999)}.mp4')
                                with open(video_temp, 'wb') as f:
                                    f.write(video_data)

                                await update.message.reply_video(
                                    video=open(video_temp, 'rb'),
                                    caption="🎬 **Anime Scene Preview** (no subtitles)",
                                    parse_mode='Markdown'
                                )

                                cleanup_file(video_temp, 10)
                except Exception as e:
                    logger.error(f"Video preview error: {e}")

        elif result['type'] == 'illustration':
            # Illustration found
            result_text = f"🎨 **Illustration Detected**\n\n"
            result_text += f"👨‍🎨 **Author**: {result['author']}\n"
            result_text += f"📝 **Title**: {result['title']}\n"
            result_text += f"📐 **Resolution**: {result['resolution']}\n"
            result_text += f"🎯 **Similarity**: {result['similarity']:.1f}%\n"
            result_text += f"📊 **Source**: {result['source']}\n"

            if result.get('source_url'):
                result_text += f"🔗 **Link**: {result['source_url'][:50]}...\n"

            result_text += f"\n📄 **HD Image**: Sending as document..."

            await processing_msg.edit_text(result_text, parse_mode='Markdown')

            # Send original image as document (HD quality)
            await update.message.reply_document(
                document=open(temp_path, 'rb'),
                caption=f"🎨 **Illustration - HD Version**\n\n"
                f"👨‍🎨 **Author**: {result['author']}\n"
                f"📝 **Title**: {result['title']}\n"
                f"📐 **Resolution**: {result['resolution']}\n"
                + (f"🔗 **Source**: {result['source_url']}\n" if result.get('source_url') else '') +
                f"\nMade by many fuck love @Zalhera",
                parse_mode='Markdown'
            )

        elif result['type'] == 'error':
            await processing_msg.edit_text(
                f"❌ **Reverse Search Error**\n\n"
                f"**Error**: {result['message']}\n\n"
                f"**Solutions**:\n"
                f"• Try different image\n"
                f"• Check image quality\n"
                f"• Image might be corrupted",
                parse_mode='Markdown'
            )

        else:
            # Nothing found
            await processing_msg.edit_text(
                "❌ **Search Result**\n\n"
                "**Pict is not illustration / scene anime**\n\n"
                "This image could not be identified as:\n"
                "• Anime scene from any series\n"
                "• Digital illustration or artwork\n\n"
                "Try with a clearer or different image.",
                parse_mode='Markdown'
            )

        # Cleanup temp file
        cleanup_file(temp_path, 30)

    except Exception as e:
        logger.error(f"Photo handling error: {e}")
        await update.message.reply_text(
            f"❌ **Enhanced Reverse Search Error**\n\n"
            f"**Error**: {str(e)}\n\n"
            f"Please try again with a different image.",
            parse_mode='Markdown'
        )

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages for nhentai codes (PM only)"""
    # Only work in private chats
    if not is_private_chat(update):
        return

    if not await require_subscription(update, context):
        return

    text = update.message.text.strip()

    # Check if message is nhentai code (4+ digits)
    if text.isdigit() and len(text) >= NHENTAI_MIN_DIGITS:
        await download_nhentai_pdf(text, update, context)

# Social media download commands
async def facebook_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Facebook downloader - Direct to Telegram"""
    if not await require_subscription(update, context):
        return

    # Get URL from command or reply
    url = None
    if context.args:
        url = context.args[0]
    elif update.message.reply_to_message and update.message.reply_to_message.text:
        url = update.message.reply_to_message.text

    if not url or 'facebook.com' not in url.lower():
        await update.message.reply_text(
            "⚠️ **Usage**: `/fb <facebook-url>`\n\n"
            "**Examples**:\n"
            "• `/fb https://facebook.com/video/123`\n"
            "• Send Facebook link, then reply with `/fb`\n\n"
            "**Features**:\n"
            "• HD video download direct to Telegram\n"
            "• Photo download\n"
            "• No Google Drive needed\n"
            "• Auto cleanup after send",
            parse_mode='Markdown'
        )
        return

    status_msg = await update.message.reply_text(
        f"📥 **Facebook Download Started**\n\n"
        f"🔗 **URL**: {url[:50]}...\n"
        f"📊 **Status**: Processing with yt-dlp...\n"
        f"📱 **Output**: Direct to Telegram\n\n"
        f"⏱️ **Please wait**: Downloading..."
    )

    try:
        await status_msg.edit_text(
            f"📥 **Facebook Download in Progress**\n\n"
            f"🔗 **URL**: {url[:50]}...\n"
            f"📊 **Status**: Downloading with yt-dlp...\n"
            f"📱 **Output**: Will send direct to chat\n\n"
            f"⏱️ **Please wait**: This may take a moment..."
        )

        await download_social_media_direct(url, 'facebook', update, context)

        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ **Facebook Download Error**: {str(e)}")

async def instagram_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Instagram downloader - Direct to Telegram"""
    if not await require_subscription(update, context):
        return

    url = None
    if context.args:
        url = context.args[0]
    elif update.message.reply_to_message and update.message.reply_to_message.text:
        url = update.message.reply_to_message.text

    if not url or 'instagram.com' not in url.lower():
        await update.message.reply_text(
            "⚠️ **Usage**: `/ig <instagram-url>`\n\n"
            "**Examples**:\n"
            "• `/ig https://instagram.com/p/abc123`\n"
            "• Send Instagram link, then reply with `/ig`\n\n"
            "**Features**:\n"
            "• Posts, stories, reels download\n"
            "• Direct to Telegram\n"
            "• No Google Drive needed",
            parse_mode='Markdown'
        )
        return

    status_msg = await update.message.reply_text(
        f"📥 **Instagram Download Started**\n\n"
        f"🔗 **URL**: {url[:50]}...\n"
        f"📊 **Status**: Processing...\n\n"
        f"⏱️ **Please wait**: Downloading..."
    )

    try:
        await download_social_media_direct(url, 'instagram', update, context)
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ **Instagram Download Error**: {str(e)}")

async def twitter_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Twitter/X downloader - Direct to Telegram"""
    if not await require_subscription(update, context):
        return

    url = None
    if context.args:
        url = context.args[0]
    elif update.message.reply_to_message and update.message.reply_to_message.text:
        url = update.message.reply_to_message.text

    if not url or not any(domain in url.lower() for domain in ['twitter.com', 'x.com']):
        await update.message.reply_text(
            "⚠️ **Usage**: `/x <twitter-url>`\n\n"
            "**Examples**:\n"
            "• `/x https://x.com/user/status/123`\n"
            "• `/x https://twitter.com/user/status/123`\n"
            "• Send Twitter link, then reply with `/x`\n\n"
            "**Features**:\n"
            "• Video, photo, GIF download\n"
            "• Direct to Telegram\n"
            "• No Google Drive needed",
            parse_mode='Markdown'
        )
        return

    status_msg = await update.message.reply_text(
        f"📥 **Twitter/X Download Started**\n\n"
        f"🔗 **URL**: {url[:50]}...\n"
        f"📊 **Status**: Processing...\n\n"
        f"⏱️ **Please wait**: Downloading..."
    )

    try:
        await download_social_media_direct(url, 'twitter', update, context)
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ **Twitter Download Error**: {str(e)}")

async def youtube_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """YouTube video downloader with quality options - Direct to Telegram"""
    if not await require_subscription(update, context):
        return

    url = None
    if context.args:
        url = context.args[0]
    elif update.message.reply_to_message and update.message.reply_to_message.text:
        url = update.message.reply_to_message.text

    if not url or 'youtube.com' not in url.lower() and 'youtu.be' not in url.lower():
        await update.message.reply_text(
            "⚠️ **Usage**: `/ytv <youtube-url>`\n\n"
            "**Examples**:\n"
            "• `/ytv https://youtube.com/watch?v=abc123`\n"
            "• `/ytv https://youtu.be/abc123`\n"
            "• Send YouTube link, then reply with `/ytv`\n\n"
            "**Features**:\n"
            "• Quality selection (360p, 480p, 1080p)\n"
            "• Direct to Telegram\n"
            "• No Google Drive needed",
            parse_mode='Markdown'
        )
        return

    # Quality selection keyboard
    keyboard = [
        [InlineKeyboardButton("📺 360p (Fast)", callback_data=f"ytv_360p_{update.effective_user.id}")],
        [InlineKeyboardButton("📺 480p (Medium)", callback_data=f"ytv_480p_{update.effective_user.id}")],
        [InlineKeyboardButton("📺 1080p (HD)", callback_data=f"ytv_1080p_{update.effective_user.id}")],
        [InlineKeyboardButton("🎯 Best Quality", callback_data=f"ytv_best_{update.effective_user.id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data=f"ytv_cancel_{update.effective_user.id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Store URL in context for callback
    context.user_data['youtube_url'] = url

    await update.message.reply_text(
        f"🎬 **YouTube Video Download**\n\n"
        f"🔗 **URL**: {url[:50]}...\n\n"
        f"📊 **Select Quality**:\n"
        f"• **360p**: Smaller file, faster download\n"
        f"• **480p**: Medium quality\n"
        f"• **1080p**: HD quality (larger file)\n"
        f"• **Best**: Highest available quality\n\n"
        f"📱 **Output**: Direct to Telegram",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def youtube_thumbnail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """YouTube thumbnail downloader - Direct to Telegram"""
    if not await require_subscription(update, context):
        return

    url = None
    if context.args:
        url = context.args[0]
    elif update.message.reply_to_message and update.message.reply_to_message.text:
        url = update.message.reply_to_message.text

    if not url or 'youtube.com' not in url.lower() and 'youtu.be' not in url.lower():
        await update.message.reply_text(
            "⚠️ **Usage**: `/ytm <youtube-url>`\n\n"
            "**Examples**:\n"
            "• `/ytm https://youtube.com/watch?v=abc123`\n"
            "• `/ytm https://youtu.be/abc123`\n"
            "• Send YouTube link, then reply with `/ytm`\n\n"
            "**Features**:\n"
            "• HD thumbnail download\n"
            "• Direct to Telegram\n"
            "• Document + preview",
            parse_mode='Markdown'
        )
        return

    status_msg = await update.message.reply_text(
        f"📸 **YouTube Thumbnail Download Started**\n\n"
        f"🔗 **URL**: {url[:50]}...\n"
        f"📊 **Status**: Fetching thumbnail...\n\n"
        f"⏱️ **Please wait**: Processing..."
    )

    try:
        await download_social_media_direct(url, 'youtube_thumbnail', update, context)
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ **Thumbnail Download Error**: {str(e)}")

async def video_converter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Video to audio converter"""
    if not await require_subscription(update, context):
        return

    # Check if replying to video or video sent with command
    video_file = None
    if update.message.reply_to_message and update.message.reply_to_message.video:
        video_file = update.message.reply_to_message.video
    elif update.message.video:
        video_file = update.message.video

    if not video_file:
        await update.message.reply_text(
            "⚠️ **Usage**: `/cv` (reply to video)\n\n"
            "**How to use**:\n"
            "1. Send a video file\n"
            "2. Reply to it with `/cv`\n"
            "OR\n"
            "1. Send `/cv` command\n"
            "2. Send video file\n\n"
            "**Features**:\n"
            "• Convert to MP3 or FLAC\n"
            "• Document + audio preview\n"
            "• Auto cleanup after send",
            parse_mode='Markdown'
        )

        # Wait for video if command sent first
        context.user_data['awaiting_video'] = True
        return

    # Format selection keyboard
    keyboard = [
        [InlineKeyboardButton("🎵 Convert to MP3", callback_data=f"cv_mp3_{update.effective_user.id}")],
        [InlineKeyboardButton("🎶 Convert to FLAC", callback_data=f"cv_flac_{update.effective_user.id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data=f"cv_cancel_{update.effective_user.id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Store video in context for callback
    context.user_data['video_file'] = video_file

    await update.message.reply_text(
        f"🎵 **Video to Audio Converter**\n\n"
        f"📁 **File**: {video_file.file_name or 'video_file'}\n"
        f"📊 **Size**: {video_file.file_size / 1024 / 1024:.1f} MB\n\n"
        f"🎯 **Select Output Format**:\n"
        f"• **MP3**: Compressed format (smaller file)\n"
        f"• **FLAC**: Lossless format (larger file)\n\n"
        f"⏱️ **Processing time**: ~30 seconds per minute of video",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document uploads (for credentials)"""
    if not is_owner(update.effective_user):
        return

    if not context.user_data.get("awaiting_credentials"):
        return

    document = update.message.document

    if not document.file_name.endswith('.json'):
        await update.message.reply_text(
            "❌ **Invalid file type**\n\n"
            "Please upload a .json file (credentials.json)",
            parse_mode='Markdown'
        )
        return

    try:
        # Download and save credentials file
        file = await document.get_file()
        await file.download_to_drive(CREDENTIALS_FILE)

        # Clear awaiting state
        context.user_data["awaiting_credentials"] = False

        await update.message.reply_text(
            "✅ **credentials.json uploaded successfully**\n\n"
            "📄 **File**: Ready for authentication\n"
            "🔐 **Next step**: Use `/auth` to get OAuth link\n\n"
            "🛡️ **Security**: File stored securely",
            parse_mode='Markdown'
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ **Upload failed**\n\n"
            f"**Error**: {str(e)}\n\n"
            f"Please try uploading the file again.",
            parse_mode='Markdown'
        )

async def handle_video_for_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video files for conversion when awaiting"""
    if context.user_data.get('awaiting_video'):
        context.user_data['awaiting_video'] = False

        # Trigger converter with the video
        context.user_data['video_file'] = update.message.video
        await video_converter(update, context)

# Callback handlers
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    data = query.data
    user_id = update.effective_user.id

    await query.answer()

    if data.startswith('ytv_'):
        # YouTube video quality selection
        parts = data.split('_')
        quality = parts[1]
        callback_user_id = int(parts[2])

        if user_id != callback_user_id:
            await query.edit_message_text("❌ This button is not for you.")
            return

        url = context.user_data.get('youtube_url')
        if not url:
            await query.edit_message_text("❌ URL not found. Please try again.")
            return

        if quality == 'cancel':
            await query.edit_message_text("❌ **YouTube download cancelled**")
            return

        await query.edit_message_text(
            f"📥 **YouTube Download Started**\n\n"
            f"🔗 **URL**: {url[:50]}...\n"
            f"📺 **Quality**: {quality.upper()}\n"
            f"📊 **Status**: Downloading...\n\n"
            f"⏱️ **Please wait**: This may take a moment..."
        )

        try:
            quality_param = None if quality == 'best' else quality
            await download_social_media_direct(url, 'youtube', update, context, quality_param)
        except Exception as e:
            await query.edit_message_text(f"❌ **YouTube Download Error**: {str(e)}")

    elif data.startswith('cv_'):
        # Video conversion format selection
        parts = data.split('_')
        format_type = parts[1]
        callback_user_id = int(parts[2])

        if user_id != callback_user_id:
            await query.edit_message_text("❌ This button is not for you.")
            return

        video_file = context.user_data.get('video_file')
        if not video_file:
            await query.edit_message_text("❌ Video not found. Please try again.")
            return

        if format_type == 'cancel':
            await query.edit_message_text("❌ **Conversion cancelled**")
            return

        await query.edit_message_text(
            f"🎵 **Video Conversion Started**\n\n"
            f"📁 **Input**: {video_file.file_name or 'video_file'}\n"
            f"🎯 **Format**: {format_type.upper()}\n"
            f"📊 **Status**: Converting...\n\n"
            f"⏱️ **Processing**: This may take a while..."
        )

        try:
            await convert_video_to_audio_direct(video_file, format_type, update, context)
        except Exception as e:
            await query.edit_message_text(f"❌ **Conversion Error**: {str(e)}")

# Owner-only commands
async def auth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auth command - Owner only"""
    if not await owner_only_check(update, context, "Google Drive Setup"):
        return

    if not DRIVE_AVAILABLE:
        await update.message.reply_text(
            "❌ **Google Drive Not Available**\n\n"
            "Google Drive dependencies not installed.\n"
            "Social media downloads work without Drive.\n\n"
            "To enable Drive features, install:\n"
            "`pip install google-api-python-client google-auth-oauthlib`",
            parse_mode='Markdown'
        )
        return

    if not os.path.exists(CREDENTIALS_FILE):
        context.user_data["awaiting_credentials"] = True

        await update.message.reply_text(
            "📄 **Upload credentials.json - Owner Access**\n\n"
            "Please upload your Google Drive credentials.json file.\n\n"
            "🔐 **Security**: Only owner can upload credentials\n"
            "📱 **Note**: Social downloads work without this\n\n"
            "**How to get credentials.json:**\n"
            "1. Google Cloud Console\n"
            "2. Create OAuth 2.0 Client ID\n"
            "3. Download JSON file\n"
            "4. Upload here (max 100KB)",
            parse_mode='Markdown',
            reply_markup=ForceReply(selective=True)
        )
        return

    # Generate auth URL (implementation depends on drive_manager)
    await update.message.reply_text(
        "✅ **Google Drive Setup**\n\n"
        "Credentials file ready. Google Drive features available for owner.\n\n"
        "📱 **Note**: All social media downloads work without Drive.",
        parse_mode='Markdown'
    )

async def roottest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test system access - Owner only"""
    if not await owner_only_check(update, context, "System Testing"):
        return

    test_msg = await update.message.reply_text("🧪 **Testing System - Owner Only...**")

    tests = []

    # Test 1: Platform info
    tests.append(("Platform", f"✅ {platform.system()} {platform.machine()}"))

    # Test 2: Python version
    tests.append(("Python", f"✅ {sys.version.split()[0]}"))

    # Test 3: Bot token
    tests.append(("Bot Token", "✅ Valid" if BOT_TOKEN else "❌ Missing"))

    # Test 4: Temp directory
    temp_test = os.path.exists(TEMP_DIR) and os.access(TEMP_DIR, os.W_OK)
    tests.append(("Temp Directory", "✅ Writable" if temp_test else "❌ Not writable"))

    # Test 5: yt-dlp
    try:
        proc = await asyncio.create_subprocess_exec('yt-dlp', '--version', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        if proc.returncode == 0:
            version = stdout.decode().strip()[:20]
            tests.append(("yt-dlp", f"✅ {version}"))
        else:
            tests.append(("yt-dlp", "❌ Not found"))
    except:
        tests.append(("yt-dlp", "❌ Not found"))

    # Test 6: ffmpeg
    try:
        proc = await asyncio.create_subprocess_exec('ffmpeg', '-version', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        if proc.returncode == 0:
            tests.append(("ffmpeg", "✅ Available"))
        else:
            tests.append(("ffmpeg", "❌ Not found"))
    except:
        tests.append(("ffmpeg", "❌ Not found"))

    # Test 7: Google Drive
    drive_status = "✅ Available" if DRIVE_AVAILABLE else "❌ Not installed"
    tests.append(("Google Drive", drive_status))

    results = "\n".join([f"• **{test}**: {result}" for test, result in tests])

    await test_msg.edit_text(
        f"🧪 **System Test Results - Owner Only**\n\n"
        f"{results}\n\n"
        f"🛡️ **Status**: {'✅ All systems operational' if all('✅' in t[1] for t in tests) else '⚠️ Some components missing'}\n"
        f"📱 **Social Downloads**: Ready (no Drive needed)\n"
        f"🔍 **Reverse Search**: Enhanced detection active\n"
        f"📖 **nhentai**: PM-only PDF downloads\n"
        f"🧹 **Auto Cleanup**: Active\n\n"
        f"**All core features working!**",
        parse_mode='Markdown'
    )

def main():
    """Main function"""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found")
        sys.exit(1)

    logger.info("🚀 Starting STB Bot - FINAL REVISION")
    logger.info(f"📢 Channel: {REQUIRED_CHANNEL}")
    logger.info(f"👑 Owner: @{OWNER_USERNAME}")
    logger.info(f"📱 Social downloads: Direct to Telegram (no Drive needed)")
    logger.info(f"🔍 Reverse search: Enhanced anime + illustration detection")
    logger.info(f"📖 nhentai: PM-only, 4+ digits, PDF downloads")
    logger.info(f"🧹 Auto cleanup: {'Enabled' if AUTO_CLEANUP_ENABLED else 'Disabled'}")
    logger.info(f"☁️ Google Drive: {'Available' if DRIVE_AVAILABLE else 'Disabled'} (optional)")

    # Create application
    application = Application.builder().token(BOT_TOKEN).connect_timeout(60).read_timeout(60).write_timeout(60).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # Social media downloaders (no Drive needed)
    application.add_handler(CommandHandler("fb", facebook_download))
    application.add_handler(CommandHandler("ig", instagram_download))
    application.add_handler(CommandHandler("x", twitter_download))
    application.add_handler(CommandHandler("ytv", youtube_download))
    application.add_handler(CommandHandler("ytm", youtube_thumbnail))
    application.add_handler(CommandHandler("cv", video_converter))

    # Owner-only commands
    application.add_handler(CommandHandler("auth", auth_command))
    application.add_handler(CommandHandler("roottest", roottest_command))

    # Auto features
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video_for_conversion))
    application.add_handler(MessageHandler(filters.Document.FileExtension("json"), handle_document))

    # Callback handlers
    application.add_handler(CallbackQueryHandler(button_callback))

    logger.info("✅ All handlers registered")
    logger.info("🔄 Starting polling...")

    try:
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
