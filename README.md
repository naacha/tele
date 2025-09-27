# STB HG680P Telegram Bot - File Upload credentials.json

## 🎯 Revolutionary File Upload Credentials Management

### ✅ Key Features:
- **📄 Upload credentials.json via Telegram** - No SSH access needed
- **🔄 Easy Google account switching** - Perfect when Drive is full
- **🔒 Automatic file validation** - JSON format & structure checking
- **🔧 Secure file handling** - chmod 600, proper permissions
- **⚡ Commands blocked until auth** - Clean user experience
- **🌟 All JMDKH features** - Torrent, mirror, clone capabilities

### ✅ Pre-configured Credentials:
- **Bot Token:** `8436081597:AAE-8bfWrbvhl26-l9y65p48DfWjQOYPR2A`
- **Channel ID:** `-1001802424804` (@ZalheraThink)

## 📋 Quick Deployment

### 1. Extract and Setup
```bash
unzip telegram-bot-stb-file-upload-complete.zip
cd telegram-bot-stb-file-upload-complete
sudo ./setup.sh
```

**What gets fixed/installed:**
- GPG key errors resolved
- AnyDesk dependency issues fixed
- Docker + Docker Compose (ARM64)
- Enhanced system tools

### 2. Start Bot
```bash
./start.sh
```

### 3. Upload Credentials via Telegram
1. Start bot → `/start` → `/auth`
2. Bot requests: "📄 Upload credentials.json file"
3. Upload your credentials.json file in chat
4. Bot validates → saves → provides OAuth link
5. Complete OAuth → `/code [authorization-code]`
6. Ready to use all features!

## 🔄 Easy Google Account Switching

### When Drive Storage is Full:
1. Get new Google account
2. Create new credentials.json in Cloud Console
3. Send new file to bot (any time)
4. Bot automatically replaces old file
5. Run `/auth` again → connected to new account

### Multiple Account Management:
```
User: *uploads credentials.json (Account A)*
Bot: ✅ credentials.json uploaded. Use /auth to connect.

# After some time, Drive full...
User: *uploads credentials.json (Account B)*  
Bot: 🔄 File replaced. Old connection cleared. Use /auth for new account.
```

## 📱 Complete Command List

| Command | Function | Notes |
|---------|----------|-------|
| `/start` | Welcome & system info | Shows credentials status |
| `/auth` | Upload credentials.json & connect | Requests file if not uploaded |
| `/setcreds` | Manual credential replacement | Same as uploading directly |
| `/code <auth-code>` | Complete OAuth authorization | After uploading file |
| `/d <link>` | Mirror to Google Drive | Blocked until Drive connected |
| `/t <magnet/torrent>` | Torrent to Google Drive | Blocked until Drive connected |
| `/dc <gdrive-url>` | Clone Google Drive | Blocked until Drive connected |
| `/system` | System info + credentials status | File upload specific info |
| `/anydesk` | AnyDesk remote access info | |
| `/stats` | Bot usage statistics | |
| `/help` | Complete help with file upload | |

## 🎯 File Upload Process (Detailed)

### First Time Setup:
```
1. User: /auth
2. Bot: 📄 Upload credentials.json file
3. User: *uploads file*
4. Bot: ✅ File processed. Here's OAuth link: [URL]
5. User: *clicks link* → *authorizes* → *copies code*
6. User: /code 4/0AdQt8qi...
7. Bot: ✅ Google Drive Connected Successfully!
```

### Account Switching:
```
1. User: *uploads new credentials.json*
2. Bot: 🔄 File replaced. Old connection cleared.
3. User: /auth  
4. Bot: 🔗 OAuth link: [URL] (for new account)
5. User: *completes auth*
6. Bot: Connected to new Google account!
```

### File Validation:
- **Size check:** < 100KB
- **Name check:** Must be exactly "credentials.json"
- **JSON validation:** Proper structure required
- **Format check:** Desktop application credentials

## 🔒 Security Features

### File Security:
- Downloaded to `/tmp` first for validation
- Moved to `/app/credentials/` with chmod 600
- Only container can access the file
- Old credentials automatically cleared

### Validation Process:
```python
def validate_credentials_file(file_path):
    # Check JSON format
    # Verify 'installed' section exists
    # Validate required fields
    # Return detailed error messages
```

## 🔧 Expected Results

### Successful File Upload:
```
User: *uploads credentials.json*
Bot: ⏳ Processing credentials.json...
     ✅ credentials.json Uploaded Successfully!

     📄 File processed:
     • File validated and saved
     • Secure permissions applied (chmod 600)
     • Ready for authentication

     🔗 Authorization Link:
     https://accounts.google.com/o/oauth2/auth?...
```

### System Status:
```
User: /system
Bot: 💻 STB HG680P System Information - File Upload Credentials

     📄 Credentials Status:
     • credentials.json: ✅ Uploaded & Ready
     • File size: 2847 bytes
     • Google Drive: ✅ Connected

     🌟 File Upload Features:
     • Upload credentials via Telegram: ✅ Active
     • Replace Google accounts easily: ✅ Active
```

## 🎉 Advantages

### No More SSH:
- ❌ No `scp credentials.json root@stb:/path/`
- ❌ No manual file permissions
- ❌ No container restarts needed
- ✅ Everything through Telegram chat

### Easy Account Management:
- ✅ Switch accounts in seconds
- ✅ Perfect for Drive storage limits
- ✅ Multiple Google accounts supported
- ✅ Automatic credential replacement

### Enhanced Security:
- ✅ File validation before use
- ✅ Secure permissions (chmod 600)
- ✅ Automatic cleanup of old tokens
- ✅ Container-based isolation

## ✅ All Features Working

- ✅ **File Upload via Telegram** - Upload credentials.json directly
- ✅ **Automatic Validation** - JSON format & structure checking
- ✅ **Secure File Handling** - chmod 600, proper permissions
- ✅ **Easy Account Switching** - Replace Google accounts easily
- ✅ **Commands Blocked Until Auth** - Clean UX, no confusing errors
- ✅ **All JMDKH Features** - Torrent, mirror, clone intact
- ✅ **AnyDesk Integration** - Remote access with dependency fixing
- ✅ **Error Fixing** - GPG keys, repositories, dependencies

**🎉 Complete file upload solution - no SSH needed! 🚀**

**Extract → Setup → Start → Upload credentials.json → Auth → Ready! 📄**
