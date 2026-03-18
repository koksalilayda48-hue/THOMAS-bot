import telebot
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import os
import json

TOKEN = os.environ.get("BOT_TOKEN")

KANAL = "@bedavakampanyalarorg"
KANAL_LINK = "https://t.me/bedavakampanyalarorg"

ADMIN_ID = 33397779

bot = telebot.TeleBot(TOKEN)

# ---------------- DATA ----------------

def load_data():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except:
        return {"refs": {}, "users": {}}

def save_data():
    with open("data.json", "w") as f:
        json.dump(DATA, f)

DATA = load_data()

# ---------------- KANAL KONTROL ----------------

def kanalda_mi(user_id):
    try:
        uye = bot.get_chat_member(KANAL, user_id)
        return uye.status in ["member","administrator","creator"]
    except:
        return False

# ---------------- START ----------------

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    args = message.text.split()

    if user_id not in DATA["users"]:
        DATA["users"][user_id] = {"ref_by": None}

    # REFERANS
    if len(args) > 1:
        ref = args[1]
        if ref != user_id and DATA["users"][user_id]["ref_by"] is None:
            if ref not in DATA["refs"]:
                DATA["refs"][ref] = 0

            DATA["refs"][ref] += 1
            DATA["users"][user_id]["ref_by"] = ref
            save_data()

    # Kanal kontrol
    if not kanalda_mi(message.from_user.id):
        bot.send_message(
            message.chat.id,
            f"🚀 Botu kullanmak için kanala katıl:\n{KANAL_LINK}\n\nSonra tekrar /start"
        )
        return

    refs = DATA["refs"].get(user_id, 0)
    link = f"https://t.me/{KANAL.replace('@','')}?start={user_id}"

    bot.send_message(
        message.chat.id,
        f"""
✅ NUMBERONE BOT

Referansın: {refs}

Linkin:
{link}

/durum
/kampanya
"""
    )

# ---------------- DURUM ----------------

@bot.message_handler(commands=['durum'])
def durum(message):
    user_id = str(message.from_user.id)
    refs = DATA["refs"].get(user_id, 0)
    link = f"https://t.me/{KANAL.replace('@','')}?start={user_id}"

    bot.send_message(
        message.chat.id,
        f"📊 Referans: {refs}/10\n\nLink:\n{link}"
    )

# ---------------- KAMPANYA ----------------

@bot.message_handler(commands=['kampanya'])
def kampanya(message):
    user_id = str(message.from_user.id)
    refs = DATA["refs"].get(user_id, 0)

    if refs < 10:
        bot.send_message(message.chat.id, f"❌ 10 referans gerekli\nSenin: {refs}")
        return

    siteler = {
        "Turkcell":"https://www.turkcell.com.tr/kampanyalar",
        "Vodafone":"https://www.vodafone.com.tr/kampanyalar",
        "Türk Telekom":"https://www.turktelekom.com.tr/kampanyalar"
    }

    kampanyalar = []

    for site, url in siteler.items():
        try:
            r = requests.get(url, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            basliklar = soup.find_all("h3")
            for b in basliklar[:2]:
                kampanyalar.append(f"{site} ➜ {b.text.strip()}")
        except:
            kampanyalar.append(f"{site} ➜ alınamadı")

    bot.send_message(message.chat.id, "\n".join(kampanyalar))

# ---------------- ADMIN ----------------

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        "🔧 Admin Panel\n\n/reset_all\n/reset_user ID"
    )

@bot.message_handler(commands=['reset_all'])
def reset_all(message):
    if message.from_user.id != ADMIN_ID:
        return

    DATA["refs"] = {}
    DATA["users"] = {}
    save_data()

    bot.send_message(message.chat.id, "✅ Tüm veriler sıfırlandı")

@bot.message_handler(commands=['reset_user'])
def reset_user(message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = message.text.split()[1]

        DATA["refs"][user_id] = 0
        save_data()

        bot.send_message(message.chat.id, f"✅ {user_id} sıfırlandı")
    except:
        bot.send_message(message.chat.id, "Hatalı kullanım")

# ---------------- FLASK ----------------

app = Flask('')

@app.route('/')
def home():
    return "BOT AKTİF"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 3000)))

Thread(target=run).start()

# ---------------- START BOT ----------------

bot.infinity_polling()
