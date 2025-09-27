#!/usr/bin/env python3
"""
STB Telegram Bot (CLI-only, Bookworm Amlogic S905x)
- File upload credentials.json
- No GUI, no AnyDesk, no X11
- Bookworm kernel 6.1.149-ophub only
"""
import os, json, logging, platform, asyncio, random, sys
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

BOT_TOKEN = os.getenv('BOT_TOKEN')
OWNER = os.getenv('OWNER_USERNAME','zalhera')
CHANNEL = os.getenv('REQUIRED_CHANNEL','@ZalheraThink')
CHANNEL_ID = int(os.getenv('CHANNEL_ID','-1001802424804'))
TOKEN_FILE = '/app/data/token.json'
CREDS_FILE = '/app/credentials/credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

for d in ('/app/data','/app/credentials','/app/downloads','/app/logs','/app/torrents'):
    os.makedirs(d, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
log = logging.getLogger(__name__)

class Drive:
    def __init__(self):
        self.svc=None; self.creds=None; self.load()
    def load(self):
        if not (os.path.exists(CREDS_FILE) and os.path.exists(TOKEN_FILE)): return
        with open(CREDS_FILE) as f: ci=json.load(f)['installed']
        with open(TOKEN_FILE) as f: tk=json.load(f)
        self.creds=Credentials(tk['token'],tk['refresh_token'],ci['client_id'],ci['client_secret'],'https://oauth2.googleapis.com/token',SCOPES)
        if self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request()); self.save()
        if self.creds.valid:
            self.svc=build('drive','v3',credentials=self.creds,cache_discovery=False)
    def save(self):
        if not self.creds: return
        with open(TOKEN_FILE,'w') as f: json.dump({'token':self.creds.token,'refresh_token':self.creds.refresh_token,'scopes':self.creds.scopes},f)
        os.chmod(TOKEN_FILE,0o600)
    def invalidate(self):
        if os.path.exists(TOKEN_FILE): os.remove(TOKEN_FILE)
        self.svc=None; self.creds=None
    def validate_creds(self,p):
        try:
            d=json.load(open(p)); inst=d['installed']
            for k in ('client_id','client_secret','auth_uri','token_uri'):
                if k not in inst: return False,f'missing {k}'
            return True,'ok'
        except Exception as e: return False,str(e)
    def auth_url(self):
        if not os.path.exists(CREDS_FILE): return None,'upload creds'
        flow=InstalledAppFlow.from_client_secrets_file(CREDS_FILE,SCOPES); flow.redirect_uri='http://localhost:8080'
        url,_=flow.authorization_url(access_type='offline',prompt='consent')
        self._flow=flow; return url,None
    def finish(self,code):
        if not hasattr(self,'_flow'): return False,'run /auth again'
        try:
            self._flow.fetch_token(code=code.strip()); self.creds=self._flow.credentials; self.save(); self.svc=build('drive','v3',credentials=self.creds,cache_discovery=False); return True,''
        except Exception as e: return False,str(e)

drive=Drive()

def is_owner(u): return u and u.lower()==OWNER.lower()

async def subscribed(ctx,user):
    if is_owner(user.username): return True
    try:
        mem=await ctx.bot.get_chat_member(CHANNEL_ID,user.id);
        return mem.status in ('member','administrator','creator')
    except: return False

async def gate(update,ctx):
    if await subscribed(ctx,update.effective_user): return True
    kb=[[InlineKeyboardButton('Join Channel',url=f'https://t.me/{CHANNEL.lstrip("@")}')]]
    await update.message.reply_text('Join channel terlebih dahulu.',reply_markup=InlineKeyboardMarkup(kb)); return False

async def start(update:Update,ctx:ContextTypes.DEFAULT_TYPE):
    if not await gate(update,ctx): return
    txt=f"STB Bot CLI (Bookworm 25.11, S905x)
Creds file: {'✅' if os.path.exists(CREDS_FILE) else '❌'}
Drive: {'✅' if drive.svc else '❌'}
Commands: /auth /setcreds /code /system"
    await update.message.reply_text(txt)
async def system(update:Update,ctx:ContextTypes.DEFAULT_TYPE):
    if not await gate(update,ctx): return
    mem=int(open('/proc/meminfo').readline().split()[1])//1024
    await update.message.reply_text(f"Arch: {platform.machine()}
Mem: {mem} MB
Creds: {os.path.exists(CREDS_FILE)}
Drive: {bool(drive.svc)}")
async def auth(update:Update,ctx:ContextTypes.DEFAULT_TYPE):
    if not await gate(update,ctx): return
    if not os.path.exists(CREDS_FILE):
        ctx.user_data['await']=True; await update.message.reply_text('Upload credentials.json',reply_markup=ForceReply()); return
    url,err=drive.auth_url();
    if err: await update.message.reply_text(err); return
    await update.message.reply_text(f'Open:
{url}
Kirim /code <kode>')
async def setcreds(update:Update,ctx:ContextTypes.DEFAULT_TYPE):
    if not await gate(update,ctx): return
    ctx.user_data['await']=True; await update.message.reply_text('Upload credentials.json baru',reply_markup=ForceReply())
async def code(update:Update,ctx:ContextTypes.DEFAULT_TYPE):
    if not await gate(update,ctx): return
    if not ctx.args: return await update.message.reply_text('Gunakan /code <authorization-code>')
    ok,err=drive.finish(' '.join(ctx.args))
    await update.message.reply_text('✅ Drive connected' if ok else '❌ '+err)
async def doc(update:Update,ctx:ContextTypes.DEFAULT_TYPE):
    if not ctx.user_data.get('await'): return
    doc=update.message.document
    if doc.file_name!='credentials.json': return await update.message.reply_text('nama harus credentials.json')
    p=f'/tmp/{random.randint(1,1e9)}.json'; await doc.get_file().download_to_drive(p)
    v,msg=drive.validate_creds(p)
    if not v: os.remove(p); return await update.message.reply_text('Invalid: '+msg)
    os.makedirs('/app/credentials',exist_ok=True)
    if os.path.exists(CREDS_FILE): drive.invalidate(); os.remove(CREDS_FILE)
    os.rename(p,CREDS_FILE); os.chmod(CREDS_FILE,0o600); drive.load(); ctx.user_data['await']=False
    await update.message.reply_text('✅ credentials.json diunggah, lanjut /auth')

def main():
    if not BOT_TOKEN: print('token?'); sys.exit(1)
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start',start)); app.add_handler(CommandHandler('system',system))
    app.add_handler(CommandHandler('auth',auth)); app.add_handler(CommandHandler('setcreds',setcreds))
    app.add_handler(CommandHandler('code',code))
    app.add_handler(MessageHandler(filters.Document.ALL,doc))
    app.run_polling()
if __name__=='__main__': main()
