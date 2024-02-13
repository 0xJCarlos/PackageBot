import os
import telebot
import requests
import time
import json

from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
RapidAPIKey = os.environ.get('X-RapidAPI-Key')

print("Bot starting...")

bot = telebot.TeleBot(BOT_TOKEN)

print("Bot started...")

# Dictionary to store latest updates for each tracking number
tracking_updates = {}
# Dictionary to store tracking numbers and their corresponding package IDs
packages = {}


def create_tracking(message):
    # Ask user for the tracking code
    bot.reply_to(message, "Por favor, introduce el código de seguimiento del paquete:")
    # Set a state to indicate that we are waiting for the tracking code
    bot.register_next_step_handler(message, process_tracking_code)

def process_tracking_code(message):
    track_code = message.text.strip()
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
    response = requests.post(url, data=payload, headers=headers)
    print("Status code: " + str(response.status_code))
    time.sleep(1)

    if response.status_code >= 200 and response.status_code < 300:
        package_id = str(response.json().get('pkgId'))
        print("ID del paquete retornado por la función create_tracking : " + package_id)
        # Store the tracking number and package ID in the packages dictionary
        packages[track_code] = package_id
        # Return the package ID
        bot.reply_to(message, f"Paquete añadido al seguimiento con ID: {package_id}")
        print(f"Paquete añadido al seguimiento con ID: {package_id}")
    elif (response.status_code == 429):
        bot.reply_to(message, "Se alcanzó el límite diario de solicitudes a la API de Postal Ninja.")
    else:
        bot.reply_to(message, "Hubo un error al crear el ID del paquete.")
        bot.reply_to(message, "Status de la Respuesta de la API de Postal Ninja: " + str(response.status_code))

def get_package_updates(message):
    # Display list of tracking numbers to choose from
    options = "\n".join([f"{index + 1}. {track_code}" for index, track_code in enumerate(reversed(packages.keys()))])
    bot.reply_to(message, f"Selecciona el número de seguimiento:\n{options}")
    # Set a state to indicate that we are waiting for the user to select a tracking number
    bot.register_next_step_handler(message, process_tracking_selection)

def process_tracking_selection(message):
    try:
        selection_index = int(message.text.strip()) - 1
        selected_track_code = list(reversed(packages.keys()))[selection_index]
        package_id = packages[selected_track_code]
        latest_update = fetch_package_updates(package_id)
        bot.reply_to(message, f"Última actualización para el paquete {selected_track_code}: {latest_update}")
    except Exception as e:
        bot.reply_to(message, "Opción inválida. Por favor, selecciona un número válido.")
        print("Error:", e)

def fetch_package_updates(package_id):
    url = f"https://postal-ninja.p.rapidapi.com/v1/track/{package_id}"
    querystring = {"await": "false", "lang": "AS_IS"}
    headers = {
        "Accept": "application/json; charset=UTF-8",
        "X-RapidAPI-Key": RapidAPIKey,
        "X-RapidAPI-Host": "postal-ninja.p.rapidapi.com"
    }
    time.sleep(1)
    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code >= 200 and response.status_code < 300:
        package_data = response.json().get('pkg')
        events = package_data.get('events', [])
        if "Package delivered" in events[-1].get('dsc'):
            latest_update = f"{events[-1].get('dt')}: {events[-1].get('dsc')}" if events else "No hay actualizaciones disponibles"
        else:
            latest_update = f"{events[-2].get('dt')}: {events[-2].get('dsc')}\n{events[-1].get('dt')}: {events[-1].get('dsc')}" if events else "No hay actualizaciones disponibles"
        print(str(latest_update))
        return latest_update
    else:
        print("Hubo un error de conexión a la API de Postal Ninja")
        return None

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    print("Message received: " + str(message.text.strip()))
    bot.reply_to(message, "Buenas, ¿Cómo andamos?")

@bot.message_handler(commands=['start_tracking'])
def start_tracking(message):
    create_tracking(message)

@bot.message_handler(commands=['see_updates'])
def see_updates(message):
    get_package_updates(message)

bot.infinity_polling()