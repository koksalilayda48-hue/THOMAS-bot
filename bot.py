import json
import os
import telebot
from threading import Thread

TOKEN = os.environ.get("BOT_TOKEN","8614343476:AAFLwJRSRco-kXUriXJfchq7ecyFeU3Gv2c")
KANAL_LINK = "@bedavakampanyalarorg"
GRUP_LINK = "vipgrubum"
ODUL_KULLANICI = "weghrumi1"

bot = telebot.TeleBot(TOKEN)

# ---------------------
# REFERANS VERİSİ
# ---------------------
def load_refs():
    try:
        with open("ref.json","r") as f:
            return json.load(f)
    except:
        return {}

def save_refs():
    with open("ref.json","w") as f:
        json.dump(REFERANS_DATABASE,f)

REFERANS_DATABASE = load_refs()

def add_ref(ref_id):
    uid = str(ref_id)
    REFERANS_DATABASE[uid] = REFERANS_DATABASE.get(uid,0) + 1
    save_refs()

def check_reward(user_id):
    uid = str(user_id)
    return REFERANS_DATABASE.get(uid,0) >= 25

# ---------------------
# ZORUNLU KANAL VE GRUP KONTROL
# ---------------------
def kanalda_ve_grupta_mi(user_id):
    try:
        uye = bot.get_chat_member(KANAL_LINK,user_id)
        kanal = uye.status in ["member","administrator","creator"]
    except:
        kanal = False

    try:
        uye2 = bot.get_chat_member(GRUP_LINK,user_id)
        grup = uye2.status in ["member","administrator","creator"]
    except:
        grup = False

    return kanal and grup

# ---------------------
# START KOMUTU
# ---------------------
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    ref = message.text.split()[1] if len(message.text.split())>1 else None

    if ref:
        try:
            ref = int(ref)
            if ref != user_id:
                add_ref(ref)
        except:
            pass

    # Zorunlu kontrol
    if not kanalda_ve_grupta_mi(user_id):
        bot.send_message(
            message.chat.id,
            f"🚨 Botu kullanabilmek için önce kanala ve gruba katılın:\n"
            f"{KANAL_LINK}\nhttps://t.me/{GRUP_LINK}"
        )
        return

    # Katıldıysa devam
    refs = REFERANS_DATABASE.get(str(user_id),0)
    bot.send_message(
        message.chat.id,
        f"✅ PANEL AKTİF\nReferans: {refs}\nBot işte referans linkin: {KANAL_LINK}\n\n"
        f"Komutlar:\n/durum\n/kampanya\n/odul"
    )

    # Ödül kontrolü
    if check_reward(user_id):
        try:
            odul_user = bot.get_chat(ODUL_KULLANICI)
            bot.send_message(odul_user.id,"🎉 25 referans toplandı! 2GB ödül hazır!")
        except Exception as e:
            print("Ödül mesajı gönderilemedi:",e)

# ---------------------
# DURUM KOMUTU
# ---------------------
@bot.message_handler(commands=["durum"])
def durum(message):
    user_id = message.from_user.id
    refs = REFERANS_DATABASE.get(str(user_id),0)
    kalan = max(25 - refs,0)
    odul = "✅ Ödül kazanıldı" if check_reward(user_id) else "❌ Ödül henüz kazanılmadı"

    bot.send_message(
        message.chat.id,
        f"📊 NUMBERONE PANEL\n\n"
        f"Referanslarınız: {refs} / 25\n"
        f"Kalan: {kalan} kişi\n"
        f"Referans linkiniz: {KANAL_LINK}\n\n"
        f"Ödül durumu: {odul}"
    )

# ---------------------
# ÖDÜL KOMUTU
# ---------------------
@bot.message_handler(commands=["odul"])
def odul(message):
    user_id = message.from_user.id
    if check_reward(user_id):
        bot.send_message(message.chat.id,"🎉 25 referans topladınız! 2GB ödül kazandınız.")
    else:
        bot.send_message(message.chat.id,f"🔹 Şu an {REFERANS_DATABASE.get(str(user_id),0)} referansınız var. 25 referansa ulaşınca ödül kazanacaksınız.")

# ---------------------
# TELEBOT 7/24 ÇALIŞMA
# ---------------------
def run_bot():
    bot.infinity_polling()

Thread(target=run_bot).start()
