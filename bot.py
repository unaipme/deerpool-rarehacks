from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
from telegram import ParseMode
import finder
import time


def unai(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Hey hola que tal?")
	print("H")
	#bot.send_contact(chat_id=update.message.chat_id, phone_number="112", first_name="Teléfono de emergencias")
	print("A")
	location_keyboard = telegram.KeyboardButton(text="Share your location", request_location=True)
	custom_keyboard = [[location_keyboard]]
	inline_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=update.message.chat_id, text="Would you be so kind as to share your location?", reply_markup=inline_markup)


def location(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Let me try to find a hospital that is close to you...")
	poi = finder.find(lat=update.message.location.latitude, lng=update.message.location.longitude)
	results = [finder.get_details(poi[i].attrib["id"]) for i in range(0, len(poi))]
	print(results)
	bot.send_message(chat_id=update.message.chat_id, parse_mode=ParseMode.MARKDOWN,
					 text="The closest hospital from your position is *{}*.".format(results[0]["name"]))
	bot.send_location(chat_id=update.message.chat_id, latitude=poi[0].attrib["lat"], longitude=poi[0].attrib["lon"])
	if len(results) > 1:
		time.sleep(1.5 + 0.5 * (len(results) - 1))
		other_options = "Other options could be:\n"
		for i in results[1:]:
			other_options += "∙ *{}*\n".format(i["name"])
		bot.send_message(chat_id=update.message.chat_id, text=other_options, parse_mode=ParseMode.MARKDOWN)

def echo(bot, update):
	print(update.message)
	#bot.send_message(chat_id=update.message.chat_id, text=update.message.text)
	bot.send_message(chat_id=update.message.chat_id, text="Algo\n∙ Algo")


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

