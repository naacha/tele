# STB Bot - SECURE VERSION WITH AUTO CLEANUP

## 🛡️ SECURITY IMPROVEMENTS IMPLEMENTED

### 🔐 Owner-Only Sensitive Commands
**SECURITY RESTRICTION**: System-sensitive operations now restricted to owner only:
- `/auth` - Upload credentials.json (Owner only)
- `/setcreds` - Replace credentials (Owner only) 
- `/code <auth-code>` - Complete OAuth (Owner only)
- `/roottest` - Test system access (Owner only)

**Access Control**: Non-owners get security denial message with reason.

### 📖 nhentai PM-Only with Enhanced Validation
**PRIVACY PROTECTION**: nhentai search now restricted to private chats only:
- **PM Only**: Groups completely ignore number messages
- **Minimum Digits**: Increased from 3 to 4 digits minimum
- **Enhanced Validation**: Stricter code format checking
- **Group Behavior**: Bot silently ignores numbers in groups

### 🧹 Auto File Cleanup System
**STORAGE MANAGEMENT**: Automatic file deletion after upload:
- **Post-Upload Cleanup**: Files deleted 30 seconds after Telegram upload
- **Temp File Cleanup**: Temporary files deleted after processing
- **Directory Cleanup**: Empty directories automatically removed
- **System Protection**: Prevents storage overflow

## 🎯 SECURITY IMPLEMENTATION DETAILS

### Owner-Only Command Security
```python
async def owner_only_check(update, context, command_name):
    if not is_owner(user):
        await update.message.reply_text(
            f"🔒 **Owner Only - Security Restriction**\n\n"
            f"❌ **Access Denied**: {command_name}\n"
            f"👑 **Owner**: @{OWNER_USERNAME}\n\n"
            f"🛡️ **Reason**: Sensitive system operations restricted"
        )
        return False
    return True
```

### nhentai PM-Only Implementation
```python
async def handle_text_message(update, context):
    # SECURITY: Only work in private chats
    if not is_private_chat(update):
        # Silently ignore numbers in groups
        return

    text = update.message.text.strip()

    # Enhanced validation: 4+ digits minimum
    if text.isdigit() and len(text) >= 4:
        # Process nhentai search only in PM
```

### Auto Cleanup System
```python
def cleanup_file(file_path, delay=5):
    async def delayed_cleanup():
        await asyncio.sleep(delay)
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Auto cleanup: {file_path}")

    asyncio.create_task(delayed_cleanup())
```

## 🚀 SECURE DEPLOYMENT

### 1. System Setup (Root Required)
```bash
unzip stb-bot-revised-security.zip
cd stb-bot-revised-security
sudo ./setup.sh  # Must run as root for security setup
```

### 2. Start Secure Bot
```bash
./start.sh
```

**Expected Secure Output:**
```
✅ STB Bot started - SECURE VERSION WITH AUTO CLEANUP!

🛡️ SECURITY FEATURES:
• ✅ Owner-only sensitive commands
• ✅ System operations restricted to owner
• ✅ Credentials upload: Owner only
• ✅ OAuth setup: Owner only

📖 NHENTAI SECURITY:
• ✅ PM only: Groups ignored
• ✅ Minimum 4 digits (was 3)
• ✅ Enhanced validation

🧹 AUTO CLEANUP FEATURES:
• ✅ Files deleted after upload
• ✅ Temp directories cleaned
• ✅ System space management

🔑 Secure Password: hakumen12312
Made by many fuck love @Zalhera
```

## 🎯 SECURE USAGE EXAMPLES

### Owner-Only Commands (Security Restricted)
```
Non-Owner: /auth
Bot:       🔒 Owner Only - Security Restriction

           ❌ Access Denied: Google Drive Setup
           👑 Owner: @zalhera

           🛡️ Reason: Sensitive system operations restricted
           🔐 Security: Full access controls active

Owner: /auth
Bot:   📄 Upload credentials.json - SECURE OWNER ACCESS
       🔐 Security: Only owner can upload credentials
       🛡️ Protection: System-level access controls
```

### nhentai PM-Only Behavior
```
# In GROUP CHAT:
User: 177013
Bot:  *silently ignores - no response*

# In PRIVATE CHAT:
User: 177013
Bot:  📖 Auto nhentai Search - PM Only
      🔢 Code detected: 177013 (6 digits)
      🔍 Searching: nhentai database...
      🔒 Security: Private chat verified

# In PRIVATE CHAT (too short):
User: 123
Bot:  ❌ nhentai Search Failed - PM Only
      Code: 123
      Error: Code too short. Minimum 4 digits required.
```

### Auto Cleanup in Action
```
User: /fb https://facebook.com/video/123
Bot:  📥 Facebook Download Started - Auto Cleanup
      🧹 Auto Cleanup: Files deleted after upload

Bot:  ✅ Facebook Download Complete - Auto Cleanup
      📁 File: video.mp4
      📊 Size: 125.6 MB
      🧹 Cleanup: File will be auto-deleted

*Bot sends document*
*30 seconds later: file automatically deleted from server*
```

### Reverse Image Search with Cleanup
```
User: *sends photo*
Bot:  🔍 Auto Reverse Image Search
      📸 Photo downloaded ✅
      🔎 Searching: Analyzing image...

Bot:  🔍 Reverse Search Results
      🎨 Details: Artist info...
      🔗 Sources Found: 2 sources...
      📄 HD Image: Sending as document...
      🧹 Auto Cleanup: Temp files will be deleted

*Bot sends HD image as document*
*30 seconds later: temp files automatically deleted*
```

## 📋 COMPLETE SECURE COMMAND LIST

### Public Commands (All Users)
- `/start` - Bot info with security status
- `/help` - Help with security information
- `/fb <link>` - Facebook download + cleanup
- `/ig <link>` - Instagram download + cleanup
- `/x <link>` - Twitter download + cleanup
- `/ytv <link>` - YouTube video + cleanup
- `/ytm <link>` - YouTube thumbnail + cleanup
- `/cv` - Video converter + cleanup
- `/d <link>` - Google Drive mirror + cleanup
- `/t <magnet>` - Torrent leech + cleanup
- `/etadl` - Download status
- `/stop1` `/stop2` - Cancel downloads

### Auto Features (Security Enhanced)
- **Send photo** → Reverse search + cleanup (all users)
- **Send 4+ digits in PM** → nhentai search + cleanup (PM only)

### Owner-Only Commands (Security Restricted)
- `/auth` - Upload credentials.json (secure)
- `/setcreds` - Replace credentials (secure)
- `/code <auth-code>` - Complete OAuth (secure)
- `/roottest` - Test system access (secure)

## 🔐 WEBHOOK INTEGRATION CAPABILITY

**Answer to your question**: Yes, I can create Telegram bot integration with Discord webhooks! 

**Technical Capabilities**:
- ✅ Receive Discord webhook POST requests
- ✅ Parse Discord message data (content, embeds, attachments)
- ✅ Forward to Telegram with proper formatting
- ✅ Handle Discord attachments → Telegram media
- ✅ Bidirectional communication (Telegram → Discord webhook)
- ✅ Message formatting conversion (Discord markdown → Telegram)
- ✅ Embed support with proper Telegram formatting

**Implementation Options**:
1. **HTTP Server**: Built-in webhook receiver in bot
2. **Message Forwarding**: Discord → Telegram automation
3. **Command Triggers**: Telegram commands trigger Discord webhooks
4. **Status Updates**: Bot status updates sent to Discord
5. **File Sharing**: Attachments shared between platforms

**Integration Points**:
```python
# Discord webhook receiver
@app.route('/discord-webhook', methods=['POST'])
async def handle_discord_webhook():
    data = request.get_json()
    # Process Discord message
    # Send to Telegram

# Telegram to Discord sender
async def send_to_discord_webhook(message, webhook_url):
    payload = {"content": message}
    # Send to Discord webhook
```

Let me know if you want me to implement this Discord webhook integration!

## 🎉 SUMMARY: SECURITY IMPROVEMENTS IMPLEMENTED

✅ **Owner-Only Sensitive Commands**: System operations restricted  
✅ **nhentai PM-Only**: Groups ignored, 4+ digits minimum  
✅ **Auto File Cleanup**: Storage management, files deleted after upload  
✅ **All Previous Features**: Nothing removed, everything enhanced  
✅ **Security Controls**: Access denied messages with reasons  
✅ **Enhanced Validation**: Stricter input checking  

Made by many fuck love @Zalhera

**Deploy now - Secure bot with auto cleanup ready! 🛡️**
