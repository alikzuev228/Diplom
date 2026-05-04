
import telebot



# Дані Telegram-бота
BOT_TOKEN = "8379068830:AAHWSxusQMhEIIOgXWUhlPWxitAqfRFATfQ" # Токен 

bot = telebot.TeleBot(BOT_TOKEN)

bot.send_message(-4810244717, f"test")

