import telebot
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import os

# Bot token
TOKEN = os.environ.get("BOT_TOKEN", "8614343476:AAFLwJRSRco-kXUriXJfchq7ecyFeU3Gv2c")
KANAL = "@bedavakampanyalarorg"
KANAL_LINK = "https://t.me/bedavakampanyalarorg"
REFERANS_DATABASE = {}

bot = telebot.TeleBot(TOKEN)

def kanalda_mi(user_id):
    try:
        uye = bot.get_chat_member(KANAL, user_id)
        return uye.status in ["member","administrator","creator"]
    except Exception as e:
        print("Kanal kontrol hatası:", e)
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    ref = message.text.split()[1] if len(message.text.split()) > 1 else None

    if ref:
        try:
            ref = int(ref)
            if ref != user_id:
                REFERANS_DATABASE[ref] = REFERANS_DATABASE.get(ref, 0) + 1
        except:
            pass

    if not kanalda_mi(user_id):
        bot.send_message(message.chat.id,
            f"🚀 NUMBERONE Sistemine hoş geldin\n\nBotu kullanmak için önce kanala katıl:\n{KANAL_LINK}\n\nKatıldıktan sonra tekrar /start yaz"
        )
        return

    refs = REFERANS_DATABASE.get(user_id, 0)
    link = f"{KANAL_LINK}?ref={user_id}"

    bot.send_message(message.chat.id,
        f"✅ NUMBERONE BOT AKTİF\n\nReferansın: {refs}\nReferans linkin: {link}\n\nKomutlar\n/durum\n/kampanya"
    )

@bot.message_handler(commands=['durum'])
def durum(message):
    user_id = message.from_user.id
    refs = REFERANS_DATABASE.get(user_id, 0)
    link = f"{KANAL_LINK}?ref={user_id}"

    bot.send_message(message.chat.id,
        f"📊 NUMBERONE PANEL\n\nReferans: {refs}/10\nKanal referans linkin: {link}\n\n10 kişi getirince kampanyaları görebilirsin."
    )

@bot.message_handler(commands=['kampanya'])
def kampanya(message):
    user_id = message.from_user.id
    refs = REFERANS_DATABASE.get(user_id, 0)

    if refs < 10:
        bot.send_message(message.chat.id,
            f"❌ Kampanyaları görmek için 10 referans gerekli\n\nSenin referansın: {refs}"
        )
        return

    siteler = {
        "Turkcell":"https://www.turkcell.com.tr/kampanyalar",
        "Vodafone":"https://www.vodafone.com.tr/kampanyalar",
        "Türk Telekom":"https://www.turktelekom.com.tr/kampanyalar",
        "Bimcell":"https://www.bimcell.com.tr/kampanyalar",
        "Pttcell":"https://www.pttcell.com.tr/kampanyalar",
        "Teknosacell":"https://www.teknosacell.com.tr/kampanyalar"
    }

    kampanyalar = []

    for site, url in siteler.items():
        try:
            r = requests.get(url, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            basliklar = soup.find_all("h3")
            for b in basliklar[:2]:
                kampanyalar.append(f"{site} ➜ {b.text.strip()}")
        except Exception as e:
            kampanyalar.append(f"{site} ➜ Kampanya alınamadı ({e})")

    bot.send_message(message.chat.id, "\n".join(kampanyalar))

# Flask server (Render için)
app = Flask('')

@app.route('/')
def home():
    return "KAMPANYA BOT AKTİF"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 3000)))

Thread(target=run).start()

# TELEBOT ARKA PLANDA KESİNTİSİZ
bot.infinity_polling()