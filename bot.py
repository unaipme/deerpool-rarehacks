from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from random import randrange
import telegram
import finder
import time
import i18n


def get_lang(update):
	return update.message.from_user.language_code


def rand_str(lang, code):
	n = int(i18n.t("strings.{}.{}-n".format(lang, code)))
	return i18n.t("strings.{}.{}-{}".format(lang, code, randrange(n)))


def unai(bot, update):
	#bot.send_message(chat_id=update.message.chat_id, text="Hey hola que tal?")
	#bot.send_contact(chat_id=update.message.chat_id, phone_number="112", first_name="Teléfono de emergencias")
	location_keyboard = telegram.KeyboardButton(text=i18n.t("strings.{}.share-loc".format(get_lang(update))), request_location=True)
	custom_keyboard = [[location_keyboard]]
	inline_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=update.message.chat_id, text=rand_str(get_lang(update), "give-location-pls"), reply_markup=inline_markup)


def location(bot, update):
	lang = get_lang(update)
	bot.send_message(chat_id=update.message.chat_id, text=rand_str(lang, "try-find-close-hospital"))
	poi = finder.find(lat=update.message.location.latitude, lng=update.message.location.longitude)
	results = [finder.get_details(poi[i].attrib["id"]) for i in range(0, len(poi))]
	bot.send_message(chat_id=update.message.chat_id, parse_mode=telegram.ParseMode.MARKDOWN,
					 text=i18n.t("strings.{}.closest-hospital-is".format(get_lang(update)), name=results[0]["name"]))
	bot.send_location(chat_id=update.message.chat_id, latitude=poi[0].attrib["lat"], longitude=poi[0].attrib["lon"])
	if len(results) > 1:
		time.sleep(1.5 + 0.5 * (len(results) - 1))
		other_options = rand_str(get_lang(update), "other-hospital-options") + "\n"
		for i in results[1:]:
			other_options += "∙ *{}*\n".format(i["name"])
		bot.send_message(chat_id=update.message.chat_id, text=other_options, parse_mode=telegram.ParseMode.MARKDOWN)

def echo(bot, update):
	print(update.message)
	bot.send_message(chat_id=update.message.chat_id, text="Algo\n∙ Algo")


i18n.load_path.append("lang")

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
