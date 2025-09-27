#!/usr/bin/env python3
"""
STB HG680P / S905x Telegram Bot (Bookworm-only, File Upload credentials.json)
- Supports Armbian v25.11.0 bookworm 6.1.149-ophub
- Removed AnyDesk & Bullseye support
- Handles externally-managed-environment via PIP_BREAK_SYSTEM_PACKAGES env (container)
"""
import os, sys, json, logging, platform, subprocess, asyncio
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload

TOKEN_FILE = '/app/data/token.json'
CREDS_FILE = '/app/credentials/credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive']
BOT_TOKEN = os.getenv('BOT_TOKEN')
OWNER = os.getenv('OWNER_USERNAME','zalhera')
CH_ID = int(os.getenv('CHANNEL_ID','-1001802424804'))
CH_USER = os.getenv('REQUIRED_CHANNEL','@ZalheraThink')

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

# Ensure dirs
for d in ('/app/data','/app/credentials','/app/downloads','/app/logs','/app/torrents'):
    os.makedirs(d, exist_ok=True)

class DriveMgr:
    def __init__(self):
        self.service=None; self.creds=None
        self._load()
    def _load(self):
        if not (os.path.exists(TOKEN_FILE) and os.path.exists(CREDS_FILE)):return
        with open(CREDS_FILE) as f: ci=json.load(f)['installed']
        with open(TOKEN_FILE) as f: tk=json.load(f)
        self.creds=Credentials(tk['token'],tk['refresh_token'],ci['client_id'],ci['client_secret'],'https://oauth2.googleapis.com/token',SCOPES)
        if self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request()); self._save()
        if self.creds.valid:
            self.service=build('drive','v3',credentials=self.creds,cache_discovery=False)
    def _save(self):
        if not self.creds:return
        with open(TOKEN_FILE,'w') as f: json.dump({'token':self.creds.token,'refresh_token':self.creds.refresh_token,'scopes':self.creds.scopes},f)
        os.chmod(TOKEN_FILE,0o600)
    def invalidate(self):
        if os.path.exists(TOKEN_FILE): os.remove(TOKEN_FILE)
        self.service=None; self.creds=None
    def val_file(self,p):
        try:
            d=json.load(open(p)); inst=d['installed'];
            for k in ('client_id','client_secret','auth_uri','token_uri'):
                if k not in inst: return False,f'missing {k}'
            return True,'ok'
        except Exception as e: return False,str(e)
    def auth_url(self):
        if not os.path.exists(CREDS_FILE):return None,'upload creds file first'
        flow=InstalledAppFlow.from_client_secrets_file(CREDS_FILE,SCOPES)
        flow.redirect_uri='http://localhost:8080'
        url,_=flow.authorization_url(access_type='offline',prompt='consent',include_granted_scopes='true')
        self._flow=flow; return url,None
    def finish_code(self,code):
        if not hasattr(self,'_flow'): return False,'run /auth first'
        try:
            self._flow.fetch_token(code=code.strip())
            self.creds=self._flow.credentials; self._save()
            self.service=build('drive','v3',credentials=self.creds,cache_discovery=False)
            return True,''
        except Exception as e: return False,str(e)

drive=DriveMgr()

def is_owner(u): return u and u.lower()==OWNER.lower()

async def sub_chk(up,ctx):
    if is_owner(up.effective_user.username):return True
    try:
        mem=await ctx.bot.get_chat_member(CH_ID,up.effective_user.id)
        return mem.status in ('member','administrator','creator')
    except: return False
async def gate(up,ctx):
    if await sub_chk(up,ctx): return True
    kb=[[InlineKeyboardButton('Join Channel',url=f'https://t.me/{CH_USER.lstrip("@")}')]]
    await up.message.reply_text('Join channel dulu',reply_markup=InlineKeyboardMarkup(kb)); return False

# Commands
async def start(up,ctx):
    if not await gate(up,ctx):return
    st=f"Credentials: {'✅' if os.path.exists(CREDS_FILE) else '❌'}
Drive: {'✅' if drive.service else '❌'}"
    await up.message.reply_text(f"STB Bot Bookworm (S905x)
{st}
Commands: /auth /setcreds /code /d /t /dc /system /help")
async def system(up,ctx):
    if not await gate(up,ctx):return
    mem=open('/proc/meminfo').readline().split()[1];
    await up.message.reply_text(f"Arch: {platform.machine()}
Mem: {int(mem)//1024} MB
Creds: {os.path.exists(CREDS_FILE)}
Drive: {bool(drive.service)}")
async def auth(up,ctx):
    if not await gate(up,ctx):return
    if not os.path.exists(CREDS_FILE):
        ctx.user_data['await']=True
        await up.message.reply_text('Upload credentials.json dahulu.',reply_markup=ForceReply())
        return
    url,err=drive.auth_url();
    if err: await up.message.reply_text('Error: '+err); return
    await up.message.reply_text(f'Klik link & ijinkan:
{url}
Lalu kirim /code <kode>')
async def setcreds(up,ctx):
    if not await gate(up,ctx):return
    ctx.user_data['await']=True
    await up.message.reply_text('Upload credentials.json baru untuk mengganti file lama.',reply_markup=ForceReply())
async def code(up,ctx):
    if not await gate(up,ctx):return
    if not ctx.args: await up.message.reply_text('Gunakan /code <authorization-code>'); return
    ok,err=drive.finish_code(' '.join(ctx.args))
    await up.message.reply_text('✅ Connected' if ok else '❌ '+err)
async def doc(up,ctx):
    if not ctx.user_data.get('await'): return
    doc=up.message.document
    if doc.file_name!='credentials.json': return await up.message.reply_text('Nama file harus credentials.json')
    path=f'/tmp/{random.randint(1,1e9)}.json'; await doc.get_file().download_to_drive(path)
    valid,msg=drive.val_file(path)
    if not valid: os.remove(path); return await up.message.reply_text('Invalid file: '+msg)
    os.makedirs('/app/credentials',exist_ok=True)
    if os.path.exists(CREDS_FILE): drive.invalidate(); os.remove(CREDS_FILE)
    os.rename(path,CREDS_FILE); os.chmod(CREDS_FILE,0o600); drive._load(); ctx.user_data['await']=False
    await up.message.reply_text('✅ creds uploaded. Lanjut /auth')

# placeholders for /d /t /dc
async def placeholder(up,ctx):
    if not await gate(up,ctx):return
    if not drive.service: return await up.message.reply_text('Connect Drive dulu.')
    await up.message.reply_text('Fitur belum diimplementasi.')

def main():
    if not BOT_TOKEN:
        print('BOT_TOKEN env missing'); sys.exit(1)
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start',start))
    app.add_handler(CommandHandler('system',system))
    app.add_handler(CommandHandler('auth',auth))
    app.add_handler(CommandHandler('setcreds',setcreds))
    app.add_handler(CommandHandler('code',code))
    app.add_handler(CommandHandler(['d','t','dc'],placeholder))
    app.add_handler(MessageHandler(filters.Document.ALL,doc))
    app.run_polling()
if __name__=='__main__': main()
