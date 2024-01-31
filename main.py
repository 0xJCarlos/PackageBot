#Necessary imports
import os 
from dotenv import load_dotenv
import telebot
import requests


#Read Telegram and Postal Ninja API Token
load_dotenv() 
BOT_TOKEN = os.environ.get('BOT_TOKEN')
RapidAPIKey = os.environ.get('X-RapidAPI-Key')


#Initialize Bot
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start','hello'])
def send_welcome(message):
    bot.reply_to(message, "Buenas, ¿Como andamos?")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)

bot.infinity_polling()