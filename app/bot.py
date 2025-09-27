
    #!/usr/bin/env python3
    """
    STB HG680P Telegram Bot (Bookworm CLI-only)
    - File upload credentials.json (swapable)
    - Channel subscription gate
    - Commands: start, auth, setcreds, code, system, stats, d, t, dc, help
    - No GUI/X11, no AnyDesk
    """
    import os, json, logging, platform, random, sys
    from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    BOT_TOKEN=os.getenv('BOT_TOKEN')
    OWNER=os.getenv('OWNER_USERNAME','zalhera')
    CHANNEL=os.getenv('REQUIRED_CHANNEL','@ZalheraThink')
    CHANNEL_ID=int(os.getenv('CHANNEL_ID','-1001802424804'))
    TOKEN_FILE='/app/data/token.json'
    CREDS_FILE='/app/credentials/credentials.json'
    SCOPES=['https://www.googleapis.com/auth/drive']
    for d in ('/app/data','/app/credentials','/app/downloads','/app/torrents','/app/logs'): os.makedirs(d,exist_ok=True)
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s'); log=logging.getLogger('BOT')

    class Drive:
        def __init__(self):
            self.service=None; self.creds=None; self._load()
        def _load(self):
            if not (os.path.exists(CREDS_FILE) and os.path.exists(TOKEN_FILE)): return
            ci=json.load(open(CREDS_FILE))['installed']; tk=json.load(open(TOKEN_FILE))
            self.creds=Credentials(tk['token'],tk['refresh_token'],ci['client_id'],ci['client_secret'],tk.get('token_uri','https://oauth2.googleapis.com/token'),SCOPES)
            if self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request()); self._save()
            if self.creds.valid:
                self.service=build('drive','v3',credentials=self.creds,cache_discovery=False)
        def _save(self):
            with open(TOKEN_FILE,'w') as f:
                json.dump({'token':self.creds.token,'refresh_token':self.creds.refresh_token,'token_uri':self.creds.token_uri,'scopes':self.creds.scopes},f)
            os.chmod(TOKEN_FILE,0o600)
        def invalidate(self):
            if os.path.exists(TOKEN_FILE): os.remove(TOKEN_FILE)
            self.creds=None; self.service=None
        def validate(self,p):
            try:
                d=json.load(open(p)); inst=d['installed']
                for k in ('client_id','client_secret','auth_uri','token_uri'):
                    if k not in inst: return False,'missing '+k
                return True,'ok'
            except Exception as e:
                return False,str(e)
        def auth_link(self):
            if not os.path.exists(CREDS_FILE): return None,'upload creds'
            flow=InstalledAppFlow.from_client_secrets_file(CREDS_FILE,SCOPES)
            flow.redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            url,_=flow.authorization_url(access_type='offline',prompt='consent'); self._flow=flow; return url,None
        def finish(self,code):
            if not hasattr(self,'_flow'): return False,'/auth first'
            try:
                self._flow.fetch_token(code=code.strip()); self.creds=self._flow.credentials; self._save(); self.service=build('drive','v3',credentials=self.creds,cache_discovery=False); return True,''
            except Exception as e:
                return False,str(e)
    drive=Drive()

    def is_owner(u): return u and u.lower()==OWNER.lower()

    async def subscribed(ctx,user):
        if is_owner(user.username): return True
        try:
            m=await ctx.bot.get_chat_member(CHANNEL_ID,user.id); return m.status in ('member','administrator','creator')
        except:
            return False

    async def gate(update,ctx):
        if await subscribed(ctx,update.effective_user): return True
        kb=[[InlineKeyboardButton('Join',url=f'https://t.me/{CHANNEL.lstrip("@")}')]]
        await update.message.reply_text('Join channel terlebih dahulu.',reply_markup=InlineKeyboardMarkup(kb)); return False

    async def start(update:Update,ctx:ContextTypes.DEFAULT_TYPE):
        if not await gate(update,ctx): return
        creds='✅' if os.path.exists(CREDS_FILE) else '❌'; drive_stat='✅' if drive.service else '❌'
        await update.message.reply_text(f"HG680P Bot CLI (Bookworm)
Creds: {creds} Drive: {drive_stat}
Commands: /auth /setcreds /code /d /t /dc /system /stats /help")

    async def system(update:Update,ctx):
        if not await gate(update,ctx): return
        mem=int(open('/proc/meminfo').readline().split()[1])//1024
        await update.message.reply_text(f"Arch:{platform.machine()} Mem:{mem}MB Creds:{os.path.exists(CREDS_FILE)} Drive:{bool(drive.service)}")

    async def auth(update:Update,ctx):
        if not await gate(update,ctx): return
        if not os.path.exists(CREDS_FILE):
            ctx.user_data['await']=True; await update.message.reply_text('Upload credentials.json',reply_markup=ForceReply()); return
        url,err=drive.auth_link();
        if err: await update.message.reply_text(err); return
        await update.message.reply_text(f'Buka link, izinkan, copy code lalu /code <code>
{url}')

    async def setcreds(update,ctx):
        if not await gate(update,ctx): return
        ctx.user_data['await']=True; await update.message.reply_text('Upload credentials.json baru',reply_markup=ForceReply())

    async def code(update,ctx):
        if not await gate(update,ctx): return
        if not ctx.args: return await update.message.reply_text('Gunakan /code <authorization-code>')
        ok,err=drive.finish(' '.join(ctx.args))
        await update.message.reply_text('✅ Drive connected' if ok else '❌ '+err)

    async def upload(update,ctx):
        if not ctx.user_data.get('await'): return
        doc=update.message.document
        if doc.file_name!='credentials.json': return await update.message.reply_text('Nama file harus credentials.json')
        temp=f'/tmp/{random.randint(1,1e9)}.json'; await doc.get_file().download_to_drive(temp)
        valid,msg=drive.validate(temp)
        if not valid: os.remove(temp); return await update.message.reply_text('Invalid file: '+msg)
        if os.path.exists(CREDS_FILE): drive.invalidate(); os.remove(CREDS_FILE)
        os.makedirs('/app/credentials',exist_ok=True)
        os.rename(temp,CREDS_FILE); os.chmod(CREDS_FILE,0o600); drive._load(); ctx.user_data['await']=False
        await update.message.reply_text('✅ credentials.json diunggah, lanjut /auth')

    async def stats(update,ctx):
        if not await gate(update,ctx): return
        await update.message.reply_text('Stats feature belum dibuat')

    async def placeholder(update,ctx):
        if not await gate(update,ctx): return
        if not drive.service: return await update.message.reply_text('Connect Drive dulu')
        await update.message.reply_text('Fitur belum diimplementasi')

    def main():
        if not BOT_TOKEN:
            print('Set BOT_TOKEN env'); sys.exit(1)
        app=Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler('start',start)); app.add_handler(CommandHandler('system',system))
        app.add_handler(CommandHandler('auth',auth)); app.add_handler(CommandHandler('setcreds',setcreds))
        app.add_handler(CommandHandler('code',code)); app.add_handler(CommandHandler('stats',stats))
        app.add_handler(CommandHandler(['d','t','dc'],placeholder))
        app.add_handler(MessageHandler(filters.Document.ALL,upload))
        app.run_polling()
    if __name__=='__main__': main()
