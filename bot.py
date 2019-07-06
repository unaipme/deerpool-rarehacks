# importing Telegram API
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram

def unai(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Hey hola que tal")
	bot.send_contact(chat_id=update.message.chat_id, phone_number= "112", first_name="Teléfono de emergencias")
	location_keyboard = telegram.KeyboardButton(text="Share your location", request_location=True)
	custom_keyboard = [[location_keyboard]]
	inline_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=update.message.chat_id, text="algo", reply_markup=inline_markup)

def location(bot, update):
	pass

def echo(bot, update):
	print(update.message.text)
	bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


# loading the access token from token.txt
TOKEN = open('token.txt').read().strip()

# call main Telegram objects
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

# handling callbacks functions to the commands
dispatcher.add_handler(CommandHandler('unai', unai))
dispatcher.add_handler(MessageHandler(Filters.location, location))
dispatcher.add_handler(MessageHandler(Filters.all, echo))

# starting the bot
updater.start_polling()

