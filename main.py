import os 
import telebot
import requests
import time

from dotenv import load_dotenv

load_dotenv() 
BOT_TOKEN = os.environ.get('BOT_TOKEN')
RapidAPIKey = os.environ.get('X-RapidAPI-Key')

print("Bot starting...")

bot = telebot.TeleBot(BOT_TOKEN)

print("Bot started...")

# Dictionary to store latest updates for each tracking number
tracking_updates = {}

def create_tracking(track_code):
    print("Código de seguimiento recibido: " + track_code)
    url = "https://postal-ninja.p.rapidapi.com/v1/track"

    payload = {"trackCode": track_code}
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Accept": "application/json; charset=UTF-8",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": RapidAPIKey,
        "X-RapidAPI-Host": "postal-ninja.p.rapidapi.com"
    }
    time.sleep(2) 
    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        package_id = response.json().get('pkgId')
        print("ID del paquete retornado por la función create_tracking : " + package_id)
        return package_id
    else:
        print("Hubo un error al crear el ID del paquete.")
        print("Status de la Respuesta de la API de Postal Ninja: " + str(response.status_code))
        if (response.status_code == 429):
            print("Se alcanzó el limite diario de solicitudes a la API de Postal Ninja.")
        return None

def get_package_updates(package_id):
    url = f"https://postal-ninja.p.rapidapi.com/v1/track/{package_id}"
    querystring = {"await": "false", "lang": "AS_IS"}
    headers = {
        "Accept": "application/json; charset=UTF-8",
        "X-RapidAPI-Key": RapidAPIKey,
        "X-RapidAPI-Host": "postal-ninja.p.rapidapi.com"
    }
    time.sleep(2) 
    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        package_data = response.json().get('pkg')
        events = package_data.get('events', [])
        latest_update = f"{events[-1].get('dt')}: {events[-1].get('dsc')}" if events else "No updates available"
        print(latest_update)
        return latest_update
    else:
        print("Hubo un error de conexión a la API de Postal Ninja")
        return None

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    print("Message received: " + str(message.text.strip()))
    bot.reply_to(message, "Buenas, ¿Cómo andamos?")

@bot.message_handler(func=lambda msg: True)
def handle_tracking_request(message):
    track_code = message.text.strip()
    print(track_code)

    if track_code in tracking_updates:
        latest_update = tracking_updates[track_code]
        bot.reply_to(message, f"El paquete ya está siendo rastreado. Última actualización: {latest_update}")
        print(f"El paquete ya está siendo rastreado. Última actualización: {latest_update}")
    else:
        package_id = create_tracking(track_code)

        if package_id:
            latest_update = get_package_updates(package_id)

            if latest_update:
                tracking_updates[track_code] = latest_update
                bot.reply_to(message, f"Paquete rastreado. Última actualización: {latest_update}")
                print(f"Paquete rastreado. Última actualización: {latest_update}")
            else:
                bot.reply_to(message, "No se pudo obtener la información del paquete en este momento.")
                print("No se pudo obtener la información del paquete en este momento.")
        else:
            bot.reply_to(message, "Hubo un error, revisa tu número de paquete o revisa la consola.")
            print("Hubo un error, revisa tu número de paquete o revisa la consola..")

@bot.message_handler(commands=['latest'])
def handle_latest_update_request(message):
    track_code = message.text.strip().split()[1] if len(message.text.strip().split()) > 1 else None

    if track_code in tracking_updates:
        latest_update = tracking_updates[track_code]
        bot.reply_to(message, f"Última actualización para el paquete {track_code}: {latest_update}")
        print(f"Última actualización para el paquete {track_code}: {latest_update}")
    else:
        bot.reply_to(message, "No se encontraron actualizaciones para este paquete.")
        print("No se encontraron actualizaciones para este paquete.")

bot.infinity_polling()